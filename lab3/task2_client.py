import string
from datetime import datetime
import random

from smart_m3.m3_kp_api import *

# Клиент отправляет серверу запрос вида Triple(URI(AgentId), URI("game"), Literal(1))
# Сервер проверяет, есть ли уже созданная игра
# Если созданная игра есть, то приходит ошибка вида Triple(URI(AgentId), URI("response"), "неверное имя")
# Если нет, то создает игру.
# Клиет отправляет серверу запрос вида Triple(URI(AgentId), URI("answer"), Literal(число))
# Если число совпало, то сервер отправляет ответ вида Triple(URI(AgentId), URI("response"), Literal("number:1"))
# Если число не совпало, то сервер отправляет ответ вида Triple(URI(AgentId), URI("response"), Literal("number:0"))
# Если клиент хочет завершить игру, не угадав число, то он отправляет запрос вида
# Triple(URI(AgentId), URI("game"), Literal(0))
# В этом случае сервер удаляет данные о начале игры


class Client:

    def __init__(self, kp=None):

        print("Инициализация клиента")
        self.kp = kp if kp else m3_kp_api()
        self.agent_name = None
        self.start = False
        self.current_number = None

    def handle(self, added, removed):
        print('Client reporting: {}'.format(datetime.now()))
        print('    added', added)
        print('    removed', removed)

        for data in added:
            print("Input data: " + str(data))

            if str(data[0]) == self.agent_name and str(data[1]) == "response" and self.start:
                # Если сервер вернул ошибку
                if str(data[2]) == Literal("error"):
                    print("Произошла ошибка")
                    self.start_game()

                # Если сервер подтвердил начало игры
                elif str(data[2]) == "1":
                    self.guesser()

                # Если сервер отреагировал на запрос клиента
                elif str(data[2]) == "{number}:1".format(number=self.current_number):
                    raise Exception("Вы угадали. Это было число: " + self.current_number)

                elif str(data[2]) == "{number}:2".format(number=self.current_number):
                    print("Число: " + self.current_number + " неправильное")
                    self.guesser()

    def start_game(self):
        """Метод для начала игры"""
        self.agent_name = ''.join([random.choice(string.ascii_letters) for _ in range(10)])
        self.start = True
        self.kp.load_rdf_insert(Triple(URI(self.agent_name), URI("game"), Literal(1)))

    def guesser(self):
        """Метод для угадывания чисел в игре"""

        print("Введите число или quit")
        self.current_number = input()
        try:
            if self.current_number == "quit" or self.current_number == "QUIT":
                print("Завершение работы")
                raise Exception("Приложение завершено пользователем")

            if (0 > int(self.current_number)) or (int(self.current_number) > 100):
                raise EOFError

            self.kp.load_rdf_insert(Triple(URI(self.agent_name), URI("answer"), Literal(self.current_number)))

        except (TypeError, EOFError):
            print("Неверно задано число")
            self.guesser()

        return False


kp = m3_kp_api(PrintDebug=True)

subscription_triple = Triple(None, None, None)
handler = Client(kp)

handler_subscription = kp.load_subscribe_RDF(subscription_triple, handler)
handler.start_game()
