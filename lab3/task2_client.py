import os
import string
from datetime import datetime, time
import random
from time import sleep

from smart_m3.m3_kp_api import *


# AgentUniqId / game / {1 - новая, 0 - завершить}
# AgentUniqId / response / {0 - no, 1 - yes, "error"} - Ответ клиента
# AgentUniqId / answer / {"number": 0 - no, 1 - yes} - Ответ сервера

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

    def handle(self, added, removed):
        print('Agent_X reporting: {}'.format(datetime.now()))
        print('    added', added)
        print('    removed', removed)

    def start_game(self, count=3, sleep_time=1):
        """Метод для начала игры"""
        self.kp.load_rdf_insert(Triple(URI(self.agent_name), URI("game"), Literal(1)))

        requests = 0
        while requests <= count:
            self.kp.load_query_rdf(Triple(URI(self.agent_name), URI("response"), None))
            if self.kp.result_rdf_query:
                literal = str(self.kp.result_rdf_query[-1])
                if literal == "1":
                    return True
                elif literal == "error":
                    return False

            requests += 1
            sleep(sleep_time)

        return False

    def guesser(self, sleep_time=1, count=3):
        """Метод для угадывания чисел в игре"""

        print("Введите число")
        number = input()
        try:
            if number == "quit" or number == "QUIT":
                print("Завершение работы")
                return True

            if 0 > int(number) > 100:
                raise EOFError
        except (TypeError, EOFError):
            print("Неверно задано число")

        self.kp.load_rdf_insert(Triple(URI(self.agent_name), URI("answer"), Literal(number)))

        requests = 0
        while requests <= count:
            sleep(sleep_time)
            self.kp.load_query_rdf(Triple(URI(self.agent_name), URI("response"), None))
            list_of_result = [res.split()[2] for res in self.kp.result_rdf_query]

            for result in list_of_result:
                if int(result.split(":")[0]) == number:
                    print("Вы угадали. Это было число: " + number)
                    return True

            requests += 1

        return False


kp = m3_kp_api(PrintDebug=True)

subscription_triple = Triple(None, None, None)
handler = Client(kp)

handler_subscription = kp.load_subscribe_RDF(subscription_triple, handler)

flag_started_game = False
while not flag_started_game:
    handler.agent_name = ''.join([random.choice(string.ascii_letters) for _ in range(10)])
    flag_started_game = handler.start_game()
    time.sleep(1)

flag_guesser = False
while not flag_guesser:
    flag_guesser = handler.guesser()

kp.load_unsubscribe(handler_subscription)

kp.clean_sib()
kp.leave()

raise os._exit(0)
