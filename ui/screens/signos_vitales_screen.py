"""
Pantalla de Signos Vitales — CustomTkinter
"""
import customtkinter as ctk
from datetime import date
import calendar

# ── Paleta ────────────────────────────────────────────────────────────────────
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


# Widget: Calendario emergente (igual al de medicaciones)
# ─────────────────────────────────────────────────────────────────────────────
class CalendarPicker(ctk.CTkToplevel):
    DIAS  = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
    MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

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
        self._view_year  = self._current.year
        self._view_month = self._current.month
        self._container  = inner
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

        ctk.CTkButton(header, text="‹", width=28, height=28,
                      fg_color=CLR_BG, hover_color=CLR_BORDER,
                      text_color=CLR_TEXT, corner_radius=6,
                      font=ctk.CTkFont(size=14),
                      command=self._prev_month).pack(side="left")
        ctk.CTkLabel(header,
                     text=f"{self.MESES[self._view_month-1]} {self._view_year}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=CLR_TEXT).pack(side="left", expand=True)
        ctk.CTkButton(header, text="›", width=28, height=28,
                      fg_color=CLR_BG, hover_color=CLR_BORDER,
                      text_color=CLR_TEXT, corner_radius=6,
                      font=ctk.CTkFont(size=14),
                      command=self._next_month).pack(side="right")

        days_hdr = ctk.CTkFrame(self._container, fg_color="transparent")
        days_hdr.pack(fill="x", padx=12, pady=(2, 0))
        for i, d in enumerate(self.DIAS):
            ctk.CTkLabel(days_hdr, text=d, width=32,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=CLR_MUTED).grid(row=0, column=i, padx=1)

        grid = ctk.CTkFrame(self._container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=12, pady=(2, 10))

        cal   = calendar.monthcalendar(self._view_year, self._view_month)
        today = date.today()

        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    ctk.CTkFrame(grid, fg_color="transparent", width=32, height=30).grid(
                        row=r, column=c, padx=1, pady=1)
                    continue
                d = date(self._view_year, self._view_month, day)
                is_sel   = (d == self._current)
                is_today = (d == today)
                if is_sel:
                    bg, fg, hover = CLR_SKY_DARK, CLR_WHITE, CLR_SKY_XDARK
                elif is_today:
                    bg, fg, hover = CLR_SKY_LIGHT, CLR_SKY_XDARK, "#bae6fd"
                else:
                    bg, fg, hover = "transparent", CLR_TEXT, CLR_BG
                ctk.CTkButton(
                    grid, text=str(day), width=32, height=30,
                    fg_color=bg, hover_color=hover, text_color=fg,
                    corner_radius=6,
                    font=ctk.CTkFont(size=11, weight="bold" if is_sel or is_today else "normal"),
                    command=lambda _d=d: self._pick(_d)
                ).grid(row=r, column=c, padx=1, pady=1)

    def _prev_month(self):
        if self._view_month == 1:
            self._view_month = 12; self._view_year -= 1
        else:
            self._view_month -= 1
        self._build()

    def _next_month(self):
        if self._view_month == 12:
            self._view_month = 1; self._view_year += 1
        else:
            self._view_month += 1
        self._build()

    def _pick(self, d: date):
        self._on_select(d.isoformat())
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
def _center(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")


class SignosVitalesScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._selected_id    = None
        self._selected_frame = None
        self._selected_bg    = CLR_WHITE
        self._expanded_id    = None
        self._all_rows       = []

        self._build_topbar()
        self._build_table()
        self._load_data()

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        title_col = ctk.CTkFrame(bar, fg_color="transparent")
        title_col.grid(row=0, column=0, padx=28, pady=14, sticky="w")
        ctk.CTkLabel(title_col, text="Signos Vitales",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Registro diario por residente",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")

        search_wrap = ctk.CTkFrame(bar, fg_color=CLR_BG, corner_radius=10,
                                   border_width=1, border_color=CLR_BORDER)
        search_wrap.grid(row=0, column=1, padx=16, pady=14, sticky="ew")
        search_wrap.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(search_wrap, text="⌕", font=ctk.CTkFont(size=13),
                     text_color=CLR_MUTED, width=30).grid(row=0, column=0, padx=(10, 2), pady=9)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filters())
        ctk.CTkEntry(search_wrap, textvariable=self.search_var,
                     placeholder_text="Buscar por residente u observaciones...",
                     fg_color="transparent", border_width=0,
                     text_color=CLR_TEXT, placeholder_text_color=CLR_MUTED,
                     font=ctk.CTkFont(size=12), height=34).grid(
                         row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkButton(bar, text="+ Nuevo registro",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=10, height=38, command=self._open_form,
                      ).grid(row=0, column=2, padx=(8, 8), pady=14)

        ctk.CTkButton(bar, text="Reportes",
                      fg_color="#f59e0b", hover_color="#d97706",
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=10, height=38, command=self._open_report_modal,
                      ).grid(row=0, column=3, padx=(0, 28), pady=14)

        # ── Barra de filtros de fecha ─────────────────────────────────────────
        filter_bar = ctk.CTkFrame(bar, fg_color=CLR_BG, corner_radius=0, height=44)
        filter_bar.grid(row=1, column=0, columnspan=3, sticky="ew")
        filter_bar.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(filter_bar, text="Filtrar por fecha:",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=CLR_TEXT_SOFT).grid(row=0, column=0, padx=(20, 8), pady=10)

        ctk.CTkLabel(filter_bar, text="Desde",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).grid(
                         row=0, column=1, padx=(0, 4), pady=10)

        from_wrap = ctk.CTkFrame(filter_bar, fg_color=CLR_WHITE, corner_radius=8,
                                 border_width=1, border_color=CLR_BORDER)
        from_wrap.grid(row=0, column=2, padx=(0, 10), pady=8)
        self._date_from = ctk.CTkEntry(from_wrap, placeholder_text="YYYY-MM-DD",
                                       fg_color="transparent", border_width=0,
                                       text_color=CLR_TEXT, placeholder_text_color=CLR_MUTED,
                                       height=28, width=100)
        self._date_from.pack(side="left", padx=(6, 0))
        self._date_from.bind("<KeyRelease>", lambda *_: self._apply_filters())
        ctk.CTkButton(from_wrap, text="▷", width=28, height=28,
                      fg_color="transparent", hover_color=CLR_SKY_LIGHT,
                      text_color=CLR_SKY_DARK, font=ctk.CTkFont(size=14),
                      command=lambda: self._pick_date(self._date_from),
                      ).pack(side="left", padx=(2, 4))

        ctk.CTkLabel(filter_bar, text="Hasta",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).grid(
                         row=0, column=3, padx=(0, 4), pady=10)

        to_wrap = ctk.CTkFrame(filter_bar, fg_color=CLR_WHITE, corner_radius=8,
                               border_width=1, border_color=CLR_BORDER)
        to_wrap.grid(row=0, column=4, padx=(0, 10), pady=8)
        self._date_to = ctk.CTkEntry(to_wrap, placeholder_text="YYYY-MM-DD",
                                     fg_color="transparent", border_width=0,
                                     text_color=CLR_TEXT, placeholder_text_color=CLR_MUTED,
                                     height=28, width=100)
        self._date_to.pack(side="left", padx=(6, 0))
        self._date_to.bind("<KeyRelease>", lambda *_: self._apply_filters())
        ctk.CTkButton(to_wrap, text="▷", width=28, height=28,
                      fg_color="transparent", hover_color=CLR_SKY_LIGHT,
                      text_color=CLR_SKY_DARK, font=ctk.CTkFont(size=14),
                      command=lambda: self._pick_date(self._date_to),
                      ).pack(side="left", padx=(2, 4))

        # Accesos rápidos
        for label, cmd in [
            ("Hoy",        self._filter_today),
            ("Esta semana", self._filter_week),
            ("Este mes",   self._filter_month),
            ("Limpiar",    self._filter_clear),
        ]:
            is_clear = label == "Limpiar"
            ctk.CTkButton(
                filter_bar, text=label,
                fg_color=CLR_RED_LIGHT if is_clear else CLR_WHITE,
                hover_color="#fecaca" if is_clear else CLR_SKY_LIGHT,
                text_color=CLR_RED if is_clear else CLR_TEXT_SOFT,
                border_width=1,
                border_color="#fca5a5" if is_clear else CLR_BORDER,
                font=ctk.CTkFont(size=11),
                height=28, corner_radius=8, width=90,
                command=cmd,
            ).grid(row=0, column=filter_bar.grid_size()[0], padx=(0, 6), pady=8)

        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).grid(
            row=2, column=0, columnspan=4, sticky="ew")

    # ── Selector de fecha (popup calendario) ─────────────────────────────────
    def _pick_date(self, entry_widget):
        current_val = ""
        try:
            current_val = entry_widget.get().strip()
        except Exception:
            pass

        def _on_select(iso_date: str):
            try:
                entry_widget.delete(0, "end")
            except Exception:
                pass
            try:
                entry_widget.insert(0, iso_date)
            except Exception:
                pass
            self._apply_filters()

        CalendarPicker(entry_widget, current_val, _on_select)

    # ── Filtros rápidos ───────────────────────────────────────────────────────
    def _filter_today(self):
        today = date.today().isoformat()
        self._date_from.delete(0, "end"); self._date_from.insert(0, today)
        self._date_to.delete(0, "end");   self._date_to.insert(0, today)
        self._apply_filters()

    def _filter_week(self):
        from datetime import timedelta
        today = date.today()
        monday = (today - timedelta(days=today.weekday())).isoformat()
        self._date_from.delete(0, "end"); self._date_from.insert(0, monday)
        self._date_to.delete(0, "end");   self._date_to.insert(0, today.isoformat())
        self._apply_filters()

    def _filter_month(self):
        today = date.today()
        first = today.replace(day=1).isoformat()
        self._date_from.delete(0, "end"); self._date_from.insert(0, first)
        self._date_to.delete(0, "end");   self._date_to.insert(0, today.isoformat())
        self._apply_filters()

    def _filter_clear(self):
        self._date_from.delete(0, "end")
        self._date_to.delete(0, "end")
        self.search_var.set("")
        self._apply_filters()

    def _apply_filters(self):
        q        = self.search_var.get().strip().lower()
        date_from = self._date_from.get().strip()
        date_to   = self._date_to.get().strip()

        def _get(r, key, idx):
            return str(r.get(key, "") if isinstance(r, dict) else (r[idx] or "")).lower()

        result = self._all_rows
        if q:
            result = [r for r in result
                      if q in _get(r, "residente_nombre", 3)
                      or q in _get(r, "observaciones", 13)]
        if date_from:
            try:
                result = [r for r in result
                          if _get(r, "fecha", 1) >= date_from]
            except Exception:
                pass
        if date_to:
            try:
                result = [r for r in result
                          if _get(r, "fecha", 1) <= date_to]
            except Exception:
                pass

        self._render_list(result)

    # ── Tabla ─────────────────────────────────────────────────────────────────
    def _build_table(self):
        wrap = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=14,
                            border_width=1, border_color=CLR_BORDER)
        wrap.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        COLS   = ["Residente", "Fecha", "F.C.", "Presión", "Oxig.", "Glucosa", "Temp.", "Sueño", "Personal"]
        WIDTHS = [230,          90,      60,     80,        60,      75,        60,      40,      190]
        self._COL_WIDTHS = list(zip(COLS, WIDTHS))

        hdr = ctk.CTkFrame(wrap, fg_color=CLR_BG, corner_radius=0, height=38)
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(hdr, text="", width=28).grid(row=0, column=0, padx=(8, 0))
        for c, (col, w) in enumerate(self._COL_WIDTHS):
            ctk.CTkLabel(hdr, text=col.upper(),
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=CLR_MUTED, width=w, anchor="w").grid(
                             row=0, column=c + 1, padx=(4, 0), pady=10, sticky="w")

        self._list_scroll = ctk.CTkScrollableFrame(wrap, fg_color=CLR_WHITE, corner_radius=0)
        self._list_scroll.grid(row=1, column=0, sticky="nsew")
        self._list_scroll.grid_columnconfigure(0, weight=1)

        # ── Barra de acciones ─────────────────────────────────────────────────
        action_bar = ctk.CTkFrame(wrap, fg_color=CLR_BG, corner_radius=0, height=52)
        action_bar.grid(row=2, column=0, sticky="ew")
        action_bar.grid_propagate(False)
        ctk.CTkFrame(action_bar, fg_color=CLR_BORDER, height=1).place(relx=0, rely=0, relwidth=1)

        self._lbl_sel = ctk.CTkLabel(
            action_bar, text="Selecciona un registro para ver las acciones",
            font=ctk.CTkFont(size=11), text_color=CLR_MUTED)
        self._lbl_sel.pack(side="left", padx=20)

        self._btn_del = ctk.CTkButton(
            action_bar, text="Eliminar",
            fg_color=CLR_RED_LIGHT, hover_color="#fecaca",
            text_color=CLR_RED, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=34, width=100,
            border_width=1, border_color="#fca5a5",
            state="disabled", command=self._confirm_delete)
        self._btn_del.pack(side="right", padx=(4, 20), pady=9)

        self._btn_edit = ctk.CTkButton(
            action_bar, text="Editar",
            fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
            text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=34, width=100,
            border_width=1, border_color="#7dd3fc",
            state="disabled", command=self._open_edit)
        self._btn_edit.pack(side="right", padx=4, pady=9)

    # ── Carga y render ────────────────────────────────────────────────────────
    def _load_data(self):
        try:
            from modules.signos_vitales import listar_registros
            rows = listar_registros()
        except Exception:
            rows = []
        self._all_rows = [dict(r) if hasattr(r, "keys") else r for r in rows]
        self._apply_filters()

    def _render_list(self, rows):
        for w in self._list_scroll.winfo_children():
            w.destroy()
        self._selected_id    = None
        self._selected_frame = None
        self._expanded_id    = None
        self._set_actions(False)

        if not rows:
            empty = ctk.CTkFrame(self._list_scroll, fg_color="transparent")
            empty.grid(row=0, column=0, pady=50)
            ctk.CTkLabel(empty, text="", font=ctk.CTkFont(size=32)).pack()
            ctk.CTkLabel(empty, text="Sin registros de signos vitales",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(pady=(6, 2))
            ctk.CTkLabel(empty, text="Usa el botón '+ Nuevo registro' para agregar",
                         font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack()
            return

        for idx, row in enumerate(rows):
            if isinstance(row, dict):
                rid      = row.get("id")
                res_name = row.get("residente_nombre", "-") or "-"
                fecha    = row.get("fecha", "-") or "-"
                fc       = row.get("frecuencia_cardiaca", "-") or "-"
                presion  = row.get("presion", "-") or "-"
                oxig     = row.get("oxigenacion", "-") or "-"
                glucosa  = row.get("glucosa", "-") or "-"
                temp     = row.get("temperatura", "-") or "-"
                sueno    = row.get("sueno", "-") or "-"
                panales  = row.get("panales_usados", 0) or 0
                orino    = bool(row.get("orino"))
                evacuo   = bool(row.get("evacuo"))
                obs      = row.get("observaciones") or ""
                enf_name = row.get("enfermero_nombre", "-") or "-"
            else:
                rid, fecha, res_name = row[0], row[1] or "-", row[3] or "-"
                fc       = row[4] or "-"
                presion  = row[5] or "-"
                oxig     = row[6] or "-"
                glucosa  = row[7] or "-"
                temp     = row[8] or "-"
                panales  = row[9] or 0
                orino    = bool(row[10])
                evacuo   = bool(row[11])
                sueno    = row[12] or "-"
                obs      = row[13] or ""
                enf_name = row[15] or "-"

            bg = CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT

            outer = ctk.CTkFrame(self._list_scroll, fg_color=bg, corner_radius=0)
            outer.grid(row=idx, column=0, sticky="ew")
            outer.grid_columnconfigure(0, weight=1)

            rf = ctk.CTkFrame(outer, fg_color="transparent", corner_radius=0, height=44)
            rf.grid(row=0, column=0, sticky="ew")

            chev = ctk.CTkLabel(rf, text="▶", font=ctk.CTkFont(size=9),
                                text_color=CLR_MUTED, width=28, anchor="center")
            chev.grid(row=0, column=0, padx=(8, 0), sticky="w")

            def _u(v, suf=""):
                return f"{v}{suf}" if v not in ("-", None, "") else "-"

            vals = [
                res_name, fecha,
                _u(fc, " lpm"), _u(presion),
                _u(oxig, "%"), _u(glucosa, " mg/dL"),
                _u(temp, "°C"), _u(sueno, " h"),
                enf_name,
            ]

            row_labels = []
            for c, ((_, w), v) in enumerate(zip(self._COL_WIDTHS, vals)):
                lbl = ctk.CTkLabel(rf, text=v, font=ctk.CTkFont(size=12),
                                   text_color=CLR_TEXT_SOFT, width=w, anchor="w")
                lbl.grid(row=0, column=c + 1, padx=(4, 0), sticky="w")
                row_labels.append(lbl)

            # ── Panel detalle ─────────────────────────────────────────────────
            detail = ctk.CTkFrame(outer, fg_color="#f0f9ff", corner_radius=0)
            det_parts = [
                f"Pañales: {panales}",
                f"Orinó: {'Sí' if orino else 'No'}",
                f"Evacuó: {'Sí' if evacuo else 'No'}",
            ]
            if obs:
                det_parts.append(f"Obs: {obs}")
            ctk.CTkLabel(
                detail,
                text="   ·   ".join(det_parts),
                font=ctk.CTkFont(size=11),
                text_color=CLR_TEXT_SOFT,
                anchor="w", wraplength=900,
            ).pack(padx=(44, 16), pady=6, anchor="w")

            # ── Toggle expansión ──────────────────────────────────────────────
            def _toggle(r=rid, ot=outer, dt=detail, ch=chev):
                if self._expanded_id == r:
                    dt.grid_remove()
                    ch.configure(text="▶", text_color=CLR_MUTED)
                    self._expanded_id = None
                else:
                    for sibling in self._list_scroll.winfo_children():
                        children = sibling.winfo_children()
                        if len(children) > 1:
                            children[1].grid_remove()
                        if children:
                            rf_ch = children[0].winfo_children()
                            if rf_ch:
                                rf_ch[0].configure(text="▶", text_color=CLR_MUTED)
                    dt.grid(row=1, column=0, sticky="ew")
                    ch.configure(text="▼", text_color=CLR_SKY_DARK)
                    self._expanded_id = r
                self._select(r, ot)

            for widget in [rf, chev] + row_labels:
                widget.bind("<Button-1>", lambda e, fn=_toggle: fn())
                widget.configure(cursor="hand2")

    # ── Selección ─────────────────────────────────────────────────────────────
    def _select(self, rid, frame):
        if self._selected_frame and self._selected_frame != frame:
            self._selected_frame.configure(fg_color=self._selected_bg)
        self._selected_bg    = frame.cget("fg_color")
        frame.configure(fg_color=CLR_SKY_LIGHT)
        self._selected_id    = rid
        self._selected_frame = frame
        self._set_actions(True)
        self._lbl_sel.configure(text=f"Registro ID {rid} seleccionado",
                                text_color=CLR_SKY_XDARK)

    def _set_actions(self, on: bool):
        s = "normal" if on else "disabled"
        self._btn_edit.configure(state=s)
        self._btn_del.configure(state=s)

    # ── Formulario ────────────────────────────────────────────────────────────
    def _open_form(self, reg=None):
        edit = reg is not None
        win  = ctk.CTkToplevel(self)
        win.title("Nuevo registro" if not edit else "Editar registro")
        win.grab_set()
        win.resizable(False, False)
        win.configure(fg_color=CLR_WHITE)
        _center(win, 540, 580)

        win.grid_rowconfigure(1, weight=1)
        win.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(win, fg_color=CLR_SKY_DARK, corner_radius=0, height=56)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr,
                     text="Nuevo registro" if not edit else "Editar registro",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=CLR_WHITE).pack(side="left", padx=24, pady=14)
        ctk.CTkLabel(hdr, text="Residente, fecha y enfermero son obligatorios",
                     font=ctk.CTkFont(size=10), text_color="#bae6fd").pack(side="right", padx=20)

        body = ctk.CTkScrollableFrame(win, fg_color=CLR_WHITE, corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkFrame(win, fg_color=CLR_BORDER, height=1).grid(row=2, column=0, sticky="ew")
        btn_bar = ctk.CTkFrame(win, fg_color=CLR_WHITE, height=60, corner_radius=0)
        btn_bar.grid(row=3, column=0, sticky="ew")
        btn_bar.grid_propagate(False)
        btn_bar.grid_columnconfigure((0, 1), weight=1)

        try:
            from modules.residentes import listar_residentes
            res_rows = listar_residentes()
            res_opts = {f"{r['nombre']} - {r['curp']}": r['id_residente']
                        for r in [dict(r) for r in res_rows]}
        except Exception:
            res_opts = {}

        try:
            from db.connection import get_connection
            conn = get_connection()
            enf_rows = conn.execute(
                "SELECT id, nombre, usuario, rol FROM usuarios "
                "WHERE activo = 1 AND rol IN ('enfermero', 'doctor') ORDER BY nombre"
            ).fetchall()
            conn.close()
            enf_opts = {f"{r[1]} ({r[3]}) - {r[2]}": r[0] for r in enf_rows}
        except Exception:
            enf_opts = {}

        def _field(label, row, col=0, colspan=1):
            grp = ctk.CTkFrame(body, fg_color="transparent")
            grp.grid(row=row, column=col, columnspan=colspan,
                     padx=(20 if col == 0 else 8, 20 if col + colspan >= 2 else 8),
                     pady=(0, 10), sticky="ew")
            ctk.CTkLabel(grp, text=label,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0, 3))
            return grp

        def _entry(grp, placeholder="", val=""):
            e = ctk.CTkEntry(grp, fg_color=CLR_BG, border_color=CLR_BORDER,
                             text_color=CLR_TEXT, height=36, corner_radius=8,
                             placeholder_text=placeholder,
                             placeholder_text_color=CLR_MUTED)
            e.pack(fill="x")
            if val:
                e.insert(0, val)
            return e

        grp_res = _field("Residente *", 0, 0, 2)
        combo_res = ctk.CTkComboBox(grp_res,
                                    values=list(res_opts.keys()) if res_opts else ["Sin residentes"],
                                    fg_color=CLR_BG, border_color=CLR_BORDER,
                                    text_color=CLR_TEXT, button_color=CLR_SKY_DARK,
                                    dropdown_fg_color=CLR_WHITE, dropdown_text_color=CLR_TEXT,
                                    height=36, corner_radius=8)
        combo_res.pack(fill="x")
        combo_res.set("Selecciona un residente...")
        if edit and res_opts:
            for k, v in res_opts.items():
                if v == reg.get("id_residente"):
                    combo_res.set(k); break

        grp_fecha = _field("Fecha *", 1, 0)
        fecha_val = reg.get("fecha", date.today().isoformat()) if edit else date.today().isoformat()
        fecha_frame = ctk.CTkFrame(grp_fecha, fg_color=CLR_BG, corner_radius=8,
                                   border_width=1, border_color=CLR_BORDER, height=38)
        fecha_frame.pack(fill="x")
        fecha_frame.pack_propagate(False)
        entry_fecha = ctk.CTkEntry(fecha_frame, fg_color="transparent", border_width=0,
                                   text_color=CLR_TEXT, height=36)
        entry_fecha.insert(0, fecha_val)
        entry_fecha.pack(side="left", fill="both", expand=True, padx=(8, 0))
        ctk.CTkButton(fecha_frame, text="▷", width=32, height=34,
                      fg_color="transparent", hover_color=CLR_SKY_LIGHT,
                      text_color=CLR_SKY_DARK, font=ctk.CTkFont(size=14),
                      command=lambda: CalendarPicker(
                          entry_fecha,
                          entry_fecha.get().strip(),
                          lambda d: (entry_fecha.delete(0, "end"), entry_fecha.insert(0, d))
                      )).pack(side="right", padx=(0, 4))

        grp_enf = _field("Enfermero / Doctor *", 1, 1)
        combo_enf = ctk.CTkComboBox(grp_enf,
                                    values=list(enf_opts.keys()) if enf_opts else ["Sin enfermeros/doctores"],
                                    fg_color=CLR_BG, border_color=CLR_BORDER,
                                    text_color=CLR_TEXT, button_color=CLR_SKY_DARK,
                                    dropdown_fg_color=CLR_WHITE, dropdown_text_color=CLR_TEXT,
                                    height=36, corner_radius=8)
        combo_enf.pack(fill="x")
        combo_enf.set("Selecciona")
        if edit and enf_opts:
            for k, v in enf_opts.items():
                if v == reg.get("id_enfermero"):
                    combo_enf.set(k); break

        grp_fc  = _field("Frecuencia cardiaca (lpm)", 2, 0)
        entry_fc = _entry(grp_fc, "Ej. 72", str(reg.get("frecuencia_cardiaca") or "") if edit else "")

        grp_pre = _field("Presión arterial (mmHg)", 2, 1)
        entry_pre = _entry(grp_pre, "Ej. 120/80", str(reg.get("presion") or "") if edit else "")

        grp_oxi = _field("Oxigenación (%)", 3, 0)
        entry_oxi = _entry(grp_oxi, "Ej. 98", str(reg.get("oxigenacion") or "") if edit else "")

        grp_glu = _field("Glucosa (mg/dL)", 3, 1)
        entry_glu = _entry(grp_glu, "Ej. 90", str(reg.get("glucosa") or "") if edit else "")

        grp_temp = _field("Temperatura (°C)", 4, 0)
        entry_temp = _entry(grp_temp, "Ej. 36.5", str(reg.get("temperatura") or "") if edit else "")

        grp_sue = _field("Horas de sueño", 4, 1)
        entry_sue = _entry(grp_sue, "Ej. 7", str(reg.get("sueno") or "") if edit else "")

        grp_checks = _field("Registros adicionales", 5, 0, 2)
        checks_row = ctk.CTkFrame(grp_checks, fg_color="transparent")
        checks_row.pack(fill="x")

        pan_var = ctk.StringVar(value=str(reg.get("panales_usados") or "0") if edit else "0")
        ori_var = ctk.IntVar(value=int(reg.get("orino") or 0) if edit else 0)
        eva_var = ctk.IntVar(value=int(reg.get("evacuo") or 0) if edit else 0)

        pan_wrap = ctk.CTkFrame(checks_row, fg_color="transparent")
        pan_wrap.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(pan_wrap, text="Pañales usados",
                     font=ctk.CTkFont(size=11), text_color=CLR_TEXT_SOFT).pack(anchor="w")
        ctk.CTkEntry(pan_wrap, textvariable=pan_var,
                     fg_color=CLR_BG, border_color=CLR_BORDER,
                     text_color=CLR_TEXT, height=32, width=70, corner_radius=8).pack()

        ctk.CTkCheckBox(checks_row, text="Orinó", variable=ori_var,
                        font=ctk.CTkFont(size=12), text_color=CLR_TEXT_SOFT,
                        fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                        border_color=CLR_BORDER).pack(side="left", padx=(0, 16))

        ctk.CTkCheckBox(checks_row, text="Evacuó", variable=eva_var,
                        font=ctk.CTkFont(size=12), text_color=CLR_TEXT_SOFT,
                        fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                        border_color=CLR_BORDER).pack(side="left")

        grp_obs = _field("Observaciones", 6, 0, 2)
        text_obs = ctk.CTkTextbox(grp_obs, fg_color=CLR_BG, border_color=CLR_BORDER,
                                  text_color=CLR_TEXT, border_width=2,
                                  corner_radius=8, height=72,
                                  font=ctk.CTkFont(size=12))
        text_obs.pack(fill="x")
        if edit and reg.get("observaciones"):
            text_obs.insert("1.0", reg["observaciones"])

        def _show_alert(msg):
            alert = ctk.CTkToplevel(win)
            alert.title("")
            alert.grab_set()
            alert.configure(fg_color=CLR_WHITE)
            alert.resizable(False, False)
            _center(alert, 340, 170)
            ctk.CTkLabel(alert, text="▲", font=ctk.CTkFont(size=34)).pack(pady=(16, 2))
            ctk.CTkLabel(alert, text="Campo requerido",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=CLR_TEXT).pack()
            ctk.CTkLabel(alert, text=msg,
                         font=ctk.CTkFont(size=11), text_color=CLR_TEXT_SOFT,
                         wraplength=280).pack(pady=(4, 0))
            ctk.CTkButton(alert, text="Entendido",
                          fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                          text_color=CLR_WHITE, corner_radius=8, height=34,
                          command=alert.destroy).pack(padx=40, pady=12, fill="x")

        def _save():
            res_id = res_opts.get(combo_res.get())
            enf_id = enf_opts.get(combo_enf.get())
            fecha  = entry_fecha.get().strip()

            if not res_id: _show_alert("Debes seleccionar un residente."); return
            if not fecha:  _show_alert("La fecha es obligatoria."); return
            if not enf_id: _show_alert("Debes seleccionar un enfermero o doctor."); return

            def _num(val):
                v = val.strip()
                if not v: return None
                try: return float(v) if "." in v else int(v)
                except ValueError: return None

            datos = {
                "id_residente":        res_id,
                "fecha":               fecha,
                "id_enfermero":        enf_id,
                "frecuencia_cardiaca": _num(entry_fc.get()),
                "presion":             entry_pre.get().strip() or None,
                "oxigenacion":         _num(entry_oxi.get()),
                "glucosa":             _num(entry_glu.get()),
                "temperatura":         _num(entry_temp.get()),
                "sueno":               _num(entry_sue.get()),
                "panales_usados":      _num(pan_var.get()),
                "orino":               ori_var.get(),
                "evacuo":              eva_var.get(),
                "observaciones":       text_obs.get("1.0", "end").strip() or None,
            }
            datos = {k: v for k, v in datos.items() if v is not None}

            try:
                if edit:
                    from modules.signos_vitales import actualizar_registro
                    actualizar_registro(reg["id"], datos)
                    self._toast("Registro actualizado")
                else:
                    from modules.signos_vitales import crear_registro
                    crear_registro(datos)
                    self._toast("Registro guardado")
                win.destroy()
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)
                win.destroy()

        ctk.CTkButton(btn_bar, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color=CLR_BG,
                      corner_radius=8, height=36, command=win.destroy,
                      ).grid(row=0, column=0, padx=(16, 6), pady=12, sticky="ew")
        ctk.CTkButton(btn_bar, text="Guardar",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8, height=36, command=_save,
                      ).grid(row=0, column=1, padx=(6, 16), pady=12, sticky="ew")

    # ── Editar ─────────────────────────────────────────────────────────────────
    def _open_edit(self):
        if not self._selected_id:
            return
        try:
            from modules.signos_vitales import obtener_registro
            r = obtener_registro(self._selected_id)
            if r:
                self._open_form(reg=dict(r))
        except Exception as ex:
            self._toast(f"Error: {ex}", error=True)

    # ── Eliminar ───────────────────────────────────────────────────────────────
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
        ctk.CTkLabel(dialog, text="¿Eliminar este registro?",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text="Esta acción es permanente y no se puede deshacer.",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4, 0))

        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=20, padx=24, fill="x")

        def _do():
            try:
                from modules.signos_vitales import eliminar_registro
                eliminar_registro(self._selected_id)
                self._toast("Registro eliminado")
                dialog.destroy()
                self._selected_id    = None
                self._selected_frame = None
                self._set_actions(False)
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)
                dialog.destroy()

        ctk.CTkButton(row, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color=CLR_BG,
                      height=38, corner_radius=8, command=dialog.destroy,
                      ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Sí, eliminar",
                      fg_color=CLR_RED, hover_color="#dc2626",
                      text_color=CLR_WHITE, height=38, corner_radius=8,
                      command=_do,
                      ).pack(side="right", expand=True, fill="x")

    # ── Toast ──────────────────────────────────────────────────────────────────
    def _toast(self, msg: str, error=False):
        t = ctk.CTkToplevel(self)
        t.overrideredirect(True)
        t.configure(fg_color=CLR_RED if error else "#16a34a")
        t.attributes("-topmost", True)
        self.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() - 320
        y = self.winfo_rooty() + self.winfo_height() - 72
        t.geometry(f"300x48+{x}+{y}")
        ctk.CTkLabel(t, text=("✖  " if error else "✔  ") + msg,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_WHITE).pack(fill="both", expand=True, padx=14)
        t.after(2800, t.destroy)

    # ── Reporte modal ──────────────────────────────────────────────────────────
    def _open_report_modal(self):
        from datetime import datetime
        modal = ctk.CTkToplevel(self)
        modal.title("Generar Reporte de Signos Vitales")
        _center(modal, 460, 420)
        modal.grab_set()
        modal.configure(fg_color=CLR_BG)
        modal.resizable(False, False)

        hdr = ctk.CTkFrame(modal, fg_color=CLR_SKY_DARK, corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="Generar Reporte",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=CLR_WHITE).pack(side="left", padx=24, pady=16)
        ctk.CTkLabel(hdr, text="Filtra y exporta signos vitales",
                     font=ctk.CTkFont(size=10), text_color="#bae6fd").pack(side="right", padx=20)

        frame = ctk.CTkFrame(modal, fg_color=CLR_WHITE, corner_radius=12,
                             border_width=1, border_color=CLR_BORDER)
        frame.pack(fill="both", expand=True, padx=20, pady=16)

        def _lbl(text):
            ctk.CTkLabel(frame, text=text,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", padx=20, pady=(12, 2))

        _lbl("Residente")
        residentes = sorted({r.get("residente_nombre", "") for r in self._all_rows
                             if isinstance(r, dict) and r.get("residente_nombre", "")})
        self._rep_res_var = ctk.StringVar(value="Todos")
        ctk.CTkComboBox(frame, values=["Todos"] + residentes,
                        variable=self._rep_res_var,
                        fg_color=CLR_BG, border_color=CLR_BORDER,
                        text_color=CLR_TEXT, button_color=CLR_SKY_DARK,
                        dropdown_fg_color=CLR_WHITE, dropdown_text_color=CLR_TEXT,
                        height=36, corner_radius=8).pack(fill="x", padx=20, pady=(0, 4))

        ctk.CTkFrame(frame, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=20, pady=(8, 4))

        dates_row = ctk.CTkFrame(frame, fg_color="transparent")
        dates_row.pack(fill="x", padx=20, pady=(4, 4))
        dates_row.grid_columnconfigure((0, 1), weight=1)

        def _date_field(parent, col, label, default_val):
            grp = ctk.CTkFrame(parent, fg_color="transparent")
            grp.grid(row=0, column=col, padx=(0, 8 if col == 0 else 0), sticky="ew")
            ctk.CTkLabel(grp, text=label,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0, 3))
            wrap = ctk.CTkFrame(grp, fg_color=CLR_BG, corner_radius=8,
                                border_width=1, border_color=CLR_BORDER, height=38)
            wrap.pack(fill="x")
            wrap.pack_propagate(False)
            entry = ctk.CTkEntry(wrap, height=36, fg_color="transparent", border_width=0,
                                 text_color=CLR_TEXT, font=ctk.CTkFont(size=12))
            entry.insert(0, default_val)
            entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
            ctk.CTkButton(wrap, text="▷", width=34, height=34,
                          fg_color="transparent", hover_color=CLR_SKY_LIGHT,
                          text_color=CLR_MUTED, corner_radius=6,
                          command=lambda: self._pick_date(entry)).pack(side="right", padx=(0, 2))
            return entry

        today = date.today()
        ini_entry = _date_field(dates_row, 0, "▷  Fecha inicio", today.replace(day=1).isoformat())
        fin_entry = _date_field(dates_row, 1, "▷  Fecha fin",    today.isoformat())

        info = ctk.CTkFrame(frame, fg_color=CLR_SKY_XLIGHT, corner_radius=8,
                            border_width=1, border_color="#bae6fd")
        info.pack(fill="x", padx=20, pady=(12, 4))
        ctk.CTkLabel(info,
                     text="Incluirá todos los registros de signos vitales en el rango seleccionado.",
                     font=ctk.CTkFont(size=10), text_color=CLR_SKY_XDARK,
                     wraplength=380, justify="left").pack(anchor="w", padx=12, pady=8)

        ctk.CTkFrame(frame, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=20, pady=(8, 0))
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(12, 16))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=8, height=38, command=modal.destroy
                      ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        def _generar():
            res  = self._rep_res_var.get()
            ini  = ini_entry.get().strip()
            fin  = fin_entry.get().strip()
            modal.destroy()
            self._open_report_result(res, ini, fin)

        ctk.CTkButton(btn_row, text="Generar Reporte",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8, height=38, command=_generar
                      ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

    # ── Resultado del reporte ──────────────────────────────────────────────────
    def _open_report_result(self, residente, fecha_ini, fecha_fin):
        from tkinter import filedialog
        rows = self._all_rows
        if residente and residente != "Todos":
            rows = [r for r in rows if (r.get("residente_nombre","") if isinstance(r,dict) else (r[3] or "")) == residente]
        if fecha_ini:
            rows = [r for r in rows if (r.get("fecha","") if isinstance(r,dict) else (r[1] or "")) >= fecha_ini]
        if fecha_fin:
            rows = [r for r in rows if (r.get("fecha","") if isinstance(r,dict) else (r[1] or "")) <= fecha_fin]

        win = ctk.CTkToplevel(self)
        win.title("Reporte de Signos Vitales")
        _center(win, 1200, 620)
        win.grab_set()
        win.configure(fg_color=CLR_WHITE)

        hdr = ctk.CTkFrame(win, fg_color=CLR_SKY_DARK, corner_radius=0, height=70)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="✚  Sistema de Gestión de Asilo - CREAN",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=CLR_WHITE).pack(side="left", padx=24, pady=20)

        crit = ctk.CTkFrame(win, fg_color=CLR_SKY_XLIGHT, corner_radius=10,
                            border_width=1, border_color=CLR_BORDER)
        crit.pack(fill="x", padx=20, pady=(12, 0))
        ctk.CTkLabel(crit, text=f"Residente: {residente if residente and residente != 'Todos' else 'Todos'}",
                     font=ctk.CTkFont(size=12), text_color=CLR_TEXT).pack(anchor="w", padx=12, pady=4)
        ctk.CTkLabel(crit, text=f"Período: {fecha_ini}  →  {fecha_fin}   |   Total: {len(rows)} registros",
                     font=ctk.CTkFont(size=12), text_color=CLR_TEXT).pack(anchor="w", padx=12, pady=4)

        body = ctk.CTkScrollableFrame(win, fg_color=CLR_WHITE, corner_radius=0)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        headers = ["Residente", "Fecha", "F.C.", "Presión", "Oxig.", "Glucosa", "Temp.", "Sueño", "Enfermero"]
        widths  = [250, 90, 70, 80, 60, 75, 60, 60, 250]
        hdr_row = ctk.CTkFrame(body, fg_color=CLR_BG, corner_radius=0, height=36)
        hdr_row.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(hdr_row, text=h, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=CLR_TEXT_SOFT, width=w, anchor="w").pack(side="left", padx=6)

        for idx, row in enumerate(rows):
            if isinstance(row, dict):
                res_name = row.get("residente_nombre", "-") or "-"
                fecha    = row.get("fecha", "-") or "-"
                fc       = str(row.get("frecuencia_cardiaca", "-") or "-")
                presion  = str(row.get("presion", "-") or "-")
                oxig     = str(row.get("oxigenacion", "-") or "-")
                glucosa  = str(row.get("glucosa", "-") or "-")
                temp     = str(row.get("temperatura", "-") or "-")
                sueno    = str(row.get("sueno", "-") or "-")
                enf_name = row.get("enfermero_nombre", "-") or "-"
            else:
                res_name = row[3] or "-"; fecha = row[1] or "-"
                fc = str(row[4] or "-"); presion = str(row[5] or "-")
                oxig = str(row[6] or "-"); glucosa = str(row[7] or "-")
                temp = str(row[8] or "-"); sueno = str(row[9] or "-")
                enf_name = (row[14] if len(row) > 14 else None) or "-"

            bg = CLR_WHITE if idx % 2 == 0 else CLR_BG
            rf = ctk.CTkFrame(body, fg_color=bg, corner_radius=0, height=38)
            rf.pack(fill="x", pady=1)
            for v, w in zip([res_name, fecha, fc, presion, oxig, glucosa, temp, sueno, enf_name], widths):
                ctk.CTkLabel(rf, text=v, font=ctk.CTkFont(size=11),
                             text_color=CLR_TEXT_SOFT, width=w, anchor="w").pack(side="left", padx=6)

        btn_bar = ctk.CTkFrame(win, fg_color=CLR_WHITE, height=60)
        btn_bar.pack(fill="x")
        ctk.CTkButton(btn_bar, text="Imprimir PDF",
                      fg_color=CLR_GREEN_DARK, hover_color=CLR_GREEN,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=10, height=38,
                      command=lambda: self._export_pdf(rows, residente, fecha_ini, fecha_fin, win)
                      ).pack(side="right", padx=20, pady=10)
        ctk.CTkButton(btn_bar, text="Cerrar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=10, height=38, command=win.destroy
                      ).pack(side="right", padx=10, pady=10)

    # ── Exportar PDF — A4 vertical (igual que Medicaciones) ───────────────────
    def _export_pdf(self, rows, residente, fecha_ini, fecha_fin, parent_win=None):
        from tkinter import filedialog
        from datetime import datetime

        # 1. Verificar/instalar reportlab
        try:
            from reportlab.lib.pagesizes import A4
        except ImportError:
            import subprocess, sys
            self._toast("Instalando reportlab, espera...")
            self.update()
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install",
                                       "reportlab", "--quiet"])
            except Exception as install_err:
                self._toast(f"No se pudo instalar reportlab: {install_err}", error=True)
                return

        # 2. Pedir ruta de guardado
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar reporte como...",
        )
        if not file_path:
            return

        # 3. Generar PDF
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                            Table, TableStyle, HRFlowable)
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

            # ── Colores corporativos (mismos que Medicaciones) ────────────────
            C_BLUE_DARK = colors.HexColor("#0284c7")
            C_BLUE      = colors.HexColor("#0ea5e9")
            C_BLUE_LITE = colors.HexColor("#e0f2fe")
            C_GRAY      = colors.HexColor("#64748b")
            C_GRAY_L    = colors.HexColor("#f8fafc")
            C_DARK      = colors.HexColor("#0f172a")
            C_WHITE     = colors.white

            def safe(v):
                return str(v).strip() if v not in (None, "", "-") else "-"

            # ── Documento A4 vertical ─────────────────────────────────────────
            LEFT_MAR  = 1.8 * cm
            RIGHT_MAR = 1.8 * cm
            TOP_MAR   = 1.5 * cm
            BOT_MAR   = 2.0 * cm

            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                leftMargin=LEFT_MAR, rightMargin=RIGHT_MAR,
                topMargin=TOP_MAR,   bottomMargin=BOT_MAR,
                title="Reporte de Signos Vitales",
                author="Sistema de Gestión de Asilo - CREAN",
            )
            page_w = A4[0] - LEFT_MAR - RIGHT_MAR   # ≈ 17.4 cm

            # ── Estilos ───────────────────────────────────────────────────────
            st_title = ParagraphStyle("t",  fontName="Helvetica-Bold", fontSize=20,
                                      textColor=C_BLUE_DARK, spaceAfter=2, alignment=TA_LEFT)
            st_sub   = ParagraphStyle("s",  fontName="Helvetica",      fontSize=10,
                                      textColor=C_GRAY, spaceAfter=8)
            st_foot  = ParagraphStyle("f",  fontName="Helvetica-Oblique", fontSize=8,
                                      textColor=C_GRAY, alignment=TA_CENTER)
            st_lbl   = ParagraphStyle("lb", fontName="Helvetica-Bold", fontSize=9,
                                      textColor=C_BLUE_DARK, leading=14)
            st_val   = ParagraphStyle("vl", fontName="Helvetica",      fontSize=9,
                                      textColor=C_DARK, leading=14)
            st_cell  = ParagraphStyle("cl", fontName="Helvetica",      fontSize=8,
                                      textColor=C_DARK, leading=11, wordWrap="CJK")
            st_head  = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=7,
                                      textColor=C_WHITE, alignment=TA_CENTER, leading=9)
            st_cnt   = ParagraphStyle("cn", fontName="Helvetica",      fontSize=8,
                                      textColor=C_DARK, alignment=TA_CENTER)
            st_num   = ParagraphStyle("nm", fontName="Helvetica",      fontSize=8,
                                      textColor=C_GRAY, alignment=TA_CENTER)

            story = []

            # ── Encabezado ────────────────────────────────────────────────────
            hdr_tbl = Table([[
                Paragraph("Sistema de Gestión de Asilo - CREAN",
                          ParagraphStyle("hd", fontName="Helvetica-Bold",
                                         fontSize=13, textColor=C_WHITE)),
                Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y  %H:%M')}",
                          ParagraphStyle("hd2", fontName="Helvetica", fontSize=9,
                                         textColor=colors.HexColor("#bae6fd"),
                                         alignment=TA_RIGHT)),
            ]], colWidths=[page_w * 0.6, page_w * 0.4])
            hdr_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C_BLUE_DARK),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING",   (0, 0), (-1, -1), 16),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
                ("TOPPADDING",    (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]))
            story += [hdr_tbl, Spacer(1, 14)]

            story.append(Paragraph("Reporte de Signos Vitales", st_title))
            story.append(Spacer(1, 10))
            story.append(Paragraph("Registro y seguimiento de constantes vitales por residente", st_sub))
            story.append(HRFlowable(width="100%", thickness=1.5, color=C_BLUE,
                                    spaceBefore=6, spaceAfter=10))

            # ── Criterios ─────────────────────────────────────────────────────
            res_txt = (safe(residente) if residente and residente != "Todos"
                       else "Todos los residentes")

            crit_inner = Table([[
                Paragraph("Residente:",       st_lbl), Paragraph(res_txt, st_val),
                Paragraph("Período:",         st_lbl),
                Paragraph(f"{safe(fecha_ini)}  →  {safe(fecha_fin)}", st_val),
                Paragraph("Total registros:", st_lbl), Paragraph(str(len(rows)), st_val),
            ]], colWidths=[page_w*0.13, page_w*0.24, page_w*0.10,
                           page_w*0.29, page_w*0.14, page_w*0.10])
            crit_inner.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 4),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ]))
            crit_tbl = Table([
                [Paragraph("Criterios del reporte",
                           ParagraphStyle("cr", fontName="Helvetica-Bold",
                                          fontSize=10, textColor=C_BLUE_DARK))],
                [crit_inner],
            ], colWidths=[page_w])
            crit_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C_BLUE_LITE),
                ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#7dd3fc")),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                ("TOPPADDING",    (0, 0), (0,  0),  10),
                ("BOTTOMPADDING", (0, 0), (0,  0),  2),
                ("TOPPADDING",    (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
            ]))
            story += [crit_tbl, Spacer(1, 14)]

            # ── Tabla principal — anchos ajustados a A4 (≈17.4 cm) ───────────
            col_heads = [
                "#", "Residente", "Fecha", "F.C.\n(lpm)", "Presión\n(mmHg)",
                "Oxig.\n(%)", "Glucosa\n(mg/dL)", "Temp.\n(°C)", "Sueño\n(h)",
                "Pañales", "Orinó", "Evacuó", "Enfermero / Doctor",
            ]
            col_w = [x * cm for x in [
                0.50,   # #
                2.80,   # Residente
                1.80,   # Fecha
                1.00,   # F.C.
                1.30,   # Presión
                1.00,   # Oxig.
                1.40,   # Glucosa
                1.10,   # Temp.
                1.10,   # Sueño
                1.30,   # Pañales
                1.00,   # Orinó
                1.20,   # Evacuó
                2.40,   # Enfermero
            ]]  # suma = 17.40 cm = page_w  ✔

            table_data = [[Paragraph(h, st_head) for h in col_heads]]

            for idx, row in enumerate(rows, 1):
                if isinstance(row, dict):
                    rn  = safe(row.get("residente_nombre"))
                    fe  = safe(row.get("fecha"))
                    fc  = safe(row.get("frecuencia_cardiaca"))
                    pr  = safe(row.get("presion"))
                    ox  = safe(row.get("oxigenacion"))
                    gl  = safe(row.get("glucosa"))
                    te  = safe(row.get("temperatura"))
                    su  = safe(row.get("sueno"))
                    pa  = safe(row.get("panales_usados"))
                    en  = safe(row.get("enfermero_nombre"))
                    ori = "✔" if row.get("orino")  else "—"
                    eva = "✔" if row.get("evacuo") else "—"
                else:
                    rn  = safe(row[3]);  fe = safe(row[1]);  fc = safe(row[4])
                    pr  = safe(row[5]);  ox = safe(row[6]);  gl = safe(row[7])
                    te  = safe(row[8]);  su = safe(row[9])
                    pa  = safe(row[10] if len(row) > 10 else None)
                    en  = safe(row[14] if len(row) > 14 else None)
                    ori = "✔" if (len(row) > 11 and row[11]) else "—"
                    eva = "✔" if (len(row) > 12 and row[12]) else "—"

                table_data.append([
                    Paragraph(str(idx), st_num),
                    Paragraph(rn, st_cell), Paragraph(fe, st_cnt),
                    Paragraph(fc, st_cnt),  Paragraph(pr, st_cnt),
                    Paragraph(ox, st_cnt),  Paragraph(gl, st_cnt),
                    Paragraph(te, st_cnt),  Paragraph(su, st_cnt),
                    Paragraph(pa, st_cnt),  Paragraph(ori, st_cnt),
                    Paragraph(eva, st_cnt), Paragraph(en, st_cell),
                ])

            tbl = Table(table_data, colWidths=col_w, repeatRows=1)
            ts = [
                ("BACKGROUND",    (0, 0), (-1,  0), C_BLUE_DARK),
                ("ALIGN",         (0, 0), (-1,  0), "CENTER"),
                ("TOPPADDING",    (0, 0), (-1,  0), 7),
                ("BOTTOMPADDING", (0, 0), (-1,  0), 7),
                ("VALIGN",        (0, 1), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 1), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 4),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
                ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                ("LINEBELOW",     (0, 0), (-1,  0), 1.5, C_BLUE),
            ]
            for i in range(1, len(table_data)):
                ts.append(("BACKGROUND", (0, i), (-1, i),
                            C_WHITE if i % 2 == 0 else C_GRAY_L))
            tbl.setStyle(TableStyle(ts))
            story += [tbl, Spacer(1, 16)]

            # ── Resumen estadístico ───────────────────────────────────────────
            n_res  = len({(r.get("residente_nombre") if isinstance(r, dict) else r[3])
                          for r in rows})
            n_dias = len({(r.get("fecha")            if isinstance(r, dict) else r[1])
                          for r in rows})

            stats_tbl = Table([[
                Paragraph(
                    f"<font color='#0ea5e9' size=18><b>{len(rows)}</b></font><br/>"
                    f"<font color='#64748b' size=8>Total registros</font>",
                    ParagraphStyle("s1", alignment=TA_CENTER, leading=20)),
                Paragraph(
                    f"<font color='#16a34a' size=18><b>{n_res}</b></font><br/>"
                    f"<font color='#64748b' size=8>Residentes</font>",
                    ParagraphStyle("s2", alignment=TA_CENTER, leading=20)),
                Paragraph(
                    f"<font color='#0284c7' size=18><b>{n_dias}</b></font><br/>"
                    f"<font color='#64748b' size=8>Días con registro</font>",
                    ParagraphStyle("s3", alignment=TA_CENTER, leading=20)),
            ]], colWidths=[page_w / 3] * 3)
            stats_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C_BLUE_LITE),
                ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#7dd3fc")),
                ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#bae6fd")),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ]))
            story += [stats_tbl, Spacer(1, 18)]

            # ── Pie de página ─────────────────────────────────────────────────
            story.append(HRFlowable(width="100%", thickness=0.8, color=C_BLUE,
                                    spaceBefore=4, spaceAfter=6))
            story.append(Paragraph(
                "Reporte generado automáticamente por el Sistema de Gestión de Asilo - CREAN.  "
                "Documento confidencial — Uso interno exclusivo.",
                st_foot))

            doc.build(story)
            self._toast("PDF guardado correctamente")
            if parent_win:
                parent_win.after(300, parent_win.destroy)

        except Exception as ex:
            import traceback
            traceback.print_exc()
            self._toast(f"Error al generar PDF: {ex}", error=True)