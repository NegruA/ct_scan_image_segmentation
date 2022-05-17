import numpy as np
from matplotlib import pyplot as plt
import cv2


# Fiecare funcție are linii de cod pentru a vedea produsl lor. Pot fi decomentate pentru afișarea imaginii rezultate

def ct_filter(img, level, window):
    # Funcția returnează imaginea după ce aduce valorile mai mici decât min la nivelul de min și valorile mai mari decât
    # max la nivelul de max. În acest mod, se facilitează observarea segmentelor dorite.

    # Parametrii de intrare sunt img = imaginea

    # Din documentarea pe care am facut-o, am aflat că fiecare organ are o arie specifică de valori pe care le poate
    # avea. Valorile pentru ficat, in cazul de față sunt mai jos. Aș fi putut încerca singur valori, dupa ce analizam
    # cam în jurul cărui nivel se află ficatul, dar mi s-a părut o soluție mai bună și mai rapidă să iau datele ca
    # atare.

    # brain  ---   40  ---  80 
    # lungs  ---  -600 ---  1500
    # liver  ---   30  ---  150
    # soft 
    # tissue ---  50   ---  250
    # bone   ---  400  ---  1800

    max_ = level + window / 2
    min_ = level - window / 2
    img = img.clip(min_, max_)

    # print("ct_filter")
    # plt.figure()
    # plt.imshow(img, cmap='gray')
    # plt.show()

    return img


def get_gaussian_kernel(m, n, sigma):
    # Funcția returnează matricea kernel gaussian

    # Parametrii de intrare sunt
    # m = nr de linii,
    # n= nr coloane
    # sigma = abaterea standard

    # Am vrut să folosesc kernel pentru blur de imagine, dar după ce am făcut câteva încercări, am observat că nu are
    # un efect mare asupra produsului final și l-am mai adăugat
    gaussian = np.zeros((m, n))
    m = m // 2
    n = n // 2

    for x in range(-m, m + 1):
        for y in range(-n, n + 1):
            xmax = sigma * (2 * np.pi) ** 2
            x2 = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
            gaussian[x + m, y + n] = (1 / xmax) * x2

    return gaussian


