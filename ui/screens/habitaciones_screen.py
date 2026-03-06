"""
Pantalla de Habitaciones — CustomTkinter
CRUD completo: listar, agregar, editar, eliminar.
"""
import customtkinter as ctk

CLR_SKY_DARK   = "#0ea5e9"
CLR_SKY_XDARK  = "#0284c7"
CLR_SKY_LIGHT  = "#e0f2fe"
CLR_SKY_XLIGHT = "#f0f9ff"
CLR_WHITE      = "#ffffff"
CLR_BORDER     = "#e2e8f0"
CLR_TEXT       = "#0f172a"
CLR_TEXT_SOFT  = "#334155"
CLR_MUTED      = "#94a3b8"
CLR_BG         = "#f8fafc"
CLR_ROW_ALT    = "#f8fafc"
CLR_RED        = "#ef4444"
CLR_RED_LIGHT  = "#fee2e2"
CLR_GREEN      = "#22c55e"
CLR_AMBER      = "#f59e0b"
CLR_AMBER_LIGHT= "#fef3c7"


def _center(win, w, h):
    """Centra una ventana Toplevel en la pantalla."""
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x  = (sw - w) // 2
    y  = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

TIPO_NOMBRES = {"2":"Doble","3":"Triple","4":"Cuádruple"}
TIPO_ICONS   = {"2":"🛏🛏","3":"🛛🛏🛏","4":"🏨"}
TIPO_COLORS  = {"2":"#d1fae5","3":"#fef3c7","4":"#fce7f3"}
TIPO_FG      = {"2":"#065f46","3":"#92400e","4":"#9d174d"}


def _listar():
    from modules.habitaciones import listar_habitaciones
    return listar_habitaciones()

def _listar_por_tipo(tipo):
    from modules.habitaciones import listar_habitaciones_por_tipo
    return listar_habitaciones_por_tipo(tipo)

def _crear(datos):
    from modules.habitaciones import crear_habitacion
    return crear_habitacion(datos)

def _actualizar(hid, datos):
    from modules.habitaciones import actualizar_habitacion
    return actualizar_habitacion(hid, datos)

def _eliminar(hid):
    from modules.habitaciones import eliminar_habitacion
    return eliminar_habitacion(hid)


class HabitacionesScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._selected_id    = None
        self._selected_frame = None
        self._all_rows       = []
        self._filter_tipo    = "Todos"
        self._build_topbar()
        self._build_stats()
        self._build_content()
        self._load_data()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=0, border_width=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        tc = ctk.CTkFrame(bar, fg_color="transparent")
        tc.grid(row=0, column=0, padx=28, pady=14, sticky="w")
        ctk.CTkLabel(tc, text="Habitaciones",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(tc, text="Gestión de habitaciones del asilo",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")

        # Filtro rápido por tipo
        filter_frame = ctk.CTkFrame(bar, fg_color="transparent")
        filter_frame.grid(row=0, column=1, padx=16, pady=14, sticky="w")
        for tipo in ["Todos","Doble","Triple","Cuádruple"]:
            ctk.CTkButton(filter_frame, text=tipo,
                          fg_color=CLR_SKY_DARK if tipo==self._filter_tipo else CLR_BG,
                          hover_color=CLR_SKY_LIGHT,
                          text_color=CLR_WHITE if tipo==self._filter_tipo else CLR_TEXT_SOFT,
                          font=ctk.CTkFont(size=11),
                          corner_radius=8, height=30, width=80,
                          border_width=1, border_color=CLR_BORDER,
                          command=lambda t=tipo: self._set_filter(t),
                          ).pack(side="left", padx=3)
        self._filter_frame = filter_frame

        ctk.CTkButton(bar, text="＋  Nueva habitación",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=10, height=38, command=self._open_form,
                      ).grid(row=0, column=2, padx=(8,28), pady=14)

        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).grid(row=1, column=0, columnspan=3, sticky="ew")

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _build_stats(self):
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, sticky="ew", padx=24, pady=(18,0))
        sf.grid_columnconfigure((0,1,2,3), weight=1)
        self._stat_total = self._stat_card(sf, 0, "Total", "0", "🏨", CLR_SKY_DARK, "#dbeafe")
        self._stat_dob   = self._stat_card(sf, 1, "Dobles", "0", "🛏🛏", "#065f46", "#d1fae5")
        self._stat_tri   = self._stat_card(sf, 2, "Triples", "0", "🛏🛏🛏", "#92400e", "#fef3c7")
        self._stat_cua   = self._stat_card(sf, 3, "Cuádruples", "0", "🏨", "#9d174d", "#fce7f3")

    def _stat_card(self, parent, col, title, value, icon, ic, ib):
        card = ctk.CTkFrame(parent, fg_color=CLR_WHITE, corner_radius=14,
                            border_width=1, border_color=CLR_BORDER)
        card.grid(row=0, column=col, padx=6, sticky="ew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        ib_f = ctk.CTkFrame(inner, fg_color=ib, corner_radius=10, width=40, height=40)
        ib_f.pack(side="left"); ib_f.pack_propagate(False)
        ctk.CTkLabel(ib_f, text=icon, font=ctk.CTkFont(size=18)).place(relx=.5,rely=.5,anchor="center")
        tc = ctk.CTkFrame(inner, fg_color="transparent")
        tc.pack(side="left", padx=(12,0))
        lbl = ctk.CTkLabel(tc, text=value, font=ctk.CTkFont(size=26, weight="bold"), text_color=CLR_TEXT)
        lbl.pack(anchor="w")
        ctk.CTkLabel(tc, text=title, font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")
        return lbl

    # ── Contenido (grid de tarjetas) ──────────────────────────────────────────
    def _build_content(self):
        outer = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=14,
                             border_width=1, border_color=CLR_BORDER)
        outer.grid(row=2, column=0, sticky="nsew", padx=24, pady=16)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        self._grid_scroll = ctk.CTkScrollableFrame(outer, fg_color=CLR_BG, corner_radius=0)
        self._grid_scroll.grid(row=0, column=0, sticky="nsew")

        # Barra de acciones
        bar = ctk.CTkFrame(outer, fg_color=CLR_BG, corner_radius=0, height=52)
        bar.grid(row=1, column=0, sticky="ew"); bar.grid_propagate(False)
        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).place(relx=0, rely=0, relwidth=1)

        self._lbl_sel = ctk.CTkLabel(bar, text="Selecciona una habitación para ver acciones",
                                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED)
        self._lbl_sel.pack(side="left", padx=20)

        self._btn_del = ctk.CTkButton(bar, text="Eliminar",
                                      fg_color=CLR_RED_LIGHT, hover_color="#fecaca",
                                      text_color=CLR_RED, font=ctk.CTkFont(size=12, weight="bold"),
                                      corner_radius=8, height=34, width=100,
                                      border_width=1, border_color="#fca5a5",
                                      state="disabled", command=self._confirm_delete)
        self._btn_del.pack(side="right", padx=(4,20), pady=9)

        self._btn_edit = ctk.CTkButton(bar, text="Editar",
                                       fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
                                       text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=12, weight="bold"),
                                       corner_radius=8, height=34, width=100,
                                       border_width=1, border_color="#7dd3fc",
                                       state="disabled", command=self._open_edit)
        self._btn_edit.pack(side="right", padx=4, pady=9)

    # ── Datos ─────────────────────────────────────────────────────────────────
    def _load_data(self):
        try:
            rows = _listar()
        except Exception:
            rows = []
        self._all_rows = [dict(r) for r in rows]
        self._render_grid()
        self._update_stats()

    def _update_stats(self):
        rows = self._all_rows
        total = len(rows)
        dob   = sum(1 for r in rows if str(r.get("tipo",""))=="2")
        tri   = sum(1 for r in rows if str(r.get("tipo",""))=="3")
        cua   = sum(1 for r in rows if str(r.get("tipo",""))=="4")
        self._stat_total.configure(text=str(total))
        self._stat_dob.configure(text=str(dob))
        self._stat_tri.configure(text=str(tri))
        self._stat_cua.configure(text=str(cua))

    def _set_filter(self, tipo):
        self._filter_tipo = tipo
        # Actualizar botones de filtro
        for btn in self._filter_frame.winfo_children():
            t = btn.cget("text")
            if t == tipo:
                btn.configure(fg_color=CLR_SKY_DARK, text_color=CLR_WHITE)
            else:
                btn.configure(fg_color=CLR_BG, text_color=CLR_TEXT_SOFT)
        self._render_grid()

    def _render_grid(self):
        for w in self._grid_scroll.winfo_children():
            w.destroy()
        self._selected_id = None; self._selected_frame = None
        self._set_actions(False)

        tipo_map = {"Doble":"2","Triple":"3","Cuádruple":"4"}
        rows = self._all_rows
        if self._filter_tipo != "Todos":
            t = tipo_map.get(self._filter_tipo, self._filter_tipo)
            rows = [r for r in rows if str(r.get("tipo",""))==t]

        if not rows:
            for c in range(4):
                self._grid_scroll.grid_columnconfigure(c, weight=1)
            e = ctk.CTkFrame(self._grid_scroll, fg_color="transparent")
            e.grid(row=0, column=0, columnspan=4, pady=60, sticky="ew")
            e.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(e, text="🏨", font=ctk.CTkFont(size=40), anchor="center").grid(row=0, column=0)
            ctk.CTkLabel(e, text="No hay habitaciones registradas",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=CLR_TEXT_SOFT, anchor="center").grid(row=1, column=0, pady=(8,2))
            ctk.CTkLabel(e, text="Usa el botón '＋ Nueva habitación' para agregar",
                         font=ctk.CTkFont(size=11), text_color=CLR_MUTED,
                         anchor="center").grid(row=2, column=0)
            return

        # Grid de 4 columnas
        COLS = 4
        for c in range(COLS):
            self._grid_scroll.grid_columnconfigure(c, weight=1)

        for idx, r in enumerate(rows):
            hid    = r.get("id_habitacion")
            numero = r.get("numero","—")
            tipo   = str(r.get("tipo",""))
            t_nombre = TIPO_NOMBRES.get(tipo, tipo)
            t_icon   = TIPO_ICONS.get(tipo, "🏠")
            t_color  = TIPO_COLORS.get(tipo, "#f0f9ff")
            t_fg     = TIPO_FG.get(tipo, CLR_SKY_XDARK)

            row_idx = idx // COLS
            col_idx = idx % COLS

            card = ctk.CTkFrame(self._grid_scroll, fg_color=CLR_WHITE, corner_radius=14,
                                border_width=2, border_color=CLR_BORDER)
            card.grid(row=row_idx, column=col_idx, padx=8, pady=8, sticky="ew")

            # Banda de color superior
            top_band = ctk.CTkFrame(card, fg_color=t_color, corner_radius=0, height=52)
            top_band.pack(fill="x")
            top_band.pack_propagate(False)
            ctk.CTkLabel(top_band, text=t_icon, font=ctk.CTkFont(size=28)).place(relx=.5,rely=.5,anchor="center")

            ctk.CTkLabel(card, text=f"Hab. #{numero}",
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=CLR_TEXT
                         ).pack(pady=(10,2))

            tipo_badge = ctk.CTkFrame(card, fg_color=t_color, corner_radius=6)
            tipo_badge.pack(pady=(0,12))
            ctk.CTkLabel(tipo_badge, text=t_nombre,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=t_fg).pack(padx=10, pady=3)

            def _sel(h=hid, c2=card):
                self._select(h, c2)
            for w in [card, top_band]:
                w.bind("<Button-1>", lambda e, fn=_sel: fn())
                w.configure(cursor="hand2")

            self._card_map = getattr(self, "_card_map", {})
            self._card_map[hid] = card

        self._card_map = {r.get("id_habitacion"): None for r in rows}
        # Re-store cards after render
        for idx, r in enumerate(rows):
            hid = r.get("id_habitacion")
            ri, ci = idx//COLS, idx%COLS
            children = self._grid_scroll.grid_slaves(row=ri, column=ci)
            if children:
                self._card_map[hid] = children[0]

    # ── Selección ─────────────────────────────────────────────────────────────
    def _select(self, hid, card):
        # Deseleccionar anterior
        if self._selected_frame and self._selected_frame.winfo_exists():
            self._selected_frame.configure(border_color=CLR_BORDER)
        card.configure(border_color=CLR_SKY_DARK)
        self._selected_id = hid; self._selected_frame = card
        self._set_actions(True)
        self._lbl_sel.configure(text=f"Habitación ID {hid} seleccionada", text_color=CLR_SKY_XDARK)

    def _set_actions(self, on):
        s = "normal" if on else "disabled"
        self._btn_edit.configure(state=s); self._btn_del.configure(state=s)

    # ── Formulario ────────────────────────────────────────────────────────────
    def _open_form(self, datos=None):
        edit = datos is not None
        win = ctk.CTkToplevel(self)
        win.title("Nueva habitación" if not edit else "Editar habitación")
        win.grab_set(); win.resizable(False,False)
        _center(win, 420, 310)
        win.configure(fg_color=CLR_SKY_XLIGHT)

        hdr = ctk.CTkFrame(win, fg_color=CLR_WHITE, corner_radius=0, height=56)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="Nueva habitación" if not edit else "Editar habitación",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color=CLR_TEXT
                     ).pack(side="left", padx=24, pady=14)

        body = ctk.CTkFrame(win, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)
        body.grid_columnconfigure((0,1), weight=1)

        # Número
        ctk.CTkLabel(body, text="Número de habitación *",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color=CLR_TEXT_SOFT
                     ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,4))
        num_entry = ctk.CTkEntry(body, fg_color=CLR_WHITE, border_color=CLR_BORDER,
                                 text_color=CLR_TEXT, height=36, corner_radius=8,
                                 placeholder_text="Ej: 101, A-2, etc.")
        num_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,12))
        if edit and datos.get("numero"):
            num_entry.insert(0, str(datos["numero"]))

        # Tipo
        ctk.CTkLabel(body, text="Tipo de habitación *",
                     font=ctk.CTkFont(size=11, weight="bold"), text_color=CLR_TEXT_SOFT
                     ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0,6))

        tipo_var = ctk.StringVar(value=str(datos.get("tipo","2")) if edit else "2")
        tipo_frame = ctk.CTkFrame(body, fg_color="transparent")
        tipo_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,16))

        tipo_opciones = [("2","Doble"),("3","Triple"),("4","Cuádruple")]
        for val, nombre in tipo_opciones:
            f = ctk.CTkFrame(tipo_frame, fg_color="transparent")
            f.pack(side="left", expand=True, fill="x", padx=3)
            rb = ctk.CTkRadioButton(f, text=nombre, variable=tipo_var, value=val,
                                    fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                                    text_color=CLR_TEXT_SOFT, font=ctk.CTkFont(size=12))
            rb.pack(anchor="center")

        # Botones
        btn_bar = ctk.CTkFrame(win, fg_color=CLR_WHITE, corner_radius=0)
        btn_bar.pack(fill="x", side="bottom")
        btn_bar.grid_columnconfigure((0,1), weight=1)

        def _save():
            numero = num_entry.get().strip()
            tipo   = tipo_var.get()
            if not numero:
                self._toast("El número de habitación es obligatorio", error=True)
                win.destroy(); return
            try:
                if edit:
                    _actualizar(datos["id_habitacion"], {"numero": numero, "tipo": tipo})
                    msg = "Habitación actualizada"
                else:
                    _crear({"numero": numero, "tipo": tipo})
                    msg = "Habitación creada"
                self._toast(msg); win.destroy(); self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True); win.destroy()

        ctk.CTkButton(btn_bar, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=8, height=46, command=win.destroy
                      ).grid(row=0, column=0, sticky="ew", padx=(20,8), pady=16)
        ctk.CTkButton(btn_bar, text="Guardar",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, corner_radius=8, height=46, command=_save
                      ).grid(row=0, column=1, sticky="ew", padx=(8,20), pady=16)

    def _open_edit(self):
        if not self._selected_id: return
        r = next((r for r in self._all_rows if r.get("id_habitacion")==self._selected_id), None)
        if r: self._open_form(datos=r)

    # ── Eliminar ──────────────────────────────────────────────────────────────
    def _confirm_delete(self):
        if not self._selected_id: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.grab_set(); dialog.configure(fg_color=CLR_WHITE); dialog.resizable(False,False)
        _center(dialog, 380, 210)
        ctk.CTkLabel(dialog, text="⚠️", font=ctk.CTkFont(size=36)).pack(pady=(24,4))
        ctk.CTkLabel(dialog, text="¿Eliminar esta habitación?",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text="Los residentes asignados quedarán sin habitación.",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4,0))
        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=20, padx=24, fill="x")
        def _do():
            try:
                _eliminar(self._selected_id)
                self._toast("Habitación eliminada")
                dialog.destroy(); self._selected_id=None; self._selected_frame=None
                self._set_actions(False); self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True); dialog.destroy()
        ctk.CTkButton(row, text="Cancelar", fg_color=CLR_WHITE, border_width=1,
                      border_color=CLR_BORDER, text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      height=38, corner_radius=8, command=dialog.destroy
                      ).pack(side="left", expand=True, fill="x", padx=(0,6))
        ctk.CTkButton(row, text="Sí, eliminar", fg_color=CLR_RED, hover_color="#dc2626",
                      text_color=CLR_WHITE, height=38, corner_radius=8, command=_do
                      ).pack(side="right", expand=True, fill="x")

    # ── Toast ─────────────────────────────────────────────────────────────────
    def _toast(self, msg, error=False):
        t = ctk.CTkToplevel(self)
        t.overrideredirect(True)
        t.configure(fg_color=CLR_RED if error else "#16a34a")
        t.attributes("-topmost", True)
        self.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() - 320
        y = self.winfo_rooty() + self.winfo_height() - 72
        t.geometry(f"300x48+{x}+{y}")
        ctk.CTkLabel(t, text=("❌  " if error else "✅  ") + msg,
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=CLR_WHITE
                     ).pack(fill="both", expand=True, padx=14)
        t.after(2800, t.destroy)