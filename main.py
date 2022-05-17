import input_processing as inp
import image_processing as img

# fiecare funcție e explicată mai detaliat unde este definită

# datele sunt imparțite în câte un fișier fiecare, am implementat o funcție care returnează 2 vectori care conțin căile
# pentru fiecare dintre fișierele hu.in si seg.in
hu_paths, seg_paths = inp.get_paths()

# pentru că sunt 2 vectori separați, dar trebuie sa aibă lungimi egal, am iterat valorile lungimilor lor,
# pentru a putea să am acces la fiecare element

for i in range(len(hu_paths)):
    # importarea datelor
    # hu_citit reprezintă matricea intensității pixelilor, cu valori între
    # seg reprezinta segmentarea facută de doctor, cu valori de 0 și 1
    hu_citit = inp.read_HU_data(hu_paths[i])
    seg = inp.read_seg_data(seg_paths[i])

    # vizualizarea mai bună a segmentelor de imagine care au valori intre [level - window/2; level + window/2]
    window = 150
    level = 30
    hu_filtrat = img.ct_filter(hu_citit, level, window)

    # determinarea coordonatelor care delimitează dreptunghiul în care se face procesarea imaginii, pentru creșterea
    # performanțelor
    frame = inp.frame_coords(inp.get_tags_coord(seg))

    # aplicare filtru mean pentru a reduce zgomotul din matrice
    hu_denoised = img.mean_filter(5, hu_filtrat, frame=frame, d=10)

    # aplicare filtru sobel pentru determinarea conturului pe orizontală și verticală
    hu_sobel = img.sobel_filter(hu_denoised, frame=frame, d=10)

    # determinarea valorile de threshold și a imaginii care rezultă după clasificarea fiecărui pixel ca slab, incert,
    # important
    hu_threshold, weak, strong = img.threshold(hu_sobel)

    # procesarea conturului rămas, și stabilirea dacă pixelii incerți trebuie să rămână sau nu
    hu_hys = img.hysteresis(hu_threshold, weak=weak, strong=strong, frame=frame, d=10)

    # determinarea conturului de interes
    contour_wanted = img.contour(hu_hys)

    # bazat pe conturul ales, generarea imaginii doar cu aria ficatului
    seg_final = img.final_draw(contour_wanted)

    # salvarea rezultatului în fișierul results
    inp.save(i , inp.get_ct_id(hu_paths[i]), seg_final)
