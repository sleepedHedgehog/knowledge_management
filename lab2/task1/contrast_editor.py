from datetime import datetime

from skimage import io

PATH_TO_IMAGE = "\\TestHeadPose2\\TestHeadPose\\"
PATH_TO_NEW_IMAGE = "file1.jpg"
IMAGE_NAME = "online_test_3_FAIL.jpg"


def change_contrast(path_to_image=PATH_TO_IMAGE + IMAGE_NAME, correction=256, path_to_new_image=PATH_TO_NEW_IMAGE):
    """ Метод для изменения контрастности изображения

    :param path_to_image: Полный путь до файла с изображением
    :param correction: Значение коррекции, на которое должно быть улучшенно изображение
    :param path_to_new_image: Полный путь, по которому должно быть сохранено изображение

    """
    # Получаем массив пикселей изображения
    image = io.imread(fname=path_to_image)

    # Вычисляем среднюю яркость пикселя
    iab = 0

    for row in image:
        for colom in row:
            iab += (0.299 * colom[0] + 0.587 * colom[1] + 0.114 * colom[2])

    iab /= image.size

    # Определяем коэффициент коррекции
    k = 1 + correction / 100

    # Формируем список с целевыми значениями яркости пикселя
    b = []
    for row in range(256):
        temp = iab + k * (row - iab)
        temp = 0 if temp < 0 else 255 if temp >= 255 else temp

        b.append(temp)

    # Применяем список из предыдущего шага к массиву пикселей
    for old_row in range(len(image)):
        for old_colom in range(len(image[old_row])):
            image[old_row][old_colom] = [b[image[old_row][old_colom][x]] for x in range(3)]

    # Сохраняем получившееся изображение
    io.imsave(fname=path_to_new_image, arr=image, check_contrast=False)


change_contrast()
