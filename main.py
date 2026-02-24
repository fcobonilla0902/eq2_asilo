"""
Punto de entrada de la aplicación.
Inicializa la BD y lanza la ventana de login.
"""
import sys
import os

# Asegura que los imports relativos funcionen desde cualquier directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.schema import init_db

def main():
    # 1. Inicializar BD (crea tablas si no existen)
    init_db()

    # 2. Lanzar UI  (descomentar cuando P4/P5 tengan la pantalla lista)
    # import customtkinter as ctk
    # from ui.screens.login import LoginScreen
    # ctk.set_appearance_mode("dark")
    # ctk.set_default_color_theme("blue")
    # app = LoginScreen()
    # app.mainloop()

    print("BD inicializada. UI pendiente (Sprint 1 - P4/P5).")

if __name__ == "__main__":
    main()
