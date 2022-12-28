import os
import time
import telepot
from telepot.loop import MessageLoop
import pdfCadastr_2021
from pathlib import Path
import datetime
import zipfile
import glob
import logging

logging.basicConfig(filename='land_bot_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    logging.debug(content_type, chat_type, chat_id)
    if content_type == 'text' and "ська" in msg["text"]:
        print(msg["text"])
        logging.debug(msg["text"])
        global region
        region = msg["text"]
        bot.sendMessage(chat_id, f"Дякую, працюємо з... {region} область")
        bot.sendMessage(chat_id, "Запакуйте пдф файли у zip (!!!!) архів та завантажте його в телеграм (обсяг файлу не може бути більше 20 Мб)")

    elif content_type == 'text':
        bot.sendMessage(chat_id, "Привіт! Я бот, хочу допомогти тобі системізувати дані по земельних ділянках. Для цього зробіть наступне: "
                                 "\n- вкажіть область з великої літери (наприклад: Волинська)")
        print(msg["text"])
        logging.debug(msg["text"])

    if content_type == 'document':
        file_id = msg['document']['file_id']
        print(file_id)
        logging.debug(file_id)

        # ##### download_file, smaller than one chunk (65K)
        TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        directory = f'dir_{chat_id}_{TIMESTAMP}'
        print(f'Directory: {directory}')
        logging.debug(f'Directory: {directory}')
        Path(directory).mkdir(exist_ok=True) #creating a new directory if not exist
        # if not os.path.exists(directory):
        #     os.mkdir(directory)
        print(f'Directory is made... {directory}')
        logging.debug(f'Directory is made... {directory}')
        inputFile = f'{directory}/input_file_{TIMESTAMP}.zip'
        print(f'Downloading file to {inputFile}')
        logging.debug(f'Downloading file to {inputFile}')
        bot.download_file(file_id, inputFile)
        bot.sendMessage(chat_id, "Дякую, файл отриманий і опрацьовується... Треба почекати-:)")
        with zipfile.ZipFile(inputFile) as zip_file: #extracting files
            print("zip_file.extractall")
            logging.debug("zip_file.extractall")
            zip_file.extractall(directory)
        pdfCadastr_2021.main(directory, region)
        # let the human know that the file is on its way
        bot.sendMessage(chat_id, "готую файл для відправки ...")
        file = glob.glob(f"{directory}/output_1_*.csv")
        file2 = glob.glob(f"{directory}/output_2_*.csv")
        print(file[0], file2[0]) #glob returns file in list format :(
        logging.debug(file[0], file2[0]) #glob returns file in list format :(
        # send the pdf doc
        bot.sendDocument(chat_id=chat_id, document=open(file[0], 'rb'))
        bot.sendDocument(chat_id=chat_id, document=open(file2[0], 'rb'))

        bot.sendMessage(chat_id, "Тримай! Чекаю від тебе крутого викриття. "
                                 "\nЯк імпортувати в csv файли в ексель"
                                 "\n Читайте тут: https://support.microsoft.com/uk-ua/office/%D1%96%D0%BC%D0%BF%D0%BE%D1%80%D1%82-%D1%96-%D0%B5%D0%BA%D1%81%D0%BF%D0%BE%D1%80%D1%82-%D1%82%D0%B5%D0%BA%D1%81%D1%82%D0%BE%D0%B2%D0%B8%D1%85-%D1%84%D0%B0%D0%B9%D0%BB%D1%96%D0%B2-txt-%D0%B0%D0%B1%D0%BE-csv-5250ac4c-663c-47ce-937b-339e391393ba")
        del directory #deleting varibale, in order to create a new one

# replace XXXX.. with your token
TOKEN = os.environ.get('LANDBOT')
bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')
logging.debug('Listening ...')
# Keep the program running.
while 1:
    time.sleep(10)
