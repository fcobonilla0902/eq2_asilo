"""
Pantalla de Login — UI moderna acorde al diseño del proyecto.
"""
import customtkinter as ctk

# ── Paleta (misma que dashboard) ──────────────────────────────────────────────
CLR_SKY_DARK   = "#0ea5e9"
CLR_SKY_XDARK  = "#0284c7"
CLR_SKY_LIGHT  = "#e0f2fe"
CLR_SKY_XLIGHT = "#f0f9ff"
CLR_WHITE      = "#ffffff"
CLR_TEXT       = "#0f172a"
CLR_TEXT_SOFT  = "#334155"
CLR_MUTED      = "#94a3b8"
CLR_BORDER     = "#e2e8f0"
CLR_RED        = "#ef4444"
CLR_RED_LIGHT  = "#fee2e2"
CLR_SIDEBAR_BG = "#e8f4fd"

ROL_LABELS = {
    "admin":     "Administrador",
    "enfermero": "Enfermero/a",
    "doctor":    "Doctor/a",
}

ROL_ICONS = {
    "admin":     "◈",
    "enfermero": "⊕",
    "doctor":    "◎",
}


class LoginScreen(ctk.CTkFrame):
    """
    Pantalla de login con diseño dividido en dos paneles.
    on_success(datos_usuario) se llama al autenticar correctamente.
    """

    def __init__(self, master, on_success):
        super().__init__(master, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.on_success = on_success
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────
    def _build(self):
        # Contenedor centrado
        card = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=20,
                            border_width=1, border_color=CLR_BORDER)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(0, weight=1)

        self._build_left_panel(card)
        self._build_right_panel(card)

    # ── Panel izquierdo (branding) ────────────────────────────────────────────
    def _build_left_panel(self, parent):
        left = ctk.CTkFrame(parent, fg_color=CLR_SKY_DARK, corner_radius=0,
                                    width=270, height=420)
        left.grid(row=0, column=0, sticky="ew")
        left.grid_propagate(False)

        # Icono grande
        icon_box = ctk.CTkFrame(left, fg_color=CLR_SKY_XDARK, corner_radius=20,
                                width=72, height=72)
        icon_box.place(relx=0.5, y=70, anchor="center")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="✚", font=ctk.CTkFont(size=36)).place(
            relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(left, text="CREAN",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=CLR_WHITE).place(relx=0.5, y=140, anchor="center")
        ctk.CTkLabel(left, text="Sistema de Gestión de Asilo",
                     font=ctk.CTkFont(size=13),
                     text_color="#bae6fd").place(relx=0.5, y=165, anchor="center")

        # Separador
        ctk.CTkFrame(left, fg_color="#0284c7", height=1, width=200).place(
            relx=0.5, y=195, anchor="center")

        # Info de roles
        roles_frame = ctk.CTkFrame(left, fg_color="transparent")
        roles_frame.place(relx=0.5, y=295, anchor="center")

        ctk.CTkLabel(roles_frame, text="Roles del sistema",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#bae6fd").pack(pady=(0, 8))

        for rol, label in ROL_LABELS.items():
            row = ctk.CTkFrame(roles_frame, fg_color="#0284c7",
                               corner_radius=8, height=32)
            row.pack(fill="x", pady=2, padx=4)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=f"{ROL_ICONS[rol]}  {label}",
                         font=ctk.CTkFont(size=12),
                         text_color=CLR_WHITE).pack(side="left", padx=10, pady=4)


    # ── Panel derecho (formulario) ────────────────────────────────────────────
    def _build_right_panel(self, parent):
        right = ctk.CTkFrame(parent, fg_color=CLR_WHITE, corner_radius=0, width=320, height=380)
        right.grid(row=0, column=1, sticky="nsew", padx=0)
        right.grid_propagate(False)
        right.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(right, text="Bienvenido",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=CLR_TEXT).pack(pady=(28, 2))
        ctk.CTkLabel(right, text="Ingresa tus credenciales para continuar",
                     font=ctk.CTkFont(size=12),
                     text_color=CLR_MUTED).pack()

        # Separador
        ctk.CTkFrame(right, fg_color=CLR_BORDER, height=1).pack(
            fill="x", padx=32, pady=(14, 16))

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(fill="x", padx=32)
        form.grid_columnconfigure(0, weight=1)

        # Campo usuario
        ctk.CTkLabel(form, text="Usuario (CURP)",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT,
                     anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.entry_usuario = ctk.CTkEntry(
            form, placeholder_text="CURP",
            height=42, corner_radius=10,
            border_color=CLR_BORDER, border_width=1,
            font=ctk.CTkFont(size=13))
        self.entry_usuario.grid(row=1, column=0, sticky="ew")
        self.entry_usuario.bind("<Return>", lambda e: self.entry_password.focus())

        # Campo contraseña
        ctk.CTkLabel(form, text="Contraseña",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT,
                     anchor="w").grid(row=2, column=0, sticky="w", pady=(16, 4))
        self.entry_password = ctk.CTkEntry(
            form, placeholder_text="••••••••",
            show="•", height=42, corner_radius=10,
            border_color=CLR_BORDER, border_width=1,
            font=ctk.CTkFont(size=13))
        self.entry_password.grid(row=3, column=0, sticky="ew")
        self.entry_password.bind("<Return>", lambda e: self._intentar_login())

        # Mostrar / ocultar contraseña
        self._show_pw = False
        ctk.CTkButton(
            form, text="◉ Mostrar contraseña",
            fg_color="transparent", hover_color=CLR_SKY_LIGHT,
            text_color=CLR_MUTED, font=ctk.CTkFont(size=11),
            height=24, cursor="hand2",
            command=self._toggle_pw,
        ).grid(row=4, column=0, sticky="e", pady=(4, 0))

        # Mensaje de error
        self.lbl_error = ctk.CTkLabel(form, text="",
                                      font=ctk.CTkFont(size=11),
                                      text_color=CLR_RED)
        self.lbl_error.grid(row=5, column=0, pady=(8, 0))

        # Botón login
        self.btn_login = ctk.CTkButton(
            form, text="Iniciar sesión",
            height=44, corner_radius=10,
            fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._intentar_login,
        )
        self.btn_login.grid(row=6, column=0, sticky="ew", pady=(16, 0))

        # Hint credenciales demo
        hint_frame = ctk.CTkFrame(right, fg_color=CLR_SKY_XLIGHT,
                                  corner_radius=10, border_width=1,
                                  border_color=CLR_SKY_LIGHT)
        hint_frame.pack(fill="x", padx=32, pady=(12, 0))

    # ── Lógica ────────────────────────────────────────────────────────────────
    def _toggle_pw(self):
        self._show_pw = not self._show_pw
        self.entry_password.configure(show="" if self._show_pw else "•")

    def _intentar_login(self):
        from modules.auth import validar_usuario, iniciar_sesion
        usuario  = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not usuario or not password:
            self._set_error("Por favor ingresa usuario y contraseña.")
            return

        self.btn_login.configure(text="Verificando...", state="disabled")
        self.update()

        try:
            datos = validar_usuario(usuario, password)
            if datos:
                iniciar_sesion(datos)
                self.lbl_error.configure(text="")
                self.on_success(datos)
            else:
                self._set_error("Usuario o contraseña incorrectos.")
                self.entry_password.delete(0, "end")
        except Exception as e:
            self._set_error(f"Error: {e}")
        finally:
            self.btn_login.configure(text="Iniciar sesión", state="normal")

    def _set_error(self, msg: str):
        self.lbl_error.configure(text=f"▲  {msg}")
        self.btn_login.configure(text="Iniciar sesión", state="normal")