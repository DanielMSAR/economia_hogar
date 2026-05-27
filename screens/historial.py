"""
Pantalla Historial — lista de transacciones del mes con filtros
"""

from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.app import App


class HistorialScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._anio = datetime.now().year
        self._mes  = datetime.now().month
        self._build_ui()

    MESES = ["Ene","Feb","Mar","Abr","May","Jun",
             "Jul","Ago","Sep","Oct","Nov","Dic"]

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        # ── Header ──────────────────────────────────
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56),
                             md_bg_color=(0.2, 0.6, 0.6, 1), padding=dp(8))
        header.add_widget(MDFlatButton(
            text="←",
            theme_text_color="Custom",
            text_color=(1,1,1,1),
            on_release=lambda x: setattr(self.manager, "current", "dashboard"),
        ))
        header.add_widget(MDLabel(
            text="Historial",
            theme_text_color="Custom",
            text_color=(1,1,1,1),
            font_style="H6",
            halign="center",
        ))
        header.add_widget(MDBoxLayout())
        root.add_widget(header)

        # ── Navegación de mes ────────────────────────
        nav_mes = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48),
                              padding=dp(8), spacing=dp(8))
        MDFlatButton(text="◀", on_release=lambda x: self._cambiar_mes(-1))
        self.lbl_mes_nav = MDLabel(text="", halign="center", font_style="Subtitle1")
        nav_mes.add_widget(MDFlatButton(text="◀", on_release=lambda x: self._cambiar_mes(-1)))
        nav_mes.add_widget(self.lbl_mes_nav)
        nav_mes.add_widget(MDFlatButton(text="▶", on_release=lambda x: self._cambiar_mes(1)))
        root.add_widget(nav_mes)

        # ── Resumen rápido ───────────────────────────
        self.lbl_resumen = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(28),
        )
        root.add_widget(self.lbl_resumen)

        # ── Lista scrollable ─────────────────────────
        scroll = ScrollView()
        self.lista = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(6),
            padding=(dp(10), dp(4)),
        )
        self.lista.bind(minimum_height=self.lista.setter("height"))
        scroll.add_widget(self.lista)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_pre_enter(self):
        self._refresh()

    def _cambiar_mes(self, delta):
        self._mes += delta
        if self._mes > 12:
            self._mes  = 1
            self._anio += 1
        elif self._mes < 1:
            self._mes  = 12
            self._anio -= 1
        self._refresh()

    def _refresh(self):
        nombre_mes = self.MESES[self._mes - 1]
        self.lbl_mes_nav.text = f"{nombre_mes} {self._anio}"

        db  = App.get_running_app().db
        res = db.get_resumen_mes(self._anio, self._mes)
        self.lbl_resumen.text = (
            f"Ingresos: ${res['ingresos']:,.0f}   "
            f"Egresos: ${res['egresos']:,.0f}   "
            f"Balance: ${res['balance']:,.0f}"
        )

        trans = db.get_transacciones_mes(self._anio, self._mes)
        self.lista.clear_widgets()

        if not trans:
            self.lista.add_widget(MDLabel(
                text="Sin movimientos en este mes",
                halign="center",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(60),
            ))
            return

        for t in trans:
            color  = (0.13, 0.55, 0.13, 1) if t["tipo"] == "ingreso" else (0.8, 0.2, 0.2, 1)
            signo  = "+" if t["tipo"] == "ingreso" else "-"
            card   = MDCard(orientation="horizontal", size_hint_y=None, height=dp(64),
                            padding=dp(12), radius=[dp(8)], elevation=1)

            info = MDBoxLayout(orientation="vertical")
            info.add_widget(MDLabel(
                text=f"{t['categoria']}",
                font_style="Subtitle2",
                size_hint_y=None,
                height=dp(22),
            ))
            info.add_widget(MDLabel(
                text=f"{t['fecha']}  {t['descripcion'] or ''}",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height=dp(18),
            ))
            card.add_widget(info)

            monto_lbl = MDLabel(
                text=f"{signo}${t['monto']:,.0f}",
                theme_text_color="Custom",
                text_color=color,
                halign="right",
                font_style="H6",
                size_hint_x=0.35,
            )
            card.add_widget(monto_lbl)

            # Botón eliminar
            del_btn = MDIconButton(
                icon="delete-outline",
                theme_text_color="Custom",
                text_color=(0.6, 0.6, 0.6, 1),
                size_hint_x=None,
                width=dp(36),
            )
            tid = t["id"]
            del_btn.bind(on_release=lambda x, _id=tid: self._eliminar(x, _id))
            card.add_widget(del_btn)

            self.lista.add_widget(card)

    def _eliminar(self, btn, trans_id):
        db = App.get_running_app().db
        db.delete_transaccion(trans_id)
        self._refresh()
