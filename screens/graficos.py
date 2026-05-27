"""
Pantalla Gráficos — torta de categorías + barras mensuales
Usa matplotlib renderizado en un widget Kivy (FigureCanvasKivyAgg)
"""

from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from kivy.metrics import dp
from kivy.app import App

try:
    import matplotlib
    matplotlib.use("Agg")          # backend sin ventana propia
    import matplotlib.pyplot as plt
    from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


COLORES = [
    "#2E9B6E","#E86339","#3B7FD4","#D4A43B","#9B3BD4",
    "#3BD4C8","#D43B7A","#7AD43B","#D43B3B","#3B5BD4",
]


class GraficosScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._anio      = datetime.now().year
        self._mes       = datetime.now().month
        self._vista     = "torta_egresos"   # torta_egresos | torta_ingresos | barras
        self._canvas    = None
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
            text="Gráficos",
            theme_text_color="Custom",
            text_color=(1,1,1,1),
            font_style="H6",
            halign="center",
        ))
        header.add_widget(MDBoxLayout())
        root.add_widget(header)

        # ── Selector de vista ────────────────────────
        btn_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44),
                              spacing=dp(6), padding=(dp(8), dp(4)))
        for label, vista in [
            ("Egresos",  "torta_egresos"),
            ("Ingresos", "torta_ingresos"),
            ("Tendencia","barras"),
        ]:
            btn = MDFlatButton(
                text=label,
                on_release=lambda x, v=vista: self._set_vista(v),
            )
            btn_row.add_widget(btn)
        root.add_widget(btn_row)

        # ── Navegación de mes (solo para tortas) ─────
        self.nav_mes_box = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                                       height=dp(44), padding=dp(8))
        self.nav_mes_box.add_widget(
            MDFlatButton(text="◀", on_release=lambda x: self._cambiar_mes(-1)))
        self.lbl_mes_nav = MDLabel(text="", halign="center")
        self.nav_mes_box.add_widget(self.lbl_mes_nav)
        self.nav_mes_box.add_widget(
            MDFlatButton(text="▶", on_release=lambda x: self._cambiar_mes(1)))
        root.add_widget(self.nav_mes_box)

        # ── Área del gráfico ─────────────────────────
        self.chart_box = MDBoxLayout(orientation="vertical")
        root.add_widget(self.chart_box)

        self.add_widget(root)

    def on_pre_enter(self):
        self._refresh()

    def _set_vista(self, vista):
        self._vista = vista
        # Mostrar/ocultar nav de mes
        self.nav_mes_box.opacity = 0 if vista == "barras" else 1
        self._refresh()

    def _cambiar_mes(self, delta):
        self._mes += delta
        if self._mes > 12:
            self._mes = 1; self._anio += 1
        elif self._mes < 1:
            self._mes = 12; self._anio -= 1
        self._refresh()

    def _refresh(self):
        nombre_mes = self.MESES[self._mes - 1]
        self.lbl_mes_nav.text = f"{nombre_mes} {self._anio}"

        self.chart_box.clear_widgets()

        if not MATPLOTLIB_OK:
            self.chart_box.add_widget(MDLabel(
                text="Instalá matplotlib y kivy-garden.matplotlib\npara ver los gráficos.",
                halign="center",
            ))
            return

        db = App.get_running_app().db

        if self._vista == "torta_egresos":
            datos = db.get_por_categoria_mes(self._anio, self._mes, "egreso")
            self._dibujar_torta(datos, f"Egresos — {nombre_mes} {self._anio}")

        elif self._vista == "torta_ingresos":
            datos = db.get_por_categoria_mes(self._anio, self._mes, "ingreso")
            self._dibujar_torta(datos, f"Ingresos — {nombre_mes} {self._anio}")

        else:
            datos = db.get_resumen_ultimos_meses(6)
            self._dibujar_barras(datos)

    def _dibujar_torta(self, datos, titulo):
        if not datos:
            self.chart_box.add_widget(MDLabel(
                text="Sin datos para este período.", halign="center"))
            return

        etiquetas = [d["categoria"] for d in datos]
        valores   = [d["total"]     for d in datos]
        colores   = COLORES[:len(valores)]

        fig, ax = plt.subplots(figsize=(4, 3.5), facecolor="#f5f5f5")
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=None,
            colors=colores,
            autopct="%1.0f%%",
            startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=1.5),
        )
        for at in autotexts:
            at.set_fontsize(8)

        ax.set_title(titulo, fontsize=10, pad=8)
        ax.legend(
            wedges, [f"{e} (${v:,.0f})" for e, v in zip(etiquetas, valores)],
            loc="lower center",
            bbox_to_anchor=(0.5, -0.28),
            ncol=2,
            fontsize=7,
            frameon=False,
        )
        fig.tight_layout()

        canvas = FigureCanvasKivyAgg(fig)
        self.chart_box.add_widget(canvas)
        plt.close(fig)

    def _dibujar_barras(self, datos):
        if not datos:
            self.chart_box.add_widget(MDLabel(
                text="Sin datos históricos.", halign="center"))
            return

        meses    = [d["mes"][-5:] for d in datos]   # "YYYY-MM" → "MM"
        ingresos = [d["ingresos"] for d in datos]
        egresos  = [d["egresos"]  for d in datos]
        x        = range(len(meses))
        w        = 0.35

        fig, ax = plt.subplots(figsize=(4, 3.2), facecolor="#f5f5f5")
        ax.bar([i - w/2 for i in x], ingresos, width=w, color="#2E9B6E", label="Ingresos")
        ax.bar([i + w/2 for i in x], egresos,  width=w, color="#E86339", label="Egresos")
        ax.set_xticks(list(x))
        ax.set_xticklabels(meses, fontsize=8)
        ax.yaxis.set_tick_params(labelsize=8)
        ax.set_title("Tendencia últimos 6 meses", fontsize=10, pad=8)
        ax.legend(fontsize=8, frameon=False)
        ax.set_facecolor("#f5f5f5")
        fig.patch.set_facecolor("#f5f5f5")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.yaxis.grid(True, linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)
        fig.tight_layout()

        canvas = FigureCanvasKivyAgg(fig)
        self.chart_box.add_widget(canvas)
        plt.close(fig)
