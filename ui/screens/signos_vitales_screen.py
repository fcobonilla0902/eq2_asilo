"""
Pantalla de Signos Vitales — CustomTkinter
"""
import customtkinter as ctk
from datetime import date
from tkcalendar import Calendar

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
        ctk.CTkLabel(search_wrap, text="🔍", font=ctk.CTkFont(size=13),
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
                      ).grid(row=0, column=2, padx=(8, 28), pady=14)

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
        ctk.CTkButton(from_wrap, text="📅", width=28, height=28,
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
        ctk.CTkButton(to_wrap, text="📅", width=28, height=28,
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
            row=2, column=0, columnspan=3, sticky="ew")

    # ── Selector de fecha (popup calendario) ─────────────────────────────────
    def _pick_date(self, entry_widget):
        import tkinter.ttk as ttk

        popup = ctk.CTkToplevel(self)
        popup.title("")
        popup.grab_set()
        popup.resizable(False, False)
        popup.configure(fg_color=CLR_WHITE)
        popup.overrideredirect(True)

        # Posicionar cerca del widget
        popup.update_idletasks()
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height() + 4
        popup.geometry(f"260x300+{x}+{y}")

        # Estilo ttk para el calendario
        style = ttk.Style(popup)
        style.theme_use("clam")
        style.configure("custom.Calendar",
                         background=CLR_WHITE,
                         foreground=CLR_TEXT,
                         headersbackground=CLR_SKY_DARK,
                         headersforeground=CLR_WHITE,
                         selectbackground=CLR_SKY_DARK,
                         selectforeground=CLR_WHITE,
                         normalbackground=CLR_WHITE,
                         normalforeground=CLR_TEXT,
                         weekendbackground=CLR_SKY_XLIGHT,
                         weekendforeground=CLR_SKY_XDARK,
                         othermonthbackground="#f8fafc",
                         othermonthforeground=CLR_MUTED,
                         bordercolor=CLR_BORDER,
                         )

        # Fecha inicial: la que ya tenga el entry o hoy
        try:
            init = date.fromisoformat(entry_widget.get().strip())
        except Exception:
            init = date.today()

        cal = Calendar(
            popup,
            selectmode="day",
            year=init.year, month=init.month, day=init.day,
            date_pattern="yyyy-mm-dd",
            style="custom.Calendar",
            showweeknumbers=False,
            firstweekday="monday",
        )
        cal.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        def _select():
            entry_widget.delete(0, "end")
            entry_widget.insert(0, cal.get_date())
            popup.destroy()
            self._apply_filters()

        ctk.CTkButton(popup, text="Seleccionar",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, height=32, corner_radius=8,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=_select,
                      ).pack(fill="x", padx=8, pady=(0, 8))

        # Cerrar si se hace clic fuera
        popup.bind("<FocusOut>", lambda e: popup.destroy() if popup.winfo_exists() else None)

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

        COLS   = ["Residente",  "Fecha", "F.C.",  "Presión", "Oxig.", "Glucosa",  "Temp.", "Sueño", "Enfermero / Doctor"]
        WIDTHS = [155,           95,      90,       85,        65,      85,         65,      65,      150]
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
            ctk.CTkLabel(empty, text="🩺", font=ctk.CTkFont(size=32)).pack()
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
                _u(fc, " bpm"), _u(presion),
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
                     text="🩺  Nuevo registro" if not edit else "🩺  Editar registro",
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
        entry_fecha = _entry(grp_fecha, val=reg.get("fecha", date.today().isoformat()) if edit else date.today().isoformat())

        grp_enf = _field("Enfermero / Doctor *", 1, 1)
        combo_enf = ctk.CTkComboBox(grp_enf,
                                    values=list(enf_opts.keys()) if enf_opts else ["Sin enfermeros/doctores"],
                                    fg_color=CLR_BG, border_color=CLR_BORDER,
                                    text_color=CLR_TEXT, button_color=CLR_SKY_DARK,
                                    dropdown_fg_color=CLR_WHITE, dropdown_text_color=CLR_TEXT,
                                    height=36, corner_radius=8)
        combo_enf.pack(fill="x")
        combo_enf.set("Selecciona enfermero o doctor...")
        if edit and enf_opts:
            for k, v in enf_opts.items():
                if v == reg.get("id_enfermero"):
                    combo_enf.set(k); break

        grp_fc  = _field("Frecuencia cardiaca (bpm)", 2, 0)
        entry_fc = _entry(grp_fc, "Ej. 72", str(reg.get("frecuencia_cardiaca") or "") if edit else "")

        grp_pre = _field("Presión arterial", 2, 1)
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
            ctk.CTkLabel(alert, text="⚠️", font=ctk.CTkFont(size=34)).pack(pady=(16, 2))
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
        ctk.CTkButton(btn_bar, text="💾  Guardar",
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

        ctk.CTkLabel(dialog, text="⚠️", font=ctk.CTkFont(size=36)).pack(pady=(24, 4))
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
        ctk.CTkLabel(t, text=("❌  " if error else "✅  ") + msg,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_WHITE).pack(fill="both", expand=True, padx=14)
        t.after(2800, t.destroy)