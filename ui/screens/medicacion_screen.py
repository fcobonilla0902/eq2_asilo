"""
Pantalla de Medicaciones — CustomTkinter
Diseño mejorado: más claro, agradable, legible.
"""
import customtkinter as ctk
from datetime import date, datetime

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
        ctk.CTkLabel(search_wrap, text="🔍", font=ctk.CTkFont(size=13),
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

        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).grid(row=1, column=0, columnspan=3, sticky="ew")

    # ── Stats (4 tarjetas ahora) ───────────────────────────────────────────────
    def _build_stats(self):
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, sticky="ew", padx=24, pady=(18, 0))
        sf.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._stat_total   = self._stat_card(sf, 0, "Total programadas", "0", "📋", CLR_SKY_DARK,   "#dbeafe")
        self._stat_admin   = self._stat_card(sf, 1, "Administradas",     "0", "✅", CLR_GREEN_DARK, CLR_GREEN_LIGHT)
        self._stat_vencida = self._stat_card(sf, 2, "Vencidas hoy",      "0", "⚠️", CLR_AMBER,      CLR_AMBER_LIGHT)
        self._stat_omision = self._stat_card(sf, 3, "Omisiones",         "0", "🔴", CLR_RED,        CLR_RED_LIGHT)

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
            tab_bar, text="📋  Lista",
            fg_color=CLR_WHITE, hover_color=CLR_SKY_LIGHT,
            text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=0, height=46, width=140, border_width=0,
            command=lambda: self._switch_tab("lista"),
        )
        self._tab_list_btn.pack(side="left")

        self._tab_alert_btn = ctk.CTkButton(
            tab_bar, text="🔔  Alertas",
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
        if tab == "lista":
            self._page_alertas.grid_remove()
            self._page_lista.grid(row=0, column=0, sticky="nsew")
            self._tab_list_btn.configure(fg_color=CLR_WHITE, text_color=CLR_SKY_XDARK,
                                         font=ctk.CTkFont(size=12, weight="bold"))
            self._tab_alert_btn.configure(fg_color="transparent", text_color=CLR_MUTED,
                                          font=ctk.CTkFont(size=12))
        else:
            self._page_lista.grid_remove()
            self._page_alertas.grid(row=0, column=0, sticky="nsew")
            self._tab_alert_btn.configure(fg_color=CLR_WHITE, text_color=CLR_SKY_XDARK,
                                          font=ctk.CTkFont(size=12, weight="bold"))
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
            ctk.CTkLabel(empty, text="💊", font=ctk.CTkFont(size=32)).pack()
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
                    rf, text="✓ Aplicada",
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

        ctk.CTkLabel(dialog, text="↩️", font=ctk.CTkFont(size=36)).pack(pady=(20, 4))
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
            ctk.CTkLabel(empty, text="✅", font=ctk.CTkFont(size=40)).pack()
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
            icon = "⚠️" if estado_txt == "Vencida" else "🔴"

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
                     text="💊  Nueva medicacion" if not edit else "💊  Editar medicacion",
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

        grp_fecha = _field(body, "Fecha", 2, 0)
        entry_fecha = ctk.CTkEntry(grp_fecha, fg_color=CLR_BG, border_color=CLR_BORDER,
                                   text_color=CLR_TEXT, height=36, corner_radius=8)
        entry_fecha.pack(fill="x")
        fecha_val = med.get("fecha", date.today().isoformat()) if edit else date.today().isoformat()
        entry_fecha.insert(0, fecha_val)

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

        grp_hora = _field(body, "Horario", 3, 0, 2)

        hora_init = "08"; min_init = "00"
        if edit and med.get("horario"):
            parts = str(med["horario"]).split(":")
            if len(parts) >= 2:
                hora_init = parts[0].zfill(2)
                min_init  = parts[1].zfill(2)

        hora_var = ctk.StringVar(value=hora_init)
        min_var  = ctk.StringVar(value=min_init)
        horas_vals = [str(h).zfill(2) for h in range(24)]
        mins_vals  = ["00","05","10","15","20","25","30","35","40","45","50","55"]

        hora_wrap = ctk.CTkFrame(grp_hora, fg_color=CLR_BG, corner_radius=8,
                                 border_width=1, border_color=CLR_BORDER)
        hora_wrap.pack(anchor="w")

        ctk.CTkLabel(hora_wrap, text="🕐", font=ctk.CTkFont(size=15),
                     text_color=CLR_MUTED).pack(side="left", padx=(10, 6), pady=8)

        hora_sel = ctk.CTkOptionMenu(hora_wrap, values=horas_vals, variable=hora_var,
                                     fg_color=CLR_BG, button_color=CLR_SKY_DARK,
                                     button_hover_color=CLR_SKY_XDARK,
                                     text_color=CLR_TEXT, dropdown_fg_color=CLR_WHITE,
                                     dropdown_text_color=CLR_TEXT,
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     width=72, height=34, corner_radius=6)
        hora_sel.pack(side="left", pady=6)

        ctk.CTkLabel(hora_wrap, text=":",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(side="left", padx=3)

        min_sel = ctk.CTkOptionMenu(hora_wrap, values=mins_vals, variable=min_var,
                                    fg_color=CLR_BG, button_color=CLR_SKY_DARK,
                                    button_hover_color=CLR_SKY_XDARK,
                                    text_color=CLR_TEXT, dropdown_fg_color=CLR_WHITE,
                                    dropdown_text_color=CLR_TEXT,
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    width=72, height=34, corner_radius=6)
        min_sel.pack(side="left", pady=6)

        preview_lbl = ctk.CTkLabel(hora_wrap,
                                   text=f"  {hora_init}:{min_init} hrs",
                                   font=ctk.CTkFont(size=12), text_color=CLR_MUTED)
        preview_lbl.pack(side="left", padx=(8, 12))

        def _update_preview(*_):
            preview_lbl.configure(text=f"  {hora_var.get()}:{min_var.get()} hrs")
        hora_var.trace_add("write", _update_preview)
        min_var.trace_add("write", _update_preview)

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
                          command=alert.destroy
                          ).pack(padx=40, pady=12, fill="x")

        def _save():
            res_key = combo_res.get()
            enf_key = combo_enf.get()
            res_id  = res_opts.get(res_key)
            enf_id  = enf_opts.get(enf_key)
            dosis   = entry_dosis.get().strip()
            fecha   = entry_fecha.get().strip()
            horario = f"{hora_var.get()}:{min_var.get()}"

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
        ctk.CTkButton(btn_bar, text="💾  Guardar",
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

        ctk.CTkLabel(dialog, text="⚠️", font=ctk.CTkFont(size=36)).pack(pady=(24, 4))
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
        ctk.CTkLabel(t, text=("❌  " if error else "✅  ") + msg,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_WHITE).pack(fill="both", expand=True, padx=14)
        t.after(2800, t.destroy)