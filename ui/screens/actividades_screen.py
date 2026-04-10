"""
Pantalla de Actividades — CustomTkinter
CRUD de actividades fijas y programadas + registro de participación.
"""

import customtkinter as ctk
from datetime import date, datetime
import calendar

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
CLR_GREEN_DARK = "#16a34a"
CLR_GREEN_LIGHT= "#dcfce7"
CLR_AMBER      = "#f59e0b"
CLR_AMBER_LIGHT= "#fef3c7"


def _center(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")


def _estado_actividad(es_fija: str, fecha_programada: str, hora_programada: str):
    es_fija_txt = str(es_fija or "").strip().lower()

    if es_fija_txt in ("sí", "si", "1", "true", "fija"):
        return "Fija", CLR_GREEN_LIGHT, CLR_GREEN_DARK

    today = date.today()
    now = datetime.now().strftime("%H:%M")

    try:
        f = date.fromisoformat(str(fecha_programada))
    except Exception:
        return "Programada", CLR_SKY_LIGHT, CLR_SKY_XDARK

    hora = str(hora_programada or "")

    if f < today:
        return "Vencida", CLR_RED_LIGHT, CLR_RED
    if f == today and hora and hora <= now:
        return "Hoy", CLR_AMBER_LIGHT, CLR_AMBER
    return "Programada", CLR_SKY_LIGHT, CLR_SKY_XDARK


# ─────────────────────────────────────────────────────────────────────────────
# Widget: Calendario emergente
# ─────────────────────────────────────────────────────────────────────────────
class CalendarPicker(ctk.CTkToplevel):
    """Popup con un calendario mensual para seleccionar fecha."""

    DIAS = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    MESES = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    def __init__(self, parent, initial_date: str, on_select):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(fg_color=CLR_WHITE)
        self.attributes("-topmost", True)

        outer = ctk.CTkFrame(self, fg_color=CLR_BORDER, corner_radius=14)
        outer.pack(padx=1, pady=1, fill="both", expand=True)
        inner = ctk.CTkFrame(outer, fg_color=CLR_WHITE, corner_radius=13)
        inner.pack(padx=1, pady=1, fill="both", expand=True)

        self._on_select = on_select

        try:
            self._current = date.fromisoformat(initial_date)
        except Exception:
            self._current = date.today()
        self._view_year = self._current.year
        self._view_month = self._current.month

        self._container = inner
        self._build()

        parent.update_idletasks()
        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height() + 4
        self.geometry(f"280x300+{x}+{y}")

        self.bind("<FocusOut>", self._on_focus_out)
        self.focus_set()

    def _on_focus_out(self, event):
        self.after(100, self._check_focus)

    def _check_focus(self):
        try:
            focused = self.focus_get()
            if focused is None or str(focused) not in str(self.winfo_children()):
                self.destroy()
        except Exception:
            self.destroy()

    def _build(self):
        for w in self._container.winfo_children():
            w.destroy()

        header = ctk.CTkFrame(self._container, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkButton(
            header, text="‹", width=28, height=28,
            fg_color=CLR_BG, hover_color=CLR_BORDER,
            text_color=CLR_TEXT, corner_radius=6, font=ctk.CTkFont(size=14),
            command=self._prev_month
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"{self.MESES[self._view_month - 1]} {self._view_year}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=CLR_TEXT
        ).pack(side="left", expand=True)

        ctk.CTkButton(
            header, text="›", width=28, height=28,
            fg_color=CLR_BG, hover_color=CLR_BORDER,
            text_color=CLR_TEXT, corner_radius=6, font=ctk.CTkFont(size=14),
            command=self._next_month
        ).pack(side="right")

        days_hdr = ctk.CTkFrame(self._container, fg_color="transparent")
        days_hdr.pack(fill="x", padx=12, pady=(2, 0))
        for i, d in enumerate(self.DIAS):
            ctk.CTkLabel(
                days_hdr, text=d, width=32,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=CLR_MUTED
            ).grid(row=0, column=i, padx=1)

        grid = ctk.CTkFrame(self._container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=12, pady=(2, 10))

        cal = calendar.monthcalendar(self._view_year, self._view_month)
        today = date.today()

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    ctk.CTkFrame(grid, fg_color="transparent", width=32, height=30).grid(
                        row=r, column=c, padx=1, pady=1
                    )
                    continue

                d = date(self._view_year, self._view_month, day)
                is_selected = (d == self._current)
                is_today = (d == today)

                if is_selected:
                    bg, fg, hover = CLR_SKY_DARK, CLR_WHITE, CLR_SKY_XDARK
                elif is_today:
                    bg, fg, hover = CLR_SKY_LIGHT, CLR_SKY_XDARK, "#bae6fd"
                else:
                    bg, fg, hover = "transparent", CLR_TEXT, CLR_BG

                btn = ctk.CTkButton(
                    grid, text=str(day), width=32, height=30,
                    fg_color=bg, hover_color=hover,
                    text_color=fg, corner_radius=6,
                    font=ctk.CTkFont(size=11, weight="bold" if is_selected or is_today else "normal"),
                    command=lambda _d=d: self._pick(_d)
                )
                btn.grid(row=r, column=c, padx=1, pady=1)

    def _prev_month(self):
        if self._view_month == 1:
            self._view_month = 12
            self._view_year -= 1
        else:
            self._view_month -= 1
        self._build()

    def _next_month(self):
        if self._view_month == 12:
            self._view_month = 1
            self._view_year += 1
        else:
            self._view_month += 1
        self._build()

    def _pick(self, d: date):
        self._on_select(d.isoformat())
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Helper: campo de fecha con botón de calendario
# ─────────────────────────────────────────────────────────────────────────────
def _make_date_field(parent, initial_value: str):
    """
    Retorna (frame, var) donde var es un StringVar con la fecha seleccionada.
    Al hacer clic en el campo o el ícono, abre el CalendarPicker.
    """
    var = ctk.StringVar(value=initial_value)

    frame = ctk.CTkFrame(
        parent, fg_color=CLR_WHITE, corner_radius=8,
        border_width=1, border_color=CLR_BORDER, height=38
    )
    frame.pack_propagate(False)

    entry = ctk.CTkEntry(
        frame, textvariable=var, height=36,
        fg_color="transparent", border_width=0,
        text_color=CLR_TEXT, font=ctk.CTkFont(size=12)
    )
    entry.pack(side="left", fill="both", expand=True, padx=(10, 0))

    icon_btn = ctk.CTkButton(
        frame, text="▷", width=36, height=36,
        fg_color="transparent", hover_color=CLR_SKY_LIGHT,
        text_color=CLR_MUTED, corner_radius=8
    )
    icon_btn.pack(side="right", padx=(0, 2))

    _picker_ref = [None]

    def _open_calendar(event=None):
        if _picker_ref[0] and _picker_ref[0].winfo_exists():
            return
        def _on_date(d):
            var.set(d)
        _picker_ref[0] = CalendarPicker(icon_btn, var.get(), _on_date)

    icon_btn.configure(command=_open_calendar)
    entry.bind("<Button-1>", _open_calendar)

    return frame, var


# ─────────────────────────────────────────────────────────────────────────────
# Helper: selector de hora con spinners ▲/▼ (igual que Medicaciones)
# ─────────────────────────────────────────────────────────────────────────────
def _make_time_field(parent, initial_value: str):
    """
    Retorna (frame, get_hora) donde get_hora() devuelve la hora como 'HH:MM'.
    Usa spinners ▲/▼ idénticos al formulario de Medicaciones.
    """
    try:
        parts = initial_value.strip().split(":")
        _h0 = int(parts[0]) % 24
        _m0 = int(parts[1]) % 60
    except Exception:
        _h0, _m0 = 9, 0

    frame = ctk.CTkFrame(
        parent, fg_color=CLR_BG, corner_radius=10,
        border_width=1, border_color=CLR_BORDER
    )

    picker_row = ctk.CTkFrame(frame, fg_color="transparent")
    picker_row.pack(pady=10, padx=16, anchor="w")

    def _spin_col(parent_frame, init_val, max_val):
        """Columna con ▲ display ▼. Devuelve lista mutable [val]."""
        _val = [init_val]

        col = ctk.CTkFrame(parent_frame, fg_color="transparent")
        col.pack(side="left")

        btn_up = ctk.CTkButton(
            col, text="▲", width=52, height=22,
            fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
            text_color=CLR_SKY_XDARK,
            font=ctk.CTkFont(size=10, weight="bold"),
            corner_radius=6, border_width=0
        )
        btn_up.pack(pady=(0, 2))

        display = ctk.CTkFrame(
            col, fg_color=CLR_WHITE, corner_radius=8,
            border_width=2, border_color=CLR_SKY_DARK,
            width=52, height=48
        )
        display.pack()
        display.pack_propagate(False)

        lbl = ctk.CTkLabel(
            display, text=f"{init_val:02d}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=CLR_SKY_XDARK
        )
        lbl.place(relx=0.5, rely=0.5, anchor="center")

        btn_dn = ctk.CTkButton(
            col, text="▼", width=52, height=22,
            fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
            text_color=CLR_SKY_XDARK,
            font=ctk.CTkFont(size=10, weight="bold"),
            corner_radius=6, border_width=0
        )
        btn_dn.pack(pady=(2, 0))

        def _up():
            _val[0] = (_val[0] + 1) % (max_val + 1)
            lbl.configure(text=f"{_val[0]:02d}")

        def _dn():
            _val[0] = (_val[0] - 1) % (max_val + 1)
            lbl.configure(text=f"{_val[0]:02d}")

        btn_up.configure(command=_up)
        btn_dn.configure(command=_dn)
        return _val

    _hora_h = _spin_col(picker_row, _h0, 23)

    # Separador ":"
    sep_col = ctk.CTkFrame(picker_row, fg_color="transparent")
    sep_col.pack(side="left", padx=6)
    ctk.CTkFrame(sep_col, fg_color="transparent", height=22).pack()  # spacer
    ctk.CTkLabel(
        sep_col, text=":",
        font=ctk.CTkFont(size=26, weight="bold"),
        text_color=CLR_SKY_DARK
    ).pack()

    _hora_m = _spin_col(picker_row, _m0, 59)

    # Etiquetas hh / mm al lado
    hint_col = ctk.CTkFrame(picker_row, fg_color="transparent")
    hint_col.pack(side="left", padx=(14, 0))
    ctk.CTkFrame(hint_col, fg_color="transparent", height=22).pack()
    ctk.CTkLabel(hint_col, text="hh", font=ctk.CTkFont(size=9), text_color=CLR_MUTED).pack()
    ctk.CTkFrame(hint_col, fg_color="transparent", height=48).pack()
    ctk.CTkLabel(hint_col, text="mm", font=ctk.CTkFont(size=9), text_color=CLR_MUTED).pack()

    def get_hora():
        return f"{_hora_h[0]:02d}:{_hora_m[0]:02d}"

    return frame, get_hora


# ─────────────────────────────────────────────────────────────────────────────
# Pantalla principal
# ─────────────────────────────────────────────────────────────────────────────
class ActividadesScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._selected_id = None
        self._selected_frame = None
        self._all_rows = []

        self._build_topbar()
        self._build_stats()
        self._build_table_area()
        self._load_data()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=0, border_width=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        title_col = ctk.CTkFrame(bar, fg_color="transparent")
        title_col.grid(row=0, column=0, padx=28, pady=14, sticky="w")
        ctk.CTkLabel(
            title_col,
            text="Actividades",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=CLR_TEXT
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_col,
            text="Gestión de actividades fijas y programadas",
            font=ctk.CTkFont(size=11),
            text_color=CLR_MUTED
        ).pack(anchor="w")

        search_wrap = ctk.CTkFrame(
            bar, fg_color=CLR_BG, corner_radius=10,
            border_width=1, border_color=CLR_BORDER
        )
        search_wrap.grid(row=0, column=1, padx=16, pady=14, sticky="ew")
        search_wrap.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_wrap, text="⌕", font=ctk.CTkFont(size=13),
            text_color=CLR_MUTED, width=30
        ).grid(row=0, column=0, padx=(10, 2), pady=9)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())

        ctk.CTkEntry(
            search_wrap, textvariable=self.search_var,
            placeholder_text="Buscar por nombre, fecha u hora...",
            fg_color="transparent", border_width=0,
            text_color=CLR_TEXT, placeholder_text_color=CLR_MUTED,
            font=ctk.CTkFont(size=12), height=34
        ).grid(row=0, column=1, sticky="ew", padx=(0, 8))

        btns = ctk.CTkFrame(bar, fg_color="transparent")
        btns.grid(row=0, column=2, padx=(8, 28), pady=14)

        ctk.CTkButton(
            btns, text="▤ Participación",
            fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
            text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10, height=38, command=self._open_participacion
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns, text="+ Nueva actividad",
            fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
            text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10, height=38, command=self._open_form
        ).pack(side="left")

        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).grid(
            row=1, column=0, columnspan=3, sticky="ew"
        )

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _build_stats(self):
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, sticky="ew", padx=24, pady=(18, 0))
        sf.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._stat_total = self._stat_card(sf, 0, "Total actividades", "0", "◉", CLR_SKY_DARK, "#dbeafe")
        self._stat_fijas = self._stat_card(sf, 1, "Fijas", "0", "∞", CLR_GREEN_DARK, CLR_GREEN_LIGHT)
        self._stat_prog  = self._stat_card(sf, 2, "Opcionales", "0", "◉", CLR_SKY_XDARK, CLR_SKY_LIGHT)
        self._stat_part  = self._stat_card(sf, 3, "Participaciones", "0", "+", CLR_AMBER, CLR_AMBER_LIGHT)

    def _stat_card(self, parent, col, title, value, icon, icon_color, icon_bg):
        card = ctk.CTkFrame(parent, fg_color=CLR_WHITE, corner_radius=14,
                            border_width=1, border_color=CLR_BORDER)
        card.grid(row=0, column=col, padx=6, sticky="ew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=16)

        icon_box = ctk.CTkFrame(inner, fg_color=icon_bg, corner_radius=10, width=44, height=44)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon, font=ctk.CTkFont(size=20)).place(relx=.5, rely=.5, anchor="center")

        tc = ctk.CTkFrame(inner, fg_color="transparent")
        tc.pack(side="left", padx=(14, 0))

        val_lbl = ctk.CTkLabel(tc, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=CLR_TEXT)
        val_lbl.pack(anchor="w")
        ctk.CTkLabel(tc, text=title, font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")
        return val_lbl

    # ── Tabla ─────────────────────────────────────────────────────────────────
    def _build_table_area(self):
        wrap = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=14,
                            border_width=1, border_color=CLR_BORDER)
        wrap.grid(row=2, column=0, sticky="nsew", padx=24, pady=16)
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        cols = ["Nombre", "Tipo", "Fecha", "Hora", "Estado", "Participación"]
        widths = [340, 100, 110, 90, 110, 120]

        hdr = ctk.CTkFrame(wrap, fg_color=CLR_BG, corner_radius=0, height=40)
        hdr.grid(row=0, column=0, sticky="ew")

        for c, (col_name, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(
                hdr, text=col_name.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=CLR_MUTED, width=w, anchor="w"
            ).grid(row=0, column=c, padx=(14 if c == 0 else 4, 0), pady=10, sticky="w")

        self._table = ctk.CTkScrollableFrame(wrap, fg_color=CLR_WHITE, corner_radius=0)
        self._table.grid(row=1, column=0, sticky="nsew")
        self._table.grid_columnconfigure(0, weight=1)

        self._build_action_bar(wrap)

    def _build_action_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=CLR_BG, corner_radius=0, height=52)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).place(relx=0, rely=0, relwidth=1)

        self._lbl_sel = ctk.CTkLabel(
            bar, text="Selecciona una actividad para ver las acciones",
            font=ctk.CTkFont(size=11), text_color=CLR_MUTED
        )
        self._lbl_sel.pack(side="left", padx=20)

        self._btn_del = ctk.CTkButton(
            bar, text="Eliminar",
            fg_color=CLR_RED_LIGHT, hover_color="#fecaca",
            text_color=CLR_RED, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=34, width=100,
            border_width=1, border_color="#fca5a5",
            state="disabled", command=self._confirm_delete
        )
        self._btn_del.pack(side="right", padx=(4, 20), pady=9)

        self._btn_edit = ctk.CTkButton(
            bar, text="Editar",
            fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
            text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=34, width=100,
            border_width=1, border_color="#7dd3fc",
            state="disabled", command=self._open_edit
        )
        self._btn_edit.pack(side="right", padx=4, pady=9)

    # ── Datos ─────────────────────────────────────────────────────────────────
    def _load_data(self):
        try:
            from modules.actividades import listar_actividades
            rows = listar_actividades()
        except Exception:
            rows = []

        self._all_rows = [dict(r) if hasattr(r, "keys") else r for r in rows]
        self._render_rows(self._all_rows)
        self._update_stats(self._all_rows)

    def _update_stats(self, rows):
        total = len(rows)
        fijas = 0
        opcionales = 0
        participaciones = 0

        for r in rows:
            es_fija = str(r.get("es_fija", "")).strip().lower()
            if es_fija in ("sí", "si", "1", "true", "fija"):
                fijas += 1
            else:
                opcionales += 1
            participaciones += int(r.get("total_registros") or 0)

        self._stat_total.configure(text=str(total))
        self._stat_fijas.configure(text=str(fijas))
        self._stat_prog.configure(text=str(opcionales))
        self._stat_part.configure(text=str(participaciones))

    def _filter(self):
        q = self.search_var.get().strip().lower()
        filtered = self._all_rows if not q else [
            r for r in self._all_rows
            if q in str(r.get("nombre", "")).lower()
            or q in str(r.get("fecha_programada", "")).lower()
            or q in str(r.get("hora_programada", "")).lower()
            or q in str(r.get("es_fija", "")).lower()
        ]
        self._render_rows(filtered)

    def _render_rows(self, rows):
        for w in self._table.winfo_children():
            w.destroy()

        self._selected_id = None
        self._selected_frame = None
        self._set_actions(False)

        if not rows:
            e = ctk.CTkFrame(self._table, fg_color="transparent")
            e.grid(row=0, column=0, pady=50)
            ctk.CTkLabel(e, text="", font=ctk.CTkFont(size=32)).pack()
            ctk.CTkLabel(
                e, text="Sin actividades registradas",
                font=ctk.CTkFont(size=14, weight="bold"), text_color=CLR_TEXT_SOFT
            ).pack(pady=(6, 2))
            ctk.CTkLabel(
                e, text="Usa '+ Nueva actividad' para agregar una",
                font=ctk.CTkFont(size=11), text_color=CLR_MUTED
            ).pack()
            return

        for idx, row in enumerate(rows):
            rid = row.get("id_actividad")
            nombre = row.get("nombre", "—") or "—"
            es_fija = row.get("es_fija", "—") or "—"
            fecha = row.get("fecha_programada", "—") or "—"
            hora = row.get("hora_programada", "—") or "—"
            total_registros = int(row.get("total_registros") or 0)

            tipo_txt = "Fija" if str(es_fija).strip().lower() in ("sí", "si", "1", "true", "fija") else "Opcional"
            estado_txt, estado_bg, estado_fg = _estado_actividad(es_fija, fecha, hora)

            bg = CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT
            rf = ctk.CTkFrame(self._table, fg_color=bg, corner_radius=0, height=52)
            rf.grid(row=idx, column=0, sticky="ew")

            def _bind(w, r=rid, f=rf):
                w.bind("<Button-1>", lambda e, _r=r, _f=f: self._select(_r, _f))
                w.configure(cursor="hand2")

            _bind(rf)

            datos_cols = [
                (nombre, 340, CLR_TEXT, "w"),
                (tipo_txt, 100, CLR_TEXT_SOFT, "w"),
                (fecha, 110, CLR_TEXT_SOFT, "center"),
                (hora, 90, CLR_TEXT_SOFT, "center"),
            ]

            for c, (val, w, color, anchor) in enumerate(datos_cols):
                lbl = ctk.CTkLabel(
                    rf, text=val, font=ctk.CTkFont(size=12),
                    text_color=color, width=w, anchor=anchor
                )
                lbl.grid(row=0, column=c, padx=(14 if c == 0 else 4, 0), sticky="w")
                _bind(lbl)

            badge = ctk.CTkFrame(rf, fg_color=estado_bg, corner_radius=6, width=90, height=26)
            badge.grid(row=0, column=4, padx=(4, 4), pady=12)
            badge.grid_propagate(False)
            ctk.CTkLabel(
                badge, text=estado_txt,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=estado_fg
            ).place(relx=.5, rely=.5, anchor="center")

            part_lbl = ctk.CTkLabel(
                rf, text=str(total_registros),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=CLR_SKY_XDARK, width=120, anchor="center"
            )
            part_lbl.grid(row=0, column=5, padx=(4, 12), sticky="w")
            _bind(part_lbl)

    # ── Selección ─────────────────────────────────────────────────────────────
    def _select(self, rid, frame):
        if self._selected_frame:
            children = list(self._table.winfo_children())
            if self._selected_frame in children:
                idx = children.index(self._selected_frame)
                self._selected_frame.configure(fg_color=CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT)

        frame.configure(fg_color=CLR_SKY_LIGHT)
        self._selected_id = rid
        self._selected_frame = frame
        self._set_actions(True)
        self._lbl_sel.configure(text=f"Actividad ID {rid} seleccionada", text_color=CLR_SKY_XDARK)

    def _set_actions(self, on):
        s = "normal" if on else "disabled"
        self._btn_edit.configure(state=s)
        self._btn_del.configure(state=s)

    # ── Formulario actividad ──────────────────────────────────────────────────
