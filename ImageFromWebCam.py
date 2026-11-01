import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2  # Per la gestione della telecamera
from PIL import Image, ImageTk  # Per convertire le immagini per Tkinter
import os
import matplotlib
matplotlib.use("TkAgg")  # Assicura la compatibilità grafica del grafico con Tkinter
import matplotlib.pyplot as plt

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Acquisizione da Telecamera Esterna")
        self.root.geometry("900x550")
        
        # Variabili di stato per OpenCV
        self.cap = None  # Conterrà l'oggetto cv2.VideoCapture
        self.is_camera_on = False


        # Variabili di stato interne
        self.pil_image = None      


        # --- 1. LAYOUT PRINCIPALE: PANNELLO SINISTRO (MENU) ---
        self.left_panel = tk.Frame(self.root, width=280, bg="#2c3e50", padx=10, pady=10)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.left_panel.pack_propagate(False)

        # --- 2. LAYOUT PRINCIPALE: PANNELLO DESTRO (CONTENUTI) ---
        self.view_panel = tk.Frame(self.root, bg="#e0e0e0")
        self.view_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # --- 3. ELEMENTI DEL PANNELLO DESTRO (SEGNAPOSTO/VIDEO) ---
        self.image_label = tk.Label(self.view_panel, text="Nessuna telecamera connessa", 
                                    bg="#e0e0e0", fg="#7f8c8d", font=("Arial", 14))
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # --- 4. ELEMENTI DEL PANNELLO SINISTRO (PULSANTI) ---
        self.menu_title = tk.Label(self.left_panel, text="PANNELLO DI CONTROLLO", 
                                   bg="#2c3e50", fg="#ecf0f1", font=("Arial", 12, "bold"))
        self.menu_title.pack(pady=(0, 20))

        # Pulsante ON/OFF Telecamera
        self.btn_camera = tk.Button(self.left_panel, text="Avvia Streaming", 
                                    bg="#2ecc71", fg="#000000", font=("Arial", 11, "bold"),
                                    bd=0, height=2, command=self.toggle_camera)
        self.btn_camera.pack(fill=tk.X, pady=5)


       # Pulsante per Scattare Foto e bloccarle nella finestra (Inizialmente DISATTIVATO)
        self.btn_snap_2 = tk.Button(self.left_panel, text="Scatta e Blocca Foto", 
                                  bg="#34495e", fg="white", font=("Arial", 11, "bold"),
                                  bd=0, height=2, state=tk.DISABLED, command=self.take_snapshot)
        self.btn_snap_2.pack(fill=tk.X, pady=5)


        # Pulsante per l'analisi della foto con Matplotlib (Inizialmente DISATTIVATO)
        self.btn_analizza = tk.Button(self.left_panel, text="Analisi Cromatica Foto",
                                      command=self.analizza_image, bg="#34495e", fg="#3498db", font=("Arial", 11, "bold"),
                                      bd=0, height=2, state=tk.DISABLED)
        self.btn_analizza.pack(fill=tk.X, pady=5)


        # Pulsante per Salvare Foto (Inizialmente DISATTIVATO)
        self.btn_save = tk.Button(self.left_panel, text="Salva Foto", 
                                  bg="#34495e", fg="white", font=("Arial", 11, "bold"),
                                  bd=0, height=2, state=tk.DISABLED, command=self.save_snapshot)
        self.btn_save.pack(fill=tk.X, pady=5)


        # Gestione chiusura pulita della finestra del sistema operativo
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def toggle_camera(self):
        """Gestisce l'accensione e lo spegnimento della telecamera reale"""
        if not self.is_camera_on:
            # Tenta di aprire la telecamera predefinita del PC (indice 1)
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                messagebox.showerror("Errore", "Impossibile accedere alla telecamera!")
                return
            
            self.is_camera_on = True
            self.btn_camera.config(text="Ferma Streaming", bg="#e74c3c")

            # ATTIVIAMO il pulsante Scatta e Blocca Foto al volo!
            self.btn_snap_2.config(state=tk.NORMAL, bg="#2ecc71", fg="#000000")
            self.view_panel.config(bg="#ffffff")



            # DISATTIVIAMO il pulsante di Analisi foto con Matplotlib
            self.btn_analizza.config(state=tk.DISABLED, bg="#34495e")
            
            
            # DISATTIVIAMO il pulsante per Salvare la  Foto
            self.btn_save.config(state=tk.DISABLED, bg="#34495e")

            
            # Avvia il loop di aggiornamento dei frame
            self.update_video_stream()
        else:
            self.is_camera_on = False
            self.btn_camera.config(text="Avvia Streaming", bg="#2ecc71")

            # DISATTIVIAMO il pulsante Scatta e Blocca Foto
            self.btn_snap_2.config(state=tk.DISABLED, bg="#34495e")

            
            # Rilascia la risorsa hardware della webcam
            if self.cap:
                self.cap.release()
            
            self.image_label.config(text="Nessuna telecamera connessa", image="", bg="#e0e0e0", fg="#7f8c8d")
            self.view_panel.config(bg="#e0e0e0")
            
            
    def update_video_stream(self):
        """Cattura un fotogramma da OpenCV, lo converte e lo mostra nella Label"""
        if self.is_camera_on and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # 1. Capovolge l'immagine  (opzionale ma comodo)
                frame = cv2.flip(frame, 0)
                
                # 2. OpenCV usa BGR, Tkinter vuole RGB. Convertiamo!
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 3. Convertiamo l'array OpenCV in un oggetto Immagine PIL
                img = Image.fromarray(cv2image)
                
                # 4. Convertiamo l'immagine PIL nel formato finale PhotoImage per Tkinter
                imgtk = ImageTk.PhotoImage(image=img)
                
                # 5. Applichiamo l'immagine alla label
                self.image_label.imgtk = imgtk  # Mantiene una referenza in memoria (evita il garbage collector)
                self.image_label.config(image=imgtk, bg="#ffffff")
            
            # Richiama questa funzione dopo 15 millisecondi (~60 FPS stabili)
            self.root.after(15, self.update_video_stream)
            

    def take_snapshot(self):
        """Cattura il frame attuale e lo blocca nella finestra"""
        if self.is_camera_on and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # 1. Capovolge l'immagine  (opzionale ma comodo)
                frame = cv2.flip(frame, 0)
                
                # 2. OpenCV usa BGR, Tkinter vuole RGB. Convertiamo!
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 3. Convertiamo l'array OpenCV in un oggetto Immagine PIL
                img = Image.fromarray(cv2image)

                # 4. Salviamo l'immagine PIL per l'eventuale analisi cromatica
                self.pil_image = img

                
                # 5. Convertiamo l'immagine PIL nel formato finale PhotoImage per Tkinter
                imgtk = ImageTk.PhotoImage(image=img)


                # 6. Blocchiamo lo streaming dalla fotocamera
                
                self.is_camera_on = False
                self.btn_camera.config(text="Avvia Streaming", bg="#2ecc71")


                # DISATTIVIAMO il pulsante Scatta e Blocca Foto
                self.btn_snap_2.config(state=tk.DISABLED, bg="#34495e")


                # ATTIVIAMO il pulsante di Analisi foto con Matplotlib
                self.btn_analizza.config(state=tk.NORMAL, bg="#2ecc71", fg="#000000")
                self.view_panel.config(bg="#ffffff")

            
                # ATTIVIAMO il pulsante Salva Foto 
                self.btn_save.config(state=tk.NORMAL, bg="#2ecc71", fg="#000000")
                self.view_panel.config(bg="#ffffff")
               
                
                # 6. Applichiamo l'immagine alla label
                self.image_label.imgtk = imgtk  # Mantiene una referenza in memoria (evita il garbage collector)
                self.image_label.config(image=imgtk, bg="#ffffff")

 
    def analizza_image(self):
        if self.pil_image:
            plt.figure("Analisi Cromatica Foto")
            preview_img = self.pil_image.copy()
            plt.imshow(preview_img)
            plt.show()

    
    def save_snapshot(self):
        """Cattura il frame attuale e lo salva su file"""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 0)
            filename = "snapshot.jpg"
            # Salva l'immagine sul computer usando OpenCV
            cv2.imwrite(filename, frame)
            messagebox.showinfo("Successo", f"Immagine salvata correttamente come '{filename}'!")

            

    def on_closing(self):
        """Assicura che la telecamera si spenga se l'utente chiude l'app improvvisamente"""
        if self.is_camera_on and self.cap:
            self.cap.release()
        self.root.destroy()


# Esecuzione dell'applicazione
if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
