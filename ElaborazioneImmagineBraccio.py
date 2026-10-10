from PIL import Image
import matplotlib.pyplot as plt
import numpy as np


# 1. Si carica l'immagine e poi da essa viene creato un array NumPy contenente i pixel
# con tre byte per ciascuno per esprimere il colore. Con RGB si esprimono le componenti
# dei colori Red, Green, Blue i cui livelli variano ciascuno da 0 a 255.
# Essi sono immessi in un array di dimensione 3: [R, G, B] per ciascun pixel
# Le dimensioni dell'immagine in pixel è  width x height



img = Image.open('prova3.jpg')
pixels = img.load()
width, height = img.size
r_width = 275  # larghezza reale dell'immagine in mm
r_height = 200   # altezza reale dell'immagine in mm
img_array = np.array(img)
print("Le dimensioni dell'immagine sono: ", width, height, "pixel")


# 2. Definisci il range minimo e massimo per ogni canale (R, G, B)
lower_bound = np.array([50, 60, 70])   # [R_min, G_min, B_min]
upper_bound = np.array([60, 70, 80])  # [R_max, G_max, B_max]

# 3. Trova i pixel che rientrano nel range per tutti e tre i canali
maschera = np.all((img_array >= lower_bound) & (img_array <= upper_bound), axis=-1)


# 4. Ottieni le coordinate (indici y, x) dei pixel individuati e il loro baricentro
coordinata_y, coordinata_x = np.where(maschera)



if (len(coordinata_x)!=0  and len(coordinata_y) != 0) :
    print(f"Trovati {len(coordinata_x)} pixel del colore nel range dei colori specificato.")
    x_p = sum(coordinata_x)// len(coordinata_x)
    y_p = sum(coordinata_y)// len(coordinata_y)
    x_b = x_p*(r_width/width)-r_width/2         # ascissa rispetto al centro dell'immagine
    y_b = r_height - y_p*(r_height/height)      # ordinata rispetto al bordo inferiore dell'immagine
    print("Il baricentro dei pixel del colore specificato è nel pixel: ", x_p, y_p)
    print("Il baricentro dei pixel del colore specificato ha coordinate: ", np.int64(x_b), "mm",np.int64(y_b),"mm")  
else:
    print("Non esiste alcun pixel nel range dei colori specificato! ")



# 5. Visualizza l'immagine e i pixel trovati
fig, ax = plt.subplots()
ax.imshow(img)
ax.scatter(coordinata_x, coordinata_y, color='yellow', s=10, label='Pixel target')
ax.legend()
plt.show()