# ── Formulario actividad (Versión Compacta Sin Scroll) ────────────────────────
    def _open_form(self, datos_edicion=None):
        edit = datos_edicion is not None

        win = ctk.CTkToplevel(self)
        win.title("Nueva actividad" if not edit else "Editar actividad")
        win.grab_set()
        win.configure(fg_color=CLR_WHITE)
        win.resizable(False, False)
        
        # Ajustamos la altura a una medida donde quepa todo (560 es suficiente si compactamos)
        _center(win, 440, 560)

        # Encabezado más apretado
        ctk.CTkLabel(
            win, text="Nueva actividad" if not edit else "Editar actividad",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=CLR_TEXT
        ).pack(pady=(15, 0))
        
        ctk.CTkLabel(
            win, text="Completa los datos de la actividad",
            font=ctk.CTkFont(size=11), text_color=CLR_MUTED
        ).pack(pady=(2, 10))

        form = ctk.CTkFrame(win, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # ── Nombre ──
        ctk.CTkLabel(form, text="Nombre de la actividad", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w")
        entry_nombre = ctk.CTkEntry(form, height=35, corner_radius=8, border_color=CLR_BORDER)
        entry_nombre.pack(fill="x", pady=(2, 8))
        if edit and datos_edicion.get("nombre"):
            entry_nombre.insert(0, str(datos_edicion["nombre"]))

        # ── Tipo y Fecha en la misma fila para ahorrar espacio vertical ──
        row_mid = ctk.CTkFrame(form, fg_color="transparent")
        row_mid.pack(fill="x", pady=(0, 8))
        row_mid.grid_columnconfigure((0, 1), weight=1)

        # Columna Tipo
        col_tipo = ctk.CTkFrame(row_mid, fg_color="transparent")
        col_tipo.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(col_tipo, text="Tipo", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w")
        
        es_fija_val = str(datos_edicion.get("es_fija", "")).strip().lower() if edit else ""
        tipo_inicial = "Fija" if es_fija_val in ("sí", "si", "1", "true", "fija") else "Opcional"
        
        tipo_var = ctk.StringVar(value=tipo_inicial)
        ctk.CTkOptionMenu(col_tipo, values=["Fija", "Opcional"], variable=tipo_var, 
                          height=35, corner_radius=8).pack(fill="x", pady=(2, 0))

        # Columna Fecha
        col_fecha = ctk.CTkFrame(row_mid, fg_color="transparent")
        col_fecha.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(col_fecha, text="Fecha", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w")
        
        fecha_inicial = str(datos_edicion.get("fecha_programada", date.today().isoformat())) if edit else date.today().isoformat()
        fecha_frame, fecha_var = _make_date_field(col_fecha, fecha_inicial)
        fecha_frame.configure(height=35) # Forzamos altura menor
        fecha_frame.pack(fill="x", pady=(2, 0))

        # ── Hora (Selector compactado) ──
        ctk.CTkLabel(form, text="Horario", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w")
        
        hora_inicial = str(datos_edicion.get("hora_programada", "09:00")) if edit else "09:00"
        hora_frame, get_hora = _make_time_field(form, hora_inicial)
        # Reducimos el padding interno del frame de la hora
        hora_frame.pack(fill="x", pady=(2, 5))

        # Ajuste de mensaje de error
        lbl_msg = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=11), text_color=CLR_RED)
        lbl_msg.pack(pady=(0, 5))

        # ── Barra de botones ──
        btn_bar = ctk.CTkFrame(win, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, 20), padx=30)
        btn_bar.grid_columnconfigure((0, 1), weight=1)

        def _guardar():
            nombre = entry_nombre.get().strip()
            if not nombre:
                lbl_msg.configure(text="▲ El nombre es obligatorio.")
                return

            try:
                from modules.actividades import crear_actividad, actualizar_actividad
                datos = {
                    "nombre": nombre,
                    "es_fija": "Fija" if tipo_var.get() == "Fija" else "No",
                    "fecha_programada": fecha_var.get().strip(),
                    "hora_programada": get_hora(),
                }
                if edit:
                    actualizar_actividad(datos_edicion["id_actividad"], datos)
                else:
                    crear_actividad(datos)
                
                self._toast("Éxito al guardar")
                win.destroy()
                self._load_data()
            except Exception as ex:
                lbl_msg.configure(text=f"▲ {ex}")

        ctk.CTkButton(btn_bar, text="Cancelar", fg_color=CLR_WHITE, border_width=1, 
                      border_color=CLR_BORDER, text_color=CLR_TEXT_SOFT, height=40,
                      command=win.destroy).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(btn_bar, text="Guardar", fg_color=CLR_SKY_DARK, text_color=CLR_WHITE, 
                      font=ctk.CTkFont(weight="bold"), height=40,
                      command=_guardar).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def _open_edit(self):
        if not self._selected_id:
            return
        try:
            from modules.actividades import obtener_actividad
            r = obtener_actividad(self._selected_id)
            if r:
                self._open_form(datos_edicion=dict(r))
        except Exception as ex:
            self._toast(f"Error: {ex}", error=True)

    # ── Participación ─────────────────────────────────────────────────────────
    def _open_participacion(self):
        win = ctk.CTkToplevel(self)
        win.title("Registrar participación")
        win.grab_set()
        win.configure(fg_color=CLR_WHITE)
        win.resizable(False, False)
        _center(win, 520, 480)

        ctk.CTkLabel(
            win, text="+ Registrar participación",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=CLR_TEXT
        ).pack(pady=(20, 2))
        ctk.CTkLabel(
            win, text="Selecciona residente, actividad y estado de participación",
            font=ctk.CTkFont(size=11), text_color=CLR_MUTED
        ).pack()

        ctk.CTkFrame(win, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=24, pady=(12, 0))

        form = ctk.CTkFrame(win, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=28, pady=(16, 0))

        try:
            from modules.residentes import listar_residentes
            res_rows = listar_residentes()
            res_opts = {f"{r['nombre']} - {r['curp']}": r["id_residente"] for r in [dict(r) for r in res_rows]}
        except Exception:
            res_opts = {}

        try:
            from modules.actividades import listar_actividades
            act_rows = listar_actividades()
            act_opts = {f"{r['nombre']}": r["id_actividad"] for r in [dict(r) for r in act_rows]}
        except Exception:
            act_opts = {}

        ctk.CTkLabel(form, text="Residente", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0, 3))
        combo_res = ctk.CTkComboBox(
            form,
            values=list(res_opts.keys()) if res_opts else ["Sin residentes"],
            height=38, corner_radius=8
        )
        combo_res.pack(fill="x", pady=(0, 12))
        combo_res.set("Selecciona un residente...")

        ctk.CTkLabel(form, text="Actividad", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0, 3))
        combo_act = ctk.CTkComboBox(
            form,
            values=list(act_opts.keys()) if act_opts else ["Sin actividades"],
            height=38, corner_radius=8
        )
        combo_act.pack(fill="x", pady=(0, 12))
        combo_act.set("Selecciona una actividad...")

        ctk.CTkLabel(form, text="Participó", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0, 3))
        participo_var = ctk.StringVar(value="Sí")
        ctk.CTkOptionMenu(form, values=["Sí", "No"], variable=participo_var, height=38, corner_radius=8).pack(fill="x", pady=(0, 12))

        lbl_msg = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=11), text_color=CLR_RED)
        lbl_msg.pack(pady=(8, 0))

        def _guardar():
            res_key = combo_res.get()
            act_key = combo_act.get()
            res_id = res_opts.get(res_key)
            act_id = act_opts.get(act_key)
            fecha = date.today().isoformat()
            hora = datetime.now().strftime("%H:%M")
            participo = 1 if participo_var.get() == "Sí" else 0

            if not res_id:
                lbl_msg.configure(text="▲ Debes seleccionar un residente.")
                return
            if not act_id:
                lbl_msg.configure(text="▲ Debes seleccionar una actividad.")
                return

            try:
                from modules.actividades import registrar_participacion
                registrar_participacion({
                    "id_residente": res_id,
                    "id_actividad": act_id,
                    "fecha": fecha,
                    "hora": hora,
                    "participo": participo,
                })
                self._toast("Participación registrada")
                win.destroy()
                self._load_data()
            except Exception as ex:
                lbl_msg.configure(text=f"▲ {ex}")

        btn_bar = ctk.CTkFrame(win, fg_color=CLR_WHITE, corner_radius=0)
        btn_bar.pack(fill="x", pady=(14, 16))
        btn_bar.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_bar, text="Cancelar",
            fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
            text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
            corner_radius=8, height=44, command=win.destroy
        ).grid(row=0, column=0, sticky="ew", padx=(20, 8))

        ctk.CTkButton(
            btn_bar, text="Guardar participación",
            fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
            text_color=CLR_WHITE, corner_radius=8, height=44,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=_guardar
        ).grid(row=0, column=1, sticky="ew", padx=(8, 20))

    # ── Eliminar ──────────────────────────────────────────────────────────────
    def _confirm_delete(self):
        if not self._selected_id:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.grab_set()
        dialog.configure(fg_color=CLR_WHITE)
        dialog.resizable(False, False)
        _center(dialog, 380, 200)

        ctk.CTkLabel(dialog, text="▲", font=ctk.CTkFont(size=36)).pack(pady=(24, 4))
        ctk.CTkLabel(dialog, text="¿Eliminar esta actividad?",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text="Esta acción también eliminará sus participaciones.",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4, 0))

        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=20, padx=24, fill="x")

        def _do():
            try:
                from modules.actividades import eliminar_actividad
                eliminar_actividad(self._selected_id)
                self._toast("Actividad eliminada")
                dialog.destroy()
                self._selected_id = None
                self._selected_frame = None
                self._set_actions(False)
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)
                dialog.destroy()

        ctk.CTkButton(
            row, text="Cancelar",
            fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
            text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
            height=38, corner_radius=8, command=dialog.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            row, text="Sí, eliminar",
            fg_color=CLR_RED, hover_color="#dc2626",
            text_color=CLR_WHITE, height=38, corner_radius=8,
            command=_do
        ).pack(side="right", expand=True, fill="x")

    # ── Toast ─────────────────────────────────────────────────────────────────
    def _toast(self, msg: str, error=False):
        t = ctk.CTkToplevel(self)
        t.overrideredirect(True)
        t.configure(fg_color=CLR_RED if error else "#16a34a")
        t.attributes("-topmost", True)
        self.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() - 320
        y = self.winfo_rooty() + self.winfo_height() - 72
        t.geometry(f"300x48+{x}+{y}")
        ctk.CTkLabel(
            t, text=("✖  " if error else "✔  ") + msg,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=CLR_WHITE
        ).pack(fill="both", expand=True, padx=14)
        t.after(2800, t.destroy)