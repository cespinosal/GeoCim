from PySide6.QtWidgets import QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QFont, QPen, QBrush, QPainterPath
)

W, H = 520, 562


def draw_icon_badge(p: QPainter, cx: int, cy: int, size: int):
    """
    Dibuja el ícono de la app: cuadro redondeado oscuro con borde ámbar
    + corte transversal de zapata aislada (igual que la segunda imagen).
    """
    half = size // 2
    rad  = size * 22 // 100        # radio de esquinas ~22 %

    # — Fondo oscuro del ícono —
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#1b2330"))
    p.drawRoundedRect(cx - half, cy - half, size, size, rad, rad)

    # — Cuadrícula sutil —
    pen_grid = QPen(QColor("#2a3848"), 0.9)
    p.setPen(pen_grid)
    step = size // 10
    for gx in range(cx - half, cx + half + 1, step):
        p.drawLine(gx, cy - half, gx, cy + half)
    for gy in range(cy - half, cy + half + 1, step):
        p.drawLine(cx - half, gy, cx + half, gy)

    # — Geometría de la zapata —
    col_w  = size * 18 // 100
    foot_w = size * 65 // 100
    foot_h = size * 14 // 100
    col_h  = size * 30 // 100
    gnd_y  = cy - size * 5 // 100   # línea de suelo (NTN)

    gray = QColor("#b9c0cb")

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(gray)

    # columna (arriba del NTN)
    p.drawRect(cx - col_w // 2, gnd_y - col_h, col_w, col_h)

    # losa de zapata (abajo del NTN)
    foot_top = gnd_y + size * 6 // 100
    p.drawRect(cx - foot_w // 2, foot_top, foot_w, foot_h)

    # — Línea NTN + rayado de suelo —
    amber_pen = QPen(QColor("#d98a1f"), max(1, size // 48))
    p.setPen(amber_pen)
    margin = size // 9
    p.drawLine(cx - half + margin, gnd_y, cx + half - margin, gnd_y)

    hatch_step = size // 13
    hatch_len  = size // 13
    x_start = cx - half + margin
    x_end   = cx + half - margin
    for hx in range(x_start, x_end, hatch_step):
        p.drawLine(hx, gnd_y, hx - hatch_len, gnd_y + hatch_len)

    # — Borde ámbar del ícono —
    border_pen = QPen(QColor("#d98a1f"), max(2, size // 22))
    border_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(border_pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    inset = size // 22
    p.drawRoundedRect(
        cx - half + inset, cy - half + inset,
        size - 2 * inset, size - 2 * inset,
        rad - inset // 2, rad - inset // 2
    )


def build_splash_pixmap() -> QPixmap:
    pm = QPixmap(W, H)
    pm.fill(Qt.GlobalColor.transparent)

    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # ── Fondo oscuro redondeado ──────────────────────────────────────
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#1b2330"))
    p.drawRoundedRect(0, 0, W, H, 42, 42)

    # ── Cuadrícula sutil de fondo ────────────────────────────────────
    pen_grid = QPen(QColor("#232f40"), 1.0)
    p.setPen(pen_grid)
    step_g = 36
    for gx in range(step_g, W, step_g):
        p.drawLine(gx, 0, gx, H)
    for gy in range(step_g, H, step_g):
        p.drawLine(0, gy, W, gy)

    # ── Zapata grande ─────────────────────────────────────────────────
    cx       = W // 2
    ntn      = int(H * 0.345)          # ancla estructural
    soil_y   = int(H * 0.200)          # línea NTN y rayado
    col_w    = int(W * 0.175)
    col_h    = int(H * 0.255)
    foot_w   = int(W * 0.635)
    foot_h   = int(H * 0.098)
    foot_top = ntn                     # zapata pegada a la base de la columna
    margin   = int(W * 0.082)

    gray = QColor("#b9c0cb")
    amber = QColor("#d98a1f")

    # ── 1. NTN y rayado AL FONDO ──────────────────────────────────────
    p.setPen(QPen(amber, 2.2))
    p.drawLine(margin, soil_y, W - margin, soil_y)

    hatch_pen = QPen(QColor("#8a95a4"), 1.3)
    p.setPen(hatch_pen)
    hs = int(W * 0.056)
    hl = int(H * 0.040)
    for hx in range(margin, W - margin, hs):
        p.drawLine(hx, soil_y, hx - hl, soil_y + hl)

    # ── 2. Figura T unificada (relleno + contorno ámbar) ─────────────
    col_l = cx - col_w // 2
    col_r = cx + col_w // 2
    col_t = ntn - col_h
    foot_l = cx - foot_w // 2
    foot_r = cx + foot_w // 2
    foot_b = foot_top + foot_h

    path = QPainterPath()
    path.moveTo(col_l,  col_t)
    path.lineTo(col_r,  col_t)
    path.lineTo(col_r,  foot_top)
    path.lineTo(foot_r, foot_top)
    path.lineTo(foot_r, foot_b)
    path.lineTo(foot_l, foot_b)
    path.lineTo(foot_l, foot_top)
    path.lineTo(col_l,  foot_top)
    path.closeSubpath()

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(gray)
    p.drawPath(path)

    outline_pen = QPen(amber, 3.5)
    outline_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
    p.setPen(outline_pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(path)

    # ── Borde exterior ámbar ─────────────────────────────────────────
    inset = 7
    border_pen = QPen(QColor("#d98a1f"), 5.5)
    border_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(border_pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(inset, inset, W - 2 * inset, H - 2 * inset, 38, 38)

    # ── "GeoCim" ─────────────────────────────────────────────────────
    p.setPen(QColor("white"))
    f = QFont("Archivo", 42, QFont.Weight.Bold)
    p.setFont(f)
    p.drawText(0, int(H * 0.628), W, 58, Qt.AlignmentFlag.AlignHCenter, "GeoCim")

    # ── "SUITE DE CIMENTACIONES" ──────────────────────────────────────
    p.setPen(QColor("#d98a1f"))
    f2 = QFont("IBM Plex Mono", 9, QFont.Weight.Normal)
    f2.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3.5)
    p.setFont(f2)
    p.drawText(0, int(H * 0.746), W, 22, Qt.AlignmentFlag.AlignHCenter,
               "SUITE DE CIMENTACIONES")

    # ── Línea roja ────────────────────────────────────────────────────
    p.setPen(QPen(QColor("#d4453b"), 2.5))
    p.drawLine(W // 2 - 88, int(H * 0.814), W // 2 + 88, int(H * 0.814))

    # ── Autor ─────────────────────────────────────────────────────────
    p.setPen(QColor("#7a8a9e"))
    f3 = QFont("IBM Plex Sans", 9)
    p.setFont(f3)
    p.drawText(0, int(H * 0.850), W, 24, Qt.AlignmentFlag.AlignHCenter,
               "Ing. Juan Christian Espinosa López")

    # ── "V1.0" en azul ────────────────────────────────────────────────
    p.setPen(QColor("#1f6fd6"))
    f4 = QFont("IBM Plex Mono", 16, QFont.Weight.Bold)
    p.setFont(f4)
    p.drawText(0, int(H * 0.904), W, 44, Qt.AlignmentFlag.AlignHCenter, "V1.0")

    p.end()
    return pm


class SplashGeoCim(QSplashScreen):
    def __init__(self):
        super().__init__(build_splash_pixmap())
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
