"""
Dashboard principal con sidebar lateral y control de acceso por rol.
"""
import customtkinter as ctk

CLR_SKY_DARK     = "#0ea5e9"
CLR_SKY_XDARK    = "#0284c7"
CLR_SKY_XLIGHT   = "#f0f9ff"
CLR_SKY_LIGHT    = "#e0f2fe"
CLR_WHITE        = "#ffffff"
CLR_SIDEBAR_BG   = "#e8f4fd"
CLR_SIDEBAR_LINE = "#bae6fd"
CLR_ACTIVE_BG    = "#bfdbfe"
CLR_ACTIVE_TEXT  = "#1e40af"
CLR_TEXT         = "#0f172a"
CLR_TEXT_SOFT    = "#334155"
CLR_MUTED        = "#94a3b8"
CLR_LOCKED_BG    = "#f8fafc"
CLR_LOCKED_TEXT  = "#cbd5e1"

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

# (key, icon, label, modulo_permiso)
NAV_ITEMS = [
    ("residentes",     "◯", "Residentes",     "residentes"),
    ("medicaciones",   "⊕", "Medicaciones",   "medicaciones"),
    ("habitaciones",   "▣", "Habitaciones",   "habitaciones"),
    ("signos_vitales", "≈", "Signos Vitales", "signos_vitales"),
    ("actividades",    "◆", "Actividades",    "actividades"),
    ("usuarios",       "◉", "Usuarios",       "usuarios"),
    ("respaldo",       "▦", "Respaldo BD",    "respaldo"),
]