def convolution(kernel, img, frame=np.zeros(4), d=0):
    # Funcția returnează convoluția dintre o matrice și fiecare pixel prin care trece

    # Parametrii de intrare sunt
    # kernel = matricea cu care se face convoluția
    # img = imaginea care trebuie procesată
    # frame, d --->>> vezi explicația în input_processing.frame_coords

    if frame[0] == 0 and frame[1] == 0 and frame[2] == 0 and frame[3] == 0:
        ymin = 0
        ymax = img.shape[0]
        xmin = 0
        xmax = img.shape[1]
    else:
        ymin = int(frame[0])
        ymax = int(frame[1])
        xmin = int(frame[2])
        xmax = int(frame[3])

    ksize = kernel.shape[0]
    out = np.zeros(img.shape)

    # Variabilele y și x reprezintă coordonatele fiecărui pixel, se iterează pentru toți pixelii aflați în frame + d,
    # dacă este cazul, sau pentru toată imaginea dacă frame nu există
    for y in range(ymin + ksize // 2 - d, ymax - ksize // 2 + d):
        for x in range(xmin + ksize // 2 - d, xmax - ksize // 2 + d):

            # region reprezinta vecinătatea în care a ajuns matricea kernel să își facă efectul
            region = img[y - ksize // 2:y + ksize // 2 + 1, x - ksize // 2:x + ksize // 2 + 1]
            for i in range(ksize):
                for j in range(ksize):
                    # valoarea pixelului care rezultă in matricea de ieșire out este suma fiecărui produs dintre
                    # valoarea pe care îl are fiecare pixel din regiunea în care se află matricea kernel și valoarea
                    # efectivă a fiecărui element (fiecărei greutăți) din kernel
                    out[y, x] += region[i, j] * kernel[i, j]

    # print("convolutie")
    # plt.figure()
    # plt.imshow(out, cmap='gray' , vmin = 0 )
    # plt.show()

    return out


def sharpening_filter(factor, img, blurred_img):
    # Funcția returnează imaginea după filtrarea sharp

    # Parametrii de intrare sunt
    # factor = factorul de sharp
    # img = imaginea care trebuie procesată
    # blurred_img  = imaginea blurată cu ajutorul căreia se crează filtrul sharp

    # Filtrul sharp este simplu, implică doar suprapunerea peste imaginea inițilă a unei imagini care are elementele
    # opuse blurării

    # Am vrut să folosesc acest filtru sperând că va delimita mai bine schimbările de țesut, dar nu a avut rezultate
    # foarte importante și am renunțat la el după câteva teste

    # print("sharpening_filter")
    # plt.figure()
    # plt.imshow(img, cmap='gray')
    # plt.show()

    return img + factor * (img - blurred_img)


def mean_filter(k_size, img, frame=np.zeros(4), d=0):
    # Funcția returnează imaginea după aplicarea filtrului, care "netezește" valorile fiecărui pixel, bazat pe valoarea
    # pixelilor învecinați

    # Parametrii de intrare sunt
    # k_size = numărul de pixeli care sunt luați în calcul pentru mediere
    # img = imaginea care trebuie procesată
    # frame, d --->>> vezi explicația în input_processing.frame_coords

    out = np.zeros(img.shape)

    if frame[0] == 0 and frame[1] == 0 and frame[2] == 0 and frame[3] == 0:
        ymin = 0
        ymax = img.shape[0]
        xmin = 0
        xmax = img.shape[1]

    else:
        ymin = int(frame[0])
        ymax = int(frame[1])
        xmin = int(frame[2])
        xmax = int(frame[3])

    # Variabilele y și x reprezintă coordonatele fiecărui pixel, se iterează pentru toți pixelii aflați în frame + d,
    # dacă este cazul, sau pentru toată imaginea dacă frame nu există

    for y in range(ymin - d, ymax + d):
        for x in range(xmin - d, xmax + d):
            # pixelul din matricea de ieșire este media aritmetică dintre intensitățile tuturor pixelilor pe o lungime
            # de k_size
            out[y, x] = np.mean(img[y - k_size // 2:y + k_size // 2 + 1, x - k_size // 2:x + k_size // 2 + 1])

    # plt.figure()
    # plt.imshow(out, cmap='gray' , vmin = 0 )
    # plt.show()

    return out


def sobel_filter(img, frame=np.zeros(4), d=0):
    # Funcția returnează imaginea după aplicarea filtrului sobel, care e folositor la determinat conturului obiectelor.
    # Reprezinta o convoluție cu 2 kerneli care "cantăresc" mult pe o parte, deloc pe mijloc și opus pe partea
    # cealaltă, astfel produsul pixelului din mijloc va fi influențat cel mai mult de valorile pixelilor de pe
    # laturile orizontale și separat, de valorile pixelilor de pe  laturile verticale

    # parametrii de intrare sunt
    # img = imaginea care trebuie procesată
    # frame, d --->>> vezi explicația în input_processing.frame_coords
    kernel_orizontal = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    kernel_vertical = kernel_orizontal.T

    img_orizontala = np.abs(convolution(kernel_orizontal, img, frame=frame, d=d))
    img_verticala = np.abs(convolution(kernel_vertical, img, frame=frame, d=d))

    out = (img_orizontala ** 2 + img_verticala ** 2) ** (1 / 2)

    # print("produs final sober ")
    # plt.figure()
    # plt.imshow(dim_grad, cmap='gray')
    # plt.show()

    return out


def threshold(img, lowThresholdRatio=0.1, highThresholdRatio=0.12):
    # Funcția returnează imaginea procesată pentru 2 niveluri de threshold și aceste niveluri. Aceste 2 niveluri
    # le-am determinat după ce am analizat matricea de valori a pixelilor și am văzut la ce nivel se situează fiecare
    # segment de interes.

    weak = np.int32(30)
    strong = np.int32(img.max())

    # parametrii de intrare sunt
    # img = imaginea care trebuie procesată
    # Pentru că pixelii nu au o valoare constantă, parametrii highThresholdRatio și lowThresholdRatio determină
    # valorile până la cât se pot abate intensitățile pixelilor din contur. Acești parametrii au fost determinați
    # tot prin teste.
    highThreshold = strong * highThresholdRatio
    lowThreshold = highThreshold * lowThresholdRatio

    M, N = img.shape
    out = np.zeros((M, N), dtype=np.int32)

    # Se caută și se stochează coordonatele fiecărui pixel care se află în cele 3 categorii:
    # 1. mai mic decât lowThreshold
    # 2. între lowThreshold și highThreshold
    # 3. mai mare decât highThreshold
    strong_i, strong_j = np.where(img >= highThreshold)
    zeros_i, zeros_j = np.where(img < lowThreshold)
    weak_i, weak_j = np.where((img <= highThreshold) & (img >= lowThreshold))

    # Fiecărui pixel i se dă o valoare bazat pe intervalul în care face parte:
    # 1. nu vor mai conta, se fac 0
    # 2. se dă o valoarea intermediară, pentru a se putea decide după aceea dacă aparțin conturului sau nu
    # 3. contează și valoarea lor se face maximă
    out[strong_i, strong_j] = strong
    out[weak_i, weak_j] = weak
    out[zeros_i, zeros_j] = 0

    print("threshold ")
    plt.figure()
    plt.imshow(out, cmap='gray')
    plt.show()

    return out, weak, strong


def hysteresis(img, weak, strong, frame=np.zeros(4), d=0):
    # Funcția returnează imaginea care rezultă după ce se stabilește dacă pixelii care au primit o valoarea
    # intermediară fac sau nu parte din contur

    # parametrii de intrare sunt
    # img = imaginea care trebuie procesată
    # weak = valoarea intensității slabe
    # strong = valoarea intensității intermediare
    # frame, d --->>> vezi explicația în input_processing.frame_coords

    if frame[0] == 0 and frame[1] == 0 and frame[2] == 0 and frame[3] == 0:
        ymin = 0
        ymax = img.shape[0]
        xmin = 0
        xmax = img.shape[1]
    else:
        ymin = int(frame[0])
        ymax = int(frame[1])
        xmin = int(frame[2])
        xmax = int(frame[3])

    # Determinarea apartenenței la contur este făcută prin analizarea pixelilor vecini. Dacă oricare pixel vecin
    # pixelului analizat = strong, atunci și pixelul analizat devine = strong, altfel  el va fi 0.
    out = img.copy()
    for y in range(ymin + 1 - d, ymax + d):
        for x in range(xmin + 1 - d, xmax - 1 + d):
            if out[y, x] == weak:
                if ((out[y + 1, x - 1] == strong) or (out[y + 1, x] == strong) or (
                        out[y + 1, x + 1] == strong)
                        or (out[y, x - 1] == strong) or (out[y, x + 1] == strong)
                        or (out[y - 1, x - 1] == strong) or (out[y - 1, x] == strong) or (
                                out[y - 1, x + 1] == strong)):
                    out[y, x] = 255
                else:
                    out[y, x] = 0

    print("hysteresis ")
    plt.figure()
    plt.imshow(out, cmap='gray')
    plt.show()

    return out


def contour(img):
    # Funcția returnează coordonatele conturului de interes.

    # Parametrul de intrare este imaginea în care trebuie să caute conturul.

    # am creat această imagine color pentru a putea fi vizionat conturul găsit
    dim = np.zeros(img.shape)
    img_color = np.stack((img, dim, dim), axis=2)
    img_color = img_color + np.stack((dim, img, dim), axis=2)
    img_color = img_color + np.stack((dim, dim, img), axis=2)

    img_gray = img.astype(np.uint8)
    areaarray = []

    # Determinarea tuturor contururilor din imagine
    contours, hierarchy = cv2.findContours(img_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # După determinarea contururilor, le ordonez în ordine crescătoare
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        areaarray.append(area)
    sorteddata = sorted(zip(areaarray, contours), key=lambda x: x[0], reverse=True)

    # Dacă s-a lucrat în chenar, sigur conturul căutat va fi mereu al doilea
    contour_wanted = sorteddata[1][1]

    # contoured_image= cv2.drawContours(img_color, contour_wanted ,-1,(255,0,0),3)
    # plt.figure()
    # plt.imshow(contoured_image)
    # plt.show()

    return contour_wanted


def final_draw(contour):
    # Funcția returnează matricea în care a fost desenată zona delimitată de contur

    # Parametrul de intrare este conturul care trebuie să delimiteze zona
    out = np.zeros((512, 512))
    out = cv2.drawContours(out, [contour], -1, 255, thickness=-1)

    print("rezultat")
    plt.figure()
    plt.imshow(out, cmap='gray')
    plt.show()
    return out
