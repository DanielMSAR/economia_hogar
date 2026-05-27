"""
Pantalla Dashboard — muestra el resumen del mes actual
"""

from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.metrics import dp
from kivy.app import App


class DashboardScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        # ── Encabezado ──────────────────────────────
        header = MDBoxLayout(
            orientation="vertical",
            md_bg_color=App.get_running_app().theme_cls.primary_color if App.get_running_app() else (0.2, 0.6, 0.6, 1),
            padding=dp(20),
            size_hint_y=None,
            height=dp(120),
        )
        self.lbl_mes = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6",
            halign="center",
        )
        self.lbl_balance = MDLabel(
            text="Balance: $0",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H4",
            halign="center",
        )
        header.add_widget(self.lbl_mes)
        header.add_widget(self.lbl_balance)
        root.add_widget(header)

        # ── Tarjetas ingresos / egresos ──────────────
        cards_row = MDBoxLayout(
            orientation="horizontal",
            padding=dp(12),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(110),
        )

        self.card_ingresos = self._make_card("Ingresos", "$0", (0.13, 0.55, 0.13, 1))
        self.card_egresos  = self._make_card("Egresos",  "$0", (0.8, 0.2, 0.2, 1))
        cards_row.add_widget(self.card_ingresos)
        cards_row.add_widget(self.card_egresos)
        root.add_widget(cards_row)

        # ── Últimas transacciones ────────────────────
        root.add_widget(MDLabel(
            text="Últimas transacciones",
            font_style="Subtitle1",
            halign="left",
            padding=(dp(16), dp(4)),
            size_hint_y=None,
            height=dp(36),
        ))

        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView()
        self.lista_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
            padding=dp(10),
        )
        self.lista_box.bind(minimum_height=self.lista_box.setter("height"))
        scroll.add_widget(self.lista_box)
        root.add_widget(scroll)

        # ── Botones de navegación ────────────────────
        nav = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8),
            padding=dp(8),
            md_bg_color=(0.95, 0.95, 0.95, 1),
        )
        for label, screen in [
            ("+ Nuevo", "registrar"),
            ("Historial", "historial"),
            ("Gráficos", "graficos"),
        ]:
            btn = MDRaisedButton(text=label, on_release=lambda x, s=screen: self._goto(s))
            nav.add_widget(btn)
        root.add_widget(nav)

        self.add_widget(root)

    def _make_card(self, titulo, valor, color):
        card = MDCard(
            orientation="vertical",
            padding=dp(12),
            radius=[dp(12)],
            md_bg_color=color,
        )
        card.add_widget(MDLabel(
            text=titulo,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.85),
            halign="center",
            font_style="Caption",
        ))
        lbl = MDLabel(
            text=valor,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            halign="center",
            font_style="H5",
        )
        card.add_widget(lbl)
        # Guardamos referencia para actualizar
        card._valor_label = lbl
        return card

    def on_pre_enter(self):
        self._refresh()

    def _refresh(self):
        db   = App.get_running_app().db
        now  = datetime.now()
        res  = db.get_resumen_mes(now.year, now.month)
        meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                 "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

        self.lbl_mes.text     = f"{meses[now.month - 1]} {now.year}"
        self.lbl_balance.text = f"Balance: ${res['balance']:,.0f}"
        self.card_ingresos._valor_label.text = f"${res['ingresos']:,.0f}"
        self.card_egresos._valor_label.text  = f"${res['egresos']:,.0f}"

        # Últimas 5 transacciones
        self.lista_box.clear_widgets()
        trans = db.get_transacciones_mes(now.year, now.month)[:5]
        if not trans:
            self.lista_box.add_widget(MDLabel(
                text="Sin movimientos este mes",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(40),
            ))
        for t in trans:
            color = (0.13, 0.55, 0.13, 1) if t["tipo"] == "ingreso" else (0.8, 0.2, 0.2, 1)
            signo = "+" if t["tipo"] == "ingreso" else "-"
            row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(44),
                padding=(dp(8), 0),
            )
            row.add_widget(MDLabel(
                text=f"{t['fecha'][-5:]}  {t['categoria']}",
                size_hint_x=0.65,
            ))
            row.add_widget(MDLabel(
                text=f"{signo}${t['monto']:,.0f}",
                halign="right",
                theme_text_color="Custom",
                text_color=color,
                size_hint_x=0.35,
            ))
            self.lista_box.add_widget(row)

    def _goto(self, screen):
        self.manager.current = screen
