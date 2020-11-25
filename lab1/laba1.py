import pymysql
import matplotlib.pyplot as plt

connection = pymysql.connect(host='77.234.220.70',
                             user='mastercjpa',
                             password='TestPassword',
                             database='competencyjpa',
                             cursorclass=pymysql.cursors.DictCursor)


def get_skills(cursor, parent_ids=None, need_names=False):
    """ Функция получения навыков по их родителю

        :param cursor: объект для работы с бд
        :param parent_ids: строка из идентификаторов навыков
        :param need_names: флаг, нужно ли возвращать имя
        :return: если need_names=False (по дефолту), то список id
        если need_names=True, то словарь {id: name}
    """
    sql_get_skills = "select ID, NAME_RU from SKILL s where s.PARENT {}"

    cursor.execute(query=sql_get_skills.format('in (' + parent_ids + ')' if parent_ids else 'is NULL'))

    if need_names:
        return {str(root_id['ID']): str(root_id['NAME_RU']) for root_id in cursor.fetchall()}
    else:
        return [str(root_id['ID']) for root_id in cursor.fetchall()]


def get_child(cursor, parent_ids=None):
    """ Функция получения потомков навыка в дереве навыков

        :param cursor: объект для работы с бд
        :param parent_ids: строка из идентификаторов навыков"""
    skills = []

    list_of_level_skills = get_skills(cursor=cursor, parent_ids=parent_ids)
    skills.extend(list_of_level_skills)

    while list_of_level_skills:
        list_of_level_skills = get_skills(cursor=cursor, parent_ids=', '.join(list_of_level_skills))
        skills.extend(list_of_level_skills)

    return skills


def get_profile(cursor, skill_ids=None):
    """Функция получения списка уникальных идетификаторов пользователя по индетификаторам навыков"""
    sql_get_profile_with_skills = "select DISTINCT (OWNER) from COMPETENCY c where SKILL in ({})"

    cursor.execute(query=sql_get_profile_with_skills.format(skill_ids))
    return cursor.fetchall()


try:
    cursors = connection.cursor()
    # получаем самые первые навыки
    root_ids = get_skills(cursor=cursors)

    print('Quantity of root parentIds: ', len(root_ids))

    # получаем первых потомков навыков
    second_level_skills = get_skills(cursor=cursors, parent_ids=', '.join(root_ids), need_names=True)
    print('Quantity of second level skills: ', len(second_level_skills))

    # получаем потомков навыков из предыдущего шага
    target_list_of_skills = {}
    for skill in second_level_skills.keys():
        skill_child = get_child(cursor=connection.cursor(), parent_ids=skill)
        users = get_profile(cursor=connection.cursor(), skill_ids=', '.join(skill_child))
        target_list_of_skills[second_level_skills[skill]] = len(users)

    # рисуем диаграмму
    fig, ax = plt.subplots()
    first = list(target_list_of_skills.keys())
    second = list(target_list_of_skills.values())
    plt.barh(first, second)
    plt.show()

finally:
    connection.close()
