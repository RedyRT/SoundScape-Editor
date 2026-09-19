# make_splash.py — генерирует splash.png для бутлоадера PyInstaller.
# Геометрия и шрифты 1:1 из SplashScreen (SoundScapeEditor.py).
# ВАЖНО: рендерим на НАТИВНОЙ платформе, чтобы хинтинг шрифтов совпадал
# с живым Qt-сплэшем (offscreen — только headless-фолбэк). Это убирает
# «съезд шрифтов» на стыке двух сплэшей.
import os
import sys
import math
import random

try:
    from PySide6.QtGui import (QImage, QPainter, QColor, QPen, QBrush,
                               QLinearGradient, QFont, QPainterPath, QPolygonF,
                               QGuiApplication)
    from PySide6.QtCore import Qt, QRect, QRectF, QPointF
except ImportError:
    from PyQt6.QtGui import (QImage, QPainter, QColor, QPen, QBrush,
                             QLinearGradient, QFont, QPainterPath, QPolygonF,
                             QGuiApplication)
    from PyQt6.QtCore import Qt, QRect, QRectF, QPointF

# Сначала нативная платформа (идентичные шрифты рантайму).
# Если дисплея нет (CI/headless) — падаем на offscreen с системными шрифтами.
try:
    _app = QGuiApplication(sys.argv)
except Exception:
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    if sys.platform.startswith("win"):
        _FONTS = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    elif sys.platform == "darwin":
        _FONTS = "/System/Library/Fonts"
    else:
        _FONTS = "/usr/share/fonts"
    if os.path.isdir(_FONTS):
        os.environ.setdefault("QT_QPA_FONTDIR", _FONTS)
    _app = QGuiApplication(sys.argv)

W, H = 560, 320
SS = 4

LOGO_RECT  = (24, 24, 44, 44)
TITLE_RECT = (80, 26, W - 170, 26)
SUB_RECT   = (80, 50, W - 170, 20)
VER_RECT   = (W - 96, 26, 72, 44)
SEP_Y      = 84
EQ_X, EQ_W = 24, W - 48
EQ_CY, EQ_MAXH, EQ_N = 170, 56, 36
TX, TY, TW, TH = 24, H - 46, W - 48, 10
CAP_RECT   = (TX, H - 30, TW, 16)

# ---- 1) ФИГУРЫ в 4x (гладкие края, бинарная альфа) ----
img4 = QImage(W * SS, H * SS, QImage.Format.Format_ARGB32)
img4.fill(Qt.GlobalColor.transparent)
p = QPainter(img4)
p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
p.scale(SS, SS)

path = QPainterPath()
path.addRoundedRect(0.5, 0.5, W - 1, H - 1, 12, 12)
grad = QLinearGradient(0, 0, 0, H)
grad.setColorAt(0.0, QColor("#202326"))
grad.setColorAt(1.0, QColor("#141618"))
p.fillPath(path, QBrush(grad))
p.setPen(QPen(QColor("#f7941e"), 2))
p.drawPath(path)

logo = QPainterPath()
logo.addRoundedRect(LOGO_RECT[0], LOGO_RECT[1], LOGO_RECT[2], LOGO_RECT[3], 6, 6)
p.fillPath(logo, QBrush(QColor("#f7941e")))

p.setPen(QPen(QColor("#3f4245"), 1))
p.drawLine(24, SEP_Y, W - 24, SEP_Y)
p.setPen(QPen(QColor("#f7941e"), 2))
p.drawLine(24, SEP_Y, 96, SEP_Y)

# эквалайзер: фикс-кадр t=7 (тот же, что стартует в Qt-сплэше)
step = EQ_W / EQ_N
bw = max(2.0, step * 0.55)
p.setPen(Qt.PenStyle.NoPen)
t = 7
for i in range(EQ_N):
    f = 0.45 + 0.55 * (((i * 37) % 13) / 13.0)
    h = (0.18 + 0.82 * abs(math.sin(t * 0.11 + i * 0.47))) * EQ_MAXH * f
    col = QColor("#f7941e")
    col.setAlpha(int(120 + 135 * min(1.0, h / EQ_MAXH)))
    p.setBrush(QBrush(col))
    x = EQ_X + i * step + (step - bw) / 2.0
    p.drawRoundedRect(QRectF(x, EQ_CY - h, bw, 2 * h), 2, 2)

# индетерминат-бар (штриховка) вместо пустого прогресса
track = QPainterPath()
track.addRoundedRect(QRectF(TX + 0.5, TY + 0.5, TW - 1, TH - 1), 5, 5)
p.setPen(QPen(QColor("#3f4245"), 1))
p.setBrush(QBrush(QColor("#26282b")))
p.drawPath(track)
inner = QPainterPath()
inner.addRoundedRect(QRectF(TX + 1.5, TY + 1.5, TW - 3, TH - 3), 4, 4)
p.setClipPath(inner)
p.setPen(Qt.PenStyle.NoPen)
p.setBrush(QBrush(QColor("#3f4245")))
x = TX - TH
while x < TX + TW:
    p.drawPolygon(QPolygonF([
        QPointF(x, TY + TH), QPointF(x + 4, TY + TH),
        QPointF(x + 4 + TH, TY), QPointF(x + TH, TY)]))
    x += 12
p.setClipping(False)
p.end()

# даунсэмпл + бинарная альфа (0/255) — без розовых ореолов Tcl/Tk
img = img4.scaled(W, H, Qt.AspectRatioMode.IgnoreAspectRatio,
                  Qt.TransformationMode.SmoothTransformation)
for y in range(H):
    for x in range(W):
        c = img.pixelColor(x, y)
        if c.alpha() >= 128:
            c.setAlpha(255)
            img.setPixelColor(x, y, c)
        else:
            img.setPixelColor(x, y, QColor(0, 0, 0, 0))

# ---- 2) ТЕКСТ в 1x на нативной платформе = те же глифы, что в рантайме ----
p = QPainter(img)
p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

p.setPen(QColor("#101112"))
p.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
p.drawText(QRect(*LOGO_RECT), Qt.AlignmentFlag.AlignCenter, "λ")

p.setPen(QColor("#c7d0d9"))
p.setFont(QFont("Trebuchet MS", 15, QFont.Weight.Bold))
p.drawText(QRect(*TITLE_RECT),
           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
           "SOURCE SOUNDSCAPE EDITOR")

p.setPen(QColor("#7d858d"))
p.setFont(QFont("Consolas", 9))
p.drawText(QRect(*SUB_RECT),
           Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
           "// soundscape tool")
p.drawText(QRect(*VER_RECT),
           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, "v2.1")

p.setFont(QFont("Consolas", 8))
p.drawText(QRect(*CAP_RECT),
           Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
           "source engine // soundscape")
p.end()

img.save("splash.png")
print("splash.png сохранён (нативные шрифты, бесшовный стык)")