#!/home/investigator/anaconda3/envs/bots_chat/bin/python
# pdfCadastr.py - open pdf of landing plot and then export data to xlsx files.
import pdfx, os, re
import json
from pathlib import Path
import datetime
import csv
import requests




def emit_row(output_file, row): #get data to csv
    if output_file.is_file():
        with open(output_file, 'a') as o_file:
            fieldnames = row.keys()
            writer = csv.DictWriter(o_file, fieldnames=fieldnames)
            writer.writerow(row)
    else:
        with open(output_file, 'w') as o_file:
            fieldnames = row.keys()
            writer = csv.DictWriter(o_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(row)

def parsePdf(OUTPUT_FILE, OUTPUT_FILE_2, pdfFiles, regexStrings, PATH, region):
    relation = {}
    for filename in range(len(pdfFiles)):
        print(f'Working with...%s' % pdfFiles[filename])
        pdf = pdfx.PDFx(PATH + pdfFiles[filename])
        global text
        text = pdf.get_text()
        # print(text)
        for i in range(len(regexStrings)):
            try:
                # Find all matches in loop
                regex = re.compile(regexStrings[i][1], re.DOTALL|re.MULTILINE)
                regexVar = regex.search(text)
                stringStripN = regexVar.group(regexStrings[i][2]).strip('\n') #removing paragraphs
                replaceS = stringStripN.replace('\n', ' ') #replacing remaining paragraphs with spaces
                print(replaceS)
                if regexStrings[i] == regexStrings[2]: #if parsing place adding region string to place, if not skip this
                    relation[regexStrings[i][0]] = region + ' ' + replaceS
                else:
                    relation[regexStrings[i][0]] = replaceS
                if i == 4: #go to check owner in declarations
                    if relation['name_owner']:
                        declarationCheck(relation['name_owner'], OUTPUT_FILE_2)
            except AttributeError:
                print('No data in %s' % pdfFiles[filename])
                relation[regexStrings[i][0]] = 'No data'
        emit_row(OUTPUT_FILE, relation)  # putting all in csv

def declarationCheck(name, OUTPUT_FILE_2): #getting json data from declaration
    print(f'Checking declaratons of owner ... {name}')
    response = requests.get(f"https://declarations.com.ua/search?q=%22{name}%22"
                            f"&deepsearch=on&declaration_year%5B%5D=2021&declaration_year%5B%5D=2020&declaration_year%5B%5D=2019&declaration_year%5B%5D=2018&format=opendata") #request for all land owners
    response.raise_for_status()
    decl = json.loads(response.text)
    info = decl['results']['object_list']
    for i in range(len(info)):
        relation = {}  # forming dictionary to record key(fields name) and values from e data
        """getting all data - making field names and values"""
        print(f"Getting declartions of ... {info[i]['infocard']['last_name']}")
        relation['owner_name'] = name
        relation['first_name'] = info[i]['infocard']['first_name']
        relation['patronymic'] = info[i]['infocard']['patronymic']
        relation['last_name'] = info[i]['infocard']['last_name']
        relation['declaration_year'] = info[i]['infocard']['declaration_year']
        relation['office'] = info[i]['infocard']['office']
        relation['position'] = info[i]['infocard']['position']
        relation['url'] = info[i]['infocard']['url']
        emit_row(OUTPUT_FILE_2, relation)  # putting all in csv

    ######################################
def main(directory, region):
    print(directory)
    print(region)
    PATH = f'{directory}/'
    TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    OUTPUT_FILE = Path(f'{PATH}output_1_{TIMESTAMP}.csv')
    OUTPUT_FILE_2 = Path(f'{PATH}output_2_{TIMESTAMP}.csv')

    regexStrings = [["number", "(\d{10}:\d{2}:\d{3}:\d{4})", 0],  # parse number of plot
                    # ["area", "(Площа.*ділянки.*Місце розташування)(.*)(\n\d[\.]?\d*\n)(Волинська)", 3],
                    ["area", f"(Площа.*ділянки.*Місце розташування)(.*)(\n\d+[\.]?\d*\n)({region})", 3],
                    # ["place", "(Волинська.{1,90}рад[и|а])", 0],  # parse place in Volyn
                    ["place", "(область.{1,90}рад[и|а])", 0],  # parse place
                    ["price", "(Значення, гривень\n)(.*)(\n\d{3,}[\.]\d+)", 3],  # parse price
                    ['name_owner',
                     '(Прізвище.* фізичної)(.*)(\n[А-ЩЬЮЯЇІЄҐ]\w+[-]*\w+\s[А-ЩЬЮЯЇІЄҐ]\w+\s[А-ЩЬЮЯЇІЄҐ]\w+\n)', 3],
                    # parse name of owner
                    ['company_owner', '(права власності.+)(\n+.*\n+.+)(\n+)(.+юрид.+)(\n+)(.+)(\n|\s)(.+)', 8],
                    # parse name of owner
                    ['date_register', '(Дата державної.*)(\n\n\d\d\.\d\d\.\d{4})', 2],  # parse date of register
                    ['rent_company', '(право оренди земельної ділянки)(\n*)(.+)(\"|\»)(\n)', 3],  # parse rent company
                    ['rent_person',
                     '(право оренди земельної ділянки)(\n*[А-ЩЬЮЯЇІЄҐ]\w+[-]*\w+\s[А-ЩЬЮЯЇІЄҐ]\w+\s[А-ЩЬЮЯЇІЄҐ]\w+\n*)',
                     2]]  # parse name of rent person
    # Get all the PDF filenames.
    pdfFiles = []
    for filename in os.listdir(PATH):
        if filename.endswith('pdf'):
            pdfFiles.append(filename)
    pdfFiles.sort(key=str.lower)
    parsePdf(OUTPUT_FILE, OUTPUT_FILE_2, pdfFiles, regexStrings, PATH, region)
    print('Done')
