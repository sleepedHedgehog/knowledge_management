import json
from mediawiki import MediaWiki, PageError
import Levenshtein

WIKIPEDIA_URL = "https://ru.wikipedia.org/"


def check_levenshtein(name1, name2, targat_value=5):
    """ Метод для проверки растояния Левенштейна между двумя словами

    :param name1: Первое слово
    :param name2: Второе слово
    :param targat_value: Максимальное расстояние
    :return: boolean
    """
    return Levenshtein.distance(name1, name2) < targat_value


with open("task1.json", "r", encoding="utf8") as read_file:
    results = json.load(read_file)

    wikipedia = MediaWiki()
    wiki_results = []

    for res in results["elements"]:
        # Отлов ошибок, если не нашлось никаких страниц
        try:
            # Если в данных уже есть нужный тег
            if "wikipedia" in res["tags"]:
                search_page = wikipedia.page(res["tags"]["wikipedia"][3:])
            else:
                # Отлов ошибок, если в запросе нет имени
                try:
                    # Поиск по координатам
                    page_names = wikipedia.geosearch(latitude=res["lat"], longitude=res["lon"])
                    page_name = [name for name in page_names if check_levenshtein(name, res["tags"].get("name"))]

                    if not page_name and res["tags"].get("name"):
                        page_names = wikipedia.search(res["tags"].get("name"))
                        page_name = [name for name in page_names if check_levenshtein(name, res["tags"].get("name"))]

                    if page_name:
                        search_page = wikipedia.page(page_name[0])

                except TypeError:
                    continue

            if search_page:
                # Дополняем данные из первого задания
                page_dict = {"summary": search_page.summary,
                             "categories": search_page.categories,
                             "images": search_page.images}
                res.update(page_dict)
                wiki_results.append(res)
        except PageError:
            continue

    with open('task2_query.txt', 'w') as file:
        json.dump(wiki_results, file)
