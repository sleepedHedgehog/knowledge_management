from datetime import datetime
import random
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


class Server:

    def __init__(self, kp=None):

        print("Инициализация клиента")
        self.kp = kp if kp else m3_kp_api()

        self.subscriber_list = {}

    def handle(self, added, removed):

        print('Server reporting: {}'.format(datetime.now()))
        print('    added', added)
        print('    removed', removed)

        for data in added:
            print("Input data: " + str(data))

            # Клиент хочет начать игру
            if str(data[1]) == 'game':
                print(str(data[1]))
                self.kp.load_query_rdf(Triple(URI(data[0]), URI("game"), Literal("1")))

                # Проверяем, есть ли начатая игра, если есть - отправляем ошибку
                if len(self.kp.result_rdf_query) == 1:
                    self.subscriber_list.update({data[0]: random.randint(0, 100)})
                    self.kp.load_rdf_insert(Triple(URI(data[0]), URI("response"), Literal("1")))
                else:
                    self.kp.load_rdf_insert(Triple(URI(data[0]), URI("response"), Literal("error")))

            # Клиент прислал свою догадку
            elif str(data[1]) == 'answer':
                print(str(data[1]))
                target_number = self.subscriber_list.get(data[0])
                try:
                    # Игра не была инициализирована - отправяем ошибку
                    if target_number is None:
                        self.kp.load_rdf_insert(Triple(URI(data[0]), URI("response"), Literal("error")))
                        # Клиент угадал, отправляем ответ, удаляем информацию об игре
                    elif int(str(data[2])) == target_number:
                        self.kp.load_rdf_insert(Triple(
                            URI(data[0]), URI("response"), Literal("{}:1".format(target_number))))
                        del self.subscriber_list[data[0]]
                        self.kp.load_rdf_remove(Triple(URI(data[0]), URI("game"), Literal("1")))
                    else:
                        # Клиент не угадал
                        self.kp.load_rdf_insert(Triple(
                            URI(data[0]), URI("response"), Literal("{}:2".format(str(data[2])))))
                except:
                    self.kp.load_rdf_insert(Triple(URI(data[0]), URI("response"), Literal("error")))


kp = m3_kp_api(PrintDebug=True)

subscription_triple = Triple(None, None, None)
handler = Server(kp)

handler_subscription = kp.load_subscribe_RDF(subscription_triple, handler)
