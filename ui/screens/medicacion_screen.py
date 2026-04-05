"""
Pantalla de Medicaciones — CustomTkinter
Diseño mejorado: más claro, agradable, legible.
"""
import customtkinter as ctk
from datetime import date, datetime
from tkinter import filedialog
import calendar


# ── Paleta ────────────────────────────────────────────────────────────────────
CLR_SKY        = "#38bdf8"
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


def _estado(fecha_str: str, horario_str: str, administrada: int = 0):
    """
    Si administrada=1 siempre retorna 'Administrada', ignorando fecha/hora.
    """
    if administrada:
        return "Administrada", CLR_GREEN_LIGHT, CLR_GREEN_DARK

    today = date.today()
    now   = datetime.now().strftime("%H:%M")
    try:
        f = date.fromisoformat(fecha_str)
    except Exception:
        return "Desconocido", CLR_BORDER, CLR_MUTED

    if f < today:
        return "Omision",    CLR_RED_LIGHT,   CLR_RED
    if f == today and horario_str and horario_str <= now:
        return "Vencida",    CLR_AMBER_LIGHT, CLR_AMBER
    return     "Programada", CLR_GREEN_LIGHT, CLR_GREEN


# ─────────────────────────────────────────────────────────────────────────────
# Widget: Calendario emergente
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
# Widget: Selector de hora emergente
# ─────────────────────────────────────────────────────────────────────────────
class TimePicker(ctk.CTkToplevel):
    def __init__(self, parent, initial_time: str, on_select):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(fg_color=CLR_WHITE)
        self.attributes("-topmost", True)
        self._on_select = on_select
        try:
            parts = initial_time.strip().split(":")
            self._hour   = int(parts[0]) % 24
            self._minute = int(parts[1]) % 60
        except Exception:
            self._hour = 9; self._minute = 0

        outer = ctk.CTkFrame(self, fg_color=CLR_BORDER, corner_radius=14)
        outer.pack(padx=1, pady=1, fill="both", expand=True)
        inner = ctk.CTkFrame(outer, fg_color=CLR_WHITE, corner_radius=13)
        inner.pack(padx=1, pady=1, fill="both", expand=True)
        self._build(inner)

        parent.update_idletasks()
        x = parent.winfo_rootx()
        y = parent.winfo_rooty() + parent.winfo_height() + 4
        self.geometry(f"230x320+{x}+{y}")
        self.bind("<FocusOut>", self._on_focus_out)
        self.focus_set()

    def _on_focus_out(self, event):
        self.after(150, self._check_focus)

    def _check_focus(self):
        try:
            if self.focus_get() is None:
                self.destroy()
        except Exception:
            self.destroy()

    def _build(self, container):
        ctk.CTkLabel(container, text="Selecciona la hora",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT).pack(pady=(12, 6))

        cols_frame = ctk.CTkFrame(container, fg_color="transparent")
        cols_frame.pack(fill="both", expand=True, padx=16)

        hdr = ctk.CTkFrame(cols_frame, fg_color="transparent")
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="Hora",    font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=CLR_MUTED, width=90).pack(side="left",  expand=True)
        ctk.CTkLabel(hdr, text="Minutos", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=CLR_MUTED, width=90).pack(side="right", expand=True)

        wheels = ctk.CTkFrame(cols_frame, fg_color="transparent")
        wheels.pack(fill="both", expand=True, pady=4)

        hour_col = ctk.CTkScrollableFrame(wheels, fg_color=CLR_BG, corner_radius=8,
                                          width=85, height=160)
        hour_col.pack(side="left", expand=True, fill="y")
        min_col  = ctk.CTkScrollableFrame(wheels, fg_color=CLR_BG, corner_radius=8,
                                          width=85, height=160)
        min_col.pack(side="right", expand=True, fill="y")

        self._hour_btns = []
        self._min_btns  = []

        for h in range(24):
            is_sel = (h == self._hour)
            btn = ctk.CTkButton(hour_col, text=f"{h:02d}", height=30, width=75,
                                fg_color=CLR_SKY_DARK if is_sel else "transparent",
                                hover_color=CLR_SKY_LIGHT,
                                text_color=CLR_WHITE if is_sel else CLR_TEXT,
                                font=ctk.CTkFont(size=12, weight="bold" if is_sel else "normal"),
                                corner_radius=6,
                                command=lambda _h=h: self._select_hour(_h))
            btn.pack(pady=1)
            self._hour_btns.append(btn)

        for m in range(60):
            is_sel = (m == self._minute)
            btn = ctk.CTkButton(min_col, text=f"{m:02d}", height=30, width=75,
                                fg_color=CLR_SKY_DARK if is_sel else "transparent",
                                hover_color=CLR_SKY_LIGHT,
                                text_color=CLR_WHITE if is_sel else CLR_TEXT,
                                font=ctk.CTkFont(size=12, weight="bold" if is_sel else "normal"),
                                corner_radius=6,
                                command=lambda _m=m: self._select_minute(_m))
            btn.pack(pady=1)
            self._min_btns.append(btn)

        ctk.CTkButton(container, text="Confirmar",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, corner_radius=8, height=36,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._confirm).pack(fill="x", padx=16, pady=(6, 12))

        # Scroll automático al elemento seleccionado
        self.after(80, lambda: self._scroll_to_selected(hour_col, self._hour, min_col, self._minute))

    def _select_hour(self, h):
        self._hour_btns[self._hour].configure(fg_color="transparent", text_color=CLR_TEXT,
                                               font=ctk.CTkFont(size=12, weight="normal"))
        self._hour = h
        self._hour_btns[h].configure(fg_color=CLR_SKY_DARK, text_color=CLR_WHITE,
                                      font=ctk.CTkFont(size=12, weight="bold"))

    def _scroll_to_selected(self, hour_col, hour, min_col, minute):
        """Desplaza los scrollframes al elemento seleccionado."""
        try:
            btn_height = 31  # 30px altura + 1px pady
            total_hours = 24
            total_mins  = 60
            # Fracción 0..1 para mover el scroll
            frac_h = hour / max(total_hours - 1, 1)
            frac_m = minute / max(total_mins - 1, 1)
            # CTkScrollableFrame expone _parent_canvas
            hour_col._parent_canvas.yview_moveto(max(0, frac_h - 0.15))
            min_col._parent_canvas.yview_moveto(max(0, frac_m - 0.15))
        except Exception:
            pass

    def _select_minute(self, m):
        self._min_btns[self._minute].configure(fg_color="transparent", text_color=CLR_TEXT,
                                                font=ctk.CTkFont(size=12, weight="normal"))
        self._minute = m
        self._min_btns[m].configure(fg_color=CLR_SKY_DARK, text_color=CLR_WHITE,
                                     font=ctk.CTkFont(size=12, weight="bold"))

    def _confirm(self):
        self._on_select(f"{self._hour:02d}:{self._minute:02d}")
        self.destroy()


class MedicacionScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._selected_id    = None
        self._selected_frame = None
        self._all_rows       = []

        self._build_topbar()
        self._build_stats()
        self._build_tabs()
        self._load_data()
        
        

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=0, border_width=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)

        title_col = ctk.CTkFrame(bar, fg_color="transparent")
        title_col.grid(row=0, column=0, padx=28, pady=14, sticky="w")
        ctk.CTkLabel(title_col, text="Medicaciones",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Control de medicamentos programados",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")

        search_wrap = ctk.CTkFrame(bar, fg_color=CLR_BG, corner_radius=10,
                                   border_width=1, border_color=CLR_BORDER)
        search_wrap.grid(row=0, column=1, padx=16, pady=14, sticky="ew")
        search_wrap.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(search_wrap, text="⌕", font=ctk.CTkFont(size=13),
                     text_color=CLR_MUTED, width=30).grid(row=0, column=0, padx=(10, 2), pady=9)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        ctk.CTkEntry(search_wrap, textvariable=self.search_var,
                     placeholder_text="Buscar por residente, dosis o fecha...",
                     fg_color="transparent", border_width=0,
                     text_color=CLR_TEXT, placeholder_text_color=CLR_MUTED,
                     font=ctk.CTkFont(size=12), height=34,
                     ).grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkButton(bar, text="+ Nueva medicacion",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=10, height=38, command=self._open_form,
                      ).grid(row=0, column=2, padx=(8, 28), pady=14)
        
        # Botón de Reportes
        ctk.CTkButton(bar, text="▤ Reportes",
                      fg_color=CLR_AMBER, hover_color=CLR_AMBER_LIGHT,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=10, height=38, command=self._open_report_modal,
                      ).grid(row=0, column=3, padx=(0, 28), pady=14)


        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).grid(row=1, column=0, columnspan=4, sticky="ew")

    # ── Stats (4 tarjetas ahora) ───────────────────────────────────────────────
    def _build_stats(self):
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, sticky="ew", padx=24, pady=(18, 0))
        sf.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._stat_total   = self._stat_card(sf, 0, "Total programadas", "0", "▤", CLR_SKY_DARK,   "#dbeafe")
        self._stat_admin   = self._stat_card(sf, 1, "Administradas",     "0", "✔", CLR_GREEN_DARK, CLR_GREEN_LIGHT)
        self._stat_vencida = self._stat_card(sf, 2, "Vencidas hoy",      "0", "▲", CLR_AMBER,      CLR_AMBER_LIGHT)
        self._stat_omision = self._stat_card(sf, 3, "Omisiones",         "0", "●", CLR_RED,        CLR_RED_LIGHT)

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
        val_lbl = ctk.CTkLabel(tc, text=value,
                               font=ctk.CTkFont(size=28, weight="bold"), text_color=CLR_TEXT)
        val_lbl.pack(anchor="w")
        ctk.CTkLabel(tc, text=title, font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")
        return val_lbl

    # ── Tabs ──────────────────────────────────────────────────────────────────
    def _build_tabs(self):
        tab_wrap = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=14,
                                border_width=1, border_color=CLR_BORDER)
        tab_wrap.grid(row=2, column=0, sticky="nsew", padx=24, pady=16)
        tab_wrap.grid_rowconfigure(1, weight=1)
        tab_wrap.grid_columnconfigure(0, weight=1)

        tab_bar = ctk.CTkFrame(tab_wrap, fg_color="#f8fafc", corner_radius=0, height=46)
        tab_bar.grid(row=0, column=0, sticky="ew")
        tab_bar.grid_propagate(False)
        ctk.CTkFrame(tab_bar, fg_color=CLR_BORDER, height=1).place(relx=0, rely=1.0, relwidth=1, anchor="sw")

        self._tab_list_btn = ctk.CTkButton(
            tab_bar, text="▤  Lista",
            fg_color=CLR_WHITE, hover_color=CLR_SKY_LIGHT,
            text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=0, height=46, width=140, border_width=0,
            command=lambda: self._switch_tab("lista"),
        )
        self._tab_list_btn.pack(side="left")

        self._tab_alert_btn = ctk.CTkButton(
            tab_bar, text="◈  Alertas",
            fg_color="transparent", hover_color=CLR_SKY_LIGHT,
            text_color=CLR_MUTED, font=ctk.CTkFont(size=12),
            corner_radius=0, height=46, width=140, border_width=0,
            command=lambda: self._switch_tab("alertas"),
        )
        self._tab_alert_btn.pack(side="left")

        self._tab_container = ctk.CTkFrame(tab_wrap, fg_color=CLR_WHITE, corner_radius=0)
        self._tab_container.grid(row=1, column=0, sticky="nsew")
        self._tab_container.grid_rowconfigure(0, weight=1)
        self._tab_container.grid_columnconfigure(0, weight=1)

        self._page_lista   = self._build_list_page(self._tab_container)
        self._page_alertas = self._build_alerts_page(self._tab_container)
        self._page_lista.grid(row=0, column=0, sticky="nsew")
        self._current_tab = "lista"

    def _switch_tab(self, tab: str):
        if tab == self._current_tab:
            return
        self._current_tab = tab
        # Preservar texto actual del botón de alertas (puede tener conteo)
        alert_text = self._tab_alert_btn.cget("text")
        if tab == "lista":
            self._page_alertas.grid_remove()
            self._page_lista.grid(row=0, column=0, sticky="nsew")
            self._tab_list_btn.configure(fg_color=CLR_WHITE, text_color=CLR_SKY_XDARK,
                                         font=ctk.CTkFont(size=12, weight="bold"))
            self._tab_alert_btn.configure(fg_color="transparent", text_color=CLR_MUTED,
                                          font=ctk.CTkFont(size=12), text=alert_text)
        else:
            self._page_lista.grid_remove()
            self._page_alertas.grid(row=0, column=0, sticky="nsew")
            self._tab_alert_btn.configure(fg_color=CLR_WHITE, text_color=CLR_SKY_XDARK,
                                          font=ctk.CTkFont(size=12, weight="bold"), text=alert_text)
            self._tab_list_btn.configure(fg_color="transparent", text_color=CLR_MUTED,
                                         font=ctk.CTkFont(size=12))

    # ── Página Lista ──────────────────────────────────────────────────────────
    def _build_list_page(self, parent):
        page = ctk.CTkFrame(parent, fg_color=CLR_WHITE, corner_radius=0)
        page.grid_rowconfigure(1, weight=1)
        page.grid_columnconfigure(0, weight=1)

        cols   = ["Residente", "Dosis", "Horario", "Fecha", "Enfermero / Doctor", "Estado", "Aplicacion"]
        widths = [170,          155,     80,         100,    135,          100,       120]
        hdr = ctk.CTkFrame(page, fg_color="#f8fafc", corner_radius=0, height=38)
        hdr.grid(row=0, column=0, sticky="ew")
        for c, (col, w) in enumerate(zip(cols, widths)):
            ctk.CTkLabel(hdr, text=col.upper(),
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=CLR_MUTED, width=w, anchor="w",
                         ).grid(row=0, column=c, padx=(14 if c == 0 else 4, 0), pady=10, sticky="w")

        self._list_scroll = ctk.CTkScrollableFrame(page, fg_color=CLR_WHITE, corner_radius=0)
        self._list_scroll.grid(row=1, column=0, sticky="nsew")
        self._list_scroll.grid_columnconfigure(0, weight=1)

        bar = ctk.CTkFrame(page, fg_color="#f8fafc", corner_radius=0, height=52)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).place(relx=0, rely=0, relwidth=1)

        self._lbl_sel = ctk.CTkLabel(bar, text="Selecciona una medicacion para ver las acciones",
                                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED)
        self._lbl_sel.pack(side="left", padx=20)

        self._btn_del = ctk.CTkButton(
            bar, text="Eliminar",
            fg_color=CLR_RED_LIGHT, hover_color="#fecaca",
            text_color=CLR_RED, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=34, width=100,
            border_width=1, border_color="#fca5a5",
            state="disabled", command=self._confirm_delete)
        self._btn_del.pack(side="right", padx=(4, 20), pady=9)

        self._btn_edit = ctk.CTkButton(
            bar, text="Editar",
            fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
            text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8, height=34, width=100,
            border_width=1, border_color="#7dd3fc",
            state="disabled", command=self._open_edit)
        self._btn_edit.pack(side="right", padx=4, pady=9)

        return page

    # ── Página Alertas ────────────────────────────────────────────────────────
    def _build_alerts_page(self, parent):
        page = ctk.CTkFrame(parent, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        page.grid_rowconfigure(0, weight=1)
        page.grid_columnconfigure(0, weight=1)
        self._alerts_scroll = ctk.CTkScrollableFrame(page, fg_color="transparent", corner_radius=0)
        self._alerts_scroll.grid(row=0, column=0, sticky="nsew")
        self._alerts_scroll.grid_columnconfigure(0, weight=1)
        return page

    # ── Cargar datos ──────────────────────────────────────────────────────────
    def _load_data(self):
        try:
            from modules.medicacion import listar_medicaciones
            rows = listar_medicaciones()
        except Exception:
            rows = []
        self._all_rows = [dict(r) if hasattr(r, "keys") else r for r in rows]
        self._render_list(self._all_rows)
        self._render_alerts()
        self._update_stats()

    def _get_adm(self, r):
        return int(r.get("administrada", 0) or 0) if isinstance(r, dict) else (int(r[8]) if len(r) > 8 and r[8] else 0)

    def _update_stats(self):
        total   = len(self._all_rows)
        admin   = sum(1 for r in self._all_rows if self._get_adm(r))
        vencida = sum(1 for r in self._all_rows
                      if _estado(r.get("fecha","") if isinstance(r,dict) else r[1],
                                 r.get("horario","") if isinstance(r,dict) else r[2],
                                 self._get_adm(r))[0] == "Vencida")
        omision = sum(1 for r in self._all_rows
                      if _estado(r.get("fecha","") if isinstance(r,dict) else r[1],
                                 r.get("horario","") if isinstance(r,dict) else r[2],
                                 self._get_adm(r))[0] == "Omision")
        self._stat_total.configure(text=str(total))
        self._stat_admin.configure(text=str(admin))
        self._stat_vencida.configure(text=str(vencida))
        self._stat_omision.configure(text=str(omision))

        # Actualizar texto del botón Alertas con conteo
        n_alertas = vencida + omision
        if n_alertas > 0:
            self._tab_alert_btn.configure(text=f"◈  Alertas  ({n_alertas})")
        else:
            self._tab_alert_btn.configure(text="◈  Alertas")

    def _filter(self):
        q = self.search_var.get().strip().lower()
        filtered = self._all_rows if not q else [
            r for r in self._all_rows
            if q in str(r.get("residente_nombre","") if isinstance(r,dict) else r[5]).lower()
            or q in str(r.get("dosis","")           if isinstance(r,dict) else r[3]).lower()
            or q in str(r.get("fecha","")           if isinstance(r,dict) else r[1]).lower()
        ]
        self._render_list(filtered)

    def _render_list(self, rows):
        for w in self._list_scroll.winfo_children():
            w.destroy()
        self._selected_id    = None
        self._selected_frame = None
        self._set_actions(False)

        if not rows:
            empty = ctk.CTkFrame(self._list_scroll, fg_color="transparent")
            empty.grid(row=0, column=0, pady=50)
            ctk.CTkLabel(empty, text="⊕", font=ctk.CTkFont(size=32)).pack()
            ctk.CTkLabel(empty, text="Sin medicaciones registradas",
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=CLR_TEXT_SOFT).pack(pady=(6, 2))
            ctk.CTkLabel(empty, text="Usa el boton '+ Nueva medicacion' para agregar",
                         font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack()
            return

        for idx, row in enumerate(rows):
            if isinstance(row, dict):
                rid          = row.get("id_medicacion")
                fecha        = row.get("fecha", "") or ""
                horario      = row.get("horario", "") or ""
                dosis        = row.get("dosis", "-") or "-"
                res_name     = row.get("residente_nombre", "-") or "-"
                enf_name     = row.get("enfermero_nombre", "-") or "-"
                administrada = int(row.get("administrada", 0) or 0)
            else:
                rid, fecha, horario, dosis = row[0], row[1] or "", row[2] or "", row[3] or "-"
                res_name, enf_name = row[5] or "-", row[7] or "-"
                administrada = int(row[8]) if len(row) > 8 and row[8] else 0

            estado_txt, estado_bg, estado_fg = _estado(fecha, horario, administrada)
            bg = CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT

            rf = ctk.CTkFrame(self._list_scroll, fg_color=bg, corner_radius=0, height=50)
            rf.grid(row=idx, column=0, sticky="ew")

            def _bind(w, r=rid, f=rf):
                w.bind("<Button-1>", lambda e: self._select(r, f))
                w.configure(cursor="hand2")

            _bind(rf)

            vals   = [res_name, dosis, horario or "-", fecha or "-", enf_name]
            widths = [170,       155,   80,             100,           135]
            for c, (val, w) in enumerate(zip(vals, widths)):
                lbl = ctk.CTkLabel(rf, text=val, font=ctk.CTkFont(size=12),
                                   text_color=CLR_TEXT_SOFT, width=w, anchor="w")
                lbl.grid(row=0, column=c, padx=(14 if c == 0 else 4, 0), sticky="w")
                _bind(lbl)

            badge_frame = ctk.CTkFrame(rf, fg_color=estado_bg, corner_radius=6, width=88, height=26)
            badge_frame.grid(row=0, column=5, padx=(4, 4), pady=12)
            badge_frame.grid_propagate(False)
            ctk.CTkLabel(badge_frame, text=estado_txt,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=estado_fg).place(relx=.5, rely=.5, anchor="center")

            if administrada:
                btn_app = ctk.CTkButton(
                    rf, text="✔ Aplicada",
                    fg_color=CLR_GREEN_LIGHT, hover_color="#bbf7d0",
                    text_color=CLR_GREEN_DARK,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    corner_radius=6, height=26, width=100,
                    border_width=1, border_color="#86efac",
                    command=lambda r=rid: self._toggle_administrada(r, True),
                )
            else:
                btn_app = ctk.CTkButton(
                    rf, text="Registrar",
                    fg_color=CLR_BG, hover_color=CLR_GREEN_LIGHT,
                    text_color=CLR_MUTED,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    corner_radius=6, height=26, width=100,
                    border_width=1, border_color=CLR_BORDER,
                    command=lambda r=rid: self._toggle_administrada(r, False),
                )

            btn_app.grid(row=0, column=6, padx=(4, 12), pady=12)

    # ── Toggle administrada ────────────────────────────────────────────────────
    def _toggle_administrada(self, rid: int, ya_administrada: bool):
        if ya_administrada:
            self._confirm_revertir(rid)
        else:
            try:
                from modules.medicacion import marcar_administrada
                marcar_administrada(rid)
                self._toast("Medicacion registrada como administrada")
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)

    def _confirm_revertir(self, rid: int):
        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.grab_set()
        dialog.configure(fg_color=CLR_WHITE)
        dialog.resizable(False, False)
        _center(dialog, 400, 215)

        ctk.CTkLabel(dialog, text="↩", font=ctk.CTkFont(size=36)).pack(pady=(20, 4))
        ctk.CTkLabel(dialog, text="Revertir aplicacion?",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog,
                     text="Esto marcara la medicacion como pendiente nuevamente.\nFue un error de registro?",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED, justify="center").pack(pady=(6, 0))

        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=18, padx=24, fill="x")

        def _do():
            try:
                from modules.medicacion import desmarcar_administrada
                desmarcar_administrada(rid)
                self._toast("Aplicacion revertida a pendiente")
                dialog.destroy()
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)
                dialog.destroy()

        ctk.CTkButton(row, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      height=38, corner_radius=8, command=dialog.destroy,
                      ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Si, revertir",
                      fg_color=CLR_AMBER, hover_color="#d97706",
                      text_color=CLR_WHITE, height=38, corner_radius=8,
                      command=_do,
                      ).pack(side="right", expand=True, fill="x")

    # ── Selección ─────────────────────────────────────────────────────────────
    def _select(self, rid, frame):
        if self._selected_frame:
            idx = list(self._list_scroll.winfo_children()).index(self._selected_frame)
            self._selected_frame.configure(fg_color=CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT)
        frame.configure(fg_color=CLR_SKY_LIGHT)
        self._selected_id    = rid
        self._selected_frame = frame
        self._set_actions(True)
        self._lbl_sel.configure(text=f"Medicacion ID {rid} seleccionada",
                                text_color=CLR_SKY_XDARK)

    def _set_actions(self, on: bool):
        s = "normal" if on else "disabled"
        self._btn_edit.configure(state=s)
        self._btn_del.configure(state=s)

    # ── Alertas ────────────────────────────────────────────────────────────────
    def _render_alerts(self):
        for w in self._alerts_scroll.winfo_children():
            w.destroy()

        alertas = [r for r in self._all_rows
                   if _estado(r.get("fecha","") if isinstance(r,dict) else r[1],
                              r.get("horario","") if isinstance(r,dict) else r[2],
                              self._get_adm(r))[0] in ("Vencida", "Omision")]

        if not alertas:
            empty = ctk.CTkFrame(self._alerts_scroll, fg_color="transparent")
            empty.grid(row=0, column=0, pady=60)
            ctk.CTkLabel(empty, text="✔", font=ctk.CTkFont(size=40)).pack()
            ctk.CTkLabel(empty, text="Sin alertas activas",
                         font=ctk.CTkFont(size=15, weight="bold"), text_color="#16a34a").pack(pady=(6, 2))
            ctk.CTkLabel(empty, text="Todas las medicaciones estan al dia",
                         font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack()
            return

        for i, row in enumerate(alertas):
            if isinstance(row, dict):
                rid      = row.get("id_medicacion")
                fecha    = row.get("fecha","-") or "-"
                horario  = row.get("horario","-") or "-"
                dosis    = row.get("dosis","-") or "-"
                res_name = row.get("residente_nombre","-") or "-"
                enf_name = row.get("enfermero_nombre","-") or "-"
                administrada = self._get_adm(row)
            else:
                rid = row[0]
                fecha, horario, dosis = row[1] or "-", row[2] or "-", row[3] or "-"
                res_name, enf_name = row[5] or "-", row[7] or "-"
                administrada = self._get_adm(row)

            estado_txt, estado_bg, estado_fg = _estado(fecha, horario, administrada)
            icon = "▲" if estado_txt == "Vencida" else "●"

            card = ctk.CTkFrame(self._alerts_scroll, fg_color=CLR_WHITE,
                                corner_radius=12, border_width=1,
                                border_color="#fca5a5" if estado_txt == "Omision" else "#fde68a")
            card.grid(row=i, column=0, sticky="ew", padx=16, pady=5)

            stripe = ctk.CTkFrame(card, fg_color=estado_fg, corner_radius=4, width=4)
            stripe.pack(side="left", fill="y", padx=(0, 12), pady=0)
            stripe.pack_propagate(False)

            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(side="left", fill="both", expand=True, pady=14)

            top_row = ctk.CTkFrame(content, fg_color="transparent")
            top_row.pack(fill="x")

            ctk.CTkLabel(top_row, text=f"{icon}  {res_name}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=CLR_TEXT).pack(side="left")

            ctk.CTkButton(
                top_row, text="Registrar aplicacion",
                fg_color=CLR_GREEN_LIGHT, hover_color="#bbf7d0",
                text_color=CLR_GREEN_DARK, font=ctk.CTkFont(size=10, weight="bold"),
                corner_radius=6, height=24, width=150,
                border_width=1, border_color="#86efac",
                command=lambda r=rid: self._registrar_desde_alerta(r),
            ).pack(side="right", padx=(0, 16))

            badge = ctk.CTkFrame(top_row, fg_color=estado_bg, corner_radius=5, width=72, height=22)
            badge.pack(side="right", padx=(0, 8))
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=estado_txt,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=estado_fg).place(relx=.5, rely=.5, anchor="center")

            ctk.CTkLabel(content,
                         text=f"Dosis: {dosis}   Horario: {horario}   Fecha: {fecha}   Enfermero / Doctor: {enf_name}",
                         font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w", pady=(3, 0))

    def _registrar_desde_alerta(self, rid: int):
        try:
            from modules.medicacion import marcar_administrada
            marcar_administrada(rid)
            self._toast("Medicacion registrada como administrada")
            self._load_data()
        except Exception as ex:
            self._toast(f"Error: {ex}", error=True)

    # ── Formulario ─────────────────────────────────────────────────────────────
    def _open_form(self, med=None):
        edit = med is not None
        win = ctk.CTkToplevel(self)
        win.title("Nueva medicacion" if not edit else "Editar medicacion")
        win.grab_set()
        win.resizable(False, False)
        win.configure(fg_color=CLR_WHITE)
        _center(win, 480, 540)

        win.grid_rowconfigure(1, weight=1)
        win.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(win, fg_color=CLR_SKY_DARK, corner_radius=0, height=56)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr,
                     text="⊕  Nueva medicacion" if not edit else "⊕  Editar medicacion",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=CLR_WHITE).pack(side="left", padx=24, pady=14)
        ctk.CTkLabel(hdr, text="Todos los campos son obligatorios",
                     font=ctk.CTkFont(size=10), text_color="#bae6fd").pack(side="right", padx=20)

        body = ctk.CTkFrame(win, fg_color=CLR_WHITE, corner_radius=0)
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

        # ── Consultar solo enfermeros y doctores activos ─────────────────────
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

        def _field(parent, label, row, col=0, colspan=1):
            grp = ctk.CTkFrame(parent, fg_color="transparent")
            grp.grid(row=row, column=col, columnspan=colspan,
                     padx=(20 if col == 0 else 8, 20 if col + colspan >= 2 else 8),
                     pady=(0, 10), sticky="ew")
            ctk.CTkLabel(grp, text=label,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0, 3))
            return grp

        grp_res = _field(body, "Residente", 0, 0, 2)
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
                if v == med.get("id_residente"):
                    combo_res.set(k); break

        grp_dosis = _field(body, "Dosis", 1, 0, 2)
        entry_dosis = ctk.CTkEntry(grp_dosis, fg_color=CLR_BG, border_color=CLR_BORDER,
                                   text_color=CLR_TEXT, height=36, corner_radius=8,
                                   placeholder_text="Ej: Paracetamol 500mg",
                                   placeholder_text_color=CLR_MUTED)
        entry_dosis.pack(fill="x")
        if edit and med.get("dosis"):
            entry_dosis.insert(0, med["dosis"])

        # ── Fecha con calendario ──
        grp_fecha = _field(body, "Fecha", 2, 0)
        fecha_val = med.get("fecha", date.today().isoformat()) if edit else date.today().isoformat()
        fecha_var = ctk.StringVar(value=fecha_val)
        fecha_frame = ctk.CTkFrame(grp_fecha, fg_color=CLR_WHITE, corner_radius=8,
                                   border_width=1, border_color=CLR_BORDER, height=38)
        fecha_frame.pack(fill="x")
        fecha_frame.pack_propagate(False)
        fecha_entry = ctk.CTkEntry(fecha_frame, textvariable=fecha_var, height=36,
                                   fg_color="transparent", border_width=0,
                                   text_color=CLR_TEXT, font=ctk.CTkFont(size=12))
        fecha_entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
        fecha_icon = ctk.CTkButton(fecha_frame, text="▷", width=36, height=36,
                                   fg_color="transparent", hover_color=CLR_SKY_LIGHT,
                                   text_color=CLR_MUTED, corner_radius=8)
        fecha_icon.pack(side="right", padx=(0, 2))
        _cal_ref = [None]
        def _open_cal(event=None):
            if _cal_ref[0] and _cal_ref[0].winfo_exists(): return
            def _on_date(d): fecha_var.set(d)
            _cal_ref[0] = CalendarPicker(fecha_icon, fecha_var.get(), _on_date)
        fecha_icon.configure(command=_open_cal)
        fecha_entry.bind("<Button-1>", _open_cal)

        grp_enf = _field(body, "Enfermero / Doctor", 2, 1)
        combo_enf = ctk.CTkComboBox(grp_enf,
                                    values=list(enf_opts.keys()) if enf_opts else ["Sin enfermeros/doctores"],
                                    fg_color=CLR_BG, border_color=CLR_BORDER,
                                    text_color=CLR_TEXT, button_color=CLR_SKY_DARK,
                                    dropdown_fg_color=CLR_WHITE, dropdown_text_color=CLR_TEXT,
                                    height=36, corner_radius=8)
        combo_enf.pack(fill="x")
        combo_enf.set("Seleccionar...")
        if edit and enf_opts:
            for k, v in enf_opts.items():
                if v == med.get("id_enfermero"):
                    combo_enf.set(k); break

        # ── Hora con selector de ruedas ──
        grp_hora = _field(body, "Horario", 3, 0, 2)
        hora_init = "09:00"
        if edit and med.get("horario"):
            hora_init = str(med["horario"])
        try:
            _h0, _m0 = int(hora_init.split(":")[0]), int(hora_init.split(":")[1])
        except Exception:
            _h0, _m0 = 9, 0

        hora_frame = ctk.CTkFrame(grp_hora, fg_color=CLR_BG, corner_radius=10,
                                  border_width=1, border_color=CLR_BORDER)
        hora_frame.pack(anchor="w", fill="x", pady=(0, 4))

        # ── Contenedor central del selector ──
        picker_row = ctk.CTkFrame(hora_frame, fg_color="transparent")
        picker_row.pack(pady=10, padx=16, anchor="w")

        def _spin_col(parent, init_val, max_val):
            """Columna con ▲ display ▼. Devuelve lista mutable [val]."""
            _val = [init_val]

            col = ctk.CTkFrame(parent, fg_color="transparent")
            col.pack(side="left")

            btn_up = ctk.CTkButton(col, text="▲", width=52, height=22,
                                   fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
                                   text_color=CLR_SKY_XDARK,
                                   font=ctk.CTkFont(size=10, weight="bold"),
                                   corner_radius=6, border_width=0)
            btn_up.pack(pady=(0, 2))

            display = ctk.CTkFrame(col, fg_color=CLR_WHITE, corner_radius=8,
                                   border_width=2, border_color=CLR_SKY_DARK,
                                   width=52, height=48)
            display.pack()
            display.pack_propagate(False)
            lbl = ctk.CTkLabel(display, text=f"{init_val:02d}",
                               font=ctk.CTkFont(size=22, weight="bold"),
                               text_color=CLR_SKY_XDARK)
            lbl.place(relx=0.5, rely=0.5, anchor="center")

            btn_dn = ctk.CTkButton(col, text="▼", width=52, height=22,
                                   fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
                                   text_color=CLR_SKY_XDARK,
                                   font=ctk.CTkFont(size=10, weight="bold"),
                                   corner_radius=6, border_width=0)
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
        ctk.CTkFrame(sep_col, fg_color="transparent", height=22).pack()  # spacer top
        ctk.CTkLabel(sep_col, text=":",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=CLR_SKY_DARK).pack()

        _hora_m = _spin_col(picker_row, _m0, 59)

        # Etiquetas HH / MM debajo
        lbl_row = ctk.CTkFrame(picker_row, fg_color="transparent")
        # (las etiquetas van directamente bajo cada columna en picker_row)

        # Etiqueta indicativa al lado
        hint_col = ctk.CTkFrame(picker_row, fg_color="transparent")
        hint_col.pack(side="left", padx=(14, 0))
        ctk.CTkFrame(hint_col, fg_color="transparent", height=22).pack()
        ctk.CTkLabel(hint_col, text="hh",
                     font=ctk.CTkFont(size=9), text_color=CLR_MUTED).pack()
        ctk.CTkFrame(hint_col, fg_color="transparent", height=48).pack()
        ctk.CTkLabel(hint_col, text="mm",
                     font=ctk.CTkFont(size=9), text_color=CLR_MUTED).pack()

        def _get_hora():
            return f"{_hora_h[0]:02d}:{_hora_m[0]:02d}"

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
                          command=alert.destroy
                          ).pack(padx=40, pady=12, fill="x")

        def _save():
            res_key = combo_res.get()
            enf_key = combo_enf.get()
            res_id  = res_opts.get(res_key)
            enf_id  = enf_opts.get(enf_key)
            dosis   = entry_dosis.get().strip()
            fecha   = fecha_var.get().strip()
            horario = _get_hora()

            if not res_id:  _show_alert("Debes seleccionar un residente"); return
            if not dosis:   _show_alert("La dosis es obligatoria"); return
            if not fecha:   _show_alert("La fecha es obligatoria"); return
            if not enf_id:  _show_alert("Debes seleccionar un enfermero"); return

            datos = {"id_residente": res_id, "dosis": dosis,
                     "horario": horario, "fecha": fecha, "id_enfermero": enf_id}
            try:
                if edit:
                    from modules.medicacion import actualizar_medicacion
                    actualizar_medicacion(med["id_medicacion"], datos)
                    self._toast("Medicacion actualizada")
                else:
                    from modules.medicacion import crear_medicacion
                    crear_medicacion(datos)
                    self._toast("Medicacion registrada")
                win.destroy()
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)
                win.destroy()

        ctk.CTkButton(btn_bar, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=8, height=36, command=win.destroy,
                      ).grid(row=0, column=0, padx=(16, 6), pady=12, sticky="ew")
        ctk.CTkButton(btn_bar, text="▦  Guardar",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8, height=36, command=_save,
                      ).grid(row=0, column=1, padx=(6, 16), pady=12, sticky="ew")

    def _open_edit(self):
        if not self._selected_id:
            return
        try:
            from modules.medicacion import obtener_medicacion
            m = obtener_medicacion(self._selected_id)
            if m:
                self._open_form(med=dict(m))
        except Exception as ex:
            self._toast(f"Error: {ex}", error=True)

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
        ctk.CTkLabel(dialog, text="Eliminar esta medicacion?",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text="Esta accion es permanente y no se puede deshacer.",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4, 0))

        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=20, padx=24, fill="x")

        def _do():
            try:
                from modules.medicacion import eliminar_medicacion
                eliminar_medicacion(self._selected_id)
                self._toast("Medicacion eliminada")
                dialog.destroy()
                self._selected_id = None
                self._selected_frame = None
                self._set_actions(False)
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)
                dialog.destroy()

        ctk.CTkButton(row, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      height=38, corner_radius=8, command=dialog.destroy,
                      ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(row, text="Si, eliminar",
                      fg_color=CLR_RED, hover_color="#dc2626",
                      text_color=CLR_WHITE, height=38, corner_radius=8,
                      command=_do,
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
        ctk.CTkLabel(t, text=("✖  " if error else "✔  ") + msg,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_WHITE).pack(fill="both", expand=True, padx=14)
        t.after(2800, t.destroy)
        
        
        
    def _open_report_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Generar Reporte de Medicaciones")
        _center(modal, 460, 420)
        modal.grab_set()
        modal.configure(fg_color=CLR_BG)
        modal.resizable(False, False)

        # Header
        hdr = ctk.CTkFrame(modal, fg_color=CLR_SKY_DARK, corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="▤  Generar Reporte",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=CLR_WHITE).pack(side="left", padx=24, pady=16)
        ctk.CTkLabel(hdr, text="Filtra y exporta medicaciones",
                     font=ctk.CTkFont(size=10), text_color="#bae6fd").pack(side="right", padx=20)

        # Cuerpo
        frame = ctk.CTkFrame(modal, fg_color=CLR_WHITE, corner_radius=12,
                             border_width=1, border_color=CLR_BORDER)
        frame.pack(fill="both", expand=True, padx=20, pady=16)

        def _lbl(text):
            ctk.CTkLabel(frame, text=text,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", padx=20, pady=(12, 2))

        # ── Residente ──
        _lbl("Residente")
        residentes = sorted({r.get("residente_nombre","") for r in self._all_rows
                             if isinstance(r, dict) and r.get("residente_nombre","")})
        self.residente_var = ctk.StringVar(value="Todos")
        combo_res = ctk.CTkComboBox(frame, values=["Todos"] + residentes,
                                    variable=self.residente_var,
                                    fg_color=CLR_BG, border_color=CLR_BORDER,
                                    text_color=CLR_TEXT, button_color=CLR_SKY_DARK,
                                    dropdown_fg_color=CLR_WHITE, dropdown_text_color=CLR_TEXT,
                                    height=36, corner_radius=8)
        combo_res.pack(fill="x", padx=20, pady=(0, 4))

        # ── Separador ──
        ctk.CTkFrame(frame, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=20, pady=(8, 4))

        # ── Fechas en dos columnas ──
        dates_row = ctk.CTkFrame(frame, fg_color="transparent")
        dates_row.pack(fill="x", padx=20, pady=(4, 4))
        dates_row.grid_columnconfigure((0, 1), weight=1)

        def _date_field(parent, col, label, default_val):
            grp = ctk.CTkFrame(parent, fg_color="transparent")
            grp.grid(row=0, column=col, padx=(0, 8 if col == 0 else 0), sticky="ew")
            ctk.CTkLabel(grp, text=label,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0, 3))
            var = ctk.StringVar(value=default_val)
            wrap = ctk.CTkFrame(grp, fg_color=CLR_BG, corner_radius=8,
                                border_width=1, border_color=CLR_BORDER, height=38)
            wrap.pack(fill="x")
            wrap.pack_propagate(False)
            entry = ctk.CTkEntry(wrap, textvariable=var, height=36,
                                 fg_color="transparent", border_width=0,
                                 text_color=CLR_TEXT, font=ctk.CTkFont(size=12))
            entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
            icon_btn = ctk.CTkButton(wrap, text="▷", width=34, height=34,
                                     fg_color="transparent", hover_color=CLR_SKY_LIGHT,
                                     text_color=CLR_MUTED, corner_radius=6)
            icon_btn.pack(side="right", padx=(0, 2))
            _cal = [None]
            def _open_cal(event=None):
                if _cal[0] and _cal[0].winfo_exists(): return
                def _on(d): var.set(d)
                _cal[0] = CalendarPicker(icon_btn, var.get(), _on)
            icon_btn.configure(command=_open_cal)
            entry.bind("<Button-1>", _open_cal)
            return var

        fecha_ini_var = _date_field(dates_row, 0, "▷  Fecha inicio",
                                    date.today().replace(day=1).isoformat())
        fecha_fin_var = _date_field(dates_row, 1, "▷  Fecha fin",
                                    date.today().isoformat())

        # ── Info ──
        info = ctk.CTkFrame(frame, fg_color=CLR_SKY_XLIGHT, corner_radius=8,
                            border_width=1, border_color="#bae6fd")
        info.pack(fill="x", padx=20, pady=(12, 4))
        ctk.CTkLabel(info, text="ℹ️  El reporte incluirá todas las medicaciones en el rango de fechas seleccionado.",
                     font=ctk.CTkFont(size=10), text_color=CLR_SKY_XDARK,
                     wraplength=380, justify="left").pack(anchor="w", padx=12, pady=8)

        # ── Botones ──
        ctk.CTkFrame(frame, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=20, pady=(8, 0))
        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(12, 16))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_row, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=8, height=38,
                      command=modal.destroy
                      ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        def _generar():
            fecha_inicio = fecha_ini_var.get().strip()
            fecha_fin    = fecha_fin_var.get().strip()
            residente    = self.residente_var.get()
            modal.destroy()
            self._open_report_result(residente, fecha_inicio, fecha_fin)

        ctk.CTkButton(btn_row, text="▤  Generar Reporte",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=8, height=38,
                      command=_generar
                      ).grid(row=0, column=1, padx=(6, 0), sticky="ew")



    
    
    def _open_report_result(self, residente, fecha_ini, fecha_fin):
        win = ctk.CTkToplevel(self)
        win.title("Reporte de Medicaciones")
        _center(win, 900, 600)
        win.grab_set()
        win.configure(fg_color=CLR_WHITE)

        # Header institucional
        hdr = ctk.CTkFrame(win, fg_color=CLR_SKY_DARK, corner_radius=0, height=70)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="✚  Sistema de Gestión de Asilo - CREAN",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=CLR_WHITE).pack(side="left", padx=24, pady=20)

        # Bloque de criterios
        crit = ctk.CTkFrame(win, fg_color=CLR_SKY_XLIGHT, corner_radius=10, border_width=1, border_color=CLR_BORDER)
        crit.pack(fill="x", padx=20, pady=(12, 0))
        ctk.CTkLabel(crit, text=f"Residente: {residente if residente else 'Todos'}",
                    font=ctk.CTkFont(size=12), text_color=CLR_TEXT).pack(anchor="w", padx=12, pady=4)
        ctk.CTkLabel(crit, text=f"Fechas consultadas: {fecha_ini} → {fecha_fin}",
                    font=ctk.CTkFont(size=12), text_color=CLR_TEXT).pack(anchor="w", padx=12, pady=4)

        # Tabla con scroll
        body = ctk.CTkScrollableFrame(win, fg_color=CLR_WHITE, corner_radius=0)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Encabezados
        headers = ["Residente", "Dosis", "Fecha", "Horario", "Enfermero/Doctor", "Estado"]
        widths  = [160, 140, 100, 80, 160, 100]
        hdr_row = ctk.CTkFrame(body, fg_color=CLR_BG, corner_radius=0, height=36)
        hdr_row.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(hdr_row, text=h, font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=CLR_TEXT_SOFT, width=w, anchor="w").pack(side="left", padx=8)

        # Filtrar datos
        rows = self._all_rows
        if residente and residente != "Todos":
            rows = [r for r in rows if r.get("residente_nombre","") == residente]
        if fecha_ini:
            rows = [r for r in rows if r.get("fecha","") >= fecha_ini]
        if fecha_fin:
            rows = [r for r in rows if r.get("fecha","") <= fecha_fin]

        # Renderizar filas
        for idx, row in enumerate(rows):
            res_name = row.get("residente_nombre","-")
            dosis    = row.get("dosis","-")
            fecha    = row.get("fecha","-")
            horario  = row.get("horario","-")
            enf_name = row.get("enfermero_nombre","-")
            estado_txt, estado_bg, estado_fg = _estado(fecha, horario, self._get_adm(row))

            rf = ctk.CTkFrame(body, fg_color=CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT, height=40)
            rf.pack(fill="x", pady=2)
            vals = [res_name, dosis, fecha, horario, enf_name, estado_txt]
            for v, w in zip(vals, widths):
                ctk.CTkLabel(rf, text=v, font=ctk.CTkFont(size=12),
                            text_color=CLR_TEXT_SOFT, width=w, anchor="w").pack(side="left", padx=8)

        # Barra de acciones
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
                    corner_radius=10, height=38,
                    command=win.destroy
                    ).pack(side="right", padx=10, pady=10)







    def _export_pdf(self, rows, residente, fecha_ini, fecha_fin, parent_win=None):
        # Verificar/instalar reportlab automáticamente
        try:
            import reportlab
        except ImportError:
            import subprocess, sys
            self._toast("Instalando reportlab, espera...", error=False)
            self.update()
            subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab", "--quiet"])
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Guardar reporte como..."
            )
            if not file_path:
                return

            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import mm, cm
            from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                            Table, TableStyle, HRFlowable)
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

            # ── Colores corporativos ──
            C_BLUE      = colors.HexColor("#0ea5e9")
            C_BLUE_DARK = colors.HexColor("#0284c7")
            C_BLUE_LITE = colors.HexColor("#e0f2fe")
            C_GREEN     = colors.HexColor("#16a34a")
            C_GREEN_L   = colors.HexColor("#dcfce7")
            C_RED       = colors.HexColor("#ef4444")
            C_RED_L     = colors.HexColor("#fee2e2")
            C_AMBER     = colors.HexColor("#f59e0b")
            C_AMBER_L   = colors.HexColor("#fef3c7")
            C_GRAY      = colors.HexColor("#64748b")
            C_GRAY_L    = colors.HexColor("#f8fafc")
            C_DARK      = colors.HexColor("#0f172a")
            C_WHITE     = colors.white

            def safe(text):
                if text is None: return "-"
                return str(text).replace("\n", " ").replace("\r", " ").strip() or "-"

            # ── Estilos de párrafo ──
            styles = getSampleStyleSheet()
            st_title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20,
                                      textColor=C_BLUE_DARK, spaceAfter=2, alignment=TA_LEFT)
            st_sub   = ParagraphStyle("sub",   fontName="Helvetica", fontSize=10,
                                      textColor=C_GRAY, spaceAfter=8, alignment=TA_LEFT)
            st_meta  = ParagraphStyle("meta",  fontName="Helvetica", fontSize=9,
                                      textColor=C_DARK, leading=13)
            st_meta_b= ParagraphStyle("metab", fontName="Helvetica-Bold", fontSize=9,
                                      textColor=C_DARK, leading=13)
            st_footer= ParagraphStyle("foot",  fontName="Helvetica-Oblique", fontSize=8,
                                      textColor=C_GRAY, alignment=TA_CENTER)
            st_cell  = ParagraphStyle("cell",  fontName="Helvetica", fontSize=9,
                                      textColor=C_DARK, leading=12, wordWrap="CJK")
            st_cell_b= ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=9,
                                      textColor=C_DARK, leading=12)

            # ── Documento ──
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                leftMargin=1.8*cm, rightMargin=1.8*cm,
                topMargin=1.5*cm, bottomMargin=2*cm,
                title="Reporte de Medicaciones",
                author="Sistema de Gestión de Asilo - CREAN"
            )

            story = []

            # ── Cabecera ──
            page_w = A4[0] - 1.8*cm*2
            header_data = [[
                Paragraph("Sistema de Gestión de Asilo - CREAN", ParagraphStyle(
                    "hd", fontName="Helvetica-Bold", fontSize=13, textColor=C_WHITE)),
                Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y  %H:%M')}",
                          ParagraphStyle("hd2", fontName="Helvetica", fontSize=9,
                                         textColor=colors.HexColor("#bae6fd"), alignment=TA_RIGHT))
            ]]
            header_tbl = Table(header_data, colWidths=[page_w*0.6, page_w*0.4])
            header_tbl.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), C_BLUE_DARK),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING",   (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 12),
            ]))
            story.append(header_tbl)
            story.append(Spacer(1, 14))

            # ── Título y subtítulo (sin empalme) ──
            story.append(Paragraph("Reporte de Medicaciones", st_title))
            story.append(Spacer(1, 10))
            story.append(Paragraph("Control y seguimiento de medicamentos programados", st_sub))
            story.append(HRFlowable(width="100%", thickness=1.5, color=C_BLUE, spaceBefore=6, spaceAfter=10))

            # ── Bloque de criterios — filas separadas, bien alineadas ──
            res_txt  = safe(residente) if residente and residente != "Todos" else "Todos los residentes"
            per_txt  = f"{safe(fecha_ini)}  →  {safe(fecha_fin)}"
            tot_txt  = str(len(rows))

            st_lbl = ParagraphStyle("lbl", fontName="Helvetica-Bold", fontSize=9,
                                    textColor=C_BLUE_DARK, leading=14)
            st_val = ParagraphStyle("val", fontName="Helvetica", fontSize=9,
                                    textColor=C_DARK, leading=14)

            crit_inner = Table([
                [Paragraph("Residente:",       st_lbl), Paragraph(res_txt, st_val),
                 Paragraph("Período:",         st_lbl), Paragraph(per_txt, st_val),
                 Paragraph("Total registros:", st_lbl), Paragraph(tot_txt, st_val)],
            ], colWidths=[page_w*0.13, page_w*0.24, page_w*0.10, page_w*0.29, page_w*0.14, page_w*0.10])
            crit_inner.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 4),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ]))

            crit_tbl = Table(
                [[Paragraph("Criterios del reporte", ParagraphStyle(
                    "cr", fontName="Helvetica-Bold", fontSize=10, textColor=C_BLUE_DARK,
                    spaceAfter=4))],
                 [crit_inner]],
                colWidths=[page_w]
            )
            crit_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), C_BLUE_LITE),
                ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#7dd3fc")),
                ("LEFTPADDING",   (0, 0), (-1, -1), 12),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
                ("TOPPADDING",    (0, 0), (0, 0),   10),
                ("BOTTOMPADDING", (0, 0), (0, 0),   2),
                ("TOPPADDING",    (0, 1), (-1, -1),  4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
            ]))
            story.append(crit_tbl)
            story.append(Spacer(1, 14))

            # ── Tabla principal ──
            col_heads = ["#", "Residente", "Dosis / Medicamento", "Fecha", "Horario",
                         "Enfermero / Doctor", "Estado"]
            col_w = [0.6*cm, 3.2*cm, 4.4*cm, 2*cm, 1.8*cm, 3.4*cm, 2.2*cm]

            head_style = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8,
                                        textColor=C_WHITE, alignment=TA_CENTER)
            table_data = [[Paragraph(h, head_style) for h in col_heads]]

            for idx, row in enumerate(rows, start=1):
                res_name = safe(row.get("residente_nombre") if isinstance(row, dict) else row[5])
                dosis    = safe(row.get("dosis")            if isinstance(row, dict) else row[3])
                fecha    = safe(row.get("fecha")            if isinstance(row, dict) else row[1])
                horario  = safe(row.get("horario")          if isinstance(row, dict) else row[2])
                enf_name = safe(row.get("enfermero_nombre") if isinstance(row, dict) else (row[7] if len(row) > 7 else "-"))
                adm      = self._get_adm(row)
                estado_txt, _, _ = _estado(fecha, horario, adm)

                # Color de fila según estado
                row_bg = C_WHITE if idx % 2 == 0 else C_GRAY_L

                # Badge de estado
                badge_colors = {
                    "Administrada": (C_GREEN, C_GREEN_L),
                    "Programada":   (C_GREEN, C_GREEN_L),
                    "Vencida":      (C_AMBER, C_AMBER_L),
                    "Omision":      (C_RED,   C_RED_L),
                }
                est_fg, est_bg = badge_colors.get(estado_txt, (C_GRAY, C_GRAY_L))

                est_para = Paragraph(estado_txt, ParagraphStyle(
                    "est", fontName="Helvetica-Bold", fontSize=8,
                    textColor=est_fg, alignment=TA_CENTER))

                table_data.append([
                    Paragraph(str(idx), ParagraphStyle("num", fontName="Helvetica", fontSize=8,
                                                        textColor=C_GRAY, alignment=TA_CENTER)),
                    Paragraph(res_name, st_cell),
                    Paragraph(dosis,    st_cell),
                    Paragraph(fecha,    ParagraphStyle("fc", fontName="Helvetica", fontSize=8,
                                                       textColor=C_DARK, alignment=TA_CENTER)),
                    Paragraph(horario,  ParagraphStyle("hc", fontName="Helvetica-Bold", fontSize=9,
                                                       textColor=C_BLUE_DARK, alignment=TA_CENTER)),
                    Paragraph(enf_name, st_cell),
                    est_para,
                ])

            tbl = Table(table_data, colWidths=col_w, repeatRows=1)

            # Estilo base
            tbl_style = [
                # Cabecera
                ("BACKGROUND",    (0, 0), (-1, 0), C_BLUE_DARK),
                ("TEXTCOLOR",     (0, 0), (-1, 0), C_WHITE),
                ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
                ("TOPPADDING",    (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                # Filas de datos
                ("VALIGN",        (0, 1), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 1), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
                # Grid
                ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
                ("LINEBELOW",     (0, 0), (-1, 0), 1.5, C_BLUE),
                ("ROUNDEDCORNERS", [4, 4, 4, 4]),
            ]
            # Filas alternadas
            for i in range(1, len(table_data)):
                bg = C_WHITE if i % 2 == 0 else C_GRAY_L
                tbl_style.append(("BACKGROUND", (0, i), (-1, i), bg))
                # Color del badge de estado
                estado_val = rows[i-1].get("fecha","") if isinstance(rows[i-1], dict) else rows[i-1][1]
                horario_v  = rows[i-1].get("horario","") if isinstance(rows[i-1], dict) else rows[i-1][2]
                adm_v      = self._get_adm(rows[i-1])
                est, _, _  = _estado(str(estado_val), str(horario_v), adm_v)
                _, est_bg  = badge_colors.get(est, (C_GRAY, C_GRAY_L))
                tbl_style.append(("BACKGROUND", (6, i), (6, i), est_bg))

            tbl.setStyle(TableStyle(tbl_style))
            story.append(tbl)
            story.append(Spacer(1, 16))

            # ── Resumen estadístico ──
            adm_count  = sum(1 for r in rows if self._get_adm(r))
            prog_count = sum(1 for r in rows if _estado(
                r.get("fecha","") if isinstance(r,dict) else r[1],
                r.get("horario","") if isinstance(r,dict) else r[2],
                self._get_adm(r))[0] == "Programada")
            venc_count = sum(1 for r in rows if _estado(
                r.get("fecha","") if isinstance(r,dict) else r[1],
                r.get("horario","") if isinstance(r,dict) else r[2],
                self._get_adm(r))[0] == "Vencida")
            omis_count = sum(1 for r in rows if _estado(
                r.get("fecha","") if isinstance(r,dict) else r[1],
                r.get("horario","") if isinstance(r,dict) else r[2],
                self._get_adm(r))[0] == "Omision")

            st_stat_lbl = ParagraphStyle("sl", fontName="Helvetica", fontSize=9, textColor=C_GRAY, alignment=TA_CENTER)
            st_stat_val = ParagraphStyle("sv", fontName="Helvetica-Bold", fontSize=16, textColor=C_DARK, alignment=TA_CENTER)

            stats_data = [[
                Paragraph(f"<font color='#0ea5e9' size=18><b>{len(rows)}</b></font><br/><font color='#64748b' size=8>Total</font>", ParagraphStyle("sv2", alignment=TA_CENTER, leading=20)),
                Paragraph(f"<font color='#16a34a' size=18><b>{adm_count}</b></font><br/><font color='#64748b' size=8>Administradas</font>", ParagraphStyle("sv3", alignment=TA_CENTER, leading=20)),
                Paragraph(f"<font color='#22c55e' size=18><b>{prog_count}</b></font><br/><font color='#64748b' size=8>Programadas</font>", ParagraphStyle("sv4", alignment=TA_CENTER, leading=20)),
                Paragraph(f"<font color='#f59e0b' size=18><b>{venc_count}</b></font><br/><font color='#64748b' size=8>Vencidas</font>", ParagraphStyle("sv5", alignment=TA_CENTER, leading=20)),
                Paragraph(f"<font color='#ef4444' size=18><b>{omis_count}</b></font><br/><font color='#64748b' size=8>Omisiones</font>", ParagraphStyle("sv6", alignment=TA_CENTER, leading=20)),
            ]]
            stats_tbl = Table(stats_data, colWidths=["20%","20%","20%","20%","20%"])
            stats_tbl.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), C_BLUE_LITE),
                ("BOX",          (0, 0), (-1, -1), 1, colors.HexColor("#7dd3fc")),
                ("INNERGRID",    (0, 0), (-1, -1), 0.5, colors.HexColor("#bae6fd")),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",   (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
                ("ROUNDEDCORNERS", [6, 6, 6, 6]),
            ]))
            story.append(stats_tbl)
            story.append(Spacer(1, 18))

            # ── Pie de página ──
            story.append(HRFlowable(width="100%", thickness=0.8, color=C_BLUE, spaceBefore=4, spaceAfter=6))
            story.append(Paragraph(
                "Este reporte es generado automáticamente por el Sistema de Gestión de Asilo - CREAN.  "
                "Documento confidencial — Uso interno exclusivo.",
                st_footer))

            doc.build(story)
            self._toast(f"Reporte exportado en:\n{file_path}")

            if parent_win:
                parent_win.after(300, parent_win.destroy)

        except Exception as ex:
            self._toast(f"Error al generar PDF: {ex}", error=True)