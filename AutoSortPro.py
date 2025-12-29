# Organizador Automático de Archivos con Cambio de Tema (Dark / Minimalista)

import os
import shutil
import time
import threading
from datetime import datetime
from tkinter import *
from tkinter import ttk, filedialog
from win10toast_click import ToastNotifier

# --------------------------------
# CONFIG
# --------------------------------
ruta_descargas = os.path.join(os.path.expanduser("~"), "Downloads")
ruta_clean_folder = os.path.join(os.path.expanduser("~"), "Organizados")
os.makedirs(ruta_clean_folder, exist_ok=True)

categorias = {
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "PDF": [".pdf"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv"],
    "Musica": [".mp3", ".wav", ".aac", ".flac"],
    "Documentos": [".doc", ".docx", ".txt", ".xlsx", ".ppt", ".pptx", ".csv", ".odt"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programas": [".exe", ".msi", ".apk"],
}

def obtener_categoria(extension):
    for categoria, extensiones in categorias.items():
        if extension.lower() in extensiones:
            return categoria
    return "Otros"

notificador = ToastNotifier()
ejecutando = False

# --------------------------------
# Funcion principal
# --------------------------------
def organizar_archivos():
    global ejecutando
    while ejecutando:
        movidos = 0
        for archivo in os.listdir(ruta_descargas):
            origen = os.path.join(ruta_descargas, archivo)
            if os.path.isfile(origen):
                shutil.move(origen, os.path.join(ruta_clean_folder, archivo))
                movidos += 1

        for archivo in os.listdir(ruta_clean_folder):
            origen = os.path.join(ruta_clean_folder, archivo)
            if os.path.isfile(origen):
                ext = os.path.splitext(archivo)[1]
                categoria = obtener_categoria(ext)
                fecha = datetime.fromtimestamp(os.path.getmtime(origen))
                año, mes = str(fecha.year), str(fecha.month).zfill(2)
                destino = os.path.join(ruta_clean_folder, categoria, año, mes)
                os.makedirs(destino, exist_ok=True)
                shutil.move(origen, os.path.join(destino, archivo))
                movidos += 1

        if movidos > 0:
            notificador.show_toast("Organizador activo ✅", f"{movidos} archivo(s) ordenados.")
        time.sleep(10)

# --------------------------------
# UI + THEMES
# --------------------------------
ventana = Tk()
ventana.title("AutoSort Pro")
ventana.geometry("480x360")
ventana.resizable(False, False)

# Tema actual
tema = "dark"

# Paletas de colores
temas = {
    "dark": {"bg":"#1b1b1b", "fg":"#e6e6e6", "ok":"#4dff88", "bad":"#ff4d4d", "btn":"#333", "btn_hover":"#444"},
    "light": {"bg":"#fafafa", "fg":"#000", "ok":"#088000", "bad":"#c00000", "btn":"#dcdcdc", "btn_hover":"#bfbfbf"}
}

style = ttk.Style()
style.theme_use('clam')

# funcion para aplicar tema
def aplicar_tema():
    colores = temas[tema]
    ventana.configure(bg=colores["bg"])
    estado_label.configure(bg=colores["bg"], fg=colores["bad"])
    for widget in (frame_rutas, frame_botones, frame_header):
        widget.configure(bg=colores["bg"])
    for lbl in (origen_label, destino_label):
        lbl.configure(bg=colores["bg"], fg=colores["fg"])
    style.configure("TButton", background=colores["btn"], foreground=colores["fg"], padding=6)
    style.map("TButton", background=[('active', colores["btn_hover"])])

# Cambiar tema
def toggle_tema():
    global tema
    tema = "light" if tema == "dark" else "dark"
    aplicar_tema()
    boton_tema.config(text=f"Tema: {'Claro' if tema=='light' else 'Oscuro'}")

# --- HEADER ---
frame_header = Frame(ventana)
frame_header.pack(fill="x", pady=10)

estado_label = Label(frame_header, text="Estado: ⛔ Detenido", font=("Arial", 12, "bold"))
estado_label.pack()

# --- SELECCIÓN DE RUTAS ---
frame_rutas = Frame(ventana)
frame_rutas.pack(pady=10)

# origen
def elegir_origen():
    global ruta_descargas
    ruta = filedialog.askdirectory()
    if ruta:
        ruta_descargas = ruta
        origen_label.config(text=f"📂 Origen: {ruta}")

origen_label = Label(frame_rutas, text=f"📂 Origen: {ruta_descargas}")
origen_label.grid(row=0, column=0, padx=5, pady=4, sticky="w")
ttk.Button(frame_rutas, text="Elegir", command=elegir_origen).grid(row=0, column=1, padx=5)

# destino
def elegir_destino():
    global ruta_clean_folder
    ruta = filedialog.askdirectory()
    if ruta:
        ruta_clean_folder = ruta
        destino_label.config(text=f"📁 Destino: {ruta}")

destino_label = Label(frame_rutas, text=f"📁 Destino: {ruta_clean_folder}")
destino_label.grid(row=1, column=0, padx=5, pady=4, sticky="w")
ttk.Button(frame_rutas, text="Elegir", command=elegir_destino).grid(row=1, column=1, padx=5)

# --- BOTONES CONTROL ---
frame_botones = Frame(ventana)
frame_botones.pack(pady=10)

def iniciar():
    global ejecutando
    if not ejecutando:
        ejecutando = True
        estado_label.config(text="Estado: ✅ Ejecutando", fg=temas[tema]["ok"])
        threading.Thread(target=organizar_archivos, daemon=True).start()

def detener():
    global ejecutando
    ejecutando = False
    estado_label.config(text="Estado: ⛔ Detenido", fg=temas[tema]["bad"])

ttk.Button(frame_botones, text="▶ Iniciar", width=18, command=iniciar).grid(row=0, column=0, padx=6, pady=4)
ttk.Button(frame_botones, text="⛔ Detener", width=18, command=detener).grid(row=0, column=1, padx=6, pady=4)

# Cambiar tema
boton_tema = ttk.Button(ventana, text="Tema: Oscuro", width=20, command=toggle_tema)
boton_tema.pack(pady=5)

aplicar_tema()
ventana.mainloop()
