# Economía del Hogar — Requisitos

## Dependencias Python

```
kivymd==1.1.1
kivy==2.2.1
matplotlib==3.8.0
kivy-garden.matplotlib
buildozer          # solo para compilar el APK
```

## Instalación (entorno de desarrollo)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 2. Instalar dependencias
pip install kivymd kivy matplotlib

# 3. Instalar el widget matplotlib para Kivy
pip install kivy-garden
garden install matplotlib

# 4. Ejecutar en escritorio (para probar)
python main.py
```

## Compilar APK con Buildozer

```bash
pip install buildozer
buildozer init          # genera buildozer.spec
buildozer android debug # compilar (requiere Linux o WSL)
```

### Configuración mínima en buildozer.spec
```
title = Economía del Hogar
package.name = economiadelhogar
package.domain = org.ejemplo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
requirements = python3,kivy==2.2.1,kivymd==1.1.1,matplotlib,sqlite3
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
```

## Estructura del proyecto

```
economia_hogar/
├── main.py                  ← Punto de entrada
├── economia.db              ← Base de datos SQLite (se crea automáticamente)
├── managers/
│   ├── __init__.py
│   └── database.py          ← Todo el acceso a SQLite
└── screens/
    ├── __init__.py
    ├── dashboard.py         ← Resumen mensual
    ├── registrar.py         ← Nueva transacción
    ├── historial.py         ← Lista con navegación por mes
    └── graficos.py          ← Torta y barras (matplotlib)
```

## Funcionalidades incluidas

- ✅ Registrar ingresos y egresos con monto, categoría, descripción y fecha
- ✅ 15 categorías predefinidas (5 ingresos + 10 egresos)
- ✅ Dashboard con balance, ingresos y egresos del mes actual
- ✅ Historial navegable mes a mes con opción de eliminar
- ✅ Gráfico de torta de egresos por categoría
- ✅ Gráfico de torta de ingresos por categoría
- ✅ Gráfico de barras con tendencia de 6 meses
- ✅ Persistencia local con SQLite (sin necesidad de internet)

## Próximos pasos sugeridos

- Agregar presupuesto mensual por categoría y alertas de exceso
- Exportar datos a CSV
- Selector de fecha visual (DatePicker de KivyMD)
- Soporte multi-cuenta (efectivo, banco, tarjeta)
- Tema oscuro
