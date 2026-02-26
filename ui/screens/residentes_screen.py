"""
Pantalla de Residentes — CustomTkinter
Formulario completo: datos personales, imágenes, familiar, habitación.
"""
import customtkinter as ctk
from datetime import date
import os, shutil

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
CLR_AMBER      = "#f59e0b"
CLR_AMBER_LIGHT= "#fef3c7"

AVATAR_COLORS = ["#6366f1","#8b5cf6","#ec4899","#f43f5e","#0ea5e9","#14b8a6","#22c55e","#f59e0b"]


def _center(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x  = (sw - w) // 2
    y  = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

def _iniciales(n):
    p = (n or "?").strip().split()
    return "".join(x[0].upper() for x in p[:2]) if p else "?"

def _avatar_color(n):
    return AVATAR_COLORS[sum(ord(c) for c in (n or "A")) % len(AVATAR_COLORS)]

def _pick_file(parent, title="Seleccionar imagen"):
    try:
        import tkinter.filedialog as fd
        path = fd.askopenfilename(
            parent=parent, title=title,
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.pdf"), ("Todos", "*.*")]
        )
        return path if path else None
    except Exception:
        return None

def _save_file(src_path, id_residente="0", campo="doc"):
    if not src_path:
        return None
    dest_folder = os.path.join("uploads", f"residente_{id_residente}")
    os.makedirs(dest_folder, exist_ok=True)
    ext      = os.path.splitext(src_path)[1]
    filename = f"{campo}{ext}"
    dest     = os.path.join(dest_folder, filename)
    try:
        shutil.copy2(src_path, dest)
        return dest
    except Exception:
        return src_path


# ─────────────────────────────────────────────────────────────────────────────
#  PANTALLA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
class ResidentesScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._selected_id    = None
        self._selected_frame = None
        self._all_rows       = []
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
        ctk.CTkLabel(title_col, text="Residentes",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=CLR_TEXT).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Gestión de residentes del asilo",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")

        search_wrap = ctk.CTkFrame(bar, fg_color=CLR_BG, corner_radius=10,
                                   border_width=1, border_color=CLR_BORDER)
        search_wrap.grid(row=0, column=1, padx=16, pady=14, sticky="ew")
        search_wrap.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(search_wrap, text="🔍", font=ctk.CTkFont(size=13),
                     text_color=CLR_MUTED, width=30).grid(row=0, column=0, padx=(10,2), pady=9)
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        ctk.CTkEntry(search_wrap, textvariable=self.search_var,
                     placeholder_text="Buscar por nombre o CURP…",
                     fg_color="transparent", border_width=0,
                     text_color=CLR_TEXT, placeholder_text_color=CLR_MUTED,
                     font=ctk.CTkFont(size=12), height=34,
                     ).grid(row=0, column=1, sticky="ew", padx=(0,8))

        ctk.CTkButton(bar, text="＋  Nuevo residente",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=10, height=38, command=self._open_form,
                      ).grid(row=0, column=2, padx=(8,28), pady=14)

        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).grid(row=1, column=0, columnspan=3, sticky="ew")

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _build_stats(self):
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=1, column=0, sticky="ew", padx=24, pady=(18,0))
        sf.grid_columnconfigure((0,1,2), weight=1)
        self._stat_total = self._stat_card(sf, 0, "Total residentes", "0", "👥", CLR_SKY_DARK, "#dbeafe")
        self._stat_con   = self._stat_card(sf, 1, "Con habitación",   "0", "🏠", "#10b981",   "#d1fae5")
        self._stat_sin   = self._stat_card(sf, 2, "Sin habitación",   "0", "📋", CLR_AMBER,   CLR_AMBER_LIGHT)

    def _stat_card(self, parent, col, title, value, icon, ic, ib):
        card = ctk.CTkFrame(parent, fg_color=CLR_WHITE, corner_radius=14,
                            border_width=1, border_color=CLR_BORDER)
        card.grid(row=0, column=col, padx=6, sticky="ew")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=16)
        ib_f = ctk.CTkFrame(inner, fg_color=ib, corner_radius=10, width=44, height=44)
        ib_f.pack(side="left"); ib_f.pack_propagate(False)
        ctk.CTkLabel(ib_f, text=icon, font=ctk.CTkFont(size=20)).place(relx=.5, rely=.5, anchor="center")
        tc = ctk.CTkFrame(inner, fg_color="transparent")
        tc.pack(side="left", padx=(14,0))
        lbl = ctk.CTkLabel(tc, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=CLR_TEXT)
        lbl.pack(anchor="w")
        ctk.CTkLabel(tc, text=title, font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(anchor="w")
        return lbl

    # ── Tabla ─────────────────────────────────────────────────────────────────
    def _build_table_area(self):
        wrap = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=14,
                            border_width=1, border_color=CLR_BORDER)
        wrap.grid(row=2, column=0, sticky="nsew", padx=24, pady=16)
        wrap.grid_rowconfigure(1, weight=1)
        wrap.grid_columnconfigure(0, weight=1)

        HDR_COLS   = ["ID",  "Residente", "CURP",  "Edad", "Sangre", "Habitación", "Registro"]
        HDR_WIDTHS = [ 52,    190,         155,     52,     70,       115,           100      ]

        hdr = ctk.CTkFrame(wrap, fg_color=CLR_BG, corner_radius=0, height=40)
        hdr.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(hdr, text="", width=56).grid(row=0, column=0)

        for c, (col_name, w) in enumerate(zip(HDR_COLS, HDR_WIDTHS)):
            ctk.CTkLabel(hdr, text=col_name.upper(),
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=CLR_MUTED, width=w, anchor="w",
                         ).grid(row=0, column=c + 1, padx=(0, 4), pady=10, sticky="w")

        self._table = ctk.CTkScrollableFrame(wrap, fg_color=CLR_WHITE, corner_radius=0)
        self._table.grid(row=1, column=0, sticky="nsew")
        self._table.grid_columnconfigure(0, weight=1)
        self._build_action_bar(wrap)

    def _build_action_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=CLR_BG, corner_radius=0, height=52)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        ctk.CTkFrame(bar, fg_color=CLR_BORDER, height=1).place(relx=0, rely=0, relwidth=1)

        self._lbl_sel = ctk.CTkLabel(bar, text="Selecciona un residente para ver las acciones",
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

        self._btn_detail = ctk.CTkButton(bar, text="Ver detalle",
                                         fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                                         text_color=CLR_WHITE, font=ctk.CTkFont(size=12, weight="bold"),
                                         corner_radius=8, height=34, width=110,
                                         state="disabled", command=self._open_detail)
        self._btn_detail.pack(side="right", padx=4, pady=9)

    # ── Datos ─────────────────────────────────────────────────────────────────
    def _load_data(self):
        try:
            from modules.residentes import listar_residentes
            rows = listar_residentes()
        except Exception:
            rows = []
        self._all_rows = [dict(r) if hasattr(r, "keys") else r for r in rows]
        self._render_rows(self._all_rows)
        self._update_stats(self._all_rows)

    def _update_stats(self, rows):
        total = len(rows)
        con   = sum(1 for r in rows if (r.get("habitacion_numero") if isinstance(r, dict) else r[6]))
        self._stat_total.configure(text=str(total))
        self._stat_con.configure(text=str(con))
        self._stat_sin.configure(text=str(total - con))

    def _filter(self):
        q = self.search_var.get().strip().lower()
        filtered = self._all_rows if not q else [
            r for r in self._all_rows
            if q in str(r.get("nombre", "") if isinstance(r, dict) else r[1]).lower()
            or q in str(r.get("curp", "")   if isinstance(r, dict) else r[2]).lower()
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
            ctk.CTkLabel(e, text="🔍", font=ctk.CTkFont(size=32)).pack()
            ctk.CTkLabel(e, text="Sin resultados",
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=CLR_TEXT_SOFT).pack(pady=(6,2))
            ctk.CTkLabel(e, text="Intenta con otro término",
                         font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack()
            return

        for idx, row in enumerate(rows):
            if isinstance(row, dict):
                rid    = row.get("id_residente")
                nombre = row.get("nombre",         "—") or "—"
                curp   = row.get("curp",           "—") or "—"
                edad   = str(row.get("edad",       "—") or "—")
                sangre = row.get("tipo_sangre",    "—") or "—"
                hab    = row.get("habitacion_numero") or None
                fecha  = row.get("fecha_registro", "—") or "—"
            else:
                rid    = row[0]
                nombre = row[1] or "—"
                curp   = row[2] or "—"
                edad   = str(row[3] or "—")
                sangre = row[4] or "—"
                fecha  = row[5] or "—"
                hab    = row[6] if len(row) > 6 else None

            bg = CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT
            rf = ctk.CTkFrame(self._table, fg_color=bg, corner_radius=0, height=52)
            rf.grid(row=idx, column=0, sticky="ew")

            def _bind(w, r=rid, f=rf):
                w.bind("<Button-1>", lambda e, _r=r, _f=f: self._select(_r, _f))
                w.configure(cursor="hand2")

            av = ctk.CTkFrame(rf, fg_color=_avatar_color(nombre),
                              corner_radius=18, width=36, height=36)
            av.grid(row=0, column=0, padx=(14, 4), pady=8)
            av.grid_propagate(False)
            av_l = ctk.CTkLabel(av, text=_iniciales(nombre),
                                font=ctk.CTkFont(size=12, weight="bold"),
                                text_color=CLR_WHITE)
            av_l.place(relx=.5, rely=.5, anchor="center")
            _bind(av); _bind(av_l); _bind(rf)

            hab_txt   = f"Hab. {hab}" if hab else "Sin habitación"
            hab_color = CLR_MUTED if not hab else CLR_TEXT_SOFT

            datos_cols = [
                (str(rid),  52,    CLR_MUTED,      "center"),
                (nombre,    190,   CLR_TEXT,        "w"),
                (curp,      155,   CLR_TEXT_SOFT,   "w"),
                (edad,      52,    CLR_TEXT_SOFT,   "center"),
                (sangre,    70,    CLR_TEXT_SOFT,   "center"),
                (hab_txt,   115,   hab_color,       "w"),
                (fecha,     100,   CLR_MUTED,       "center"),
            ]

            for c, (val, w, color, anchor) in enumerate(datos_cols):
                lbl = ctk.CTkLabel(rf, text=val,
                                   font=ctk.CTkFont(size=12),
                                   text_color=color,
                                   width=w, anchor=anchor)
                lbl.grid(row=0, column=c + 1, padx=(0, 4), sticky="w")
                _bind(lbl)

    # ── Selección ─────────────────────────────────────────────────────────────
    def _select(self, rid, frame):
        if self._selected_frame:
            children = list(self._table.winfo_children())
            if self._selected_frame in children:
                idx = children.index(self._selected_frame)
                self._selected_frame.configure(fg_color=CLR_WHITE if idx % 2 == 0 else CLR_ROW_ALT)
        frame.configure(fg_color=CLR_SKY_LIGHT)
        self._selected_id    = rid
        self._selected_frame = frame
        self._set_actions(True)
        self._lbl_sel.configure(
            text=f"Residente seleccionado — ID {rid}",
            text_color=CLR_SKY_XDARK)

    def _set_actions(self, on):
        s = "normal" if on else "disabled"
        for b in (self._btn_detail, self._btn_edit, self._btn_del):
            b.configure(state=s)

    # ── Formulario WIZARD ─────────────────────────────────────────────────────
    def _open_form(self, datos_edicion=None):
        edit = datos_edicion is not None
        win  = ctk.CTkToplevel(self)
        win.title("Nuevo residente" if not edit else "Editar residente")
        win.grab_set()
        _center(win, 680, 600)
        win.configure(fg_color=CLR_SKY_XLIGHT)
        win.resizable(False, False)

        entries   = {}
        img_paths = {}
        hab_var   = ctk.IntVar(value=0)
        _tipo_map_inv = {"2":"Doble","3":"Triple","4":"Cuádruple"}
        _tipo_inicial = ""
        if edit and datos_edicion.get("habitacion_tipo"):
            _tipo_inicial = _tipo_map_inv.get(str(datos_edicion["habitacion_tipo"]), "")
        tipo_var = ctk.StringVar(value=_tipo_inicial)

        STEPS = [
            ("👤", "Datos personales"),
            ("🏠", "Habitación"),
            ("👨\u200d👩\u200d👧", "Familiar"),
            ("📄", "Documentos"),
        ]
        step_state = {"current": 0}

        progress_bar = ctk.CTkFrame(win, fg_color=CLR_WHITE, corner_radius=0, height=72)
        progress_bar.pack(fill="x")
        progress_bar.pack_propagate(False)
        progress_bar.grid_columnconfigure(tuple(range(len(STEPS))), weight=1)

        step_widgets = []
        for i, (icon, title) in enumerate(STEPS):
            col_frame = ctk.CTkFrame(progress_bar, fg_color="transparent")
            col_frame.grid(row=0, column=i, sticky="nsew", padx=0)
            if i > 0:
                line = ctk.CTkFrame(col_frame, fg_color=CLR_BORDER, height=2, width=40)
                line.place(relx=0, rely=0.38, anchor="w", x=0)
            else:
                line = None
            inner = ctk.CTkFrame(col_frame, fg_color="transparent")
            inner.pack(expand=True, anchor="center", pady=12)
            circle = ctk.CTkFrame(inner, fg_color=CLR_BORDER, corner_radius=20, width=36, height=36)
            circle.pack()
            circle.pack_propagate(False)
            c_lbl = ctk.CTkLabel(circle, text=icon, font=ctk.CTkFont(size=16))
            c_lbl.place(relx=.5, rely=.5, anchor="center")
            t_lbl = ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=10), text_color=CLR_MUTED)
            t_lbl.pack(pady=(3,0))
            step_widgets.append((circle, c_lbl, t_lbl, line))

        ctk.CTkFrame(win, fg_color=CLR_BORDER, height=1).pack(fill="x")
        content_area = ctk.CTkFrame(win, fg_color=CLR_WHITE, corner_radius=0)
        content_area.pack(fill="both", expand=True)
        ctk.CTkFrame(win, fg_color=CLR_BORDER, height=1).pack(fill="x")
        nav_bar = ctk.CTkFrame(win, fg_color=CLR_WHITE, height=56, corner_radius=0)
        nav_bar.pack(fill="x")
        nav_bar.pack_propagate(False)
        nav_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(nav_bar, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=8, height=36, width=110,
                      command=win.destroy).grid(row=0, column=0, padx=(16,8), pady=10)

        step_lbl = ctk.CTkLabel(nav_bar, text="Paso 1 de 4",
                                font=ctk.CTkFont(size=11), text_color=CLR_MUTED)
        step_lbl.grid(row=0, column=1)

        btn_back = ctk.CTkButton(nav_bar, text="← Atrás",
                                 fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
                                 text_color=CLR_SKY_XDARK,
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 corner_radius=8, height=36, width=110,
                                 border_width=1, border_color="#7dd3fc")
        btn_back.grid(row=0, column=2, padx=(8,4), pady=10)

        btn_next = ctk.CTkButton(nav_bar, text="Siguiente →",
                                 fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                                 text_color=CLR_WHITE,
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 corner_radius=8, height=36, width=130)
        btn_next.grid(row=0, column=3, padx=(4,16), pady=10)

        pages = []

        # ── Página 1: Datos personales ─────────────────────────────────────
        p1  = ctk.CTkFrame(content_area, fg_color="transparent")
        sc1 = ctk.CTkScrollableFrame(p1, fg_color="transparent", height=380)
        sc1.pack(fill="both", expand=True, padx=20, pady=10)
        sc1.grid_columnconfigure((0,1), weight=1)

        for label, key, row, col in [
            ("Nombre completo", "nombre",      0, 0),
            ("CURP",            "curp",        0, 1),
            ("Edad",            "edad",        1, 0),
            ("Tipo de sangre",  "tipo_sangre", 1, 1),
            ("Complexión",      "complexion",  2, 0),
            ("Color de ojos",   "color_ojos",  2, 1),
            ("Tipo de nariz",   "tipo_nariz",  3, 0),
            ("Tez / Piel",      "tez_piel",    3, 1),
            ("Tipo de ceja",    "tipo_ceja",   4, 0),
        ]:
            grp = ctk.CTkFrame(sc1, fg_color="transparent")
            grp.grid(row=row, column=col, padx=(0, 10 if col==0 else 0), pady=4, sticky="ew")
            ctk.CTkLabel(grp, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0,2))
            e = ctk.CTkEntry(grp, fg_color=CLR_BG, border_color=CLR_BORDER,
                             text_color=CLR_TEXT, height=34, corner_radius=8)
            e.pack(fill="x")
            if edit and datos_edicion.get(key):
                e.insert(0, str(datos_edicion[key]))
            entries[key] = e

        for label, key, row, col in [
            ("Cartilla de salud",           "cartilla_salud",              5, 0),
            ("Comprobante servicio médico", "comprobante_servicio_medico", 5, 1),
        ]:
            grp = ctk.CTkFrame(sc1, fg_color="transparent")
            grp.grid(row=row, column=col, padx=(0, 10 if col==0 else 0), pady=4, sticky="ew")
            ctk.CTkLabel(grp, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0,2))
            var = ctk.StringVar(value=datos_edicion.get(key,"") if edit else "")
            img_paths[key] = var
            _make_file_row(grp, var, win)
        pages.append(p1)

        # ── Página 2: Habitación ───────────────────────────────────────────
        p2 = ctk.CTkFrame(content_area, fg_color="transparent")
        ctk.CTkLabel(p2, text="Selecciona el tipo de habitación",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=CLR_TEXT
                     ).pack(anchor="w", padx=24, pady=(16,6))

        tipo_btn_frame = ctk.CTkFrame(p2, fg_color="transparent")
        tipo_btn_frame.pack(fill="x", padx=24)
        tipo_btns = {}
        for tipo in ["Doble","Triple","Cuádruple"]:
            b = ctk.CTkButton(tipo_btn_frame, text=tipo,
                              fg_color=CLR_BG, hover_color=CLR_SKY_LIGHT,
                              text_color=CLR_TEXT_SOFT, font=ctk.CTkFont(size=12, weight="bold"),
                              corner_radius=10, height=38, border_width=2, border_color=CLR_BORDER)
            b.pack(side="left", padx=(0,8))
            tipo_btns[tipo] = b

        ctk.CTkLabel(p2, text="Habitaciones disponibles",
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=CLR_TEXT_SOFT
                     ).pack(anchor="w", padx=24, pady=(14,4))

        hab_list = ctk.CTkScrollableFrame(p2, fg_color=CLR_BG, corner_radius=10,
                                          border_width=1, border_color=CLR_BORDER, height=260)
        hab_list.pack(fill="x", padx=24, pady=(0,8))
        hab_list.grid_columnconfigure(0, weight=1)
        hab_labels = {}

        # Capacidad máxima por tipo de habitación
        CAPACIDAD_TIPO = {"2": 2, "3": 3, "4": 4}

        def _get_ocupacion_habitacion(hab_id):
            """Retorna cuántos residentes tiene actualmente la habitación."""
            try:
                from db.connection import get_connection as _gc
                conn = _gc()
                row = conn.execute(
                    "SELECT COUNT(*) FROM residentes WHERE habitacion_id = ?",
                    (hab_id,)
                ).fetchone()
                conn.close()
                return row[0] if row else 0
            except Exception:
                return 0

        def _set_tipo(t):
            tipo_var.set(t)
            for name, btn in tipo_btns.items():
                btn.configure(fg_color=CLR_SKY_DARK if name==t else CLR_BG,
                              text_color=CLR_WHITE if name==t else CLR_TEXT_SOFT,
                              border_color=CLR_SKY_DARK if name==t else CLR_BORDER)
            _load_habs()

        def _load_habs():
            for w in hab_list.winfo_children():
                w.destroy()
            hab_labels.clear()
            tipo_sel = tipo_var.get()
            try:
                tipo_map = {"Doble":"2","Triple":"3","Cuádruple":"4"}
                tipo_key = tipo_map.get(tipo_sel, tipo_sel)
                if tipo_sel:
                    from modules.habitaciones import listar_habitaciones_por_tipo
                    rows = listar_habitaciones_por_tipo(tipo_key)
                else:
                    from modules.habitaciones import listar_habitaciones
                    rows = listar_habitaciones()
            except Exception:
                rows = []

            if not rows:
                ctk.CTkLabel(hab_list,
                             text="No hay habitaciones disponibles" if tipo_sel else "Selecciona un tipo primero",
                             font=ctk.CTkFont(size=12), text_color=CLR_MUTED).pack(pady=24)
                return

            tipo_nombres = {"2":"Doble","3":"Triple","4":"Cuádruple"}

            # ── CAMBIO: filtrar habitaciones llenas ────────────────────────
            # Al editar, excluimos al propio residente del conteo de su habitación actual
            id_res_actual = datos_edicion.get("id_residente") if edit else None
            hab_actual    = datos_edicion.get("habitacion_id") if edit else None

            filas_disponibles = []
            for r in rows:
                hid, numero, tipo = r[0], r[1], r[2]
                capacidad  = CAPACIDAD_TIPO.get(str(tipo), 99)
                ocupacion  = _get_ocupacion_habitacion(hid)

                # Si estamos editando y este es el cuarto actual del residente,
                # descontamos 1 porque él ya ocupa un lugar
                if edit and hid == hab_actual:
                    ocupacion = max(0, ocupacion - 1)

                if ocupacion < capacidad:
                    filas_disponibles.append((hid, numero, tipo, ocupacion, capacidad))

            if not filas_disponibles:
                ctk.CTkLabel(hab_list,
                             text="No hay habitaciones con espacio disponible",
                             font=ctk.CTkFont(size=12), text_color=CLR_MUTED).pack(pady=24)
                return

            for hid, numero, tipo, ocupacion, capacidad in filas_disponibles:
                t_nombre = tipo_nombres.get(str(tipo), str(tipo))
                lugares_libres = capacidad - ocupacion

                card = ctk.CTkFrame(hab_list, fg_color=CLR_WHITE, corner_radius=10,
                                    border_width=2, border_color=CLR_BORDER)
                card.grid(sticky="ew", padx=4, pady=3)
                card.grid_columnconfigure(2, weight=1)
                radio = ctk.CTkRadioButton(card, text="", variable=hab_var, value=hid,
                                           fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK, width=20)
                radio.grid(row=0, column=0, padx=(12,0), pady=10)
                icon_b = ctk.CTkFrame(card, fg_color="#dbeafe", corner_radius=8, width=34, height=34)
                icon_b.grid(row=0, column=1, padx=8, pady=8)
                icon_b.grid_propagate(False)
                ctk.CTkLabel(icon_b, text="🏠", font=ctk.CTkFont(size=15)
                             ).place(relx=.5, rely=.5, anchor="center")
                ctk.CTkLabel(card, text=f"Habitación #{numero}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=CLR_TEXT).grid(row=0, column=2, sticky="w", padx=4)

                # Mostrar tipo + lugares disponibles
                info_txt = f"{t_nombre}  ·  {lugares_libres} lugar{'es' if lugares_libres != 1 else ''} libre{'s' if lugares_libres != 1 else ''}"
                ctk.CTkLabel(card, text=info_txt, font=ctk.CTkFont(size=11),
                             text_color=CLR_MUTED).grid(row=0, column=3, padx=(0,14))
                hab_labels[hid] = card

                def _sel(h=hid):
                    hab_var.set(h)
                    for k2, c2 in hab_labels.items():
                        c2.configure(border_color=CLR_SKY_DARK if k2==h else CLR_BORDER)

                for w in [card, radio]:
                    w.bind("<Button-1>", lambda e, h=hid: _sel(h))
                    w.configure(cursor="hand2")

            if edit and datos_edicion.get("habitacion_id"):
                hid_cur = datos_edicion["habitacion_id"]
                hab_var.set(hid_cur)
                if hid_cur in hab_labels:
                    hab_labels[hid_cur].configure(border_color=CLR_SKY_DARK)

        for t in ["Doble","Triple","Cuádruple"]:
            tipo_btns[t].configure(command=lambda t=t: _set_tipo(t))
        if edit and _tipo_inicial:
            _set_tipo(_tipo_inicial)
        pages.append(p2)

        # ── Página 3: Familiar ─────────────────────────────────────────────
        p3  = ctk.CTkFrame(content_area, fg_color="transparent")
        sc3 = ctk.CTkScrollableFrame(p3, fg_color="transparent", height=380)
        sc3.pack(fill="both", expand=True, padx=20, pady=10)
        sc3.grid_columnconfigure((0,1), weight=1)

        for label, key, row, col in [
            ("Nombre del familiar", "fam_nombre",   0, 0),
            ("Teléfono",            "fam_telefono", 0, 1),
        ]:
            grp = ctk.CTkFrame(sc3, fg_color="transparent")
            grp.grid(row=row, column=col, padx=(0, 10 if col==0 else 0), pady=4, sticky="ew")
            ctk.CTkLabel(grp, text=label, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0,2))
            e = ctk.CTkEntry(grp, fg_color=CLR_BG, border_color=CLR_BORDER,
                             text_color=CLR_TEXT, height=34, corner_radius=8)
            e.pack(fill="x")
            if edit:
                fk  = "familiar_nombre" if key=="fam_nombre" else "familiar_telefono"
                val = datos_edicion.get(fk,"") or ""
                if val: e.insert(0, str(val))
            entries[key] = e

        grp_ine = ctk.CTkFrame(sc3, fg_color="transparent")
        grp_ine.grid(row=1, column=0, columnspan=2, pady=4, sticky="ew")
        ctk.CTkLabel(grp_ine, text="Foto INE del familiar",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=CLR_TEXT_SOFT).pack(anchor="w", pady=(0,2))
        _fam_ine_val = ""
        if edit:
            _fam_ine_val = (datos_edicion.get("familiar_foto_ine") or
                            datos_edicion.get("fam_foto_ine") or "")
        fam_ine_var = ctk.StringVar(value=_fam_ine_val)
        img_paths["fam_foto_ine"] = fam_ine_var
        _make_file_row(grp_ine, fam_ine_var, win)
        pages.append(p3)

        # ── Página 4: Documentos ───────────────────────────────────────────
        p4  = ctk.CTkFrame(content_area, fg_color="transparent")
        sc4 = ctk.CTkScrollableFrame(p4, fg_color="transparent", height=380)
        sc4.pack(fill="both", expand=True, padx=20, pady=10)
        sc4.grid_columnconfigure(0, weight=1)

        for i, (label, key) in enumerate([
            ("Foto INE del residente",        "foto_ine"),
            ("Foto comprobante de domicilio", "foto_comprobante_domicilio"),
            ("Foto acta de nacimiento",       "foto_acta_nacimiento"),
        ]):
            grp = ctk.CTkFrame(sc4, fg_color=CLR_WHITE, corner_radius=10,
                               border_width=1, border_color=CLR_BORDER)
            grp.grid(row=i, column=0, sticky="ew", pady=5)
            ctk.CTkLabel(grp, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=CLR_TEXT_SOFT).pack(anchor="w", padx=14, pady=(10,4))
            var = ctk.StringVar(value=datos_edicion.get(key,"") if edit else "")
            img_paths[key] = var
            _make_file_row(grp, var, win, padx=14, pady_bottom=10)
        pages.append(p4)

        # ── Navegación ─────────────────────────────────────────────────────
        def _update_ui():
            i = step_state["current"]
            for j, page in enumerate(pages):
                if j == i: page.pack(fill="both", expand=True)
                else:      page.pack_forget()
            step_lbl.configure(text=f"Paso {i+1} de {len(STEPS)}")
            for j, (circle, c_lbl, t_lbl, line) in enumerate(step_widgets):
                if j < i:
                    circle.configure(fg_color=CLR_GREEN)
                    c_lbl.configure(text="✓", text_color=CLR_WHITE)
                    t_lbl.configure(text_color=CLR_GREEN)
                elif j == i:
                    circle.configure(fg_color=CLR_SKY_DARK)
                    c_lbl.configure(text=STEPS[j][0], text_color=CLR_WHITE)
                    t_lbl.configure(text_color=CLR_SKY_DARK, font=ctk.CTkFont(size=10, weight="bold"))
                else:
                    circle.configure(fg_color=CLR_BORDER)
                    c_lbl.configure(text=STEPS[j][0], text_color=CLR_MUTED)
                    t_lbl.configure(text_color=CLR_MUTED, font=ctk.CTkFont(size=10))
            btn_back.configure(state="normal" if i > 0 else "disabled")
            if i == len(STEPS) - 1:
                btn_next.configure(text="💾  Guardar", fg_color="#16a34a",
                                   hover_color="#15803d", command=_save)
            else:
                btn_next.configure(text="Siguiente →", fg_color=CLR_SKY_DARK,
                                   hover_color=CLR_SKY_XDARK, command=_go_next)

        def _validate_step(i):
            if i == 0:
                for entry, label in [
                    (entries.get("nombre"),      "Nombre completo"),
                    (entries.get("curp"),         "CURP"),
                    (entries.get("edad"),         "Edad"),
                    (entries.get("tipo_sangre"),  "Tipo de sangre"),
                    (entries.get("complexion"),   "Complexión"),
                    (entries.get("color_ojos"),   "Color de ojos"),
                    (entries.get("tipo_nariz"),   "Tipo de nariz"),
                    (entries.get("tez_piel"),     "Tez / Piel"),
                    (entries.get("tipo_ceja"),    "Tipo de ceja"),
                ]:
                    if not entry or not entry.get().strip():
                        return False, f"El campo '{label}' es obligatorio"
                for key, label in [
                    ("cartilla_salud",              "Cartilla de salud"),
                    ("comprobante_servicio_medico", "Comprobante servicio médico"),
                ]:
                    if not img_paths.get(key, ctk.StringVar()).get().strip():
                        return False, f"'{label}' es obligatorio"
                return True, ""
            elif i == 1:
                if not hab_var.get():
                    return False, "Debes seleccionar una habitación"
                return True, ""
            elif i == 2:
                if not entries.get("fam_nombre") or not entries["fam_nombre"].get().strip():
                    return False, "El nombre del familiar es obligatorio"
                if not entries.get("fam_telefono") or not entries["fam_telefono"].get().strip():
                    return False, "El teléfono del familiar es obligatorio"
                if not img_paths.get("fam_foto_ine", ctk.StringVar()).get().strip():
                    return False, "La foto INE del familiar es obligatoria"
                return True, ""
            elif i == 3:
                for key, label in [
                    ("foto_ine",                   "Foto INE del residente"),
                    ("foto_comprobante_domicilio",  "Comprobante de domicilio"),
                    ("foto_acta_nacimiento",        "Acta de nacimiento"),
                ]:
                    if not img_paths.get(key, ctk.StringVar()).get().strip():
                        return False, f"'{label}' es obligatoria"
                return True, ""
            return True, ""

        def _show_alert(msg):
            alert = ctk.CTkToplevel(win)
            alert.title("")
            alert.grab_set()
            alert.configure(fg_color=CLR_WHITE)
            alert.resizable(False, False)
            _center(alert, 360, 180)
            ctk.CTkLabel(alert, text="⚠️", font=ctk.CTkFont(size=36)).pack(pady=(18,4))
            ctk.CTkLabel(alert, text="Campo requerido",
                         font=ctk.CTkFont(size=14, weight="bold"), text_color=CLR_TEXT).pack()
            ctk.CTkLabel(alert, text=msg, font=ctk.CTkFont(size=11),
                         text_color=CLR_TEXT_SOFT, wraplength=300).pack(pady=(4,0))
            ctk.CTkButton(alert, text="Entendido",
                          fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                          text_color=CLR_WHITE, corner_radius=8, height=36,
                          command=alert.destroy).pack(padx=40, pady=14, fill="x")

        def _go_next():
            ok, msg = _validate_step(step_state["current"])
            if not ok: _show_alert(msg); return
            step_state["current"] += 1
            _update_ui()

        def _go_back():
            step_state["current"] = max(0, step_state["current"] - 1)
            _update_ui()

        def _save():
            ok, msg = _validate_step(step_state["current"])
            if not ok: _show_alert(msg); return
            datos_res = {k: e.get().strip() for k, e in entries.items()
                         if k not in ("fam_nombre","fam_telefono") and e.get().strip()}
            datos_res["fecha_registro"] = date.today().isoformat()
            if hab_var.get():
                datos_res["habitacion_id"] = hab_var.get()

            # ── CAMBIO: al crear, primero insertamos sin archivos para obtener el ID real,
            #    luego movemos los archivos a uploads/residente_<id> y actualizamos rutas ──
            try:
                fam_nombre  = entries["fam_nombre"].get().strip()
                id_familiar = datos_edicion.get("id_familiar") if edit else None
                fam_datos   = {"nombre": fam_nombre}
                tel = entries["fam_telefono"].get().strip()
                if tel: fam_datos["telefono"] = tel

                from db.connection import get_connection
                conn = get_connection()
                if id_familiar:
                    sets = ", ".join(f"{k}=?" for k in fam_datos)
                    conn.execute(f"UPDATE familiares SET {sets} WHERE id_familiar=?",
                                 list(fam_datos.values()) + [id_familiar])
                else:
                    cur = conn.execute(
                        f"INSERT INTO familiares ({','.join(fam_datos)}) VALUES ({','.join(['?']*len(fam_datos))})",
                        list(fam_datos.values()))
                    id_familiar = cur.lastrowid
                conn.commit()
                conn.close()

                if id_familiar:
                    datos_res["id_familiar"] = id_familiar

                if edit:
                    # En edición conocemos el ID desde el principio
                    id_res = str(datos_edicion["id_residente"])
                    fam_ine = img_paths.get("fam_foto_ine")
                    if fam_ine and fam_ine.get():
                        fam_datos["foto_ine"] = _save_file(fam_ine.get(), id_res, "familiar_foto_ine")
                        # Actualizar foto_ine del familiar
                        conn2 = get_connection()
                        conn2.execute("UPDATE familiares SET foto_ine=? WHERE id_familiar=?",
                                      (fam_datos["foto_ine"], id_familiar))
                        conn2.commit()
                        conn2.close()

                    for key, var in img_paths.items():
                        if var.get() and key != "fam_foto_ine":
                            saved = _save_file(var.get(), id_res, key)
                            if saved: datos_res[key] = saved

                    from modules.residentes import actualizar_residente
                    actualizar_residente(datos_edicion["id_residente"], datos_res)
                    self._toast("Residente actualizado")

                else:
                    # Crear sin archivos primero para obtener el ID real
                    from modules.residentes import crear_residente, actualizar_residente
                    id_nuevo = crear_residente(datos_res)

                    # Ahora guardar archivos con el ID real y actualizar registros
                    id_res = str(id_nuevo)
                    rutas_archivos = {}

                    fam_ine = img_paths.get("fam_foto_ine")
                    if fam_ine and fam_ine.get():
                        ruta_fam = _save_file(fam_ine.get(), id_res, "familiar_foto_ine")
                        conn3 = get_connection()
                        conn3.execute("UPDATE familiares SET foto_ine=? WHERE id_familiar=?",
                                      (ruta_fam, id_familiar))
                        conn3.commit()
                        conn3.close()

                    for key, var in img_paths.items():
                        if var.get() and key != "fam_foto_ine":
                            saved = _save_file(var.get(), id_res, key)
                            if saved: rutas_archivos[key] = saved

                    if rutas_archivos:
                        actualizar_residente(id_nuevo, rutas_archivos)

                    self._toast("Residente creado")

                win.destroy()
                self._load_data()
            except Exception as ex:
                self._toast(f"Error: {ex}", error=True)

        btn_back.configure(command=_go_back)
        btn_next.configure(command=_go_next)
        _update_ui()

    def _open_edit(self):
        if not self._selected_id: return
        try:
            from modules.residentes import obtener_residente
            r = obtener_residente(self._selected_id)
            if r: self._open_form(datos_edicion=dict(r))
        except Exception as ex:
            self._toast(f"Error: {ex}", error=True)

    # ── Detalle ───────────────────────────────────────────────────────────────
    def _open_detail(self):
        if not self._selected_id: return
        try:
            from modules.residentes import obtener_residente
            r = dict(obtener_residente(self._selected_id) or {})
        except Exception as ex:
            self._toast(f"Error: {ex}", error=True); return

        win = ctk.CTkToplevel(self)
        win.title("Detalle del residente")
        win.grab_set()
        _center(win, 520, 640)
        win.configure(fg_color=CLR_SKY_XLIGHT)

        nombre = r.get("nombre","—")
        top = ctk.CTkFrame(win, fg_color=CLR_WHITE, corner_radius=0, height=90)
        top.pack(fill="x"); top.pack_propagate(False)
        av = ctk.CTkFrame(top, fg_color=_avatar_color(nombre), corner_radius=28, width=56, height=56)
        av.place(x=24, rely=.5, anchor="w"); av.pack_propagate(False)
        ctk.CTkLabel(av, text=_iniciales(nombre),
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=CLR_WHITE).place(relx=.5, rely=.5, anchor="center")
        ctk.CTkLabel(top, text=nombre,
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=CLR_TEXT).place(x=96, y=22)
        ctk.CTkLabel(top, text=f"ID {r.get('id_residente')}  ·  Reg: {r.get('fecha_registro','—')}",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).place(x=96, y=52)

        scroll = ctk.CTkScrollableFrame(win, fg_color=CLR_SKY_XLIGHT)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        sections = [
            ("Datos personales", [
                ("CURP","curp"),("Edad","edad"),("Complexión","complexion"),
                ("Color de ojos","color_ojos"),("Tipo de nariz","tipo_nariz"),
                ("Tez / Piel","tez_piel"),("Tipo de ceja","tipo_ceja"),
                ("Tipo de sangre","tipo_sangre"),
            ]),
            ("Habitación", [("Número","habitacion_numero"),("Tipo","habitacion_tipo")]),
            ("Familiar",   [("Nombre","familiar_nombre"),("Teléfono","familiar_telefono")]),
            ("Documentos", [
                ("Cartilla salud","cartilla_salud"),
                ("Comprobante médico","comprobante_servicio_medico"),
                ("Foto INE","foto_ine"),
                ("Comprobante domicilio","foto_comprobante_domicilio"),
                ("Acta de nacimiento","foto_acta_nacimiento"),
            ]),
        ]
        for sec_title, fields in sections:
            ctk.CTkLabel(scroll, text=sec_title,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=CLR_SKY_XDARK).pack(anchor="w", padx=4, pady=(10,4))
            for label, key in fields:
                row_f = ctk.CTkFrame(scroll, fg_color=CLR_WHITE, corner_radius=8,
                                     border_width=1, border_color=CLR_BORDER)
                row_f.pack(fill="x", pady=2)
                ctk.CTkLabel(row_f, text=label, font=ctk.CTkFont(size=10, weight="bold"),
                             text_color=CLR_MUTED, width=160, anchor="w"
                             ).pack(side="left", padx=(14,0), pady=8)
                val = str(r.get(key) or "—")
                if val != "—" and ("/" in val or "\\" in val):
                    val = "✅ " + os.path.basename(val)
                ctk.CTkLabel(row_f, text=val, font=ctk.CTkFont(size=12),
                             text_color=CLR_TEXT_SOFT, anchor="w").pack(side="left", padx=8)

        ctk.CTkButton(win, text="Cerrar",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, corner_radius=10, height=40,
                      command=win.destroy).pack(padx=20, pady=(0,16), fill="x")

    # ── Eliminar ──────────────────────────────────────────────────────────────
    def _confirm_delete(self):
        if not self._selected_id: return
        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.grab_set()
        dialog.configure(fg_color=CLR_WHITE)
        dialog.resizable(False, False)
        _center(dialog, 380, 200)
        ctk.CTkLabel(dialog, text="⚠️", font=ctk.CTkFont(size=36)).pack(pady=(24,4))
        ctk.CTkLabel(dialog, text="¿Eliminar este residente?",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text="Esta acción es permanente.",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4,0))
        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=20, padx=24, fill="x")

        def _do():
            try:
                from modules.residentes import eliminar_residente
                eliminar_residente(self._selected_id)

                # ── CAMBIO: eliminar carpeta de imágenes con nombre correcto ──
                carpeta = os.path.join("uploads", f"residente_{self._selected_id}")
                if os.path.isdir(carpeta):
                    shutil.rmtree(carpeta)

                self._toast("Residente eliminado")
                dialog.destroy()
                self._selected_id = None; self._selected_frame = None
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
        x = self.winfo_rootx() + self.winfo_width()  - 320
        y = self.winfo_rooty() + self.winfo_height() - 72
        t.geometry(f"300x48+{x}+{y}")
        ctk.CTkLabel(t, text=("❌  " if error else "✅  ") + msg,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_WHITE).pack(fill="both", expand=True, padx=14)
        t.after(2800, t.destroy)


# ── Widget reutilizable: fila para seleccionar archivo ────────────────────────
def _make_file_row(parent, var: ctk.StringVar, win, padx=0, pady_bottom=0):
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=padx, pady=(0, pady_bottom))
    row.grid_columnconfigure(0, weight=1)

    entry = ctk.CTkEntry(row, textvariable=var,
                         fg_color=CLR_WHITE, border_color=CLR_BORDER,
                         text_color=CLR_TEXT_SOFT, height=34, corner_radius=8,
                         placeholder_text="Sin archivo seleccionado",
                         placeholder_text_color=CLR_MUTED,
                         state="readonly")
    entry.grid(row=0, column=0, sticky="ew", padx=(0,6))

    def _pick():
        path = _pick_file(win)
        if path:
            var.set(path)
            entry.configure(text_color=CLR_TEXT)

    ctk.CTkButton(row, text="📁  Elegir",
                  fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
                  text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=11, weight="bold"),
                  corner_radius=8, height=34, width=90,
                  border_width=1, border_color="#7dd3fc",
                  command=_pick).grid(row=0, column=1)