"""
Punto de entrada de la aplicación.
Inicializa la BD, muestra el login y luego lanza el Dashboard.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.schema import init_db


def main():
    init_db()

    # Inicializar auth (crea tabla usuarios y datos de prueba)
    from modules.auth import inicializar_modulo_auth
    inicializar_modulo_auth()

    import customtkinter as ctk
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # ── Ventana raíz temporal para el login ───────────────────────────────────
    root = ctk.CTk()
    root.title("Sistema de Gestión — Asilo")
    root.resizable(False, False)
    root.configure(fg_color="#f0f9ff")

    # Centrar ventana en la mitad de la pantalla
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    w, h = 620, 420
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    def on_login_success(datos_usuario):
        root.destroy()
        # Lanzar dashboard con el usuario autenticado
        app = Dashboard(usuario=datos_usuario)
        app.mainloop()

    from ui.screens.login import LoginScreen
    login = LoginScreen(root, on_success=on_login_success)
    login.grid(row=0, column=0, sticky="nsew")

    root.mainloop()


if __name__ == "__main__":
    from ui.screens.dashboard import Dashboard
    main()