"""
Dashboard principal con sidebar lateral izquierdo.
"""
import customtkinter as ctk

CLR_SKY_DARK     = "#0ea5e9"
CLR_SKY_XLIGHT   = "#f0f9ff"
CLR_WHITE        = "#ffffff"
CLR_SIDEBAR_BG   = "#e8f4fd"
CLR_SIDEBAR_LINE = "#bae6fd"
CLR_ACTIVE_BG    = "#bfdbfe"
CLR_ACTIVE_TEXT  = "#1e40af"
CLR_TEXT         = "#0f172a"
CLR_TEXT_SOFT    = "#334155"
CLR_MUTED        = "#94a3b8"


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión — Asilo")
        self.geometry("1300x800")
        self.minsize(960, 620)
        self.configure(fg_color=CLR_SKY_XLIGHT)
        self._current_screen = None
        self._active_key = None
        self._nav_buttons = {}
        self._build_layout()
        self._show_module("residentes")

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self.content_frame = ctk.CTkFrame(self, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=CLR_SIDEBAR_BG, corner_radius=0, width=240)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_columnconfigure(0, weight=1)

        # ── row 0: Branding ───────────────────────────────────────────────────
        brand = ctk.CTkFrame(sb, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 0))
        icon_box = ctk.CTkFrame(brand, fg_color=CLR_SKY_DARK, corner_radius=12, width=40, height=40)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="🏥", font=ctk.CTkFont(size=20)).place(relx=.5, rely=.5, anchor="center")
        title_col = ctk.CTkFrame(brand, fg_color="transparent")
        title_col.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(title_col, text="Asilo", font=ctk.CTkFont(size=17, weight="bold"), text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Sistema de Gestión", font=ctk.CTkFont(size=10), text_color=CLR_MUTED).pack(anchor="w")

        # ── row 1: separador ──────────────────────────────────────────────────
        ctk.CTkFrame(sb, fg_color=CLR_SIDEBAR_LINE, height=1).grid(row=1, column=0, sticky="ew", padx=16, pady=(20, 8))

        # ── row 2: label MÓDULOS ──────────────────────────────────────────────
        ctk.CTkLabel(sb, text="MÓDULOS", font=ctk.CTkFont(size=10, weight="bold"), text_color=CLR_MUTED).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 4))

        # ── row 3: botones activos ────────────────────────────────────────────
        nav_frame = ctk.CTkFrame(sb, fg_color="transparent")
        nav_frame.grid(row=3, column=0, sticky="ew", padx=10)
        nav_frame.grid_columnconfigure(0, weight=1)

        for i, (key, icon, label) in enumerate([("residentes","👤","Residentes"),("medicaciones","💊","Medicaciones"),("habitaciones","🏠","Habitaciones")]):
            btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent", corner_radius=10, height=46)
            btn_frame.grid(row=i, column=0, sticky="ew", pady=2)
            btn_frame.grid_columnconfigure(1, weight=1)
            btn_frame.grid_propagate(False)
            icon_lbl = ctk.CTkLabel(btn_frame, text=icon, font=ctk.CTkFont(size=16), width=36)
            icon_lbl.grid(row=0, column=0, padx=(12, 0))
            text_lbl = ctk.CTkLabel(btn_frame, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color=CLR_TEXT_SOFT, anchor="w")
            text_lbl.grid(row=0, column=1, sticky="w", padx=6)
            dot = ctk.CTkLabel(btn_frame, text="●", font=ctk.CTkFont(size=8), text_color=CLR_SIDEBAR_BG, width=16)
            dot.grid(row=0, column=2, padx=(0, 8))
            def _make_click(k, bf, il, tl, dt):
                def _click(e=None): self._show_module(k)
                for w in [bf, il, tl, dt]:
                    w.bind("<Button-1>", _click)
                    w.configure(cursor="hand2")
                return _click
            self._nav_buttons[key] = (btn_frame, icon_lbl, text_lbl, dot, _make_click(key, btn_frame, icon_lbl, text_lbl, dot))

        # ── row 4: separador ──────────────────────────────────────────────────
        ctk.CTkFrame(sb, fg_color=CLR_SIDEBAR_LINE, height=1).grid(row=4, column=0, sticky="ew", padx=16, pady=(14, 0))

        # ── row 5: label PRÓXIMAMENTE ─────────────────────────────────────────
        ctk.CTkLabel(sb, text="PRÓXIMAMENTE", font=ctk.CTkFont(size=10, weight="bold"), text_color=CLR_MUTED).grid(row=5, column=0, sticky="w", padx=20, pady=(14, 4))

        # ── row 6: ítems pendientes ───────────────────────────────────────────
        pending_frame = ctk.CTkFrame(sb, fg_color="transparent")
        pending_frame.grid(row=6, column=0, sticky="new", padx=10)
        pending_frame.grid_columnconfigure(0, weight=1)
        for i, (icon, label) in enumerate([("👥","Enfermeros"),("📈","Signos Vitales"),("❤️","Actividades"),("🔒","Autenticación")]):
            row_f = ctk.CTkFrame(pending_frame, fg_color="transparent", height=38)
            row_f.grid(row=i, column=0, sticky="ew", pady=1)
            row_f.grid_columnconfigure(1, weight=1)
            row_f.grid_propagate(False)
            ctk.CTkLabel(row_f, text=icon, font=ctk.CTkFont(size=13), width=36, text_color=CLR_MUTED).grid(row=0, column=0, padx=(12,0))
            ctk.CTkLabel(row_f, text=label, font=ctk.CTkFont(size=12), text_color=CLR_MUTED, anchor="w").grid(row=0, column=1, sticky="w", padx=4)
            badge = ctk.CTkFrame(row_f, fg_color="#dbeafe", corner_radius=4, width=44, height=18)
            badge.grid(row=0, column=2, padx=(0,12))
            badge.grid_propagate(False)
            ctk.CTkLabel(badge, text="Pronto", font=ctk.CTkFont(size=9), text_color="#3b82f6").place(relx=.5, rely=.5, anchor="center")

        # ── row 7: spacer ─────────────────────────────────────────────────────
        spacer = ctk.CTkFrame(sb, fg_color="transparent")
        spacer.grid(row=7, column=0, sticky="nsew")
        sb.grid_rowconfigure(7, weight=1)

        # ── row 8: separador footer ───────────────────────────────────────────
        ctk.CTkFrame(sb, fg_color=CLR_SIDEBAR_LINE, height=1).grid(row=8, column=0, sticky="ew", padx=16)

        # ── row 9: footer usuario ─────────────────────────────────────────────
        footer = ctk.CTkFrame(sb, fg_color="transparent")
        footer.grid(row=9, column=0, sticky="ew", padx=16, pady=(10, 4))
        avatar = ctk.CTkFrame(footer, fg_color=CLR_SKY_DARK, corner_radius=20, width=36, height=36)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text="A", font=ctk.CTkFont(size=14, weight="bold"), text_color=CLR_WHITE).place(relx=.5, rely=.5, anchor="center")
        info = ctk.CTkFrame(footer, fg_color="transparent")
        info.pack(side="left", padx=(10,0), fill="x", expand=True)
        ctk.CTkLabel(info, text="Administrador", font=ctk.CTkFont(size=12, weight="bold"), text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(info, text="admin@asilo.mx", font=ctk.CTkFont(size=10), text_color=CLR_MUTED).pack(anchor="w")

        # ── row 10: cerrar sesión ─────────────────────────────────────────────
        ctk.CTkButton(
            sb, text="⏻  Cerrar sesión",
            fg_color="#fee2e2", hover_color="#fecaca",
            text_color="#dc2626", font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10, height=36,
            border_width=1, border_color="#fca5a5",
            command=self._logout,
        ).grid(row=10, column=0, sticky="ew", padx=16, pady=(4, 16))

    def _logout(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.geometry("360x185")
        dialog.grab_set()
        dialog.configure(fg_color=CLR_WHITE)
        dialog.resizable(False, False)
        ctk.CTkLabel(dialog, text="⏻", font=ctk.CTkFont(size=34)).pack(pady=(22, 4))
        ctk.CTkLabel(dialog, text="¿Cerrar sesión?", font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text="Se cerrará la aplicación.", font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(3,0))
        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=18, padx=24, fill="x")
        ctk.CTkButton(row, text="Cancelar", fg_color=CLR_WHITE, border_width=1, border_color="#e2e8f0",
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9", height=38, corner_radius=8,
                      command=dialog.destroy).pack(side="left", expand=True, fill="x", padx=(0,6))
        ctk.CTkButton(row, text="Si, salir", fg_color="#ef4444", hover_color="#dc2626",
                      text_color=CLR_WHITE, height=38, corner_radius=8,
                      command=self.destroy).pack(side="right", expand=True, fill="x")

    def _show_module(self, key: str):
        if self._current_screen:
            self._current_screen.destroy()
            self._current_screen = None
        for k, (bf, il, tl, dt, _) in self._nav_buttons.items():
            if k == key:
                bf.configure(fg_color=CLR_ACTIVE_BG)
                tl.configure(text_color=CLR_ACTIVE_TEXT, font=ctk.CTkFont(size=13, weight="bold"))
                dt.configure(text_color=CLR_SKY_DARK)
            else:
                bf.configure(fg_color="transparent")
                tl.configure(text_color=CLR_TEXT_SOFT, font=ctk.CTkFont(size=13))
                dt.configure(text_color=CLR_SIDEBAR_BG)
        if key == "residentes":
            from ui.screens.residentes_screen import ResidentesScreen
            screen = ResidentesScreen(self.content_frame)
        elif key == "medicaciones":
            from ui.screens.medicacion_screen import MedicacionScreen
            screen = MedicacionScreen(self.content_frame)
        elif key == "habitaciones":
            from ui.screens.habitaciones_screen import HabitacionesScreen
            screen = HabitacionesScreen(self.content_frame)
        else:
            screen = self._placeholder(key)
        screen.grid(row=0, column=0, sticky="nsew")
        self._current_screen = screen
        self._active_key = key

    def _placeholder(self, key: str):
        frame = ctk.CTkFrame(self.content_frame, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        inner = ctk.CTkFrame(frame, fg_color=CLR_WHITE, corner_radius=16,
                             border_width=1, border_color="#e2e8f0", width=420, height=200)
        inner.grid(row=0, column=0)
        inner.grid_propagate(False)
        ctk.CTkLabel(inner, text="🚧", font=ctk.CTkFont(size=40)).pack(pady=(28, 6))
        ctk.CTkLabel(inner, text=f"Modulo '{key}' en desarrollo",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(inner, text="Proximamente — Sprint en desarrollo",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4,0))
        return frame