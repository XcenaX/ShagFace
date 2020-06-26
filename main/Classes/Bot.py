import telebot
import sqlite3
import threading
import datetime
from telebot import types

from django.conf import settings


from main.models import Security, Student, Visit, Face, BotUser

class Bot(object):
    bot = None
    
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.bot = telebot.TeleBot(settings.BOT_TOKEN)
        
        threading.Thread(target=self.update, args=()).start()


    def sendNotification(self, student):
        parent = BotUser.objects.filter(student=student)[0]
        current_datetime = datetime.datetime.now()
        message_text = student.fullname + ' прибыл в академию! Время: ' + current_datetime.strftime("%Y-%m-%d %H:%M:%S") + '.'
        self.bot.send_message(parent.chat_id, message_text)


    def setup_bot(self):
        @self.bot.message_handler(commands=['start'])
        def start_message(message):
            self.bot.send_message(message.chat.id, 'Добро пожаловать! Данный бот умеет уведомлять вас о каждом посещении вашего ребенка академию ШАГ! Для того, чтобы зарегистрироваться и начать работу, вам нужно ввести Email вашего ребенка. ВАЖНО: нужно указать ту почту, которая указана у  ребенка в mystat!')

        @self.bot.message_handler(content_types=['text'])
        def registerparent(message):
            message_text = message.text
            response_text = ''
            if len(BotUser.objects.filter(chat_id=message.chat.id)) > 0:
                response_text = 'На данный момент бот не умеет поддерживать разговоры) Вы уже зарегистрированы, бот уведомит вас, когда ваш ребенок посетит академию ШАГ!'
            else:
                if len(Student.objects.filter(email=message_text)) > 0:
                    print('[INFO] STUDENT FOUND!!!!!!')
                    student = Student.objects.filter(email=message_text)[0]
                    if len(BotUser.objects.filter(student=student)) > 0:
                        print('[INFO] BOT USER ALREADY EXISTS')
                        response_text = 'Родители этого студента уже зарегистрированы!'
                    else:
                        print('[INFO] CREATING NEW BOT USER')
                        BotUser.objects.create(student=student, chat_id=message.chat.id)
                        response_text = 'Регистрация прошла успешно! Бот будет уведомлять вас о посещениях вашего ребенка академии ШАГ!'
                else:
                    print('[INFO] STUDENT NOT FOUND')
                    response_text = 'Студент с такой почтой не найден!'    
            
            self.bot.send_message(message.chat.id, response_text)

    def update(self):
        self.setup_bot()
        self.bot.polling()
        