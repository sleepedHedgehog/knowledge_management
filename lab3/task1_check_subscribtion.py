import os
from time import sleep
from datetime import datetime
import random

from smart_m3.m3_kp_api import *


class Writer:
    """Класс для """
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        print('Agent_X reporting: {}'.format(datetime.now()))
        print('    added', added)
        print('    removed', removed)

        for data in added:
            if str(data[1]) == 'trash_value':
                print("!!! KP_sub_reaction !!! Garbage in the smart space :(")
                break

        for data in removed:
            if str(data[1]) == 'trash_value':
                print("!!! KP_sub_reaction !!! Some garbage was removed! :)")
                break

    def write_and_check(self, delay=1, count=5):
        """Функция для записи триплета раз в delay секунд count раз"""
        for _ in range(count):
            number = random.randint(10, 50)
            triple = Triple(URI('Agent_X'), URI("has_item"), Literal(number))
            print("Add triple: " + str(triple))
            self.kp.load_rdf_insert(triple)
            sleep(delay)


class Listener:
    def __init__(self, kp=None):
        self.kp = kp

    def handle(self, added, removed):
        print('Agent_X reporting: {}'.format(datetime.now()))
        print('    added', added)
        print('    removed', removed)

        for data in added:
            if str(data[1]) == 'trash_value':
                print("!!! KP_sub_reaction !!! Garbage in the smart space :(")
                break

        for data in removed:
            if str(data[1]) == 'trash_value':
                print("!!! KP_sub_reaction !!! Some garbage was removed! :)")
                break

    def check_and_del(self, delay=1, count=2):
        """Функция для удаления триплета раз в delay секунд count раз, если его литерал будет четным числом"""
        for _ in range(count):
            self.kp.load_query_rdf(Triple(URI('Agent_X'), URI("has_item"), None))
            for result in self.kp.result_rdf_query:

                str_result = str(result)
                print("Check " + str_result)
                number = str_result.split()[2][1:3]

                # Проверяем на четность
                if int(number) % 2 == 0:
                    print("Delete " + str_result)
                    self.kp.load_rdf_remove(result)

            sleep(delay)


if __name__ == '__main__':
    kp = m3_kp_api()

    subscription_triple = Triple(None, None, None)
    print("Подключение Writer")
    writer = Writer(kp)
    writer_subscription = kp.load_subscribe_RDF(subscription_triple, writer)

    print("Подключение Listener")
    listener = Listener(kp)
    listener_subscription = kp.load_subscribe_RDF(subscription_triple, listener)

    # на случай ошибок, чтобы корректно отключилось все
    try:
        writer.write_and_check()
        # Проверим, что подписка работает
        kp.load_query_rdf(Triple(URI('Agent_X'), URI("has_item"), None))
        assert len(kp.result_rdf_query) > 0

        listener.check_and_del()

    except Exception as e:
        print(e)

    finally:
        print("Отключение всего")
        kp.load_unsubscribe(writer_subscription)
        kp.load_unsubscribe(listener_subscription)

        kp.clean_sib()

        kp.leave()
        raise os._exit(0)