class Dashboard(ctk.CTk):
    def __init__(self, usuario: dict | None = None):
        super().__init__()
        self._usuario = usuario or {}
        self.title("Sistema de Gestión de Asilo - CREAN")
        self.minsize(960, 620)
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=CLR_SKY_XLIGHT)
        self._current_screen = None
        self._active_key = None
        self._nav_buttons = {}
        self._build_layout()
        self._show_first_allowed()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self.content_frame = ctk.CTkFrame(self, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _build_sidebar(self):
        from modules.auth import tiene_permiso
        sb = ctk.CTkFrame(self, fg_color=CLR_SIDEBAR_BG, corner_radius=0, width=240)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_columnconfigure(0, weight=1)

        # ── Branding ──────────────────────────────────────────────────────────
        brand = ctk.CTkFrame(sb, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 0))
        icon_box = ctk.CTkFrame(brand, fg_color=CLR_SKY_DARK, corner_radius=12, width=40, height=40)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="✚", font=ctk.CTkFont(size=20)).place(relx=.5, rely=.5, anchor="center")
        title_col = ctk.CTkFrame(brand, fg_color="transparent")
        title_col.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(title_col, text="CREAN", font=ctk.CTkFont(size=17, weight="bold"), text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Sistema de Gestión de Asilo", font=ctk.CTkFont(size=10), text_color=CLR_MUTED).pack(anchor="w")

        # ── Separador ─────────────────────────────────────────────────────────
        ctk.CTkFrame(sb, fg_color=CLR_SIDEBAR_LINE, height=1).grid(row=1, column=0, sticky="ew", padx=16, pady=(20, 8))

        # ── Etiqueta MÓDULOS ──────────────────────────────────────────────────
        ctk.CTkLabel(sb, text="MÓDULOS", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=CLR_MUTED).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 4))

        # ── Botones de navegación ─────────────────────────────────────────────
        nav_frame = ctk.CTkFrame(sb, fg_color="transparent")
        nav_frame.grid(row=3, column=0, sticky="ew", padx=10)
        nav_frame.grid_columnconfigure(0, weight=1)

        for i, (key, icon, label, modulo) in enumerate(NAV_ITEMS):
            allowed = tiene_permiso(modulo)
            self._build_nav_btn(nav_frame, i, key, icon, label, allowed)

        # ── Spacer ────────────────────────────────────────────────────────────
        spacer = ctk.CTkFrame(sb, fg_color="transparent")
        spacer.grid(row=4, column=0, sticky="nsew")
        sb.grid_rowconfigure(4, weight=1)

        # ── Separador footer ──────────────────────────────────────────────────
        ctk.CTkFrame(sb, fg_color=CLR_SIDEBAR_LINE, height=1).grid(row=5, column=0, sticky="ew", padx=16)

        # ── Footer usuario ────────────────────────────────────────────────────
        rol  = self._usuario.get("rol", "admin")
        nombre = self._usuario.get("nombre", "Usuario")
        email  = self._usuario.get("email", "")

        footer = ctk.CTkFrame(sb, fg_color="transparent")
        footer.grid(row=6, column=0, sticky="ew", padx=16, pady=(10, 4))

        avatar = ctk.CTkFrame(footer, fg_color=CLR_SKY_DARK, corner_radius=20, width=36, height=36)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=ROL_ICONS.get(rol, "◯"),
                     font=ctk.CTkFont(size=16)).place(relx=.5, rely=.5, anchor="center")

        info = ctk.CTkFrame(footer, fg_color="transparent")
        info.pack(side="left", padx=(10, 0), fill="x", expand=True)
        ctk.CTkLabel(info, text=nombre, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT).pack(anchor="w")

        rol_lbl = ROL_LABELS.get(rol, rol)
        ctk.CTkLabel(info, text=rol_lbl, font=ctk.CTkFont(size=10),
                     text_color=CLR_MUTED).pack(anchor="w")

        # ── Cerrar sesión ─────────────────────────────────────────────────────
        ctk.CTkButton(
            sb, text="⏻  Cerrar sesión",
            fg_color="#fee2e2", hover_color="#fecaca",
            text_color="#dc2626", font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10, height=36,
            border_width=1, border_color="#fca5a5",
            command=self._logout,
        ).grid(row=7, column=0, sticky="ew", padx=16, pady=(4, 16))

    # ── Botón de navegación (activo o bloqueado) ──────────────────────────────
    def _build_nav_btn(self, parent, row_idx, key, icon, label, allowed):
        bg = "transparent" if allowed else CLR_LOCKED_BG
        btn_frame = ctk.CTkFrame(parent, fg_color=bg, corner_radius=10, height=46)
        btn_frame.grid(row=row_idx, column=0, sticky="ew", pady=2)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_propagate(False)

        icon_color = CLR_TEXT_SOFT if allowed else CLR_LOCKED_TEXT
        text_color = CLR_TEXT_SOFT if allowed else CLR_LOCKED_TEXT

        icon_lbl = ctk.CTkLabel(btn_frame, text=icon, font=ctk.CTkFont(size=16),
                                width=36, text_color=icon_color)
        icon_lbl.grid(row=0, column=0, padx=(12, 0))

        text_lbl = ctk.CTkLabel(btn_frame, text=label, font=ctk.CTkFont(size=13),
                                text_color=text_color, anchor="w")
        text_lbl.grid(row=0, column=1, sticky="w", padx=6)

        if not allowed:
            lock = ctk.CTkLabel(btn_frame, text="◉", font=ctk.CTkFont(size=10),
                                text_color=CLR_LOCKED_TEXT, width=20)
            lock.grid(row=0, column=2, padx=(0, 8))
            return  # sin interacción

        dot = ctk.CTkLabel(btn_frame, text="●", font=ctk.CTkFont(size=8),
                           text_color=CLR_SIDEBAR_BG, width=16)
        dot.grid(row=0, column=2, padx=(0, 8))

        def _make_click(k, bf, il, tl, dt):
            def _click(e=None): self._show_module(k)
            for w in [bf, il, tl, dt]:
                w.bind("<Button-1>", _click)
                w.configure(cursor="hand2")
            return _click

        self._nav_buttons[key] = (btn_frame, icon_lbl, text_lbl, dot,
                                  _make_click(key, btn_frame, icon_lbl, text_lbl, dot))

    # ── Primer módulo disponible ──────────────────────────────────────────────
    def _show_first_allowed(self):
        from modules.auth import tiene_permiso
        for key, _, _, modulo in NAV_ITEMS:
            if tiene_permiso(modulo):
                self._show_module(key)
                return
        self._show_access_denied("Sin módulos asignados")

    # ── Mostrar módulo ────────────────────────────────────────────────────────
    def _show_module(self, key: str):
        from modules.auth import tiene_permiso
        # Buscar modulo de permiso para este key
        modulo = next((m for k, _, _, m in NAV_ITEMS if k == key), key)
        if not tiene_permiso(modulo):
            return

        if self._current_screen:
            self._current_screen.destroy()
            self._current_screen = None

        # Actualizar estado visual de botones
        for k, (bf, il, tl, dt, _) in self._nav_buttons.items():
            if k == key:
                bf.configure(fg_color=CLR_ACTIVE_BG)
                tl.configure(text_color=CLR_ACTIVE_TEXT, font=ctk.CTkFont(size=13, weight="bold"))
                dt.configure(text_color=CLR_SKY_DARK)
            else:
                bf.configure(fg_color="transparent")
                tl.configure(text_color=CLR_TEXT_SOFT, font=ctk.CTkFont(size=13))
                dt.configure(text_color=CLR_SIDEBAR_BG)

        screen = self._load_screen(key)
        screen.grid(row=0, column=0, sticky="nsew")
        self._current_screen = screen
        self._active_key = key

    def _load_screen(self, key: str):
        if key == "residentes":
            from ui.screens.residentes_screen import ResidentesScreen
            return ResidentesScreen(self.content_frame)
        elif key == "medicaciones":
            from ui.screens.medicacion_screen import MedicacionScreen
            return MedicacionScreen(self.content_frame)
        elif key == "habitaciones":
            from ui.screens.habitaciones_screen import HabitacionesScreen
            return HabitacionesScreen(self.content_frame)
        elif key == "signos_vitales":
            from ui.screens.signos_vitales_screen import SignosVitalesScreen
            return SignosVitalesScreen(self.content_frame)
        elif key == "actividades":
            from ui.screens.actividades_screen import ActividadesScreen
            return ActividadesScreen(self.content_frame)
        elif key == "usuarios":
            from ui.screens.usuarios_screen import UsuariosScreen
            return UsuariosScreen(self.content_frame)
        elif key == "respaldo":
            from ui.screens.respaldo_screen import RespaldoScreen
            return RespaldoScreen(self.content_frame)
        else:
            return self._placeholder(key)

    # ── Placeholder ───────────────────────────────────────────────────────────
    def _placeholder(self, key: str):
        label_map = {k: l for k, _, l, _ in NAV_ITEMS}
        frame = ctk.CTkFrame(self.content_frame, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        inner = ctk.CTkFrame(frame, fg_color=CLR_WHITE, corner_radius=16,
                             border_width=1, border_color="#e2e8f0", width=420, height=200)
        inner.grid(row=0, column=0)
        inner.grid_propagate(False)
        ctk.CTkLabel(inner, text="◌", font=ctk.CTkFont(size=40)).pack(pady=(28, 6))
        ctk.CTkLabel(inner, text=f"Módulo '{label_map.get(key, key)}' en desarrollo",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(inner, text="Próximamente — Sprint en desarrollo",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4, 0))
        return frame

    def _show_access_denied(self, msg="Sin acceso"):
        frame = ctk.CTkFrame(self.content_frame, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        inner = ctk.CTkFrame(frame, fg_color=CLR_WHITE, corner_radius=16,
                             border_width=1, border_color="#e2e8f0", width=380, height=180)
        inner.grid(row=0, column=0)
        inner.grid_propagate(False)
        ctk.CTkLabel(inner, text="◉", font=ctk.CTkFont(size=36)).pack(pady=(28, 6))
        ctk.CTkLabel(inner, text=msg, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=CLR_TEXT).pack()
        return frame

    # ── Logout ────────────────────────────────────────────────────────────────
    def _logout(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.geometry("360x185")
        dialog.grab_set()
        dialog.configure(fg_color=CLR_WHITE)
        dialog.resizable(False, False)
        ctk.CTkLabel(dialog, text="⏻", font=ctk.CTkFont(size=34)).pack(pady=(22, 4))
        ctk.CTkLabel(dialog, text="¿Cerrar sesión?",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text="Se cerrará la aplicación.",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(3, 0))
        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=18, padx=24, fill="x")
        ctk.CTkButton(row, text="Cancelar", fg_color=CLR_WHITE,
                      border_width=1, border_color="#e2e8f0",
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      height=38, corner_radius=8,
                      command=dialog.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Sí, salir", fg_color="#ef4444",
                      hover_color="#dc2626", text_color=CLR_WHITE,
                      height=38, corner_radius=8,
                      command=self.destroy).pack(side="right", expand=True, fill="x")