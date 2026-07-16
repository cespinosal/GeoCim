"""
make_assets.py — Genera GeoCim.ico y GeoCim.png en el directorio del proyecto.
Ejecutar UNA VEZ antes de hacer el build con PyInstaller:

    python make_assets.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

from ui.splash import draw_icon_badge

app = QApplication.instance() or QApplication(sys.argv)

OUT_DIR = os.path.dirname(__file__)
SIZES = [16, 24, 32, 48, 64, 128, 256]


def render_icon(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    draw_icon_badge(p, cx=size // 2, cy=size // 2, size=size)
    p.end()
    return pm


# PNG principal (256 px)
png_path = os.path.join(OUT_DIR, "GeoCim.png")
render_icon(256).save(png_path, "PNG")
print(f"  Guardado: {png_path}")

# ICO con múltiples tamaños
ico_path = os.path.join(OUT_DIR, "GeoCim.ico")
# Qt soporta escritura ICO en Windows directamente
ok = render_icon(256).save(ico_path, "ICO")
if ok:
    print(f"  Guardado: {ico_path}")
else:
    # Fallback: intentar con Pillow
    try:
        from PIL import Image
        frames = []
        for s in SIZES:
            pm = render_icon(s)
            img_bytes = pm.toImage()
            # Convertir QImage → bytes → PIL Image
            img_bytes.save(f"_tmp_{s}.png")
            frames.append(Image.open(f"_tmp_{s}.png").convert("RGBA"))
        frames[0].save(
            ico_path, format="ICO",
            sizes=[(s, s) for s in SIZES],
            append_images=frames[1:]
        )
        for s in SIZES:
            os.remove(f"_tmp_{s}.png")
        print(f"  Guardado (via Pillow): {ico_path}")
    except Exception as e:
        print(f"  ADVERTENCIA: No se pudo generar .ico — {e}")
        print(f"  Usa GeoCim.png como ícono en su lugar.")

print("\nListo. Actualiza GeoCim.spec para incluir GeoCim.ico y GeoCim.png en datas.")
