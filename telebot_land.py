import telebot
import requests

token = '2073537137:AAESpDgrCAOIDLYClFtG3-zc5LAl6baZS9k'

bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['text'])
def repeat_all_message(message):
  print(message.text)
  bot.send_message(message.chat.id,message.text)

@bot.message_handler(content_types=["document", "video", "audio"])
def handle_files(message):
  document_id = message.document.file_id
  file_info = bot.get_file(document_id)
  print(document_id) # Выводим file_id
  print(f'http://api.telegram.org/file/bot{token}/{file_info.file_path}') # Выводим ссылку на файл
  bot.send_message(message.chat.id, document_id) # Отправляем пользователю file_id

if __name__ == '__main__':
  bot.polling(none_stop=True)