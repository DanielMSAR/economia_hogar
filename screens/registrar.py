"""
Pantalla Registrar — formulario para nueva transacción
"""

from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.app import App

COLOR_INGRESO_ON = (0.13, 0.55, 0.13, 1)
COLOR_EGRESO_ON  = (0.8,  0.2,  0.2,  1)
COLOR_OFF        = (0.75, 0.75, 0.75, 1)


class RegistrarScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tipo      = "egreso"
        self._cat_id    = None
        self._cat_items = []
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # ── Encabezado ──────────────────────────────
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
        header.add_widget(MDFlatButton(
            text="← Volver",
            on_release=lambda x: setattr(self.manager, "current", "dashboard"),
        ))
        header.add_widget(MDLabel(
            text="Nueva transacción",
            font_style="H6",
            halign="center",
        ))
        header.add_widget(MDBoxLayout())
        root.add_widget(header)

        # ── Botones INGRESO / EGRESO ─────────────────
        tipo_row = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                               height=dp(52), spacing=dp(10))
        self.btn_ingreso = MDRaisedButton(
            text="▲  INGRESO",
            md_bg_color=COLOR_OFF,
            on_release=lambda x: self._set_tipo("ingreso"),
        )
        self.btn_egreso = MDRaisedButton(
            text="▼  EGRESO",
            md_bg_color=COLOR_EGRESO_ON,
            on_release=lambda x: self._set_tipo("egreso"),
        )
        tipo_row.add_widget(self.btn_ingreso)
        tipo_row.add_widget(self.btn_egreso)
        root.add_widget(tipo_row)

        # ── Campo monto ──────────────────────────────
        self.field_monto = MDTextField(
            hint_text="Monto ($)",
            input_filter="float",
            mode="rectangle",
        )
        root.add_widget(self.field_monto)

        # ── Descripción ──────────────────────────────
        self.field_desc = MDTextField(
            hint_text="Descripción (opcional)",
            mode="rectangle",
        )
        root.add_widget(self.field_desc)

        # ── Selector de categoría ────────────────────
        self.btn_categoria = MDRaisedButton(
            text="Seleccionar categoría",
            on_release=self._abrir_menu_categorias,
        )
        root.add_widget(self.btn_categoria)

        # ── Campo fecha ──────────────────────────────
        self.field_fecha = MDTextField(
            hint_text="Fecha (AAAA-MM-DD)",
            text=datetime.now().strftime("%Y-%m-%d"),
            mode="rectangle",
        )
        root.add_widget(self.field_fecha)

        # ── Botón guardar ────────────────────────────
        self.btn_guardar = MDRaisedButton(
            text="Guardar transacción",
            on_release=self._guardar,
            md_bg_color=COLOR_EGRESO_ON,
        )
        root.add_widget(self.btn_guardar)

        self.lbl_msg = MDLabel(text="", halign="center", size_hint_y=None, height=dp(36))
        root.add_widget(self.lbl_msg)

        self.add_widget(root)

    def on_pre_enter(self):
        self._cargar_categorias()

    def _set_tipo(self, tipo):
        self._tipo   = tipo
        self._cat_id = None
        self.btn_categoria.text = "Seleccionar categoría"

        if tipo == "ingreso":
            self.btn_ingreso.md_bg_color = COLOR_INGRESO_ON
            self.btn_egreso.md_bg_color  = COLOR_OFF
            self.btn_guardar.md_bg_color = COLOR_INGRESO_ON
        else:
            self.btn_egreso.md_bg_color  = COLOR_EGRESO_ON
            self.btn_ingreso.md_bg_color = COLOR_OFF
            self.btn_guardar.md_bg_color = COLOR_EGRESO_ON

        self._cargar_categorias()

    def _cargar_categorias(self):
        db   = App.get_running_app().db
        cats = db.get_categorias(self._tipo)
        self._cat_items = cats
        self._menu_items = [
            {
                "text": c["nombre"],
                "on_release": lambda x=c: self._seleccionar_categoria(x),
            }
            for c in cats
        ]

    def _abrir_menu_categorias(self, btn):
        menu = MDDropdownMenu(
            caller=btn,
            items=self._menu_items,
            width_mult=4,
        )
        menu.open()

    def _seleccionar_categoria(self, cat):
        self._cat_id = cat["id"]
        self.btn_categoria.text = cat["nombre"]

    def _guardar(self, *args):
        monto_txt = self.field_monto.text.strip()
        fecha_txt = self.field_fecha.text.strip()
        desc      = self.field_desc.text.strip()

        if not monto_txt:
            self._mostrar_msg("Por favor ingresá un monto.", error=True)
            return
        try:
            monto = float(monto_txt)
            assert monto > 0
        except (ValueError, AssertionError):
            self._mostrar_msg("El monto debe ser un número positivo.", error=True)
            return

        if self._cat_id is None:
            self._mostrar_msg("Seleccioná una categoría.", error=True)
            return

        try:
            datetime.strptime(fecha_txt, "%Y-%m-%d")
        except ValueError:
            self._mostrar_msg("Formato de fecha inválido. Usá AAAA-MM-DD.", error=True)
            return

        db = App.get_running_app().db
        db.add_transaccion(monto, self._tipo, desc, self._cat_id, fecha_txt)

        self._mostrar_msg("✓ Transacción guardada.", error=False)
        self._limpiar()

    def _limpiar(self):
        self.field_monto.text = ""
        self.field_desc.text  = ""
        self.field_fecha.text = datetime.now().strftime("%Y-%m-%d")
        self._cat_id = None
        self.btn_categoria.text = "Seleccionar categoría"

    def _mostrar_msg(self, texto, error=False):
        self.lbl_msg.text             = texto
        self.lbl_msg.theme_text_color = "Custom"
        self.lbl_msg.text_color       = (0.8, 0.2, 0.2, 1) if error else (0.13, 0.55, 0.13, 1)
