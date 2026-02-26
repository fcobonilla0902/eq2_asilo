"""
Punto de entrada de la aplicación.
Inicializa la BD y lanza la ventana principal con sidebar.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.schema import init_db


def main():
    init_db()

    import customtkinter as ctk
    from ui.screens.dashboard import Dashboard

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = Dashboard()
    app.mainloop()


if __name__ == "__main__":
    main()