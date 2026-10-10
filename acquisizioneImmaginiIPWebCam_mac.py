import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")  # Assicura la compatibilità grafica del grafico con Tkinter
import matplotlib.pyplot as plt
import urllib.request
import io

class ExternalCameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Acquisizione da Telecamera Esterna / IP")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f0f0")

        # Variabili di stato interne
        self.pil_image = None      
        self.display_image = None  
        self.stream_active = False

        self.setup_ui()

    def setup_ui(self):
        # Layout principale
        self.left_panel = tk.Frame(self.root, width=280, bg="#2c3e50", padx=10, pady=10)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.left_panel.pack_propagate(False)

        self.view_panel = tk.Frame(self.root, bg="#e0e0e0")
        self.view_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Finestra di anteprima centrale
        self.image_label = tk.Label(self.view_panel, text="Nessuna telecamera connessa", bg="#e0e0e0", fg="#7f8c8d", font=("Arial", 14))
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Configurazione Telecamera Esterna IP
        lbl_url = tk.Label(self.left_panel, text="URL FLUSSO IP / TELECAMERA", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 10, "bold"))
        lbl_url.pack(fill=tk.X, pady=(5, 5))

        # Input box per inserire l'indirizzo IP della fotocamera esterna
        self.ent_url = tk.Entry(self.left_panel, font=("Arial", 10))
        self.ent_url.insert(0, "http://192.168.178.24:8080/shot.jpg")
        self.ent_url.pack(fill=tk.X, pady=5)

        self.btn_stream = tk.Button(self.left_panel, text="Avvia Streaming", command=self.toggle_stream, bg="#3498db", fg="#3498db", font=("Arial", 10, "bold"), bd=0, pady=8)
        self.btn_stream.pack(fill=tk.X, pady=5)

        self.btn_snap = tk.Button(self.left_panel, text="Scatta e Blocca Foto", command=self.snapshot_camera, bg="#3498db", fg="#3498db", font=("Arial", 10, "bold"), bd=0, pady=8, state=tk.DISABLED)
        self.btn_snap.pack(fill=tk.X, pady=5)

        ttk.Separator(self.left_panel, orient='horizontal').pack(fill=tk.X, pady=15)

        # Pannello strumenti di editing
        lbl_tools = tk.Label(self.left_panel, text="STRUMENTI EDITING", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 10, "bold"))
        lbl_tools.pack(fill=tk.X, pady=(0, 5))

        self.btn_gray = tk.Button(self.left_panel, text="Bianco e Nero", command=self.apply_grayscale, bg="#95a5a6", fg="#3498db", font=("Arial", 10), bd=0, pady=6, state=tk.DISABLED)
        self.btn_gray.pack(fill=tk.X, pady=5)

        self.btn_rotate = tk.Button(self.left_panel, text="Ruota 90°", command=self.apply_rotate, bg="#95a5a6", fg="#3498db", font=("Arial", 10), bd=0, pady=6, state=tk.DISABLED)
        self.btn_rotate.pack(fill=tk.X, pady=5)

        # Pannello per analisi dati Matplotlib
        ttk.Separator(self.left_panel, orient='horizontal').pack(fill=tk.X, pady=15)
        lbl_plt = tk.Label(self.left_panel, text="ANALISI MATPLOTLIB", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 10, "bold"))
        lbl_plt.pack(fill=tk.X, pady=(0, 5))

        self.btn_hist = tk.Button(self.left_panel, text="Mostra Istogramma", command=self.show_histogram, bg="#8e44ad", fg="#3498db", font=("Arial", 10), bd=0, pady=6, state=tk.DISABLED)
        self.btn_hist.pack(fill=tk.X, pady=5)

        self.btn_analizza = tk.Button(self.left_panel, text="Analisi Cromatica Foto", command=self.analizza_image, bg="#95a5a6", fg="#3498db", font=("Arial", 10), bd=0, pady=6, state=tk.DISABLED)
        self.btn_analizza.pack(fill=tk.X, pady=5)


        # Pulsante Esportazione file finale
        self.btn_save = tk.Button(self.left_panel, text="Salva Immagine", command=self.save_image, bg="#2ecc71", fg="#3498db", font=("Arial", 11, "bold"), bd=0, pady=8, state=tk.DISABLED)
        self.btn_save.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

    def toggle_stream(self):
        if not self.stream_active:
            self.stream_active = True
            self.btn_stream.config(text="Ferma Streaming", bg="#7f8c8d")
            self.btn_snap.config(state=tk.NORMAL)
            self.update_stream()
        else:
            self.stream_active = False
            self.btn_stream.config(text="Avvia Streaming", bg="#3498db")

    def update_stream(self):
        if self.stream_active:
            url = self.ent_url.get()
            try:
                # Scarica i byte del fotogramma JPEG dalla rete senza usare OpenCV
                with urllib.request.urlopen(url, timeout=2) as response:
                    img_data = response.read()
                    
                temp_img = Image.open(io.BytesIO(img_data)).convert("RGB")
                self.current_frame = temp_img.copy()
                
                # Calcola dimensioni ottimali per l'interfaccia grafica
                max_w = max(self.view_panel.winfo_width(), 400)
                max_h = max(self.view_panel.winfo_height(), 400)
                temp_img.thumbnail((max_w, max_h))
                
                self.display_image = ImageTk.PhotoImage(temp_img)
                self.image_label.config(image=self.display_image)
            except Exception:
                # Previene crash se la rete cade temporaneamente
                self.image_label.config(image='', text="Errore: Impossibile raggiungere l'URL inserito.")
            
            # Richiama la funzione dopo 100 millisecondi per aggiornare il video (~10 FPS)
            self.root.after(100, self.update_stream)

    def snapshot_camera(self):
        if hasattr(self, 'current_frame'):
            self.pil_image = self.current_frame.copy()
            self.stream_active = False
            self.btn_stream.config(text="Avvia Streaming", bg="#3498db")
            
            self.refresh_preview()
            self.btn_gray.config(state=tk.NORMAL)
            self.btn_rotate.config(state=tk.NORMAL)
            self.btn_hist.config(state=tk.NORMAL)
            self.btn_analizza.config(state=tk.NORMAL)            
            self.btn_save.config(state=tk.NORMAL)
            messagebox.showinfo("Cattura", "Fotogramma bloccato! Ora puoi modificarlo o analizzarlo.")

    def refresh_preview(self):
        if self.pil_image:
            preview_img = self.pil_image.copy()
            max_w = max(self.view_panel.winfo_width(), 400)
            max_h = max(self.view_panel.winfo_height(), 400)
            preview_img.thumbnail((max_w, max_h))
            self.display_image = ImageTk.PhotoImage(preview_img)
            self.image_label.config(image=self.display_image)

    def apply_grayscale(self):
        if self.pil_image:
            self.pil_image = self.pil_image.convert("L")
            self.refresh_preview()

    def apply_rotate(self):
        if self.pil_image:
            self.pil_image = self.pil_image.rotate(-90, expand=True)
            self.refresh_preview()

    def show_histogram(self):
        if self.pil_image:
            plt.figure("Analisi Cromatiche Foto Esterna")
            if self.pil_image.mode == "L":
                plt.plot(self.pil_image.histogram(), color='black')
                plt.title("Istogramma - Bianco e Nero")
            else:
                r, g, b = self.pil_image.split()
                plt.plot(r.histogram(), color='red', label='Rosso')
                plt.plot(g.histogram(), color='green', label='Verde')
                plt.plot(b.histogram(), color='blue', label='Blu')
                plt.legend()
                plt.title("Distribuzione Colori RGB")
            plt.xlabel("Intensità Luminosa")
            plt.ylabel("Frequenza Pixel")
            plt.show()


    def analizza_image(self):
        if self.pil_image:
            plt.figure("Analisi Cromatica Foto")
            preview_img = self.pil_image.copy()
            plt.imshow(preview_img)
            plt.show()


    def save_image(self):
        if self.pil_image:
            file_path = filedialog.asksaveasfilename(
                initialdir="/Users/enrico/Documents/Blender/Studi/TinkerKit/Matplotlib",
                initialfile="foto_cubo", 
                defaultextension=".jpg",
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
            )
            if file_path:
                self.pil_image.save(file_path)
                messagebox.showinfo("Successo", "Immagine catturata salvata correttamente!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExternalCameraApp(root)
    root.mainloop()
