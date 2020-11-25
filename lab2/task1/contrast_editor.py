# -*- coding: utf-8 -*-
import imutils
from imutils import face_utils
import dlib
import cv2

PATH_TO_IMAGE = "\\TestHeadPose2\\TestHeadPose\\"
PATH_TO_NEW_IMAGE = "file1.jpg"
IMAGE_NAME_1 = "online_test_3_FAIL.jpg"
IMAGE_NAME_2 = "online_test_1_OK.jpg"
IMAGE_NAME_3 = "online_test_2_OK.jpg"


def change_contrast(image):
    """ Метод для изменения контрастности изображения

    :param image: изображение (массив пикселей изображения)

    """

    # Вычисляем среднюю яркость пикселя
    iab = 0

    for row in image:
        for colom in row:
            iab += (0.299 * colom[0] + 0.587 * colom[1] + 0.114 * colom[2])

    iab /= image.size

    # Определяем коэффициент коррекции
    k = 1 + 256 / 100

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
    # io.imsave(fname=PATH_TO_NEW_IMAGE, arr=image, check_contrast=False)
    return image


for image_name in [IMAGE_NAME_1, IMAGE_NAME_2, IMAGE_NAME_3]:

    # Читаем и подготавливаем изображения
    image = cv2.imread(image_name)
    images = imutils.resize(image, width=500)
    gray = change_contrast(image)

    # Назначаем алиасы
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("/face-ident/shape_predictor_68_face_landmarks.dat")

    # Распознаем лицо
    rects = detector(gray, 1)

    for (i, rect) in enumerate(rects):

        # Определяем ключевые точки
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # Отрисовываем прямоугольник на изображении
        (x, y, w, h) = face_utils.rect_to_bb(rect)
        cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 255, 0), 2)

        # Отрисовываем номер лица на картинке
        cv2.putText(gray, 'Face % {}'.format(i + 1), (x - 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # Отрисовываем точки
        for (x, y) in shape:
            cv2.circle(gray, (x, y), 1, (0, 0, 255), -1)

    # Выводим изображение
    cv2.imshow("Output", gray)
    cv2.waitKey(0)
