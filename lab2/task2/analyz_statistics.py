import csv

PATH_TO_CSV = "Stats/"
FILE_NAME_DRIVER_1 = "2018-07-10-pure_param_stats_driver1.csv"
FILE_NAME_DRIVER_2 = "2018-06-27-pure_param_stats_driver2.csv"
DELIMITER_SEMICOLON = ";"

# Определяем классы
HIGH_THRESHOLD_OF_SENSITIVITY = 1
MEDIUM_THRESHOLD_OF_SENSITIVITY = 0.5
LOW_THRESHOLD_OF_SENSITIVITY = 0


def classification(z_value):
    """ Функция для классификации переданного параметра в зависимости от его значения
        :param z_value: значение (координаты Z - колонка датасета AccelerationXYZ)
        :return: float or None

    """
    abs_z = abs(z_value)

    if 0.1 < abs_z < 0.5:
        return LOW_THRESHOLD_OF_SENSITIVITY
    elif 0.5 <= abs_z < 1.5:
        return MEDIUM_THRESHOLD_OF_SENSITIVITY
    elif abs_z >= 1.5:
        return HIGH_THRESHOLD_OF_SENSITIVITY
    else:
        # Это секция на случай, если переданное значение не должно быть классифицированно
        return None


def rating_calculation(csv_file, delimiter=DELIMITER_SEMICOLON):
    """ Функция для определения стиля вождения водителя

    :param csv_file: Путь к файлу с датасетом
    :param delimiter: Разделитель в датасете, по умолчанию - точка с запятой
    :return: среднее значение массива маневров
    """
    maneuver_sensitives_list = []  # Список среднеарифметического для каждого маневра
    maneuver_sum = 0  # Сумма всех классов событий текущего маневра
    maneuver_count = 0  # Количество событий в текущем маневре
    is_negative = None  # Флаг для отслеживания окончания маневра

    with open(csv_file) as f:
        file = csv.DictReader(f, delimiter=delimiter)

        for row in file:

            # Получаем значение координаты Z и классифицируем его
            z_value = float(row["AccelerationXYZ"].split(',')[2])
            z_class = classification(z_value)

            # Если это первая итерация цикла, то определяем текущий знак маневра
            if is_negative is None:
                is_negative = z_value < 0

            # Если маневр окончился, то определяем новый
            if (z_value < 0) != is_negative:
                is_negative = z_value < 0

                # Проверка на случай, если несколько маневров подряд не учитывались, но знак менялся
                if maneuver_count != 0:
                    # Создаем новый маневр
                    maneuver_sensitives_list.append(maneuver_sum / maneuver_count)
                    maneuver_sum, maneuver_count = 0, 0

            #  Добавляем в значение в текущий
            if z_class is not None:
                maneuver_sum += z_class
                maneuver_count += 1

        return sum(maneuver_sensitives_list) / len(maneuver_sensitives_list)


print(rating_calculation(PATH_TO_CSV + FILE_NAME_DRIVER_1))
print(rating_calculation(PATH_TO_CSV + FILE_NAME_DRIVER_2))

