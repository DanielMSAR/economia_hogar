"""
Economía del Hogar — App Kivy/KivyMD
Punto de entrada principal
"""

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from screens.dashboard import DashboardScreen
from screens.registrar import RegistrarScreen
from screens.historial import HistorialScreen
from screens.graficos import GraficosScreen
from managers.database import DatabaseManager

# Tamaño de ventana para pruebas en escritorio (similar a un celular)
Window.size = (400, 700)


class EconomiaApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"

        # Inicializar base de datos
        self.db = DatabaseManager()

        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(RegistrarScreen(name="registrar"))
        sm.add_widget(HistorialScreen(name="historial"))
        sm.add_widget(GraficosScreen(name="graficos"))
        return sm

    def on_stop(self):
        self.db.close()


if __name__ == "__main__":
    EconomiaApp().run()
