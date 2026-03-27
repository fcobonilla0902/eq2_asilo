"""
Pantalla de Respaldo y Restauración de la base de datos.
Solo visible para el rol 'admin'.
Sigue el mismo estilo visual (colores, fuentes, layout) que las demás screens.
"""
import threading
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path

# ── Paleta de colores (igual que el resto del proyecto) ──────────────────────
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
CLR_AMBER      = "#f59e0b"
CLR_AMBER_LIGHT= "#fef3c7"


class RespaldoScreen(ctk.CTkFrame):
    """
    Pantalla principal de respaldo / restauración.
    Se monta en content_frame del Dashboard igual que las demás screens.
    """

    def __init__(self, master):
        super().__init__(master, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Importamos aquí para evitar ciclos al inicio
        from db.backup_manager import backup_manager
        self._mgr = backup_manager

        self._construir_ui()
        self._cargar_lista()

    # ── Construcción de UI ───────────────────────────────────────────────────
    def _construir_ui(self):
        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=CLR_WHITE, corner_radius=0, height=72)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        # Título izquierda
        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.grid(row=0, column=0, padx=28, pady=16, sticky="w")
        ctk.CTkLabel(left, text="💾  Respaldo y Restauración",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=CLR_TEXT).pack(side="left")
        ctk.CTkLabel(left, text="Solo administradores",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(
                         side="left", padx=(10, 0), pady=(4, 0))

        # Botón "Respaldar ahora" en la derecha del header
        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.grid(row=0, column=2, padx=28, pady=16, sticky="e")
        ctk.CTkButton(
            right, text="➕  Respaldar ahora",
            fg_color=CLR_SKY_DARK, hover_color=CLR_SKY_XDARK,
            text_color=CLR_WHITE, font=ctk.CTkFont(size=13, weight="bold"),
            height=38, corner_radius=10,
            command=self._respaldar_ahora,
        ).pack()

    def _build_body(self):
        body = ctk.CTkScrollableFrame(self, fg_color=CLR_SKY_XLIGHT, corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=20)
        body.grid_columnconfigure(0, weight=1)

        self._body = body

        # ── Tarjeta de estado ────────────────────────────────────────────────
        self._build_estado_card(body)

        # ── Lista de respaldos ───────────────────────────────────────────────
        ctk.CTkLabel(body, text="Respaldos disponibles",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=CLR_TEXT).grid(
                         row=1, column=0, sticky="w", pady=(20, 8))

        # Cabecera de tabla
        self._build_tabla_header(body)

        # Frame contenedor de filas (se llena en _cargar_lista)
        self._rows_frame = ctk.CTkFrame(body, fg_color="transparent")
        self._rows_frame.grid(row=3, column=0, sticky="ew")
        self._rows_frame.grid_columnconfigure(0, weight=1)

    def _build_estado_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CLR_WHITE, corner_radius=14,
                            border_width=1, border_color=CLR_BORDER)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        card.grid_columnconfigure((0, 1, 2), weight=1)

        # Celda helper
        def _celda(col, icono, titulo, var_texto, color_icon):
            c = ctk.CTkFrame(card, fg_color="transparent")
            c.grid(row=0, column=col, padx=24, pady=18, sticky="w")
            top = ctk.CTkFrame(c, fg_color="transparent")
            top.pack(anchor="w")
            ctk.CTkLabel(top, text=icono, font=ctk.CTkFont(size=20),
                         text_color=color_icon).pack(side="left")
            ctk.CTkLabel(top, text=titulo,
                         font=ctk.CTkFont(size=12), text_color=CLR_MUTED).pack(
                             side="left", padx=(6, 0))
            lbl = ctk.CTkLabel(c, textvariable=var_texto,
                               font=ctk.CTkFont(size=14, weight="bold"),
                               text_color=CLR_TEXT)
            lbl.pack(anchor="w", pady=(2, 0))
            return lbl

        self._var_total   = ctk.StringVar(value="—")
        self._var_ultimo  = ctk.StringVar(value="—")
        self._var_tamano  = ctk.StringVar(value="—")

        _celda(0, "📦", "Total de respaldos",  self._var_total,  CLR_SKY_DARK)
        _celda(1, "🕐", "Último respaldo",     self._var_ultimo, CLR_GREEN)
        _celda(2, "📁", "Espacio utilizado",   self._var_tamano, CLR_AMBER)

        # Separador vertical entre celdas
        for col in [1, 2]:
            sep = ctk.CTkFrame(card, fg_color=CLR_BORDER, width=1)
            sep.grid(row=0, column=col, sticky="ns", padx=(0, 0))
            sep.grid_remove()  # se usa border en su lugar

    def _build_tabla_header(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color=CLR_SKY_LIGHT, corner_radius=8, height=36)
        hdr.grid(row=2, column=0, sticky="ew", pady=(0, 2))
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        cols = [("  #", 40), ("Nombre del archivo", 0),
                ("Fecha", 160), ("Tamaño", 90), ("Acciones", 200)]
        for i, (txt, w) in enumerate(cols):
            kw = {"weight": 1} if w == 0 else {"minsize": w}
            hdr.grid_columnconfigure(i, **kw)
            ctk.CTkLabel(hdr, text=txt,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=CLR_TEXT_SOFT).grid(
                             row=0, column=i, sticky="w", padx=10, pady=8)

    # ── Cargar / refrescar lista ─────────────────────────────────────────────
    def _cargar_lista(self):
        # Limpiar filas anteriores
        for w in self._rows_frame.winfo_children():
            w.destroy()

        respaldos = self._mgr.listar_respaldos()

        # Actualizar tarjeta de estado
        self._var_total.set(str(len(respaldos)))
        if respaldos:
            self._var_ultimo.set(respaldos[0]["fecha"])
            total_kb = sum(r["tamano_kb"] for r in respaldos)
            self._var_tamano.set(f"{total_kb:.1f} KB")
        else:
            self._var_ultimo.set("Sin respaldos")
            self._var_tamano.set("0 KB")

        if not respaldos:
            ctk.CTkLabel(self._rows_frame,
                         text="No hay respaldos aún — haz clic en «Respaldar ahora»",
                         font=ctk.CTkFont(size=13), text_color=CLR_MUTED).grid(
                             row=0, column=0, pady=30)
            return

        for i, r in enumerate(respaldos):
            self._build_fila(i, r)

    def _build_fila(self, idx: int, datos: dict):
        bg = CLR_WHITE if idx % 2 == 0 else CLR_SKY_XLIGHT
        fila = ctk.CTkFrame(self._rows_frame, fg_color=bg, corner_radius=0, height=48)
        fila.grid(row=idx, column=0, sticky="ew")
        fila.grid_propagate(False)
        fila.grid_columnconfigure(1, weight=1)

        # Borde inferior sutil
        sep = ctk.CTkFrame(fila, fg_color=CLR_BORDER, height=1)
        sep.place(relx=0, rely=1.0, relwidth=1, anchor="sw")

        cols_cfg = [40, 0, 160, 90, 200]
        for c, w in enumerate(cols_cfg):
            if w == 0:
                fila.grid_columnconfigure(c, weight=1)
            else:
                fila.grid_columnconfigure(c, minsize=w)

        # Número
        ctk.CTkLabel(fila, text=f"  {idx+1}",
                     font=ctk.CTkFont(size=12), text_color=CLR_MUTED,
                     width=40).grid(row=0, column=0, sticky="w", padx=6, pady=12)

        # Nombre archivo (con ícono)
        nombre_frame = ctk.CTkFrame(fila, fg_color="transparent")
        nombre_frame.grid(row=0, column=1, sticky="w", padx=4, pady=8)
        ctk.CTkLabel(nombre_frame, text="🗃️",
                     font=ctk.CTkFont(size=14)).pack(side="left")
        ctk.CTkLabel(nombre_frame, text=datos["nombre"],
                     font=ctk.CTkFont(size=12), text_color=CLR_TEXT).pack(
                         side="left", padx=(6, 0))

        # Fecha
        ctk.CTkLabel(fila, text=datos["fecha"],
                     font=ctk.CTkFont(size=12), text_color=CLR_TEXT_SOFT).grid(
                         row=0, column=2, sticky="w", padx=10, pady=12)

        # Tamaño
        ctk.CTkLabel(fila, text=f"{datos['tamano_kb']} KB",
                     font=ctk.CTkFont(size=12), text_color=CLR_MUTED).grid(
                         row=0, column=3, sticky="w", padx=10, pady=12)

        # Botones de acción
        acc = ctk.CTkFrame(fila, fg_color="transparent")
        acc.grid(row=0, column=4, sticky="e", padx=12, pady=8)

        ctk.CTkButton(
            acc, text="↩  Restaurar",
            fg_color=CLR_AMBER_LIGHT, hover_color="#fde68a",
            text_color="#92400e", font=ctk.CTkFont(size=11, weight="bold"),
            height=30, corner_radius=8, width=110,
            command=lambda p=datos["path"]: self._confirmar_restaurar(p),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            acc, text="🗑",
            fg_color=CLR_RED_LIGHT, hover_color="#fecaca",
            text_color=CLR_RED, font=ctk.CTkFont(size=12),
            height=30, corner_radius=8, width=36,
            command=lambda p=datos["path"]: self._confirmar_eliminar(p),
        ).pack(side="left")

    # ── Acciones ─────────────────────────────────────────────────────────────
    def _respaldar_ahora(self):
        """Crea un respaldo manual en hilo separado para no bloquear la UI."""
        self._set_estado_boton(activo=False)

        def _tarea():
            ruta = self._mgr.crear_respaldo(etiqueta="manual")
            self.after(0, lambda: self._on_respaldo_completado(ruta))

        threading.Thread(target=_tarea, daemon=True).start()

    def _on_respaldo_completado(self, ruta):
        self._set_estado_boton(activo=True)
        if ruta:
            self._cargar_lista()
            self._mostrar_toast("✅  Respaldo creado correctamente", CLR_GREEN_LIGHT, "#166534")
        else:
            self._mostrar_toast("❌  Error al crear el respaldo — revisa el log", CLR_RED_LIGHT, CLR_RED)

    def _set_estado_boton(self, activo: bool):
        """Habilita / deshabilita el botón «Respaldar ahora» durante la operación."""
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkFrame):
                for child in w.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ctk.CTkButton):
                                btn.configure(state="normal" if activo else "disabled")

    def _confirmar_restaurar(self, ruta: Path):
        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.geometry("400x220")
        dialog.grab_set()
        dialog.configure(fg_color=CLR_WHITE)
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="↩", font=ctk.CTkFont(size=36)).pack(pady=(22, 4))
        ctk.CTkLabel(dialog, text="¿Restaurar este respaldo?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text=f"{ruta.name}\nSe creará un respaldo de seguridad previo.",
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED,
                     justify="center").pack(pady=(4, 0))

        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=16, padx=24, fill="x")

        ctk.CTkButton(row, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      height=38, corner_radius=8,
                      command=dialog.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

        def _ok():
            dialog.destroy()
            ok = self._mgr.restaurar(ruta)
            if ok:
                messagebox.showinfo(
                    "Restauración completa",
                    "La base de datos fue restaurada.\nReinicia la aplicación para aplicar los cambios.")
                # Destruir la ventana principal para forzar reinicio
                self.winfo_toplevel().destroy()
            else:
                messagebox.showerror("Error", "No se pudo restaurar. Revisa backup.log.")

        ctk.CTkButton(row, text="Sí, restaurar",
                      fg_color=CLR_AMBER, hover_color="#d97706",
                      text_color=CLR_WHITE, height=38, corner_radius=8,
                      command=_ok).pack(side="right", expand=True, fill="x")

    def _confirmar_eliminar(self, ruta: Path):
        dialog = ctk.CTkToplevel(self)
        dialog.title("")
        dialog.geometry("380x200")
        dialog.grab_set()
        dialog.configure(fg_color=CLR_WHITE)
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="🗑️", font=ctk.CTkFont(size=34)).pack(pady=(22, 4))
        ctk.CTkLabel(dialog, text="¿Eliminar este respaldo?",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=CLR_TEXT).pack()
        ctk.CTkLabel(dialog, text=ruta.name,
                     font=ctk.CTkFont(size=11), text_color=CLR_MUTED).pack(pady=(4, 0))

        row = ctk.CTkFrame(dialog, fg_color=CLR_WHITE)
        row.pack(pady=16, padx=24, fill="x")

        ctk.CTkButton(row, text="Cancelar",
                      fg_color=CLR_WHITE, border_width=1, border_color=CLR_BORDER,
                      text_color=CLR_TEXT_SOFT, hover_color="#f1f5f9",
                      height=38, corner_radius=8,
                      command=dialog.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

        def _ok():
            dialog.destroy()
            try:
                ruta.unlink()
                self._cargar_lista()
                self._mostrar_toast("🗑️  Respaldo eliminado", CLR_SKY_LIGHT, CLR_SKY_XDARK)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

        ctk.CTkButton(row, text="Sí, eliminar",
                      fg_color=CLR_RED, hover_color="#dc2626",
                      text_color=CLR_WHITE, height=38, corner_radius=8,
                      command=_ok).pack(side="right", expand=True, fill="x")

    # ── Toast de notificación ────────────────────────────────────────────────
    def _mostrar_toast(self, mensaje: str, bg: str, fg: str, duracion_ms: int = 3000):
        """Muestra una notificación flotante en la esquina superior derecha."""
        toast = ctk.CTkFrame(self, fg_color=bg, corner_radius=10,
                             border_width=1, border_color=fg)
        ctk.CTkLabel(toast, text=mensaje,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=fg).pack(padx=16, pady=10)

        # Posicionar arriba a la derecha del frame
        self.update_idletasks()
        w = 320
        toast.place(x=self.winfo_width() - w - 20, y=80, width=w)
        self.after(duracion_ms, toast.destroy)
