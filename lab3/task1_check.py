import os
from datetime import datetime
from random import random

from smart_m3.m3_kp_api import *


class KPHandler:
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


if __name__ == '__main__':
    kp = m3_kp_api(PrintDebug=True)

    subscription_triple = Triple(None, None, None)
    handler = KPHandler(kp)

    handler_subscription = kp.load_subscribe_RDF(subscription_triple, handler)

    # Могут возникать ошибки при проверках, добавлено, чтобы корректно выходить
    try:
        insert_list = [Triple(URI('Agent1'), URI("take_new_lab"), Literal(3)),
                       Triple(URI('Agent1'), URI("make_lab"), Literal("rrr")),
                       Triple(URI('Agent1'), URI("defend_lab"), Literal(5))]

        print('Добавление триплетов в хранилище')
        kp.load_rdf_insert(insert_list)

        single_triple = Triple(URI('Agent1'), URI("make_more_research"), Literal(10))
        kp.load_rdf_insert(single_triple)

        # Несколько запросов с проверками
        print('Проверка запросов')
        kp.load_query_rdf(single_triple)
        assert kp.result_rdf_query[0][0] == single_triple[0]
        assert kp.result_rdf_query[0][1] == single_triple[1]

        kp.load_query_rdf(Triple(None, URI("take_new_lab"), Literal(3)))

        kp.load_query_rdf(Triple(URI('Agent1'), None, Literal("rrr")))
        assert kp.result_rdf_query == insert_list[0]

        kp.load_query_rdf(Triple(None, None, None))
        assert len(kp.result_rdf_query) == 4

        new_triples = []

        # Проапдейтим
        for rdf in kp.result_rdf_query:
            new_triples.append(Triple(rdf[0], rdf[1], Literal(random.randint(-10, 20))))

        kp.load_rdf_update(new_triples, kp.result_rdf_query)

        kp.load_query_rdf(Triple(None, None, None))
        assert len(kp.result_rdf_query) == 4

        # Ввожу неправильное значение
        kp.load_rdf_remove(Triple(URI('Agent_1'), None, None))

        kp.load_query_rdf(Triple(URI('Agent_1'), None, None))
        assert len(kp.result_rdf_query) == 0

        # Ну теперь можно и правильное
        kp.load_rdf_remove(insert_list[0])

        kp.load_query_rdf(insert_list[0])
        assert len(kp.result_rdf_query) == 0

    except Exception as e:
        print(e)

    finally:
        kp.load_unsubscribe(handler_subscription)

        kp.clean_sib()
        kp.leave()

        raise os._exit(0)
