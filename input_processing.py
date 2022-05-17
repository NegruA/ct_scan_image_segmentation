import numpy as np
from matplotlib import pyplot as plt
import cv2
import os


def get_paths():
    # Funcția returnează 2 vectori: în fiecare se află căile pentru toate fișierele de tip HU.in și seg.in

    hus = []
    segs = []
    for file in os.listdir():
        if (file != '.git' and file != 'image_processing.py' and file != 'image_processing.py'
                and file != 'input_processing.py' and file != 'main.py' and file != 'README.md'
                and file != 'results' and file != '__pycache__'):
            directory = file
            for root, dirs, in_files in os.walk(directory):
                for in_file in in_files:
                    if in_file.endswith('-HU.in'):
                        hus.append(root + '/' + in_file)

                    if in_file.endswith('-seg.in'):
                        segs.append(root + '/' + in_file)

    return hus, segs


def get_ct_id(path):
    # Funcția returnează id-ul fiecărui scan bazat pe calea pe care o are
    # Parametrul de intrare este calea fiecărui fișier de intrare

    return path.split('/')[1].split('-')[0]


def read_HU_data(path):
    # Funcția returnează matricea corespunzătoare fiecărui fișier HU.in
    # Parametrul de intrare este calea fiecărui fișier de intrare

    with open(path, 'r') as f:
        img = f.read()
        # Fiecare fișier este citit ca un string lung. L-am redimensionat la valorile prestabilite de matrice 512*512
        img = np.fromstring(img, dtype=int, sep=" ")
        dim = (512, 512)
        img = np.array([img])
        img = img.reshape(dim)

    # print("read_HU_data")
    # plt.figure()
    # plt.imshow(img, cmap='gray')
    # plt.show()

    return img


def read_seg_data(path):
    # Funcția returnează matricea corespunzătoare fiecărui fișier seg.in
    # Parametrul de intrare este calea fiecărui fișier de intrare

    with open(path, 'r') as f:
        img = f.read()
        # Fiecare fișier este citit ca un string lung. L-am redimensionat la valorile prestabilite de matrice 512*512
        img = np.fromstring(img, dtype=int, sep=" ")
        dim = (512, 512)
        img = np.array([img])
        img = img.reshape(dim)
    # print("read_seg_data")
    # plt.figure()
    # plt.imshow(img, cmap='gray')
    # plt.show()

    return img


def get_tags_coord(img_med_tags):
    # Funcția returnează o matrice cu coordonatele tuturor pixelilor care fac parte din segmentarea doctorului.

    (i, j) = np.where(img_med_tags == 1)
    coord = np.zeros((2, len(i)))
    coord = [[x, y] for x, y in zip(i, j)]

    return coord


def get_coord_values(coord, img):
    # Funcția returnează valorile intensității pixelilor
    coord_values = []
    for i in coord:
        coord_values.append(img[i[0], i[1]])

    return coord_values


def frame_coords(tags_coord):
    # Funcția returnează un vector cu valorile prestabilite pentru delimitarea unui dreptunghi în care se va lucra
    # pentru eficientizarea timpului de procesare:

    # coordonatele frame-ului care rezulta sunt
    # out[0] = ymin punctul cel mai de sus al segmentării facute de docto,
    # out[1] = ymax punctul cel mai de jos
    # out[2] = xmin punctul cel mai din stânga
    # out[3] = xmax punctul cel mai din dreapta

    # În funcțiile de procesare a imaginilor, am adăugat și parametrul d pentru o mărire a suprafeței pe care se
    # întinde chenarul, pentru a putea fi luați în calcul mai mulți pixeli.

    # Recomand decomentarea liniilor care reproduc imaginea chenarului pentru o vizualizare practică.

    x = []
    y = []

    out = np.zeros(4, dtype=np.int32)
    for i in range(len(tags_coord)):
        x.append(tags_coord[i][1])
        y.append(tags_coord[i][0])

    out[0] = np.amin(y)
    out[1] = np.amax(y)
    out[2] = np.amin(x)
    out[3] = np.amax(x)

    # Pentru observarea parametrului d, se pot da valori acestuia în funcția din următorul rând.
    # test = highlight_working_frame(np.zeros((512,512)), out)
    # print("frame")
    # plt.figure()
    # plt.imshow(test, cmap='gray')
    # plt.show()

    return out


def highlight_working_frame(img, frame, d=0):
    # Funcția evidențiază chenarul de lucru.

    for y in range(frame[0] - d, frame[1] + d):
        for x in range(frame[2] - d, frame[3] + d):
            img[y][x] = 255
    return img


def mean_(coord_values):
    s = 0

    for coord_value in coord_values:
        s = s + coord_value
    mean = s / len(coord_values)

    return mean


def std_dev(mean, coord_values):
    s = 0
    for coord_value in coord_values:
        s = s + (coord_value - mean) ** 2

    dev = (s / (len(coord_values) - 1)) ** (1 / 2)

    return dev


def save(index, id, img):
    # Funcția scrie rezultatul procesării sub forma de imagine și de fișier optim.out în fișierul results și în
    # fiecare fișier de input

    if not ('results' in os.listdir()):
        print('a intrat')
        os.mkdir('results')

    cv2.imwrite("results/" + str(id) + 'optim.png', img)

    with open("results/" + str(id) + "-optim.out", 'w') as wf:
        wf.write(str(img))

    if index == 0:
        cv2.imwrite('input/optim.png', img)

        with open('input/optim.out', 'w') as wf:
            wf.write(str(img))

    else:
        cv2.imwrite('input' + str(index+1) + '/optim.png', img)

        with open('input' + str(index+1) + '/optim.out', 'w') as wf:
            wf.write(str(img))
