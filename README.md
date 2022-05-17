        Aplicația optimizează delimitarea facută de un doctor pentru un ficat,intr-o imagine tomograf; exclude 
zone care sunt în afara organului și corectează erorile în care cursorul medicului a tăiat o parte din organ și
acea parte nu va mai fi inclusă în selecția curentă. 
        Datele de intrare sunt o matrice în care fiecare intrare reprezintă valoarea hounsfield pentru pixel-ul 
corespunzator din imaginea tomografului și o matrice cu valori 0 si 1 in care sunt marcați cu 1 pixelii aleși de 
medic pentru conturul unui organ (ex 107-HU.in 107-seg.in).
        După rulare, aplicația scrie matricea care conține segmentarea optimizată în fiecare fișier de intrare 
( ex input2\optim.out) și în fișierul "results\89-optim".Pentru ușurarea vizualizării rezultatelor, aplicația 
crează și o imagine .png pentru fiecare matrice. 
        Parcursul în rezolvarea problemei a fost destul de lung și îl voi descrie în câteva randuri mai jos.
        Inițial, am vrut sa implementez un algoritm destul de simplu care, pe baza valorile delimitate de doctor, 
calcula media intensității pixelilor valizi. Segmentarea propriu-zisă trebuia să fie facută prin determinarea 
partenenței ficărui pixel în intervalul [medie - abatere standard; medie + abatere standard]. M-am gândit că 
această soluție nu poate fi foarte optimă pentru că în toată imaginea sigur sunt mulți pixeli care aparțin 
intervalului, dar am implementat-o pentru a vedea rezultatele. Am decis să aplic metoda doar pixelilor care se 
aflau în chenarul delimitat de maximele desenului făcut de doctor + o abatere de 10-20 de pixeli , pentru "a da 
șanse" pixelilor care nu sunt în chenar, dar au valori in interval, să fie luați în calcul.
        Rezultatele au fost bune pentru pozele în care porțiunea de ficat era mică, implicit chenarul în care se
căutau pixelii era mic. Pentru poze în care chenarul era aproape tot abdomenul,  existau multe segmente de imagine
care se încadrau în interval, dar nu erau parte din ficat. 
        Nu am fost mulțumit de rezultat, așa că am început să mă mai documentez despre procesarea imaginilor și să
caut soluții. 
        Una din primele probleme a fost că în pozele în care ficatul avea o pondere mare, exista foarte mult zgomot.
Am aflat despre filtre de imagine,convoluții și modalități prin care se poate reduce nivelul de zgomot. Am 
experimentat mai multe tipuri de filtre, dar am ajuns să folosesc doar 2, pentru ca doar ele dădeau rezultate care
schimbau performanța. 
        Următorul pas pe care am dorit să îl fac a fost stabilirea unor contururi bine definite, pentru aplicarea 
unui algoritm care delimiteză fiecare figură închisă. Am creat o funcție care delimitează niveluri de threshold. 
Pentru a mă asigura că nu există spații cu conturul discontinuu am creat funcția hysteresis care încearcă să umple
restul pixelilor care nu sunt importanți, dar care nu au fost șterși.
        După, am căutat o soluție pentru a delimita figurile inchise din imagine. Nu am găsit ceva accesibil de 
implementat de la 0, ar fi trebui să ma documentez mai mult și e prima experiență în lucrul cu imaginile. Am decis
să folosesc o funcție din libraria CV2, findContours. După determinarea conturului de interes, am creat imaginea 
cu conturul umplut. 
        Pentru o eficiență crescută, am creat aproape fiecărei funcții posibilitatea de a lucra pe o porțiune din 
poză, delimitată ,de preferat, de maximele segmentării facute de doctor + o constantă care mărește chenarul de lucru.
        Am implementat destul de multe funcții, așa că am decis să fac împărțirea în doua module:
            image_processing.py include funcțiile care prelucrează efectiv 
                valorile din matricea imaginii (filtre, nivelul de threshold, 
                hysteresis, delimitarea conturului),
            input_processing.py include funcțiile care importă/salvează datele,
                le transformă în matrice, generează porțiunea de poză în care 
                se lucreză, plus câteva funcții care fac operații simple cu 
                valorile din matrice.
        Am adăugat comentarii la toate funcțiile pentru a explica ceea ce fac și cum funcționează, cât și o detaliere
mai exactă pentru fiecare funcție pecare o folosesc în main().
