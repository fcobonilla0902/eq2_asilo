"""
Pantalla de gestión de usuarios (solo rol admin).
"""
import customtkinter as ctk

CLR_SKY_DARK   = "#0ea5e9"
CLR_SKY_XDARK  = "#0284c7"
CLR_SKY_XLIGHT = "#f0f9ff"
CLR_SKY_LIGHT  = "#e0f2fe"
CLR_WHITE      = "#ffffff"
CLR_BORDER     = "#e2e8f0"
CLR_TEXT       = "#0f172a"
CLR_TEXT_SOFT  = "#334155"
CLR_MUTED      = "#94a3b8"
CLR_RED        = "#ef4444"
CLR_RED_LIGHT  = "#fee2e2"
CLR_GREEN      = "#22c55e"
CLR_GREEN_LIGHT= "#dcfce7"

ROL_COLOR = {
    "admin":     ("#dbeafe", "#1d4ed8"),
    "enfermero": ("#d1fae5", "#065f46"),
    "doctor":    ("#fef3c7", "#92400e"),
}
ROL_ICON = {"admin": "🛡️", "enfermero": "💉", "doctor": "🩺"}
AVATAR_COLORS = ["#6366f1","#8b5cf6","#ec4899","#0ea5e9","#14b8a6","#22c55e","#f59e0b"]

def _iniciales(n):
    p = (n or "?").strip().split()
    return "".join(x[0].upper() for x in p[:2]) if p else "?"

def _avatar_color(n):
    return AVATAR_COLORS[sum(ord(c) for c in (n or "A")) % len(AVATAR_COLORS)]


class UsuariosScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build()
        self._load_data()

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=0,
                           border_width=0, height=72)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.grid(row=0, column=0, padx=28, pady=16, sticky="w")
        ctk.CTkLabel(left, text="🔒  Gestión de Usuarios",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=CLR_TEXT).pack(side="left")
        ctk.CTkLabel(left, text="Solo administradores",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(
                         side="left", padx=(10, 0), pady=(4, 0))

        ctk.CTkButton(hdr, text="＋  Nuevo usuario",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=36, corner_radius=10,
                      command=self._dialog_nuevo).grid(row=0, column=2, padx=24, pady=18)

        # ── Tabla ─────────────────────────────────────────────────────────────
        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=CLR_WHITE, corner_radius=12,
            border_width=1, border_color=CLR_BORDER)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)

        self.table_frame.grid_columnconfigure(0, weight=0, minsize=46)
        self.table_frame.grid_columnconfigure(1, weight=1)
        self.table_frame.grid_columnconfigure(2, weight=2)
        self.table_frame.grid_columnconfigure(3, weight=1)
        self.table_frame.grid_columnconfigure(4, weight=1)
        self.table_frame.grid_columnconfigure(5, weight=3, minsize=380)

        headers = ["", "Usuario", "Nombre", "Rol", "Estado", "Acciones"]
        for c, h in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=h,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_MUTED,
                         anchor="w" if c > 0 else "center").grid(
                             row=0, column=c, padx=12, pady=(14, 8), sticky="w")

    def _load_data(self):
        from modules.auth import listar_usuarios
        for w in self.table_frame.winfo_children():
            info = w.grid_info()
            if info and int(info.get("row", 0)) > 0:
                w.destroy()

        usuarios = listar_usuarios()
        for i, u in enumerate(usuarios):
            row = i + 1

            av_frame = ctk.CTkFrame(self.table_frame, fg_color=_avatar_color(u["nombre"]),
                                    corner_radius=20, width=34, height=34)
            av_frame.grid(row=row, column=0, padx=12, pady=6)
            av_frame.grid_propagate(False)
            ctk.CTkLabel(av_frame, text=_iniciales(u["nombre"]),
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=CLR_WHITE).place(relx=.5, rely=.5, anchor="center")

            ctk.CTkLabel(self.table_frame, text=u["usuario"],
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=CLR_TEXT, anchor="w").grid(
                             row=row, column=1, padx=8, pady=6, sticky="w")

            ctk.CTkLabel(self.table_frame, text=u["nombre"],
                         font=ctk.CTkFont(size=12), text_color=CLR_TEXT_SOFT,
                         anchor="w").grid(row=row, column=2, padx=8, pady=6, sticky="w")

            rbg, rtxt = ROL_COLOR.get(u["rol"], ("#f1f5f9", "#475569"))
            rol_badge = ctk.CTkFrame(self.table_frame, fg_color=rbg, corner_radius=6, height=24)
            rol_badge.grid(row=row, column=3, padx=8, pady=6, sticky="w")
            ctk.CTkLabel(rol_badge,
                         text=f"{ROL_ICON.get(u['rol'],'')}  {u['rol'].capitalize()}",
                         font=ctk.CTkFont(size=11), text_color=rtxt).pack(padx=8, pady=2)

            activo = bool(u["activo"])
            sbg = CLR_GREEN_LIGHT if activo else CLR_RED_LIGHT
            stxt = CLR_GREEN if activo else CLR_RED
            est_badge = ctk.CTkFrame(self.table_frame, fg_color=sbg, corner_radius=6, height=24)
            est_badge.grid(row=row, column=4, padx=8, pady=6, sticky="w")
            ctk.CTkLabel(est_badge, text="Activo" if activo else "Inactivo",
                         font=ctk.CTkFont(size=11), text_color=stxt).pack(padx=8, pady=2)

            acc = ctk.CTkFrame(self.table_frame, fg_color="transparent")
            acc.grid(row=row, column=5, padx=8, pady=6, sticky="w")

            uid = u["id"]
            ctk.CTkButton(acc, text="✏️ Editar", width=78, height=28, corner_radius=6,
                          fg_color="#f1f5f9", hover_color="#e2e8f0",
                          text_color=CLR_TEXT_SOFT, font=ctk.CTkFont(size=11),
                          command=lambda i=uid: self._dialog_editar(i)).pack(side="left", padx=(0, 4))

            ctk.CTkButton(acc, text="🔑 Password", width=90, height=28, corner_radius=6,
                          fg_color=CLR_SKY_LIGHT, hover_color="#bae6fd",
                          text_color=CLR_SKY_XDARK, font=ctk.CTkFont(size=11),
                          command=lambda i=uid: self._dialog_password(i)).pack(side="left", padx=(0, 4))

            toggle_txt = "Desactivar" if activo else "Activar"
            toggle_clr = CLR_RED_LIGHT if activo else CLR_GREEN_LIGHT
            toggle_txt_clr = CLR_RED if activo else CLR_GREEN
            ctk.CTkButton(acc, text=toggle_txt, width=82, height=28, corner_radius=6,
                          fg_color=toggle_clr, hover_color=toggle_clr,
                          text_color=toggle_txt_clr, font=ctk.CTkFont(size=11),
                          command=lambda i=uid: self._toggle(i)).pack(side="left", padx=(0, 4))

            ctk.CTkButton(acc, text="🗑️ Eliminar", width=86, height=28, corner_radius=6,
                          fg_color=CLR_RED_LIGHT, hover_color="#fecaca",
                          text_color=CLR_RED, font=ctk.CTkFont(size=11),
                          command=lambda i=uid: self._confirmar_eliminar(i)).pack(side="left")

    # ── Diálogos ──────────────────────────────────────────────────────────────
    def _dialog_nuevo(self):
        from modules.auth import crear_usuario
        dlg = ctk.CTkToplevel(self)
        dlg.title("Nuevo Usuario")
        dlg.grab_set()
        dlg.configure(fg_color=CLR_WHITE)
        dlg.resizable(False, False)
        dlg.geometry("620x440")

        ctk.CTkLabel(dlg, text="➕  Nuevo Usuario",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=CLR_TEXT).pack(pady=(20, 2))
        ctk.CTkLabel(dlg, text="Completa los datos del nuevo usuario",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack()
        ctk.CTkFrame(dlg, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=24, pady=(12, 0))

        form = ctk.CTkFrame(dlg, fg_color="transparent")
        form.pack(fill="x", padx=28, pady=(12, 0))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        fields = {}

        for col, (lbl, ph, show) in enumerate([
            ("Nombre completo", "Ej. Dr. Juan Pérez",     False),
            ("Usuario (CURP)",  "Ej. GARM850101MNLRRA09", False),
        ]):
            px = (0, 0) if col == 0 else (8, 0)
            ctk.CTkLabel(form, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=CLR_TEXT_SOFT, anchor="w").grid(
                             row=0, column=col, sticky="w", padx=px, pady=(0, 2))
            e = ctk.CTkEntry(form, placeholder_text=ph, height=38,
                             corner_radius=8, border_color=CLR_BORDER)
            e.grid(row=1, column=col, sticky="ew", padx=px, pady=(0, 10))
            fields[lbl] = e

        for col, (lbl, ph, show) in enumerate([
            ("Teléfono",   "Ej. 8110000000", False),
            ("Contraseña", "••••••••",        True),
        ]):
            px = (0, 0) if col == 0 else (8, 0)
            ctk.CTkLabel(form, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=CLR_TEXT_SOFT, anchor="w").grid(
                             row=2, column=col, sticky="w", padx=px, pady=(0, 2))
            e = ctk.CTkEntry(form, placeholder_text=ph, show="•" if show else "",
                             height=38, corner_radius=8, border_color=CLR_BORDER)
            e.grid(row=3, column=col, sticky="ew", padx=px, pady=(0, 10))
            fields[lbl] = e

        ctk.CTkLabel(form, text="Rol", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT, anchor="w").grid(
                         row=4, column=0, columnspan=2, sticky="w", pady=(0, 2))
        rol_var = ctk.StringVar(value="enfermero")
        ctk.CTkOptionMenu(form, values=["admin", "enfermero", "doctor"],
                          variable=rol_var, height=38, corner_radius=8).grid(
                              row=5, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        lbl_msg = ctk.CTkLabel(dlg, text="", font=ctk.CTkFont(size=11), text_color=CLR_RED)
        lbl_msg.pack(pady=(4, 0))

        def _guardar():
            nombre   = fields["Nombre completo"].get().strip()
            usuario  = fields["Usuario (CURP)"].get().strip()
            telefono = fields["Teléfono"].get().strip()
            password = fields["Contraseña"].get()
            rol      = rol_var.get()
            if not all([nombre, usuario, password]):
                lbl_msg.configure(text="⚠ Nombre, usuario y contraseña son obligatorios.")
                return
            ok = crear_usuario(usuario, password, rol, nombre, telefono)
            if ok:
                dlg.destroy()
                self._load_data()
            else:
                lbl_msg.configure(text="⚠ El usuario ya existe o hubo un error.")

        btn_bar = ctk.CTkFrame(dlg, fg_color=CLR_WHITE, corner_radius=0)
        btn_bar.pack(fill="x", pady=(6, 16))
        btn_bar.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_bar, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=8, height=46,
                      command=dlg.destroy).grid(row=0, column=0, sticky="ew", padx=(20, 8))
        ctk.CTkButton(btn_bar, text="Crear usuario",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, corner_radius=8, height=46,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=_guardar).grid(row=0, column=1, sticky="ew", padx=(8, 20))

        dlg.update_idletasks()
        W, H = 620, 440
        sw = dlg.winfo_screenwidth()
        sh = dlg.winfo_screenheight()
        dlg.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _dialog_password(self, id_usuario: int):
        from modules.auth import cambiar_password
        dlg = ctk.CTkToplevel(self)
        dlg.title("Cambiar Contraseña")
        dlg.geometry("360x240")
        dlg.grab_set()
        dlg.configure(fg_color=CLR_WHITE)
        dlg.resizable(False, False)

        ctk.CTkLabel(dlg, text="🔑  Nueva Contraseña",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=CLR_TEXT).pack(pady=(24, 4))
        ctk.CTkFrame(dlg, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=24, pady=(12, 16))

        e = ctk.CTkEntry(dlg, placeholder_text="Nueva contraseña",
                         show="•", height=40, corner_radius=8)
        e.pack(fill="x", padx=28)
        lbl_msg = ctk.CTkLabel(dlg, text="", font=ctk.CTkFont(size=11), text_color=CLR_RED)
        lbl_msg.pack(pady=(6, 0))

        def _guardar():
            pw = e.get()
            if len(pw) < 3:
                lbl_msg.configure(text="⚠ Mínimo 3 caracteres.")
                return
            cambiar_password(id_usuario, pw)
            dlg.destroy()

        ctk.CTkButton(dlg, text="Guardar", height=38, corner_radius=8,
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      command=_guardar).pack(fill="x", padx=28, pady=(12, 0))

    def _toggle(self, id_usuario: int):
        from modules.auth import toggle_activo
        toggle_activo(id_usuario)
        self._load_data()

    def _dialog_editar(self, id_usuario: int):
        from db.connection import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id_usuario,))
        u = cursor.fetchone()
        conn.close()
        if not u:
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Editar Usuario")
        dlg.grab_set()
        dlg.configure(fg_color=CLR_WHITE)
        dlg.resizable(False, False)
        dlg.geometry("620x420")

        ctk.CTkLabel(dlg, text="Editar Usuario",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=CLR_TEXT).pack(pady=(20, 2))
        ctk.CTkLabel(dlg, text=f"Editando: {u['usuario']}",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack()
        ctk.CTkFrame(dlg, fg_color=CLR_BORDER, height=1).pack(fill="x", padx=24, pady=(12, 0))

        form = ctk.CTkFrame(dlg, fg_color="transparent")
        form.pack(fill="x", padx=28, pady=(12, 0))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        fields = {}

        for col, (lbl, ph, val) in enumerate([
            ("Nombre completo", "Ej. Dr. Juan Pérez",     u["nombre"]),
            ("Usuario (CURP)",  "Ej. GARM850101MNLRRA09", u["usuario"]),
        ]):
            px = (0, 0) if col == 0 else (8, 0)
            ctk.CTkLabel(form, text=lbl, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=CLR_TEXT_SOFT, anchor="w").grid(
                             row=0, column=col, sticky="w", padx=px, pady=(0, 2))
            e = ctk.CTkEntry(form, placeholder_text=ph, height=38,
                             corner_radius=8, border_color=CLR_BORDER)
            e.insert(0, val)
            e.grid(row=1, column=col, sticky="ew", padx=px, pady=(0, 10))
            fields[lbl] = e

        ctk.CTkLabel(form, text="Teléfono", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT, anchor="w").grid(
                         row=2, column=0, sticky="w", pady=(0, 2))
        e_tel = ctk.CTkEntry(form, placeholder_text="Ej. 8110000000", height=38,
                             corner_radius=8, border_color=CLR_BORDER)
        e_tel.insert(0, u["telefono"] or "")
        e_tel.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        fields["Teléfono"] = e_tel

        ctk.CTkLabel(form, text="Rol", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=CLR_TEXT_SOFT, anchor="w").grid(
                         row=2, column=1, sticky="w", padx=(8, 0), pady=(0, 2))
        rol_var = ctk.StringVar(value=u["rol"])
        ctk.CTkOptionMenu(form, values=["admin", "enfermero", "doctor"],
                          variable=rol_var, height=38, corner_radius=8).grid(
                              row=3, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))

        lbl_msg = ctk.CTkLabel(dlg, text="", font=ctk.CTkFont(size=11), text_color=CLR_RED)
        lbl_msg.pack(pady=(4, 0))

        def _guardar():
            nombre   = fields["Nombre completo"].get().strip()
            usuario  = fields["Usuario (CURP)"].get().strip()
            telefono = fields["Teléfono"].get().strip()
            rol      = rol_var.get()
            if not nombre or not usuario:
                lbl_msg.configure(text="⚠ Nombre y usuario son obligatorios.")
                return
            try:
                conn = get_connection()
                conn.execute(
                    "UPDATE usuarios SET nombre=?, usuario=?, telefono=?, rol=? WHERE id=?",
                    (nombre, usuario, telefono, rol, id_usuario)
                )
                conn.commit()
                conn.close()
                dlg.destroy()
                self._load_data()
            except Exception as ex:
                lbl_msg.configure(text=f"⚠ Error: {ex}")

        btn_bar = ctk.CTkFrame(dlg, fg_color=CLR_WHITE, corner_radius=0)
        btn_bar.pack(fill="x", pady=(6, 16))
        btn_bar.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_bar, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      corner_radius=8, height=46,
                      command=dlg.destroy).grid(row=0, column=0, sticky="ew", padx=(20, 8))
        ctk.CTkButton(btn_bar, text="Guardar cambios",
                      fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                      text_color=CLR_WHITE, corner_radius=8, height=46,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=_guardar).grid(row=0, column=1, sticky="ew", padx=(8, 20))

        dlg.update_idletasks()
        W, H = 620, 420
        sw = dlg.winfo_screenwidth()
        sh = dlg.winfo_screenheight()
        dlg.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")

    def _confirmar_eliminar(self, id_usuario: int):
        from db.connection import get_connection
        from modules.auth import get_sesion

        sesion = get_sesion()
        if sesion and sesion["id"] == id_usuario:
            dlg = ctk.CTkToplevel(self)
            dlg.title("")
            dlg.geometry("340x160")
            dlg.grab_set()
            dlg.configure(fg_color=CLR_WHITE)
            dlg.resizable(False, False)
            ctk.CTkLabel(dlg, text="⚠️  No puedes eliminarte a ti mismo.",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=CLR_TEXT).pack(pady=(36, 8))
            ctk.CTkButton(dlg, text="Entendido", height=36, corner_radius=8,
                          fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
                          command=dlg.destroy).pack(padx=32, fill="x")
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("")
        dlg.geometry("360x200")
        dlg.grab_set()
        dlg.configure(fg_color=CLR_WHITE)
        dlg.resizable(False, False)

        dlg.update_idletasks()
        sw = dlg.winfo_screenwidth()
        sh = dlg.winfo_screenheight()
        dlg.geometry(f"360x200+{(sw-360)//2}+{(sh-200)//2}")

        ctk.CTkLabel(dlg, text="🗑️  Eliminar usuario",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=CLR_TEXT).pack(pady=(24, 4))
        ctk.CTkLabel(dlg, text="Esta acción no se puede deshacer.\n¿Estás seguro?",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED,
                     justify="center").pack()

        row = ctk.CTkFrame(dlg, fg_color=CLR_WHITE)
        row.pack(pady=20, padx=24, fill="x")

        ctk.CTkButton(row, text="Cancelar", fg_color=CLR_WHITE,
                      border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      height=38, corner_radius=8,
                      command=dlg.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

        def _eliminar():
            try:
                conn = get_connection()
                conn.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
                conn.commit()
                conn.close()
            except Exception:
                pass
            dlg.destroy()
            self._load_data()

        ctk.CTkButton(row, text="Sí, eliminar", fg_color=CLR_RED,
                      hover_color="#dc2626", text_color=CLR_WHITE,
                      height=38, corner_radius=8,
                      command=_eliminar).pack(side="right", expand=True, fill="x")