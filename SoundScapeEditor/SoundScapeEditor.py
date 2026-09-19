import sys
import os
import re
import json
import random
import math
import tempfile
from copy import deepcopy

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *

try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
except ImportError:
    try:
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    except ImportError:
        QMediaPlayer = None
        QAudioOutput = None

VLV = {
    "bg": "#1b1d1f", "panel": "#26282b", "field": "#333639",
    "border": "#3f4245", "fg": "#c7d0d9", "fg_dim": "#7d858d",
    "accent": "#f7941e", "accent_hi": "#ffb056", "accent_lo": "#c77415", "black": "#101112",
}
AUDIO_EXTS = (".wav", ".mp3", ".ogg")
DSP_ROOM_TYPES = [
    (0, "Normal (off)"), (1, "Generic"), (2, "Metal Small"), (3, "Metal Medium"),
    (4, "Metal Large"), (5, "Tunnel Small"), (6, "Tunnel Medium"), (7, "Tunnel Large"),
    (8, "Chamber Small"), (9, "Chamber Medium"), (10, "Chamber Large"),
    (11, "Bright Small"), (12, "Bright Medium"), (13, "Bright Large"),
    (14, "Water 1"), (15, "Water 2"), (16, "Water 3"),
    (17, "Concrete Small"), (18, "Concrete Medium"), (19, "Concrete Large"),
    (20, "Big 1"), (21, "Big 2"), (22, "Big 3"),
    (23, "Cavern Small"), (24, "Cavern Medium"), (25, "Cavern Large"),
    (26, "Weirdo 1"), (27, "Weirdo 2"), (28, "Weirdo 3"), (29, "Weirdo 4"),
]
SNDLVL_LIST = [
    "SNDLVL_NONE", "SNDLVL_20dB", "SNDLVL_25dB", "SNDLVL_30dB", "SNDLVL_35dB",
    "SNDLVL_40dB", "SNDLVL_45dB", "SNDLVL_50dB", "SNDLVL_55dB", "SNDLVL_60dB",
    "SNDLVL_IDLE", "SNDLVL_65dB", "SNDLVL_STATIC", "SNDLVL_70dB", "SNDLVL_75dB",
    "SNDLVL_NORM", "SNDLVL_80dB", "SNDLVL_TALKING", "SNDLVL_85dB", "SNDLVL_90dB",
    "SNDLVL_95dB", "SNDLVL_100dB", "SNDLVL_105dB", "SNDLVL_110dB", "SNDLVL_120dB",
    "SNDLVL_125dB", "SNDLVL_130dB", "SNDLVL_GUNFIRE", "SNDLVL_140dB", "SNDLVL_145dB",
    "SNDLVL_150dB", "SNDLVL_180dB",
]
SNDLVL_ATTENUATION = {
    "SNDLVL_NONE": 0.0,
    "SNDLVL_20dB": 20.0, "SNDLVL_25dB": 15.0, "SNDLVL_30dB": 10.0,
    "SNDLVL_35dB": 7.0, "SNDLVL_40dB": 5.0, "SNDLVL_45dB": 4.5,
    "SNDLVL_50dB": 3.9, "SNDLVL_55dB": 3.0, "SNDLVL_60dB": 2.0,
    "SNDLVL_IDLE": 2.0, "SNDLVL_65dB": 1.5, "SNDLVL_STATIC": 1.25,
    "SNDLVL_70dB": 1.0, "SNDLVL_75dB": 0.8, "SNDLVL_NORM": 0.8,
    "SNDLVL_80dB": 0.7, "SNDLVL_TALKING": 0.7, "SNDLVL_85dB": 0.6,
    "SNDLVL_90dB": 0.5, "SNDLVL_95dB": 0.45, "SNDLVL_100dB": 0.4,
    "SNDLVL_105dB": 0.35, "SNDLVL_110dB": 0.32, "SNDLVL_120dB": 0.3,
    "SNDLVL_125dB": 0.29, "SNDLVL_130dB": 0.28, "SNDLVL_GUNFIRE": 0.27,
    "SNDLVL_140dB": 0.2, "SNDLVL_145dB": 0.2, "SNDLVL_150dB": 0.2,
    "SNDLVL_180dB": 0.15,
}
SOUND_CHANNELS = [
    "CHAN_AUTO", "CHAN_WEAPON", "CHAN_VOICE", "CHAN_ITEM",
    "CHAN_BODY", "CHAN_STREAM", "CHAN_STATIC", "CHAN_REPLACE",
    "CHAN_WEAPON2",
]
LANGS = {
    "ru": {
        "file": "Файл", "lang": "Язык", "history": "История",
        "new": "Новый файл", "open": "Открыть...", "save": "Сохранить",
        "save_as": "Сохранить как...", "exit": "Выход",
        "untitled": "Новый файл",
        "list_cap": "Soundscape список:", "add": "+ Добавить", "del": "- Удалить",
        "search_list": "Поиск в списке...", "preview_tip": "Предпрослушка",
        "tab_general": "Основные (General)", "tab_pos": "Позиции (0-7)",
        "tab_global": "Глобальные звуки", "tab_soundscript": "Soundscripts",
        "placeholder": "Выберите или создайте запись",
        "name_lbl": "Имя Soundscape (для env_soundscape):",
        "name_ss_lbl": "Имя Soundscript (для ambient_generic):",
        "dsp": "DSP (тип комнаты):", "dsp_spatial": "DSP spatial (пространственный):",
        "dsp_vol": "DSP volume (громкость DSP-эффекта):",
        "atten": "Attenuation (затухание, напр. 0.8):",
        "not_set": "(не задано)", "channel": "Channel (звуковой канал):",
        "wave": "Wave (путь к звуку):", "pitch": "Pitch (напр. 95,105):",
        "soundlevel": "Soundlevel:", "attenuation": "Attenuation:",
        "volume": "Volume:",
        "loop_cap": "Play Looping (фоновые звуки)", "add_loop": "+ Добавить Looping",
        "rand_cap": "Play Random (случайные звуки)", "add_rand": "+ Добавить Random",
        "time": "Time (сек):", "pos": "Position (0-7 / random):",
        "origin": "Origin (x,y,z):",
        "del_block": "Удалить", "del_rblock": "Удалить блок",
        "rnd_cap": "Список звуков (rndwave):", "add_wave": "+ Добавить звук в rndwave",
        "file_type_scape": "[SOUNDSCAPE]", "file_type_script": "[SOUNDSCRIPT]",
        "ready": "Готов",
        "status_new": "Создан новый файл", "status_open": "Открыт",
        "status_saved": "Сохранено", "status_add": "Добавлена запись",
        "status_del": "Удалена запись",
        "status_copy": "Скопирована запись", "status_paste": "Вставлена запись",
        "status_undo": "Отменено", "status_redo": "Возвращено",
        "browse_title": "Выбор звука", "search": "Поиск:",
        "dbl_hint": "Двойной клик — выбрать звук",
        "cancel": "Отмена", "choose": "Выбрать",
        "no_sound_dir_t": "Папка sound не найдена",
        "no_sound_dir": ("Не удалось найти папку 'sound' рядом с папкой 'scripts',\n"
                         "в которой лежит открытый файл.\n"
                         "Откройте (или сохраните) файл из папки scripts вашего мода/игры."),
        "confirm_t": "Подтверждение", "confirm_del": "Удалить '{name}'?",
        "success_t": "Успех", "saved_msg": "Файл успешно сохранен!",
        "error_t": "Ошибка", "read_err": "Не удалось прочитать файл:",
        "save_err": "Не удалось сохранить файл:",
        "preview_sc": "Предпрослушка soundscape",
        "stop_sc": "Остановить предпрослушку",
        "prev_playing": "Играет: loop {loops}, random {rand}",
        "prev_stopped": "Предпрослушка остановлена",
        "prev_noroot": "Папка sound не найдена — предпрослушка невозможна",
        "prev_empty": "В этом soundscape нет звуков для предпрослушки",
        "prev_script_na": "Предпрослушка всего файла недоступна для soundscripts (это скрипты ambient_generic)",
        "unsaved_t": "Несохранённые изменения",
        "unsaved_msg": "В файле есть несохранённые изменения.\nСохранить их перед закрытием?",
        "b_save": "Сохранить", "b_discard": "Не сохранять", "b_cancel": "Отмена",
        "hist_initial": "Исходное состояние",
        "hist_more": "…ещё {n}",
        "hist_nochange": "без изменений",
        "hist_hint": "Клик по шагу — откат к состоянию",
        "hist_steps": "шагов: {n}",
        "float_tip": "Отстыковать / пристыковать",
        "close_tip": "Закрыть панель истории",
        "master_vol": "Громкость:",
        "open_recent": "Открыть недавние",
        "clear_recent": "Очистить список",
        "no_recent": "(пусто)",
    },
    "en": {
        "file": "File", "lang": "Language", "history": "History",
        "new": "New file", "open": "Open...", "save": "Save",
        "save_as": "Save as...", "exit": "Exit",
        "untitled": "New file",
        "list_cap": "Soundscape list:", "add": "+ Add", "del": "- Delete",
        "search_list": "Search in list...", "preview_tip": "Preview",
        "tab_general": "General", "tab_pos": "Positions (0-7)",
        "tab_global": "Global sounds", "tab_soundscript": "Soundscripts",
        "placeholder": "Select or create an entry",
        "name_lbl": "Soundscape name (for env_soundscape):",
        "name_ss_lbl": "Soundscript name (for ambient_generic):",
        "dsp": "DSP (room type):", "dsp_spatial": "DSP spatial:",
        "dsp_vol": "DSP volume (DSP effect volume):",
        "atten": "Attenuation (e.g. 0.8):",
        "not_set": "(not set)", "channel": "Channel:",
        "wave": "Wave (sound path):", "pitch": "Pitch (e.g. 95,105):",
        "soundlevel": "Soundlevel:", "attenuation": "Attenuation:",
        "volume": "Volume:",
        "loop_cap": "Play Looping (background sounds)", "add_loop": "+ Add Looping",
        "rand_cap": "Play Random (random sounds)", "add_rand": "+ Add Random",
        "time": "Time (sec):", "pos": "Position (0-7 / random):",
        "origin": "Origin (x,y,z):",
        "del_block": "Delete", "del_rblock": "Delete block",
        "rnd_cap": "Sound list (rndwave):", "add_wave": "+ Add sound to rndwave",
        "file_type_scape": "[SOUNDSCAPE]", "file_type_script": "[SOUNDSCRIPT]",
        "ready": "Ready",
        "status_new": "New file created", "status_open": "Opened",
        "status_saved": "Saved", "status_add": "Added entry",
        "status_del": "Deleted entry",
        "status_copy": "Copied entry", "status_paste": "Pasted entry",
        "status_undo": "Undone", "status_redo": "Redone",
        "browse_title": "Select sound", "search": "Search:",
        "dbl_hint": "Double click — select sound",
        "cancel": "Cancel", "choose": "Select",
        "no_sound_dir_t": "sound folder not found",
        "no_sound_dir": ("Could not find the 'sound' folder next to the 'scripts' folder\n"
                         "containing the opened file.\n"
                         "Open (or save) the file from the scripts folder of your mod/game."),
        "confirm_t": "Confirmation", "confirm_del": "Delete '{name}'?",
        "success_t": "Success", "saved_msg": "File saved successfully!",
        "error_t": "Error", "read_err": "Failed to read file:",
        "save_err": "Failed to save file:",
        "preview_sc": "Preview soundscape",
        "stop_sc": "Stop preview",
        "prev_playing": "Playing: {loops} loops, {rand} random",
        "prev_stopped": "Preview stopped",
        "prev_noroot": "sound folder not found — preview unavailable",
        "prev_empty": "No sounds to preview in this soundscape",
        "prev_script_na": "Whole-file preview not available for soundscripts (ambient_generic scripts)",
        "unsaved_t": "Unsaved changes",
        "unsaved_msg": "The file has unsaved changes.\nSave them before closing?",
        "b_save": "Save", "b_discard": "Don't save", "b_cancel": "Cancel",
        "hist_initial": "Initial state",
        "hist_more": "…+{n} more",
        "hist_nochange": "no changes",
        "hist_hint": "Click a step to roll back to it",
        "hist_steps": "steps: {n}",
        "float_tip": "Undock / dock",
        "close_tip": "Close history panel",
        "master_vol": "Volume:",
        "open_recent": "Open Recent",
        "clear_recent": "Clear List",
        "no_recent": "(empty)",
    },
}

STYLE = """
QMainWindow, QDialog { background: %(bg)s; }
QWidget { background: %(panel)s; color: %(fg)s; font-family: "Segoe UI"; font-size: 9pt; }
QLabel { background: transparent; }
QLineEdit { background: %(field)s; color: %(fg)s; border: 1px solid %(border)s;
padding: 3px; selection-background-color: %(accent)s; selection-color: %(black)s; }
QLineEdit:focus { border-color: %(accent)s; }
QPushButton { background: %(field)s; color: %(fg)s; border: 1px solid %(border)s; padding: 4px 12px; }
QPushButton:hover { background: %(accent)s; color: %(black)s; border-color: %(accent)s; }
QPushButton:pressed { background: %(accent_lo)s; }
QPushButton:disabled { color: %(fg_dim)s; background: %(panel)s; border-color: %(border)s; }
QToolButton { background: %(panel)s; color: %(fg)s; border: 1px solid %(border)s; padding: 4px 14px; font-weight: bold; }
QToolButton:hover { background: %(accent)s; color: %(black)s; border-color: %(accent)s; }
QToolButton:checked { background: %(accent)s; color: %(black)s; border-color: %(accent)s; }
QToolButton::menu-arrow { width: 0px; }
QMenu { background: %(panel)s; color: %(fg)s; border: 1px solid %(border)s; padding: 4px; }
QMenu::item { padding: 5px 24px; }
QMenu::item:selected { background: %(accent)s; color: %(black)s; }
QMenu::item:checked { background: %(field)s; }
QMenu::separator { height: 1px; background: %(border)s; margin: 4px 8px; }
QListWidget { background: %(field)s; color: %(fg)s; border: 1px solid %(border)s; outline: 0; }
QListWidget::item { padding: 3px; }
QListWidget::item:selected { background: %(accent)s; color: %(black)s; }
QListWidget#historyList { alternate-background-color: #2b2e31; border: none;
font-family: Consolas; font-size: 8pt; }
QListWidget#historyList::item { padding: 4px; }
QListWidget#historyList::item:selected { background: %(accent)s; color: %(black)s; }
QTabWidget::pane { border: 1px solid %(border)s; background: %(panel)s; }
QTabBar::tab { background: %(panel)s; color: %(fg)s; padding: 6px 14px; border: 1px solid %(border)s; font-weight: bold; }
QTabBar::tab:selected { background: %(accent)s; color: %(black)s; }
QGroupBox { border: 1px solid %(border)s; margin-top: 12px; padding: 10px 6px 6px 6px; }
QGroupBox::title { color: %(accent)s; subcontrol-origin: margin; left: 8px; padding: 0 4px; font-weight: bold; }
QScrollArea { border: none; background: %(panel)s; }
QScrollBar:vertical { background: %(bg)s; width: 12px; }
QScrollBar::handle:vertical { background: %(field)s; border-radius: 4px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: %(accent)s; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: %(bg)s; height: 12px; }
QScrollBar::handle:horizontal { background: %(field)s; border-radius: 4px; }
QScrollBar::handle:horizontal:hover { background: %(accent)s; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QTreeView { background: %(field)s; color: %(fg)s; border: 1px solid %(border)s; font-family: Consolas; }
QTreeView::item:selected { background: %(accent)s; color: %(black)s; }
QHeaderView::section { background: %(panel)s; color: %(fg)s; border: 1px solid %(border)s; padding: 4px; }
QStatusBar { background: %(black)s; color: %(fg_dim)s; }
QSizeGrip { background: transparent; image: url("@grip@"); }
QSplitter::handle { background: %(border)s; width: 4px; }
QMessageBox { background: %(panel)s; }
QDockWidget { background: %(panel)s; color: %(fg)s; }
QDockWidget::title { background: %(black)s; color: %(fg)s; padding: 5px; font-weight: bold; }
#histFloatBtn { background: transparent; border: none; }
#histFloatBtn[hovered="true"] { background: %(accent)s; }
#histFloatBtn:pressed { background: %(accent_lo)s; }
#histCloseBtn { background: transparent; border: none; }
#histCloseBtn[hovered="true"] { background: #e81123; }
#histCloseBtn:pressed { background: #9b0f1a; }
QComboBox { background: %(field)s; color: %(fg)s; border: 1px solid %(border)s; padding: 3px; }
QComboBox:hover { border-color: %(accent)s; }
QComboBox::drop-down { border: none; width: 18px; }
QComboBox::down-arrow { image: url("@arrow_down@"); width: 10px; height: 6px; margin-right: 5px; }
QComboBox QAbstractItemView { background: %(field)s; color: %(fg)s; border: 1px solid %(accent)s;
selection-background-color: %(accent)s; selection-color: %(black)s; }
QSpinBox, QDoubleSpinBox { background: %(field)s; color: %(fg)s; border: 1px solid %(border)s; padding: 2px; }
QSpinBox:focus, QDoubleSpinBox:focus { border-color: %(accent)s; }
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button { background: %(border)s; width: 16px; border: none; }
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background: %(accent)s; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: url("@spin_up@"); width: 10px; height: 6px; }
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: url("@spin_down@"); width: 10px; height: 6px; }
QSlider { background: transparent; }
QSlider::groove:horizontal { background: %(field)s; height: 6px; border-radius: 3px; }
QSlider::sub-page:horizontal { background: %(accent)s; border-radius: 3px; }
QSlider::handle:horizontal { background: %(fg)s; width: 12px; margin: -5px 0; border-radius: 4px; }
QSlider::handle:horizontal:hover { background: %(accent_hi)s; }
""" % VLV

def apply_dark_titlebar(win):
    """Тёмная системная шапка; применяется только к настоящим окнам."""
    try:
        if not win.isWindow():
            return
        import ctypes
        hwnd = int(win.winId())
        value = ctypes.c_int(1)
        for attr in (20, 19):
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                break
    except Exception:
        pass

def _ensure_arrow_assets():
    """Рисует crisp-иконки: рендер в devicePixelRatio экрана + антиалиасинг."""
    d = os.path.join(tempfile.gettempdir(), "sse_ui_assets")
    os.makedirs(d, exist_ok=True)
    try:
        dpr = QGuiApplication.primaryScreen().devicePixelRatio()
    except Exception:
        dpr = 1.0
    if not dpr or dpr <= 0:
        dpr = 1.0
    specs = {
        "arrow_down": ("down", VLV["fg_dim"], 10, 6),
        "spin_up": ("up", VLV["fg_dim"], 10, 6),
        "spin_down": ("down", VLV["fg_dim"], 10, 6),
        "close_x": ("close", "#ffffff", 12, 12),
        "float_icon": ("float", "#ffffff", 12, 12),
        "grip": ("grip", VLV["fg_dim"], 14, 14),
    }
    out = {}
    for name, (shape, color, w, h) in specs.items():
        pw = max(2, int(round(w * dpr)))
        ph = max(2, int(round(h * dpr)))
        path = os.path.join(d, name + ".png").replace("\\", "/")
        img = QImage(pw, ph, QImage.Format.Format_ARGB32)
        img.fill(Qt.GlobalColor.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        col = QColor(color)
        if shape in ("down", "up"):
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(col)
            if shape == "down":
                pts = [QPointF(0.5, 0.5), QPointF(pw - 0.5, 0.5), QPointF(pw / 2.0, ph - 0.5)]
            else:
                pts = [QPointF(pw / 2.0, 0.5), QPointF(pw - 0.5, ph - 0.5), QPointF(0.5, ph - 0.5)]
            p.drawPolygon(QPolygonF(pts))
        else:
            pen = QPen(col)
            pen.setWidthF(max(1.0, 1.6 * dpr))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            m = 2.0 * dpr
            if shape == "close":
                p.drawLine(QPointF(m, m), QPointF(pw - m, ph - m))
                p.drawLine(QPointF(pw - m, m), QPointF(m, ph - m))
            elif shape == "float":
                p.drawRect(QRectF(m, m, pw - 2 * m, ph - 2 * m))
            elif shape == "grip":
                pen.setWidthF(max(1.0, 1.4 * dpr))
                p.setPen(pen)
                for off in (0.0, 3.5 * dpr, 7.0 * dpr):
                    p.drawLine(QPointF(pw - m - off, ph - m),
                               QPointF(pw - m, ph - m - off))
        p.end()
        img.save(path)
        out[name] = path
    return out

def build_style():
    s = STYLE
    for k, p in _ensure_arrow_assets().items():
        s = s.replace(f"@{k}@", p)
    return s

class SplashScreen(QSplashScreen):
    """Уникальный сплэш: тёмная карточка Valve с λ-логотипом,
    анимированным эквалайзером и прогресс-баром загрузки."""
    W, H = 560, 320
    BAR_COUNT = 36

    def __init__(self):
        self._tick = 7
        self._progress = 0.0
        self._stage = ""
        super().__init__(self._build_base())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.SplashScreen
                            | Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint)
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._animate)
        self._timer.start()

    def _build_base(self):
        W, H = self.W, self.H
        pm = QPixmap(W, H)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(0.5, 0.5, W - 1, H - 1, 12, 12)
        grad = QLinearGradient(0, 0, 0, H)
        grad.setColorAt(0.0, QColor("#202326"))
        grad.setColorAt(1.0, QColor("#141618"))
        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor("#f7941e"), 2))
        p.drawPath(path)
        logo = QPainterPath()
        logo.addRoundedRect(24, 24, 44, 44, 6, 6)
        p.fillPath(logo, QBrush(QColor("#f7941e")))
        p.setPen(QPen(QColor("#101112")))
        p.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        p.drawText(QRect(24, 24, 44, 44), Qt.AlignmentFlag.AlignCenter, "λ")
        p.setPen(QPen(QColor("#c7d0d9")))
        p.setFont(QFont("Trebuchet MS", 15, QFont.Weight.Bold))
        p.drawText(QRect(80, 26, W - 170, 26),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   "SOURCE SOUNDSCAPE EDITOR")
        p.setPen(QPen(QColor("#7d858d")))
        p.setFont(QFont("Consolas", 9))
        p.drawText(QRect(80, 50, W - 170, 20),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   "// soundscape tool")
        p.drawText(QRect(W - 96, 26, 72, 44),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, "v2.1")
        p.setPen(QPen(QColor("#3f4245"), 1))
        p.drawLine(24, 84, W - 24, 84)
        p.setPen(QPen(QColor("#f7941e"), 2))
        p.drawLine(24, 84, 96, 84)
        p.end()
        return pm

    def _animate(self):
        self._tick += 1
        self.repaint()

    def set_progress(self, v):
        self._progress = max(0.0, min(1.0, v))
        self.repaint()

    def set_stage(self, text):
        self._stage = text
        self.repaint()

    def drawContents(self, painter):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        W, H = self.W, self.H
        area_x, area_w = 24, W - 48
        cy, maxh = 170, 56
        n = self.BAR_COUNT
        step = area_w / n
        bw = max(2.0, step * 0.55)
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(n):
            f = 0.45 + 0.55 * (((i * 37) % 13) / 13.0)
            h = (0.18 + 0.82 * abs(math.sin(self._tick * 0.11 + i * 0.47))) * maxh * f
            x = area_x + i * step + (step - bw) / 2.0
            col = QColor("#f7941e")
            col.setAlpha(int(120 + 135 * min(1.0, h / maxh)))
            painter.setBrush(QBrush(col))
            painter.drawRoundedRect(QRectF(x, cy - h, bw, 2 * h), 2, 2)
        tx, ty, tw, th = 24, H - 46, W - 48, 10
        painter.setPen(QPen(QColor("#3f4245"), 1))
        painter.setBrush(QBrush(QColor("#26282b")))
        painter.drawRoundedRect(QRectF(tx + 0.5, ty + 0.5, tw - 1, th - 1), 5, 5)
        painter.save()
        painter.setClipRect(QRectF(tx + 1, ty + 1, tw - 2, th - 2))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#3f4245")))
        off = (self._tick * 0.7) % 12.0
        x = tx - th + off - 12
        while x < tx + tw + th:
            painter.drawPolygon(QPolygonF([
                QPointF(x, ty + th), QPointF(x + 4, ty + th),
                QPointF(x + 4 + th, ty), QPointF(x + th, ty)]))
            x += 12
        painter.restore()
        pw = (tw - 4) * self._progress
        if pw > 1:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#f7941e")))
            painter.drawRoundedRect(QRectF(tx + 2, ty + 2, pw, th - 4), 3, 3)
            painter.save()
            painter.setClipRect(QRectF(tx + 2, ty + 2, pw, th - 4))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 46)))
            off2 = (self._tick * 0.7) % 12.0
            x2 = tx - th + off2 - 12
            while x2 < tx + pw + th:
                painter.drawPolygon(QPolygonF([
                    QPointF(x2, ty + th), QPointF(x2 + 4, ty + th),
                    QPointF(x2 + 4 + th, ty), QPointF(x2 + th, ty)]))
                x2 += 12
            painter.restore()
        painter.setPen(QPen(QColor("#7d858d")))
        painter.setFont(QFont("Consolas", 9))
        painter.drawText(QRect(tx, ty - 22, tw, 18),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._stage)
        painter.drawText(QRect(tx, ty - 22, tw, 18),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                         f"{int(self._progress * 100)}%")
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(QRect(tx, H - 30, tw, 16),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                         "source engine // soundscape")

class SoundBrowser(QDialog):
    def __init__(self, parent, root_dir):
        super().__init__(parent)
        self.ed = parent
        self.root_dir = root_dir
        self.result_path = None
        self._preview_started = False
        self.setWindowTitle(self.ed.t("browse_title"))
        self.resize(640, 520)
        v = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel(self.ed.t("search")))
        self.search = QLineEdit()
        top.addWidget(self.search, 1)
        v.addLayout(top)
        hint = QLabel(root_dir)
        hint.setStyleSheet(f"color: {VLV['fg_dim']}; font-family: Consolas; font-size: 8pt;")
        v.addWidget(hint)
        self.model = QFileSystemModel()
        self.model.setRootPath(root_dir)
        self.model.setNameFilters(["*.wav", "*.mp3", "*.ogg"])
        self.model.setNameFilterDisables(False)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_dir))
        for c in (1, 2, 3):
            self.tree.hideColumn(c)
        self.tree.doubleClicked.connect(self._on_tree_double)
        self.tree.selectionModel().selectionChanged.connect(
            lambda *a: self.ed._refresh_preview_buttons())
        v.addWidget(self.tree, 1)
        self.results = QListWidget()
        self.results.hide()
        self.results.itemDoubleClicked.connect(self._on_result_double)
        self.results.currentRowChanged.connect(
            lambda *a: self.ed._refresh_preview_buttons())
        v.addWidget(self.results, 1)
        bot = QHBoxLayout()
        hint2 = QLabel(self.ed.t("dbl_hint"))
        hint2.setStyleSheet(f"color: {VLV['fg_dim']}; font-family: Consolas; font-size: 8pt;")
        bot.addWidget(hint2)
        bot.addStretch(1)
        prev = QPushButton("▶")
        prev.setFixedWidth(32)
        prev.setToolTip(self.ed.t("preview_tip"))
        prev.clicked.connect(self._preview_current)
        self.ed._register_preview_button(prev, self._current_rel)
        bot.addWidget(prev)
        cancel = QPushButton(self.ed.t("cancel"))
        cancel.clicked.connect(self.reject)
        ok = QPushButton(self.ed.t("choose"))
        ok.clicked.connect(self._choose_current)
        bot.addWidget(cancel)
        bot.addWidget(ok)
        v.addLayout(bot)
        self.search.textChanged.connect(self._on_search)
        apply_dark_titlebar(self)

    def rel(self, p):
        return os.path.relpath(p, self.root_dir).replace("\\", "/")

    def _current_rel(self):
        if self.results.isVisible() and self.results.currentItem():
            return self.results.currentItem().text()
        if self.tree.selectionModel().hasSelection():
            p = self.model.filePath(self.tree.currentIndex())
            if os.path.isfile(p):
                return self.rel(p)
        return None

    def _preview_current(self):
        rel = self._current_rel()
        if rel:
            self.ed.preview_sound(rel)
            self._preview_started = True

    def _on_search(self, q):
        q = q.strip().lower()
        if not q:
            self.results.hide()
            self.tree.show()
            return
        self.tree.hide()
        self.results.show()
        self.results.clear()
        count = 0
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            for f in filenames:
                if f.lower().endswith(AUDIO_EXTS):
                    full = os.path.join(dirpath, f)
                    rel = self.rel(full)
                    if q in rel.lower():
                        self.results.addItem(rel)
                        count += 1
                        if count >= 300:
                            return

    def _on_tree_double(self, index):
        p = self.model.filePath(index)
        if os.path.isfile(p):
            self.result_path = self.rel(p)
            self.accept()

    def _on_result_double(self, item):
        self.result_path = item.text()
        self.accept()

    def _choose_current(self):
        rel = self._current_rel()
        if rel:
            self.result_path = rel
            self.accept()

class SoundscapeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1100, 780)
        self.data = {}
        self.current_sc = None
        self.filepath = None
        self.file_type = "soundscape"
        self._sb_widgets = []
        self._clipboard = None
        self._undo_stack = []
        self._redo_stack = []
        self._preview_players = []
        self._preview_oneshots = []
        self._preview_timers = []
        self._preview_info = None
        self._preview_buttons = []
        self._preview_outputs = []
        self._last_preview_rel = None
        self._dirty = False
        self._saved_sig = ""
        self._tab_key = "general"
        self._history_list = None
        self.history_dock = None
        self._history_guard = False
        self._hist_expanded = False
        self._hist_icon_cache = {}
        self._hist_sig = []
        self._restoring = False
        self._hist_hover_watch = set()
        self._states_current = 0
        self._hist_count_lbl = None

        settings = self.load_settings()
        self.lang = settings.get("lang", "en")
        if self.lang not in LANGS:
            self.lang = "en"
        self.last_dir = settings.get("last_dir", "")
        self.recent_files = settings.get("recent_files", [])
        if not isinstance(self.recent_files, list):
            self.recent_files = []

        if not os.path.isfile(self.settings_path()):
            self.save_settings()
        try:
            self.master_volume = max(0.0, min(1.0, float(settings.get("master_volume", 1.0))))
        except Exception:
            self.master_volume = 1.0

        self.setAcceptDrops(True)
        self.setup_icon()
        self._init_player()
        self.setup_menu_and_ui()
        self._setup_history_dock()

        self._hist_refresh_timer = QTimer(self)
        self._hist_refresh_timer.setSingleShot(True)
        self._hist_refresh_timer.setInterval(200)
        self._hist_refresh_timer.timeout.connect(self.refresh_history)
        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(lambda: self.status_label.setText(self.t("ready")))
        apply_dark_titlebar(self)
        self.refresh_title()

    @staticmethod
    def detect_file_type(path):
        if not path:
            return "soundscape"
        name = os.path.basename(path).lower()
        if "_level_sounds" in name:
            return "soundscript"
        return "soundscape"

    def _is_soundscript(self):
        return self.file_type == "soundscript"

    def _init_player(self):
        try:
            self.player = QMediaPlayer()
            self.audio_out = QAudioOutput()
            self.audio_out.setVolume(self.master_volume)
            self.player.setAudioOutput(self.audio_out)
            self.player.playbackStateChanged.connect(lambda _: self._refresh_preview_buttons())
            self.player.mediaStatusChanged.connect(lambda _: self._refresh_preview_buttons())
        except Exception:
            self.player = None
            self.audio_out = None
        self._last_preview = None

    def set_master_volume(self, v, save=False):
        v = max(0.0, min(1.0, float(v)))
        self.master_volume = v
        if self.audio_out is not None:
            try:
                self.audio_out.setVolume(v)
            except Exception:
                pass
        for ao, base in list(self._preview_outputs):
            try:
                ao.setVolume(min(base * v, 1.0))
            except RuntimeError:
                pass
        if hasattr(self, "_vol_pct"):
            self._vol_pct.setText(f"{int(round(v * 100))}%")
        if save:
            self.save_settings()

    def preview_sound(self, rel_path):
        if self.player is None or not rel_path:
            return
        root_dir = self.get_sound_root()
        full = None
        if root_dir:
            cand = os.path.join(root_dir, rel_path.replace("/", os.sep))
            if os.path.isfile(cand):
                full = cand
        if full is None and os.path.isfile(rel_path):
            full = rel_path
        if full is None:
            return
        if self._last_preview == full and \
                self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()
            self._last_preview = None
            self._last_preview_rel = None
            self._refresh_preview_buttons()
            return
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(full))
        self.player.play()
        self._last_preview = full
        self._last_preview_rel = rel_path
        self._refresh_preview_buttons()

    def _register_preview_button(self, btn, provider):
        self._preview_buttons.append({"btn": btn, "provider": provider})

    def _refresh_preview_buttons(self):
        if self.player is None:
            return
        playing = self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        cur_rel = self._last_preview_rel if playing else None
        alive = []
        for rec in self._preview_buttons:
            btn = rec["btn"]
            try:
                is_cur = playing and (rec["provider"]() == cur_rel)
                btn.setText("■" if is_cur else "▶")
                btn.setToolTip(self.t("stop_sc") if is_cur else self.t("preview_tip"))
                alive.append(rec)
            except RuntimeError:
                continue
        self._preview_buttons = alive

    def _preview_active(self):
        return bool(self._preview_players or self._preview_timers)

    @staticmethod
    def _parse_single(text, default):
        try:
            return float(str(text).split(",")[0].strip())
        except Exception:
            return default

    @staticmethod
    def _attenuation_to_gain(block):
        sl = str(block.get("soundlevel", "")).strip()
        if sl in SNDLVL_ATTENUATION:
            att = SNDLVL_ATTENUATION[sl]
        else:
            try:
                att = float(str(block.get("attenuation", "1.0")).strip())
            except Exception:
                att = 1.0
        if att <= 0:
            return 1.0
        return 1.0 / (1.0 + att * 0.25)

    def _resolve_wave(self, root, wave):
        w = str(wave).strip()
        if w and w[0] in "()":
            w = w[1:]
        if not w:
            return None
        full = os.path.join(root, w.replace("/", os.sep))
        return full if os.path.isfile(full) else None

    def _make_preview_player(self, root, block, looping):
        wave = str(block.get("wave", "")).strip()
        if not wave:
            return None
        full = self._resolve_wave(root, wave)
        if not full:
            return None
        try:
            pl = QMediaPlayer(self)
            ao = QAudioOutput(self)
            pl.setAudioOutput(ao)
            base_vol = min(max(self._parse_single(block.get("volume"), 1.0), 0.0), 2.0)
            atten_gain = self._attenuation_to_gain(block)
            base = base_vol * atten_gain
            ao.setVolume(min(base * self.master_volume, 1.0))
            self._preview_outputs.append((ao, base))
            rate = self._parse_single(block.get("pitch"), 100.0) / 100.0
            pl.setPlaybackRate(min(max(rate, 0.5), 2.0))
            pl.setSource(QUrl.fromLocalFile(full))
            if looping:
                pl.setLoops(getattr(QMediaPlayer, "Infinite", -1))
            pl.play()
            return pl
        except Exception:
            return None

    def preview_start(self):
        self.preview_stop()
        if self.current_sc is None or self.player is None:
            return
        if self._is_soundscript():
            self.prev_label.setText(self.t("prev_script_na"))
            return
        root = self.get_sound_root()
        if not root:
            self.prev_label.setText(self.t("prev_noroot"))
            return
        sc = self.data[self.current_sc]
        loops = []
        for i in range(8):
            b = sc.get(f"position{i}")
            if isinstance(b, list):
                b = b[0] if b else None
            if isinstance(b, dict) and b.get("wave"):
                loops.append(b)
        for b in self._ensure_list(sc, "playlooping"):
            if isinstance(b, dict) and b.get("wave"):
                loops.append(b)
        rands = [b for b in self._ensure_list(sc, "playrandom") if isinstance(b, dict)]
        for b in loops:
            p = self._make_preview_player(root, b, True)
            if p:
                self._preview_players.append(p)
        for b in rands:
            self._start_random_preview(b, root)
        if not self._preview_players and not self._preview_timers:
            self.prev_label.setText(self.t("prev_empty"))
            return
        self._preview_info = (len(self._preview_players), len(self._preview_timers))
        self._sync_preview_ui()

    def _start_random_preview(self, block, root):
        timer = QTimer(self)
        timer.setSingleShot(True)
        def fire():
            if not self._preview_active():
                return
            ao = None
            try:
                waves = [w for w in self._ensure_rndwave(block) if w]
                if waves:
                    full = self._resolve_wave(root, random.choice(waves))
                    if full:
                        pl = QMediaPlayer(self)
                        ao = QAudioOutput(self)
                        pl.setAudioOutput(ao)
                        vmin, vmax = self._parse_pair(block.get("volume"), 1.0, 1.0)
                        base_vol = random.uniform(vmin, vmax)
                        atten_gain = self._attenuation_to_gain(block)
                        base = base_vol * atten_gain
                        ao.setVolume(min(base * self.master_volume, 1.0))
                        self._preview_outputs.append((ao, base))
                        pmin, pmax = self._parse_pair(block.get("pitch"), 100.0, 100.0)
                        pl.setPlaybackRate(min(max(random.uniform(pmin, pmax) / 100.0, 0.5), 2.0))
                        pl.setSource(QUrl.fromLocalFile(full))
                        pl.mediaStatusChanged.connect(
                            lambda st, pl=pl, ao=ao: self._oneshot_finished(st, pl, ao))
                        pl.play()
                        self._preview_oneshots.append(pl)
            except Exception:
                pass
            tmin, tmax = self._parse_pair(block.get("time"), 5.0, 15.0)
            timer.start(int(random.uniform(tmin, tmax) * 1000))
        timer.timeout.connect(fire)
        self._preview_timers.append(timer)
        tmin, tmax = self._parse_pair(block.get("time"), 5.0, 15.0)
        timer.start(int(random.uniform(tmin, tmax) * 1000))

    def _oneshot_finished(self, status, pl, ao=None):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            pl.stop()
            pl.deleteLater()
            if pl in self._preview_oneshots:
                self._preview_oneshots.remove(pl)
            if ao is not None:
                self._preview_outputs = [p for p in self._preview_outputs if p[0] is not ao]

    def preview_stop(self):
        was = self._preview_active()
        for t in self._preview_timers:
            t.stop()
            t.deleteLater()
        self._preview_timers = []
        for pl in self._preview_players + self._preview_oneshots:
            try:
                pl.stop()
                pl.deleteLater()
            except Exception:
                pass
        self._preview_players = []
        self._preview_oneshots = []
        self._preview_outputs = []
        if was and hasattr(self, "prev_label"):
            self.prev_label.setText(self.t("prev_stopped"))
        self._sync_preview_ui()

    def _sync_preview_ui(self):
        if not hasattr(self, "prev_stop_btn"):
            return
        active = self._preview_active()
        self.prev_stop_btn.setEnabled(active)
        if active and self._preview_info:
            self.prev_label.setText(
                self.t("prev_playing", loops=self._preview_info[0], rand=self._preview_info[1]))

    def _content_sig(self):
        try:
            return self._serialize_all()
        except Exception:
            return repr(self.data)

    def _mark_clean(self):
        self._saved_sig = self._content_sig()
        self._dirty = False
        self.refresh_title()

    def _check_dirty(self):
        self._dirty = (self._content_sig() != self._saved_sig)
        return self._dirty

    def _mark_dirty(self):
        was = self._dirty
        if self._check_dirty() != was:
            self.refresh_title()
        self._schedule_history_refresh()

    def _schedule_history_refresh(self):
        if getattr(self, "_hist_refresh_timer", None) is not None:
            self._hist_refresh_timer.start()

    def confirm_discard(self):
        if not self._check_dirty():
            return True
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle(self.t("unsaved_t"))
        box.setText(self.t("unsaved_msg"))
        b_save = box.addButton(self.t("b_save"), QMessageBox.ButtonRole.AcceptRole)
        b_disc = box.addButton(self.t("b_discard"), QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(self.t("b_cancel"), QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(b_save)
        box.exec()
        clicked = box.clickedButton()
        if clicked is b_save:
            self.save_file()
            return not self._check_dirty()
        if clicked is b_disc:
            return True
        return False

    def closeEvent(self, event):
        if not self.confirm_discard():
            event.ignore()
            return
        self.preview_stop()
        self.save_settings()
        event.accept()

    @staticmethod
    def _has_txt_url(e):
        if not e.mimeData().hasUrls():
            return False
        return any(u.toLocalFile().lower().endswith(".txt") for u in e.mimeData().urls())

    def dragEnterEvent(self, e):
        if self._has_txt_url(e):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if self._has_txt_url(e):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            p = u.toLocalFile()
            if p and p.lower().endswith(".txt"):
                if self.confirm_discard():
                    self.open_path(p)
                break
        e.acceptProposedAction()

    def _rel_for_drop(self, p):
        root = self.get_sound_root()
        if root:
            rp = os.path.relpath(p, root)
            if not rp.startswith(".."):
                return rp.replace("\\", "/")
        return p.replace("\\", "/")

    def _update_hist_btn_hover(self):
        gp = QCursor.pos()
        for btn in (getattr(self, "_hist_float_btn", None), getattr(self, "_hist_close_btn", None)):
            if btn is None:
                continue
            inside = btn.isVisible() and btn.rect().contains(btn.mapFromGlobal(gp))
            if btn.property("hovered") != inside:
                btn.setProperty("hovered", inside)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
                btn.update()

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.Enter, QEvent.Type.Leave, QEvent.Type.MouseMove):
            if obj in self._hist_hover_watch:
                self._update_hist_btn_hover()
        if event.type() == QEvent.Type.Wheel and \
                isinstance(obj, (QAbstractSpinBox, QComboBox)):
            if obj.hasFocus():
                return False
            parent = obj.parent()
            while parent is not None and not isinstance(parent, QScrollArea):
                parent = parent.parent()
            if parent is not None:
                QApplication.sendEvent(parent.viewport(), event)
            return True
        if isinstance(obj, QLineEdit) and obj.property("wave_edit"):
            t = event.type()
            if t in (QEvent.Type.DragEnter, QEvent.Type.DragMove):
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                    return True
                return False
            if t == QEvent.Type.Drop:
                urls = event.mimeData().urls()
                if urls:
                    p = urls[0].toLocalFile()
                    if p.lower().endswith(AUDIO_EXTS):
                        obj.setText(self._rel_for_drop(p))
                        event.acceptProposedAction()
                        return True
                return False
        if event.type() == QEvent.Type.FocusIn and \
                isinstance(obj, (QLineEdit, QComboBox, QAbstractSpinBox)):
            if not self._restoring:
                self._push_history()
        return super().eventFilter(obj, event)

    def _snapshot(self):
        return (deepcopy(self.data), self.current_sc, self.file_type)

    def _push_history(self):
        snap = self._snapshot()
        if not (self._undo_stack and self._undo_stack[-1] == snap):
            self._undo_stack.append(snap)
            if len(self._undo_stack) > 50:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
        self._mark_dirty()

    def _undo_step(self):
        self._redo_stack.append(self._snapshot())
        data, cur, ft = self._undo_stack.pop()
        self.data, self.current_sc, self.file_type = data, cur, ft

    def _redo_step(self):
        self._undo_stack.append(self._snapshot())
        data, cur, ft = self._redo_stack.pop()
        self.data, self.current_sc, self.file_type = data, cur, ft

    def _reset_history(self):
        self._undo_stack = []
        self._redo_stack = []
        self._hist_sig = []

    @staticmethod
    def _fmt_val(v):
        if isinstance(v, dict):
            return "{…}"
        if isinstance(v, list):
            return f"[{len(v)}]"
        s = str(v)
        if len(s) > 48:
            s = s[:45] + "…"
        return f'"{s}"'

    @staticmethod
    def _diff_lines(a, b, path="", out=None):
        if out is None:
            out = []
        for k in list(dict.fromkeys(list(a.keys()) + list(b.keys()))):
            p = f"{path}.{k}" if path else str(k)
            if k not in a:
                out.append(f"+ {p} = {SoundscapeEditor._fmt_val(b[k])}")
                continue
            if k not in b:
                out.append(f"- {p} = {SoundscapeEditor._fmt_val(a[k])}")
                continue
            va, vb = a[k], b[k]
            if isinstance(va, dict) and isinstance(vb, dict):
                SoundscapeEditor._diff_lines(va, vb, p, out)
            elif isinstance(va, list) and isinstance(vb, list):
                if len(va) != len(vb):
                    out.append(f"{p}: [{len(va)}] → [{len(vb)}]")
                for i, (xa, xb) in enumerate(zip(va, vb)):
                    if isinstance(xa, dict) and isinstance(xb, dict):
                        SoundscapeEditor._diff_lines(xa, xb, f"{p}[{i + 1}]", out)
                    elif xa != xb:
                        out.append(f"{p}[{i + 1}]: {SoundscapeEditor._fmt_val(xa)} → {SoundscapeEditor._fmt_val(xb)}")
            elif va != vb:
                out.append(f"{p}: {SoundscapeEditor._fmt_val(va)} → {SoundscapeEditor._fmt_val(vb)}")
        return out

    def _states(self):
        cur = self._snapshot()
        prefix = list(self._undo_stack)
        if not (prefix and prefix[-1] == cur):
            prefix.append(cur)
        self._states_current = len(prefix) - 1
        return prefix + list(reversed(self._redo_stack))

    def _hist_icon(self, kind):
        if kind in self._hist_icon_cache:
            return self._hist_icon_cache[kind]
        color = {"add": "#8bd08b", "del": "#e07b7b", "init": VLV["fg_dim"]}.get(kind, VLV["accent"])
        pm = QPixmap(14, 14)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        pen = QPen(QColor(color))
        pen.setWidth(2)
        p.setPen(pen)
        if kind == "add":
            p.drawLine(7, 3, 7, 11)
            p.drawLine(3, 7, 11, 7)
        elif kind == "del":
            p.drawLine(3, 7, 11, 7)
        elif kind == "init":
            p.drawEllipse(4, 4, 6, 6)
        else:
            p.drawLine(3, 7, 10, 7)
            p.drawLine(7, 4, 10, 7)
            p.drawLine(7, 10, 10, 7)
        p.end()
        ic = QIcon(pm)
        self._hist_icon_cache[kind] = ic
        return ic

    def refresh_history(self, scroll=True):
        if self._history_list is None:
            return
        self._history_guard = True
        try:
            sb = self._history_list.verticalScrollBar()
            spos = sb.value()
            states = self._states()
            cur = self._states_current
            rows = []
            for i, st in enumerate(states):
                if i == 0:
                    lines = []
                    label = self.t("hist_initial")
                    kind = "init"
                else:
                    lines = self._diff_lines(states[i - 1][0], st[0])
                    if not lines:
                        label = self.t("hist_nochange")
                        kind = "edit"
                    else:
                        raw = lines[0]
                        kind = {"+": "add", "-": "del"}.get(raw[0], "edit")
                        if raw.startswith("+ ") or raw.startswith("- "):
                            label = raw[2:]
                        else:
                            label = raw
                        if len(lines) > 1:
                            label += " " + self.t("hist_more", n=len(lines) - 1)
                rows.append((label, kind, "\n".join(lines) if lines else label))
            sig = [(lbl, kind) for lbl, kind, _ in rows]
            same = (sig == self._hist_sig and self._history_list.count() == len(rows))
            if same:
                for i, (_, _, tip) in enumerate(rows):
                    it = self._history_list.item(i)
                    if i > cur:
                        it.setForeground(QColor(VLV["fg_dim"]))
                    else:
                        it.setData(Qt.ItemDataRole.ForegroundRole, None)
                    it.setToolTip(tip)
            else:
                self._history_list.clear()
                for i, (label, kind, tip) in enumerate(rows):
                    item = QListWidgetItem(label)
                    item.setToolTip(tip)
                    item.setIcon(self._hist_icon(kind))
                    if i > cur:
                        item.setForeground(QColor(VLV["fg_dim"]))
                    self._history_list.addItem(item)
                self._hist_sig = sig
            if 0 <= cur < self._history_list.count():
                idx = self._history_list.model().index(cur, 0)
                self._history_list.selectionModel().setCurrentIndex(
                    idx,
                    QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
                if scroll:
                    self._history_list.scrollTo(idx)
                elif not same:
                    sb.setValue(spos)
            else:
                sb.setValue(spos)
            if self._hist_count_lbl is not None:
                self._hist_count_lbl.setText(self.t("hist_steps", n=len(states)))
        finally:
            self._history_guard = False
        if not scroll:
            QTimer.singleShot(0, self._sync_hist_selection)

    def _sync_hist_selection(self):
        if self._history_list is None:
            return
        cur = self._states_current
        if not (0 <= cur < self._history_list.count()):
            return
        sel = [ix.row() for ix in self._history_list.selectionModel().selectedRows()]
        if self._history_list.currentRow() == cur and sel == [cur]:
            return
        self._history_guard = True
        try:
            idx = self._history_list.model().index(cur, 0)
            self._history_list.selectionModel().setCurrentIndex(
                idx,
                QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
        finally:
            self._history_guard = False

    def _on_history_click(self, row):
        if self._history_guard or row < 0:
            return
        self.goto_state(row, scroll=False)

    def goto_state(self, i, scroll=True):
        states = self._states()
        if i < 0 or i >= len(states):
            return
        target = states[i]
        cur_idx = self._states_current
        before = self.data
        guard = 0
        while self._snapshot() != target and guard < 300:
            if i <= cur_idx:
                if not self._undo_stack:
                    break
                self._undo_step()
            else:
                if not self._redo_stack:
                    break
                self._redo_step()
            guard += 1
        self._restoring = True
        try:
            self._refresh_after_history(before)
        finally:
            self._restoring = False
        self.refresh_history(scroll=scroll)
        self.refresh_title()

    def _setup_history_dock(self):
        wrap = QWidget()
        vl = QVBoxLayout(wrap)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)
        self._history_list = QListWidget()
        self._history_list.setObjectName("historyList")
        self._history_list.setAlternatingRowColors(True)
        self._history_list.setIconSize(QSize(14, 14))
        self._history_list.currentRowChanged.connect(self._on_history_click)
        vl.addWidget(self._history_list, 1)
        tb = QWidget()
        tb.setObjectName("histTitleBar")
        tb.setFixedHeight(32)
        tb.setStyleSheet(f"#histTitleBar {{ background: {VLV['black']}; }}")
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(8, 0, 0, 0)
        tl.setSpacing(6)
        self._hist_title_lbl = QLabel(self.t("history"))
        self._hist_title_lbl.setStyleSheet(f"color: {VLV['fg']}; font-weight: bold; background: transparent;")
        self._hist_count_lbl = QLabel("")
        self._hist_count_lbl.setStyleSheet(f"color: {VLV['fg_dim']}; font-family: Consolas; font-size: 8pt; background: transparent;")
        self._hist_hint_lbl = QLabel(self.t("hist_hint"))
        self._hist_hint_lbl.setStyleSheet(f"color: {VLV['fg_dim']}; font-size: 8pt; background: transparent;")
        self._hist_float_btn = QPushButton("")
        self._hist_float_btn.setObjectName("histFloatBtn")
        self._hist_float_btn.setFixedSize(36, 32)
        self._hist_float_btn.setProperty("hovered", False)
        self._hist_float_btn.setToolTip(self.t("float_tip"))
        self._hist_float_btn.setIcon(self._ui_icon("float_icon"))
        self._hist_float_btn.setIconSize(QSize(12, 12))
        self._hist_float_btn.clicked.connect(
            lambda: self.history_dock.setFloating(not self.history_dock.isFloating()))
        self._hist_close_btn = QPushButton("")
        self._hist_close_btn.setObjectName("histCloseBtn")
        self._hist_close_btn.setFixedSize(46, 32)
        self._hist_close_btn.setProperty("hovered", False)
        self._hist_close_btn.setToolTip(self.t("close_tip"))
        self._hist_close_btn.setIcon(self._ui_icon("close_x"))
        self._hist_close_btn.setIconSize(QSize(12, 12))
        self._hist_close_btn.clicked.connect(lambda: self.history_dock.hide())
        tl.addWidget(self._hist_title_lbl)
        tl.addWidget(self._hist_count_lbl)
        tl.addStretch(1)
        tl.addWidget(self._hist_hint_lbl)
        tl.addWidget(self._hist_float_btn)
        tl.addWidget(self._hist_close_btn)
        self.history_dock = QDockWidget(self)
        self.history_dock.setObjectName("historyDock")
        self.history_dock.setWindowTitle(self.t("history"))
        self.history_dock.setTitleBarWidget(tb)
        self.history_dock.setWidget(wrap)
        self.history_dock.setMinimumWidth(320)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.history_dock)
        self.history_dock.visibilityChanged.connect(self._on_history_visibility)
        self._hist_hover_watch = {
            tb, wrap, self.history_dock,
            self._hist_float_btn, self._hist_close_btn,
            self._hist_title_lbl, self._hist_count_lbl, self._hist_hint_lbl,
            self._history_list,
            self._history_list.viewport(),
            self._history_list.verticalScrollBar(),
        }
        for w in self._hist_hover_watch:
            w.installEventFilter(self)
        self._hist_hover_timer = QTimer(self)
        self._hist_hover_timer.setInterval(100)
        self._hist_hover_timer.timeout.connect(self._update_hist_btn_hover)
        self._hist_hover_timer.start()
        self.history_dock.hide()
        self.refresh_history()

    def _on_history_visibility(self, vis):
        if getattr(self, "hist_btn", None) is not None:
            self.hist_btn.setChecked(vis)
        DW = 460
        if vis:
            self.refresh_history()
            geo = self.screen().availableGeometry() if self.screen() else None
            if geo is not None and self.width() + DW <= geo.width():
                self._hist_expanded = True
                self.resize(self.width() + DW, self.height())
            else:
                self._hist_expanded = False
        else:
            if getattr(self, "_hist_expanded", False):
                self.resize(max(1000, self.width() - DW), self.height())
                self._hist_expanded = False
        self._update_hist_btn_hover()

    def _toggle_history(self, checked):
        if self.history_dock is not None:
            self.history_dock.setVisible(checked)

    def _tab_widget_by_key(self, key):
        return {
            "general": self.scroll_general,
            "pos": self.scroll_pos,
            "global": self.scroll_global,
            "script": self.scroll_script,
        }.get(key)

    def _on_tab_changed(self, idx):
        w = self.tabs.widget(idx)
        for key, widget in (("general", self.scroll_general),
                            ("pos", self.scroll_pos),
                            ("global", self.scroll_global),
                            ("script", self.scroll_script)):
            if widget is w:
                self._tab_key = key
                break

    def _diff_tab(self, old_data, new_data):
        if self._is_soundscript():
            name = self.current_sc
            if name is not None and name in old_data and name in new_data:
                if old_data[name] != new_data[name]:
                    return "script"
            return None
        if set(old_data.keys()) != set(new_data.keys()):
            return None
        name = self.current_sc
        if name is None or name not in old_data or name not in new_data:
            return None
        a, b = old_data[name], new_data[name]
        pos_keys = {f"position{i}" for i in range(8)}
        glob_keys = {"playlooping", "playrandom"}
        changed = []
        if {k: a.get(k) for k in pos_keys} != {k: b.get(k) for k in pos_keys}:
            changed.append("pos")
        if {k: a.get(k) for k in glob_keys} != {k: b.get(k) for k in glob_keys}:
            changed.append("global")
        if {k: v for k, v in a.items() if k not in pos_keys and k not in glob_keys} != \
           {k: v for k, v in b.items() if k not in pos_keys and k not in glob_keys}:
            changed.append("general")
        return changed[0] if len(changed) == 1 else None

    def _refresh_after_history(self, before_data=None):
        self._rebuild_tabs_for_type()
        self.refresh_list()
        if self.current_sc in self.data:
            self.build_right_panel()
        else:
            self.current_sc = None
            self.clear_right_panel()
        if before_data is not None:
            target = self._diff_tab(before_data, self.data)
            w = self._tab_widget_by_key(target) if target else None
            if w is not None and self.tabs.indexOf(w) >= 0:
                self.tabs.setCurrentWidget(w)

    def undo(self):
        if isinstance(QApplication.focusWidget(), (QLineEdit, QComboBox, QAbstractSpinBox)):
            return
        if not self._undo_stack:
            return
        before = self.data
        self._undo_step()
        self._restoring = True
        try:
            self._refresh_after_history(before)
        finally:
            self._restoring = False
        self.refresh_history()
        self.refresh_title()
        self.set_status(self.t("status_undo"))

    def redo(self):
        if isinstance(QApplication.focusWidget(), (QLineEdit, QComboBox, QAbstractSpinBox)):
            return
        if not self._redo_stack:
            return
        before = self.data
        self._redo_step()
        self._restoring = True
        try:
            self._refresh_after_history(before)
        finally:
            self._restoring = False
        self.refresh_history()
        self.refresh_title()
        self.set_status(self.t("status_redo"))

    def copy_soundscape(self):
        if self.current_sc is None or self.current_sc not in self.data:
            return
        self._clipboard = {
            "name": self.current_sc,
            "data": deepcopy(self.data[self.current_sc]),
        }
        self.set_status(f"{self.t('status_copy')}: {self.current_sc}")

    def paste_soundscape(self):
        if self._clipboard is None:
            return
        self._push_history()
        base = self._clipboard["name"]
        name = f"{base}_copy"
        counter = 2
        while name in self.data:
            name = f"{base}_copy_{counter}"
            counter += 1
        self.data[name] = deepcopy(self._clipboard["data"])
        self.refresh_list()
        rows = [self.listbox.item(i).text() for i in range(self.listbox.count())]
        if name in rows:
            self.listbox.setCurrentRow(rows.index(name))
        self.set_status(f"{self.t('status_paste')}: {name}")

    def t(self, key, **kw):
        s = LANGS[self.lang].get(key, LANGS["ru"].get(key, key))
        return s.format(**kw) if kw else s

    def settings_path(self):
        if getattr(sys, "frozen", False):
            base = os.path.dirname(os.path.abspath(sys.executable))
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "settings.json")

    def load_settings(self):
        try:
            with open(self.settings_path(), encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_settings(self):
        try:
            with open(self.settings_path(), "w", encoding="utf-8") as f:
                json.dump({"lang": self.lang, "last_dir": self.last_dir,
                           "master_volume": self.master_volume,
                           "recent_files": self.recent_files}, f)
        except Exception:
            pass

    def apply_language(self, lang):
        if lang == self.lang or lang not in LANGS:
            return
        self.lang = lang
        self.save_settings()
        old_menus = [getattr(self, "file_menu", None), getattr(self, "lang_menu", None)]
        old_search = self.search_edit.text() if getattr(self, "search_edit", None) else ""
        dock_vis = self.history_dock.isVisible() if self.history_dock else False
        old_central = self.takeCentralWidget()
        if old_central:
            old_central.deleteLater()
        self.setup_menu_and_ui()
        for m in old_menus:
            if m:
                m.deleteLater()
        if self.history_dock is not None:
            self.history_dock.setWindowTitle(self.t("history"))
            if getattr(self, "_hist_title_lbl", None) is not None:
                self._hist_title_lbl.setText(self.t("history"))
            if getattr(self, "_hist_hint_lbl", None) is not None:
                self._hist_hint_lbl.setText(self.t("hist_hint"))
            if getattr(self, "_hist_float_btn", None) is not None:
                self._hist_float_btn.setToolTip(self.t("float_tip"))
            if getattr(self, "_hist_close_btn", None) is not None:
                self._hist_close_btn.setToolTip(self.t("close_tip"))
            self.history_dock.setVisible(dock_vis)
            self.hist_btn.setChecked(dock_vis)
        self.search_edit.setText(old_search)
        self.refresh_list()
        if self.current_sc in self.data:
            self.build_right_panel()
        else:
            self.current_sc = None
            self.clear_right_panel()
        self.refresh_title()
        self.refresh_history()
        self.status_label.setText(self.t("ready"))

    def refresh_title(self):
        self._dirty = (self._content_sig() != self._saved_sig)
        base = os.path.basename(self.filepath) if self.filepath else self.t("untitled")
        star = " *" if self._dirty else ""
        ftype = self.t("file_type_script" if self._is_soundscript() else "file_type_scape")
        self.setWindowTitle(f"{base}{star} {ftype} - Source Soundscape Editor")

    @staticmethod
    def _is_frozen():
        return getattr(sys, "frozen", False)

    def _base_dir(self):
        if self._is_frozen():
            return os.path.dirname(os.path.abspath(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))

    def _bundled_ico(self):
        base = getattr(sys, "_MEIPASS", None)
        if base:
            p = os.path.join(base, "soundscape.ico")
            if os.path.isfile(p):
                return p
        return None

    def setup_icon(self):
        icon = None
        if self._is_frozen():
            try:
                prov = QFileIconProvider()
                icon = prov.icon(QFileInfo(sys.executable))
            except Exception:
                icon = None
            if icon is None or icon.isNull():
                for p in (self._bundled_ico(),
                          os.path.join(self._base_dir(), "soundscape.ico")):
                    if p and os.path.isfile(p):
                        icon = QIcon(p)
                        break
        else:
            p = os.path.join(self._base_dir(), "soundscape.ico")
            try:
                if not os.path.isfile(p):
                    with open(p, "wb") as f:
                        f.write(self._build_icon_bytes())
                icon = QIcon(p)
            except Exception:
                icon = None
        if icon is not None and not icon.isNull():
            self.setWindowIcon(icon)

    def _ui_icon(self, name):
        path = os.path.join(tempfile.gettempdir(), "sse_ui_assets", name + ".png")
        pm = QPixmap(path)
        try:
            pm.setDevicePixelRatio(QGuiApplication.primaryScreen().devicePixelRatio())
        except Exception:
            pass
        return QIcon(pm)

    @staticmethod
    def _build_icon_bytes():
        import struct, math
        W = H = 32
        DARK = (27, 29, 31, 255)
        ORANGE = (247, 148, 30, 255)
        TRANSPARENT = (0, 0, 0, 0)
        def in_rounded(x, y, x0, y0, x1, y1, r):
            cx = min(max(x, x0 + r), x1 - r)
            cy = min(max(y, y0 + r), y1 - r)
            return (x - cx) ** 2 + (y - cy) ** 2 <= r * r
        grid = [[TRANSPARENT] * W for _ in range(H)]
        for y in range(H):
            for x in range(W):
                if in_rounded(x, y, 0, 0, W - 1, H - 1, 6):
                    grid[y][x] = DARK
                if in_rounded(x, y, 0, 0, W - 1, H - 1, 6) and \
                   not in_rounded(x, y, 2, 2, W - 3, H - 3, 4):
                    grid[y][x] = ORANGE
        for y in range(13, 19):
            for x in range(7, 12):
                grid[y][x] = ORANGE
        for x in range(12, 18):
            half = 3 + (x - 12)
            for y in range(16 - half, 17 + half):
                if 0 <= y < H:
                    grid[y][x] = ORANGE
        for y in range(H):
            for x in range(19, W):
                d = math.hypot(x - 13, y - 16)
                if (abs(d - 10) <= 0.9 or abs(d - 14) <= 0.9) and \
                   in_rounded(x, y, 2, 2, W - 3, H - 3, 4):
                    grid[y][x] = ORANGE
        pixels = bytearray()
        for y in range(H - 1, -1, -1):
            for r, g, b, a in grid[y]:
                pixels += bytes((b, g, r, a))
        and_mask = b"\x00" * (4 * H)
        bih = struct.pack("<IiiHHIIiiII", 40, W, H * 2, 1, 32, 0,
                          len(pixels) + len(and_mask), 0, 0, 0, 0)
        image = bih + bytes(pixels) + and_mask
        header = struct.pack("<HHH", 0, 1, 1)
        entry = struct.pack("<BBBBHHII", W, H, 0, 0, 1, 32, len(image), 22)
        return header + entry + image

    def setup_menu_and_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_lay = QVBoxLayout(central)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)
        header = QWidget()
        header.setObjectName("headerBar")
        header.setStyleSheet(f"#headerBar {{ background: {VLV['black']}; }}")
        header.setFixedHeight(52)
        h = QHBoxLayout(header)
        h.setContentsMargins(12, 8, 12, 8)
        lam = QLabel("λ")
        lam.setStyleSheet(f"background: {VLV['accent']}; color: {VLV['black']}; font-size: 16px; font-weight: bold; padding: 2px 8px;")
        h.addWidget(lam)
        title = QLabel("SOURCE SOUNDSCAPE EDITOR")
        title.setStyleSheet(f"background: transparent; color: {VLV['fg']}; font-family: 'Trebuchet MS'; font-size: 14px; font-weight: bold;")
        h.addWidget(title)
        sub = QLabel("// soundscape tool")
        sub.setStyleSheet(f"background: transparent; color: {VLV['fg_dim']}; font-family: Consolas;")
        h.addWidget(sub)
        h.addStretch(1)
        self.hist_btn = QToolButton()
        self.hist_btn.setText(self.t("history"))
        self.hist_btn.setCheckable(True)
        self.hist_btn.clicked.connect(self._toggle_history)
        if self.history_dock is not None:
            self.hist_btn.setChecked(self.history_dock.isVisible())
        h.addWidget(self.hist_btn)
        self.lang_menu = QMenu(self)
        for code, label in (("ru", "Русский"), ("en", "English")):
            act = self.lang_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(code == self.lang)
            act.triggered.connect(lambda _=False, c=code: self.apply_language(c))
        lang_btn = QToolButton()
        lang_btn.setText(self.t("lang"))
        lang_btn.setPopupMode(QToolButton.InstantPopup)
        lang_btn.setMenu(self.lang_menu)
        h.addWidget(lang_btn)
        
        self.file_menu = QMenu(self)
        self.file_menu.addAction(self.t("new"), self.new_file)
        self.file_menu.addAction(self.t("open"), self.open_file)
        self.recent_menu = QMenu(self.t("open_recent"), self.file_menu)
        self.file_menu.addMenu(self.recent_menu)
        self._update_recent_menu()
        self.file_menu.addAction(self.t("save"), self.save_file)
        self.file_menu.addAction(self.t("save_as"), self.save_file_as)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.t("exit"), self.close)
        
        file_btn = QToolButton()
        file_btn.setText(self.t("file"))
        file_btn.setPopupMode(QToolButton.InstantPopup)
        file_btn.setMenu(self.file_menu)
        h.addWidget(file_btn)
        root_lay.addWidget(header)
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"background: {VLV['accent']};")
        root_lay.addWidget(sep)
        prev_bar = QWidget()
        prev_bar.setObjectName("previewBar")
        prev_bar.setStyleSheet(f"#previewBar {{ background: {VLV['panel']}; border-bottom: 1px solid {VLV['border']}; }}")
        prev_bar.setFixedHeight(36)
        pbx = QHBoxLayout(prev_bar)
        pbx.setContentsMargins(10, 4, 10, 4)
        pbx.setSpacing(6)
        self.prev_play_btn = QPushButton("▶")
        self.prev_play_btn.setFixedWidth(32)
        self.prev_play_btn.setToolTip(self.t("preview_sc"))
        self.prev_play_btn.clicked.connect(self.preview_start)
        self.prev_stop_btn = QPushButton("■")
        self.prev_stop_btn.setFixedWidth(32)
        self.prev_stop_btn.setToolTip(self.t("stop_sc"))
        self.prev_stop_btn.clicked.connect(self.preview_stop)
        self.prev_label = QLabel(self.t("preview_sc"))
        self.prev_label.setStyleSheet(f"color: {VLV['fg_dim']};")
        pbx.addWidget(self.prev_play_btn)
        pbx.addWidget(self.prev_stop_btn)
        pbx.addWidget(self.prev_label, 1)
        self._vol_lbl = QLabel(self.t("master_vol"))
        self._vol_lbl.setStyleSheet(f"color: {VLV['fg_dim']};")
        pbx.addWidget(self._vol_lbl)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setFixedWidth(140)
        self.vol_slider.setValue(int(round(self.master_volume * 100)))
        self.vol_slider.valueChanged.connect(lambda v: self.set_master_volume(v / 100.0))
        self.vol_slider.sliderReleased.connect(self.save_settings)
        pbx.addWidget(self.vol_slider)
        self._vol_pct = QLabel(f"{int(round(self.master_volume * 100))}%")
        self._vol_pct.setFixedWidth(42)
        self._vol_pct.setStyleSheet(f"color: {VLV['fg']}; font-family: Consolas; font-size: 8pt;")
        pbx.addWidget(self._vol_pct)
        root_lay.addWidget(prev_bar)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        lv = QVBoxLayout(left)
        cap = QLabel(self.t("list_cap"))
        cap.setStyleSheet("font-weight: bold;")
        lv.addWidget(cap)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.t("search_list"))
        self.search_edit.textChanged.connect(self._apply_filter)
        lv.addWidget(self.search_edit)
        self.listbox = QListWidget()
        self.listbox.currentRowChanged.connect(self._on_select)
        lv.addWidget(self.listbox, 1)
        QShortcut(QKeySequence("Del"), self.listbox, activated=self.delete_soundscape)
        QShortcut(QKeySequence.StandardKey.Copy, self.listbox, activated=self.copy_soundscape)
        QShortcut(QKeySequence.StandardKey.Paste, self.listbox, activated=self.paste_soundscape)
        QShortcut(QKeySequence.StandardKey.Undo, self, activated=self.undo)
        QShortcut(QKeySequence.StandardKey.Redo, self, activated=self.redo)
        btns = QHBoxLayout()
        add_b = QPushButton(self.t("add"))
        add_b.clicked.connect(self.add_soundscape)
        del_b = QPushButton(self.t("del"))
        del_b.clicked.connect(self.delete_soundscape)
        btns.addWidget(add_b)
        btns.addWidget(del_b)
        lv.addLayout(btns)
        splitter.addWidget(left)
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.general_content = QWidget()
        self.general_layout = QVBoxLayout(self.general_content)
        self.pos_content = QWidget()
        self.pos_layout = QVBoxLayout(self.pos_content)
        self.global_content = QWidget()
        self.global_layout = QVBoxLayout(self.global_content)
        self.script_content = QWidget()
        self.script_layout = QVBoxLayout(self.script_content)
        self.scroll_general = self._wrap_scroll(self.general_content)
        self.scroll_pos = self._wrap_scroll(self.pos_content)
        self.scroll_global = self._wrap_scroll(self.global_content)
        self.scroll_script = self._wrap_scroll(self.script_content)
        splitter.addWidget(self.tabs)
        splitter.setSizes([250, 850])
        root_lay.addWidget(splitter, 1)
        sb = self.statusBar()
        for w in self._sb_widgets:
            sb.removeWidget(w)
        self._sb_widgets = []
        self.status_label = QLabel(self.t("ready"))
        self._sb_widgets.append(self.status_label)
        sb.addWidget(self.status_label, 1)
        right_lbl = QLabel("source engine // soundscape")
        right_lbl.setStyleSheet(f"color: {VLV['fg_dim']}; font-family: Consolas; font-size: 8pt;")
        self._sb_widgets.append(right_lbl)
        sb.addPermanentWidget(right_lbl)
        grip = sb.findChild(QSizeGrip)
        if grip is not None:
            grip.setFixedSize(16, 16)
        self._rebuild_tabs_for_type()
        self.clear_right_panel()
        self._sync_preview_ui()

    def _rebuild_tabs_for_type(self):
        key = getattr(self, "_tab_key", "general")
        while self.tabs.count():
            self.tabs.removeTab(0)
        if self._is_soundscript():
            self.tabs.addTab(self.scroll_script, self.t("tab_soundscript"))
        else:
            self.tabs.addTab(self.scroll_general, self.t("tab_general"))
            self.tabs.addTab(self.scroll_pos, self.t("tab_pos"))
            self.tabs.addTab(self.scroll_global, self.t("tab_global"))
        w = self._tab_widget_by_key(key)
        if w is not None and self.tabs.indexOf(w) >= 0:
            self.tabs.setCurrentWidget(w)

    def _wrap_scroll(self, content):
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(content)
        return area

    def set_status(self, text, timeout=3000):
        self.status_label.setText(text)
        self._status_timer.start(timeout)

    def refresh_list(self):
        self._apply_filter(self.search_edit.text())

    def _apply_filter(self, text):
        q = text.strip().lower()
        self.listbox.blockSignals(True)
        self.listbox.clear()
        for name in self.data:
            if not q or q in name.lower():
                self.listbox.addItem(name)
        if self.current_sc is not None:
            rows = [self.listbox.item(i).text() for i in range(self.listbox.count())]
            if self.current_sc in rows:
                self.listbox.setCurrentRow(rows.index(self.current_sc))
        self.listbox.blockSignals(False)

    def parse_kv(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            QMessageBox.critical(self, self.t("error_t"), f"{self.t('read_err')}\n{e}")
            return {}
        text = re.sub(r'//.*', '', text)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        tokens = re.findall(r'"[^"]*"|\{|\}', text)
        def parse_block(idx):
            result = {}
            while idx < len(tokens):
                token = tokens[idx]
                if token == '}':
                    return result, idx + 1
                key = token.strip('"')
                idx += 1
                if idx < len(tokens) and tokens[idx] == '{':
                    idx += 1
                    nested, idx = parse_block(idx)
                    if key in result:
                        if isinstance(result[key], list):
                            result[key].append(nested)
                        else:
                            result[key] = [result[key], nested]
                    else:
                        result[key] = nested
                else:
                    value = tokens[idx].strip('"')
                    idx += 1
                    if key in result:
                        if isinstance(result[key], list):
                            result[key].append(value)
                        else:
                            result[key] = [result[key], value]
                    else:
                        result[key] = value
            return result, idx
        root = {}
        idx = 0
        while idx < len(tokens):
            if tokens[idx] in ('{', '}'):
                idx += 1
                continue
            key = tokens[idx].strip('"')
            idx += 1
            if idx < len(tokens) and tokens[idx] == '{':
                idx += 1
                nested, idx = parse_block(idx)
                root[key] = nested
        return root

    def serialize_kv(self, data, indent=1):
        lines = []
        ind = "    " * indent
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        if key == "rndwave":
                            lines.append(f'{ind}"{key}"')
                            lines.append(f'{ind}{{')
                            for w in self._get_waves(item):
                                lines.append(f'{ind}    "wave" "{w}"')
                            lines.append(f'{ind}}}')
                        else:
                            lines.append(f'{ind}"{key}"')
                            lines.append(f'{ind}{{')
                            lines.append(self.serialize_kv(item, indent + 1))
                            lines.append(f'{ind}}}')
                    else:
                        lines.append(f'{ind}"{key}" "{item}"')
            else:
                if isinstance(value, dict):
                    if key == "rndwave":
                        lines.append(f'{ind}"{key}"')
                        lines.append(f'{ind}{{')
                        for w in self._get_waves(value):
                            lines.append(f'{ind}    "wave" "{w}"')
                        lines.append(f'{ind}}}')
                    else:
                        lines.append(f'{ind}"{key}"')
                        lines.append(f'{ind}{{')
                        lines.append(self.serialize_kv(value, indent + 1))
                        lines.append(f'{ind}}}')
                else:
                    lines.append(f'{ind}"{key}" "{value}"')
        return "\n".join(lines)

    def _get_waves(self, rnd_dict):
        waves = rnd_dict.get("wave", [])
        if not isinstance(waves, list):
            waves = [waves] if waves else []
        return [w for w in waves if w]

    # ================= RECENT FILES =================
    def add_recent_file(self, path):
        """Добавляет файл в список недавних, убирает дубликаты, лимит 10."""
        if not path:
            return
        path = os.path.abspath(path)
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:10]
        self.save_settings()
        self._update_recent_menu()

    def clear_recent_files(self):
        """Полностью очищает список недавних файлов."""
        self.recent_files = []
        self.save_settings()
        self._update_recent_menu()

    def _update_recent_menu(self):
        """Пересобирает подменю Recent Files."""
        if not hasattr(self, "recent_menu"):
            return
        self.recent_menu.clear()
        if not self.recent_files:
            act = self.recent_menu.addAction(self.t("no_recent"))
            act.setEnabled(False)
        else:
            for p in self.recent_files:
                name = os.path.basename(p)
                parent = os.path.basename(os.path.dirname(p))
                act = self.recent_menu.addAction(f"{parent}\\{name}")
                act.setToolTip(p)
                act.triggered.connect(lambda checked=False, path=p: self._open_recent(path))

    def _open_recent(self, path):
        """Открывает файл из списка недавних, проверяя его существование."""
        if not os.path.isfile(path):
            QMessageBox.warning(self, self.t("error_t"), f"{self.t('read_err')}\n{path}")
            if path in self.recent_files:
                self.recent_files.remove(path)
                self.save_settings()
                self._update_recent_menu()
            return
        if self.confirm_discard():
            self.open_path(path)

    def new_file(self):
        if not self.confirm_discard():
            return
        self.preview_stop()
        self._push_history()
        self.data = {}
        self.filepath = None
        self.current_sc = None
        self._saved_sig = self._content_sig()
        self._dirty = False
        self.file_type = "soundscape"
        self._reset_history()
        self.search_edit.clear()
        self._rebuild_tabs_for_type()
        self.refresh_list()
        self.clear_right_panel()
        self.refresh_title()
        self.refresh_history()
        self.set_status(self.t("status_new"))

    def open_file(self):
        if not self.confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, self.t("open"), self.last_dir or "",
                                              "Text files (*.txt);;All files (*.*)")
        if not path:
            return
        self.open_path(path)

    def open_path(self, path):
        self.preview_stop()
        self._push_history()
        prev_sc = self.current_sc
        self.data = self.parse_kv(path)
        self.filepath = path
        self.file_type = self.detect_file_type(path)
        self._saved_sig = self._content_sig()
        self._dirty = False
        self.last_dir = os.path.dirname(os.path.abspath(path))
        self.add_recent_file(path)
        self._reset_history()
        self.search_edit.clear()
        self._rebuild_tabs_for_type()
        self.current_sc = None
        self.clear_right_panel()
        self.refresh_list()
        self.refresh_title()
        self.refresh_history()
        self.set_status(f"{self.t('status_open')}: {os.path.basename(path)} | {self.file_type} | entries: {len(self.data)}")
        if self.listbox.count() > 0:
            rows = [self.listbox.item(i).text() for i in range(self.listbox.count())]
            self.listbox.setCurrentRow(rows.index(prev_sc) if prev_sc in rows else 0)

    def save_file(self):
        if not self.filepath:
            self.save_file_as()
            return
        self._do_save(self.filepath)

    def save_file_as(self):
        start = os.path.dirname(self.filepath) if self.filepath else (self.last_dir or "")
        path, _ = QFileDialog.getSaveFileName(self, self.t("save_as"), start,
                                              "Text files (*.txt)")
        if not path:
            return
        self.filepath = path
        new_type = self.detect_file_type(path)
        if new_type != self.file_type:
            self.file_type = new_type
            self._rebuild_tabs_for_type()
        self._do_save(path)
        self.refresh_title()

    def _serialize_all(self):
        lines = []
        for sc_name, sc_data in self.data.items():
            clean_data = self._clean_empty(sc_data)
            if clean_data:
                lines.append(f'"{sc_name}"')
                lines.append('{')
                lines.append(self.serialize_kv(clean_data, 1))
                lines.append('}')
                lines.append('')
        return '\n'.join(lines)

    def _do_save(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self._serialize_all())
            self._mark_clean()
            self.last_dir = os.path.dirname(os.path.abspath(path))
            self.save_settings()
            self.refresh_title()
            QMessageBox.information(self, self.t("success_t"), self.t("saved_msg"))
            self.set_status(f"{self.t('status_saved')}: {path}")
        except Exception as e:
            QMessageBox.critical(self, self.t("error_t"), f"{self.t('save_err')}\n{e}")

    def _clean_empty(self, d):
        if not isinstance(d, dict):
            return d
        cleaned = {}
        for k, v in d.items():
            if isinstance(v, dict):
                cv = self._clean_empty(v)
                if cv:
                    cleaned[k] = cv
            elif isinstance(v, list):
                cl = [self._clean_empty(i) for i in v]
                cl = [i for i in cl if i]
                if cl:
                    cleaned[k] = cl
            elif isinstance(v, str) and v.strip():
                cleaned[k] = v
        return cleaned

    def _ensure_list(self, sc, key):
        v = sc.get(key)
        if v is None:
            sc[key] = []
            return sc[key]
        if not isinstance(v, list):
            sc[key] = [v]
        return sc[key]

    def _ensure_rndwave(self, block):
        rw = block.get("rndwave")
        if not isinstance(rw, dict):
            rw = {"wave": []}
            block["rndwave"] = rw
        waves = rw.get("wave")
        if waves is None:
            rw["wave"] = []
        elif not isinstance(waves, list):
            rw["wave"] = [waves]
        return rw["wave"]

    def _clear_layout(self, lay):
        while lay.count():
            it = lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
            elif it.layout():
                self._clear_layout(it.layout())

    def _placeholder(self):
        lbl = QLabel(self.t("placeholder"))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {VLV['fg_dim']}; padding: 50px;")
        return lbl

    @staticmethod
    def _fmt_num(v, dec):
        if dec is None:
            return str(int(round(v)))
        s = f"{v:.{dec}f}".rstrip("0").rstrip(".")
        return s if s not in ("", "-") else "0"

    @staticmethod
    def _parse_pair(text, d1, d2):
        parts = str(text).split(",")
        out = []
        for i, df in enumerate((d1, d2)):
            try:
                out.append(float(parts[i].strip()))
            except Exception:
                out.append(df)
        return out[0], out[1]

    def _combo_items_dsp(self):
        return [(self.t("not_set"), "")] + [(name, str(n)) for n, name in DSP_ROOM_TYPES]

    def _combo_items_sndlvl(self):
        return [(self.t("not_set"), "")] + [(s, s) for s in SNDLVL_LIST]

    def _combo_items_position(self):
        return [(self.t("not_set"), "")] + [(str(i), str(i)) for i in range(8)] + [("random", "random")]

    def _combo_items_channel(self):
        return [(self.t("not_set"), "")] + [(c, c) for c in SOUND_CHANNELS]

    def _make_combo(self, grid, row, col_l, col_e, label, d, key, items):
        grid.addWidget(QLabel(label), row, col_l)
        cb = QComboBox()
        cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        for txt, dat in items:
            cb.addItem(txt, dat)
        cb.blockSignals(True)
        i = cb.findData(str(d.get(key, "")))
        cb.setCurrentIndex(i if i >= 0 else 0)
        cb.blockSignals(False)
        cb.installEventFilter(self)
        cb.currentIndexChanged.connect(
            lambda _i, cb=cb, d=d, k=key: (d.__setitem__(k, cb.currentData() or ""), self._mark_dirty()))
        grid.addWidget(cb, row, col_e)
        return cb

    def _make_spin(self, grid, row, col_l, col_e, label, d, key,
                   lo, hi, step=1, dec=None, pair=False, d1=0, d2=0):
        grid.addWidget(QLabel(label), row, col_l)
        cur = str(d.get(key, ""))
        def new_spin():
            if dec is None:
                sp = QSpinBox()
                sp.setRange(int(lo), int(hi))
                sp.setSingleStep(int(step))
            else:
                sp = QDoubleSpinBox()
                sp.setRange(lo, hi)
                sp.setSingleStep(step)
                sp.setDecimals(dec)
            sp.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            sp.installEventFilter(self)
            return sp
        if not pair:
            sp = new_spin()
            try:
                v = float(cur.strip())
            except Exception:
                v = d1
            sp.blockSignals(True)
            sp.setValue(v)
            sp.blockSignals(False)
            sp.valueChanged.connect(
                lambda val, d=d, k=key: (d.__setitem__(k, self._fmt_num(val, dec)), self._mark_dirty()))
            grid.addWidget(sp, row, col_e)
            return sp
        wrap = QWidget()
        hb = QHBoxLayout(wrap)
        hb.setContentsMargins(0, 0, 0, 0)
        hb.setSpacing(4)
        sp_a, sp_b = new_spin(), new_spin()
        a, b = self._parse_pair(cur, d1, d2)
        def write_pair(*_args):
            d[key] = f"{self._fmt_num(sp_a.value(), dec)},{self._fmt_num(sp_b.value(), dec)}"
            self._mark_dirty()
        for sp, val in ((sp_a, a), (sp_b, b)):
            sp.blockSignals(True)
            sp.setValue(val)
            sp.blockSignals(False)
            sp.valueChanged.connect(write_pair)
        hb.addWidget(sp_a, 1)
        hb.addWidget(sp_b, 1)
        grid.addWidget(wrap, row, col_e)
        return wrap

    def _make_entry(self, grid, row, col_l, col_e, label, d, key, browse=False):
        grid.addWidget(QLabel(label), row, col_l)
        le = QLineEdit(str(d.get(key, "")))
        le.installEventFilter(self)
        def _on_text(t, d=d, k=key):
            d[k] = t
            self._mark_dirty()
        le.textChanged.connect(_on_text)
        if browse:
            le.setProperty("wave_edit", True)
            le.setAcceptDrops(True)
            w = QWidget()
            hb = QHBoxLayout(w)
            hb.setContentsMargins(0, 0, 0, 0)
            hb.setSpacing(4)
            hb.addWidget(le, 1)
            b = QPushButton("...")
            b.setFixedWidth(32)
            b.clicked.connect(lambda _=False, le=le: self.browse_sound(le))
            hb.addWidget(b)
            pv = QPushButton("▶")
            pv.setFixedWidth(32)
            pv.setToolTip(self.t("preview_tip"))
            pv.clicked.connect(lambda _=False, le=le: self.preview_sound(le.text()))
            self._register_preview_button(pv, lambda le=le: le.text())
            hb.addWidget(pv)
            grid.addWidget(w, row, col_e)
        else:
            le.setAcceptDrops(False)
            grid.addWidget(le, row, col_e)
        return le

    def get_sound_root(self):
        if not self.filepath:
            return None
        base = os.path.dirname(os.path.abspath(self.filepath))
        for cand in (os.path.join(base, "sound"),
                     os.path.join(os.path.dirname(base), "sound")):
            if os.path.isdir(cand):
                return cand
        return None

    def stop_browser_preview(self):
        if self.player is not None:
            self.player.stop()
        self._last_preview = None
        self._last_preview_rel = None
        self._refresh_preview_buttons()

    def browse_sound(self, line_edit):
        root_dir = self.get_sound_root()
        if not root_dir:
            QMessageBox.warning(self, self.t("no_sound_dir_t"), self.t("no_sound_dir"))
            return
        dlg = SoundBrowser(self, root_dir)
        accepted = dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_path
        if getattr(dlg, "_preview_started", False):
            self.stop_browser_preview()
        if accepted:
            line_edit.setText(dlg.result_path)
        self._refresh_preview_buttons()
        dlg.deleteLater()

    def _on_select(self, row):
        if self._preview_active():
            self.preview_stop()
        self.current_sc = self.listbox.item(row).text() if row >= 0 else None
        self.build_right_panel()

    def clear_right_panel(self):
        for lay in (self.general_layout, self.pos_layout, self.global_layout, self.script_layout):
            self._clear_layout(lay)
            lay.addWidget(self._placeholder())

    def add_soundscape(self):
        self._push_history()
        if self._is_soundscript():
            name = "new_sound"
            counter = 1
            while name in self.data:
                name = f"new_sound_{counter}"
                counter += 1
            self.data[name] = {"channel": "CHAN_AUTO", "volume": "1.0",
                               "pitch": "100", "soundlevel": "SNDLVL_75dB"}
        else:
            name = "new_soundscape"
            counter = 1
            while name in self.data:
                name = f"new_soundscape_{counter}"
                counter += 1
            self.data[name] = {"dsp": "1", "attenuation": "0.8"}
        self.refresh_list()
        rows = [self.listbox.item(i).text() for i in range(self.listbox.count())]
        if name in rows:
            self.listbox.setCurrentRow(rows.index(name))
        self.set_status(f"{self.t('status_add')}: {name}")

    def delete_soundscape(self):
        row = self.listbox.currentRow()
        if row < 0:
            return
        name = self.listbox.item(row).text()
        if QMessageBox.question(self, self.t("confirm_t"),
                                self.t("confirm_del", name=name)) \
                != QMessageBox.StandardButton.Yes:
            return
        self._push_history()
        del self.data[name]
        self.refresh_list()
        self.set_status(f"{self.t('status_del')}: {name}")
        if self.listbox.count() > 0:
            self.listbox.setCurrentRow(min(row, self.listbox.count() - 1))
        else:
            self.current_sc = None
            self.clear_right_panel()

    def _on_rename(self, new_name):
        new_name = new_name.strip()
        if not new_name or new_name == self.current_sc or new_name in self.data:
            return
        old = self.current_sc
        self.data[new_name] = self.data.pop(old)
        self.current_sc = new_name
        self._mark_dirty()
        self.refresh_list()

    def build_right_panel(self):
        if self._is_soundscript():
            self._build_soundscript_tab()
        else:
            self._build_general_tab()
            self._build_positions_tab()
            self._build_global_tab()

    def _build_general_tab(self):
        lay = self.general_layout
        self._clear_layout(lay)
        if self.current_sc is None:
            lay.addWidget(self._placeholder())
            return
        sc = self.data[self.current_sc]
        grid = QGridLayout()
        grid.addWidget(QLabel(self.t("name_lbl")), 0, 0)
        name_le = QLineEdit(self.current_sc)
        name_le.installEventFilter(self)
        name_le.setAcceptDrops(False)
        name_le.textChanged.connect(self._on_rename)
        grid.addWidget(name_le, 0, 1)
        self._make_combo(grid, 1, 0, 1, self.t("dsp"), sc, "dsp", self._combo_items_dsp())
        self._make_spin(grid, 2, 0, 1, self.t("dsp_spatial"), sc, "dsp_spatial",
                        0, 255, step=1, dec=None, d1=0)
        self._make_spin(grid, 3, 0, 1, self.t("dsp_vol"), sc, "dsp_volume",
                        0, 10, step=0.1, dec=2, d1=1)
        self._make_spin(grid, 4, 0, 1, self.t("atten"), sc, "attenuation",
                        0, 10, step=0.1, dec=2, d1=1)
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)
        lay.addStretch(1)

    def _build_positions_tab(self):
        lay = self.pos_layout
        self._clear_layout(lay)
        if self.current_sc is None:
            lay.addWidget(self._placeholder())
            return
        sc = self.data[self.current_sc]
        for i in range(8):
            pos_key = f"position{i}"
            pos_data = sc.get(pos_key)
            if isinstance(pos_data, list):
                pos_data = pos_data[0] if pos_data else {}
            if not isinstance(pos_data, dict):
                pos_data = {}
            sc[pos_key] = pos_data
            g = QGroupBox(f"Position {i}")
            grid = QGridLayout(g)
            self._make_entry(grid, 0, 0, 1, self.t("wave"), pos_data, "wave", browse=True)
            self._make_spin(grid, 1, 0, 1, self.t("volume"), pos_data, "volume",
                            0, 10, step=0.05, dec=2, d1=1)
            self._make_spin(grid, 2, 0, 1, self.t("pitch"), pos_data, "pitch",
                            1, 255, step=1, dec=None, d1=100)
            self._make_combo(grid, 3, 0, 1, self.t("soundlevel"), pos_data, "soundlevel",
                             self._combo_items_sndlvl())
            self._make_spin(grid, 4, 0, 1, self.t("attenuation"), pos_data, "attenuation",
                            0, 10, step=0.1, dec=2, d1=1)
            grid.setColumnStretch(1, 1)
            lay.addWidget(g)
        lay.addStretch(1)

    def _build_global_tab(self):
        lay = self.global_layout
        self._clear_layout(lay)
        if self.current_sc is None:
            lay.addWidget(self._placeholder())
            return
        sc = self.data[self.current_sc]
        loop_group = QGroupBox(self.t("loop_cap"))
        lv = QVBoxLayout(loop_group)
        for idx, block in enumerate(self._ensure_list(sc, "playlooping")):
            lv.addWidget(self._make_loop_block(idx, block))
        hb = QHBoxLayout()
        ab = QPushButton(self.t("add_loop"))
        ab.clicked.connect(self.add_looping_block)
        hb.addWidget(ab)
        hb.addStretch(1)
        lv.addLayout(hb)
        lay.addWidget(loop_group)
        rand_group = QGroupBox(self.t("rand_cap"))
        rv = QVBoxLayout(rand_group)
        for b_idx, block in enumerate(self._ensure_list(sc, "playrandom")):
            rv.addWidget(self._make_random_block(b_idx, block))
        hb2 = QHBoxLayout()
        ab2 = QPushButton(self.t("add_rand"))
        ab2.clicked.connect(self.add_random_block)
        hb2.addWidget(ab2)
        hb2.addStretch(1)
        rv.addLayout(hb2)
        lay.addWidget(rand_group)
        lay.addStretch(1)

    def _build_soundscript_tab(self):
        lay = self.script_layout
        self._clear_layout(lay)
        if self.current_sc is None:
            lay.addWidget(self._placeholder())
            return
        sc = self.data[self.current_sc]
        grid = QGridLayout()
        grid.addWidget(QLabel(self.t("name_ss_lbl")), 0, 0)
        name_le = QLineEdit(self.current_sc)
        name_le.installEventFilter(self)
        name_le.setAcceptDrops(False)
        name_le.textChanged.connect(self._on_rename)
        grid.addWidget(name_le, 0, 1)
        self._make_combo(grid, 1, 0, 1, self.t("channel"), sc, "channel", self._combo_items_channel())
        self._make_entry(grid, 2, 0, 1, self.t("wave"), sc, "wave", browse=True)
        self._make_spin(grid, 3, 0, 1, self.t("volume"), sc, "volume",
                        0, 10, step=0.05, dec=2, pair=True, d1=1, d2=1)
        self._make_spin(grid, 4, 0, 1, self.t("pitch"), sc, "pitch",
                        1, 255, step=1, dec=None, pair=True, d1=100, d2=100)
        self._make_combo(grid, 5, 0, 1, self.t("soundlevel"), sc, "soundlevel",
                         self._combo_items_sndlvl())
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)
        lay.addStretch(1)

    def _make_loop_block(self, idx, block):
        g = QGroupBox(f"Loop #{idx + 1}")
        grid = QGridLayout(g)
        self._make_entry(grid, 0, 0, 1, "Wave:", block, "wave", browse=True)
        self._make_spin(grid, 0, 2, 3, self.t("volume"), block, "volume",
                        0, 10, step=0.05, dec=2, d1=1)
        self._make_spin(grid, 1, 0, 1, "Pitch:", block, "pitch",
                        1, 255, step=1, dec=None, d1=100)
        self._make_combo(grid, 1, 2, 3, self.t("soundlevel"), block, "soundlevel",
                         self._combo_items_sndlvl())
        self._make_spin(grid, 2, 0, 1, self.t("attenuation"), block, "attenuation",
                        0, 10, step=0.1, dec=2, d1=1)
        self._make_combo(grid, 2, 2, 3, self.t("pos"), block, "position",
                         self._combo_items_position())
        self._make_entry(grid, 3, 0, 1, self.t("origin"), block, "origin")
        btn = QPushButton(self.t("del_block"))
        btn.clicked.connect(lambda _=False, i=idx: self.remove_looping_block(i))
        grid.addWidget(btn, 3, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        return g

    def _make_random_block(self, b_idx, block):
        g = QGroupBox(f"Random Block #{b_idx + 1}")
        outer = QVBoxLayout(g)
        grid = QGridLayout()
        self._make_spin(grid, 0, 0, 1, self.t("time"), block, "time",
                        0, 3600, step=1, dec=None, pair=True, d1=5, d2=15)
        self._make_spin(grid, 0, 2, 3, self.t("volume"), block, "volume",
                        0, 10, step=0.05, dec=2, pair=True, d1=0.5, d2=0.8)
        self._make_spin(grid, 1, 0, 1, "Pitch:", block, "pitch",
                        1, 255, step=1, dec=None, pair=True, d1=90, d2=110)
        self._make_combo(grid, 1, 2, 3, self.t("soundlevel"), block, "soundlevel",
                         self._combo_items_sndlvl())
        self._make_spin(grid, 2, 0, 1, self.t("attenuation"), block, "attenuation",
                        0, 10, step=0.1, dec=2, d1=1)
        self._make_combo(grid, 2, 2, 3, self.t("pos"), block, "position",
                         self._combo_items_position())
        self._make_entry(grid, 3, 0, 1, self.t("origin"), block, "origin")
        btn = QPushButton(self.t("del_rblock"))
        btn.clicked.connect(lambda _=False, i=b_idx: self.remove_random_block(i))
        grid.addWidget(btn, 3, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        outer.addLayout(grid)
        rnd_frame = QFrame()
        rnd_frame.setFrameShape(QFrame.Shape.StyledPanel)
        rv = QVBoxLayout(rnd_frame)
        rv.addWidget(QLabel(self.t("rnd_cap")))
        waves = self._ensure_rndwave(block)
        for w_idx, w_val in enumerate(waves):
            row_w = QHBoxLayout()
            row_w.addWidget(QLabel("Wave:"))
            le = QLineEdit(str(w_val))
            le.installEventFilter(self)
            le.setProperty("wave_edit", True)
            le.setAcceptDrops(True)
            le.textChanged.connect(lambda t, bi=b_idx, wi=w_idx: self._set_wave(bi, wi, t))
            row_w.addWidget(le, 1)
            bb = QPushButton("...")
            bb.setFixedWidth(32)
            bb.clicked.connect(lambda _=False, le=le: self.browse_sound(le))
            row_w.addWidget(bb)
            pv = QPushButton("▶")
            pv.setFixedWidth(32)
            pv.setToolTip(self.t("preview_tip"))
            pv.clicked.connect(lambda _=False, le=le: self.preview_sound(le.text()))
            self._register_preview_button(pv, lambda le=le: le.text())
            row_w.addWidget(pv)
            bx = QPushButton("X")
            bx.setFixedWidth(32)
            bx.clicked.connect(lambda _=False, bi=b_idx, wi=w_idx: self.remove_wave_from_random(bi, wi))
            row_w.addWidget(bx)
            rv.addLayout(row_w)
        hw = QHBoxLayout()
        addw = QPushButton(self.t("add_wave"))
        addw.clicked.connect(lambda _=False, i=b_idx: self.add_wave_to_random(i))
        hw.addWidget(addw)
        hw.addStretch(1)
        rv.addLayout(hw)
        outer.addWidget(rnd_frame)
        return g

    def _set_wave(self, bi, wi, text):
        b = self._ensure_list(self.data[self.current_sc], "playrandom")[bi]
        w_list = self._ensure_rndwave(b)
        if 0 <= wi < len(w_list):
            w_list[wi] = text
            self._mark_dirty()

    def add_looping_block(self):
        if self._is_soundscript():
            return
        self._push_history()
        self._ensure_list(self.data[self.current_sc], "playlooping").append(
            {"wave": "", "volume": "1.0", "pitch": "100"})
        self.build_right_panel()

    def remove_looping_block(self, idx):
        if self._is_soundscript():
            return
        self._push_history()
        self._ensure_list(self.data[self.current_sc], "playlooping").pop(idx)
        self.build_right_panel()

    def add_random_block(self):
        if self._is_soundscript():
            return
        self._push_history()
        self._ensure_list(self.data[self.current_sc], "playrandom").append(
            {"time": "5,15", "volume": "0.5,0.8", "pitch": "90,110", "rndwave": {"wave": [""]}})
        self.build_right_panel()

    def remove_random_block(self, idx):
        if self._is_soundscript():
            return
        self._push_history()
        self._ensure_list(self.data[self.current_sc], "playrandom").pop(idx)
        self.build_right_panel()

    def add_wave_to_random(self, b_idx):
        if self._is_soundscript():
            return
        self._push_history()
        block = self._ensure_list(self.data[self.current_sc], "playrandom")[b_idx]
        self._ensure_rndwave(block).append("")
        self.build_right_panel()

    def remove_wave_from_random(self, b_idx, w_idx):
        if self._is_soundscript():
            return
        self._push_history()
        block = self._ensure_list(self.data[self.current_sc], "playrandom")[b_idx]
        waves = self._ensure_rndwave(block)
        if 0 <= w_idx < len(waves):
            waves.pop(w_idx)
        self.build_right_panel()

if __name__ == "__main__":
    import time
    def _base_dir():
        if getattr(sys, "frozen", False):
            return os.path.dirname(os.path.abspath(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))
    try:
        import pyi_splash
        def _pyi_text(t):
            try: pyi_splash.update_text(t)
            except Exception: pass
        def _pyi_close():
            try: pyi_splash.close()
            except Exception: pass
    except Exception:
        def _pyi_text(t): pass
        def _pyi_close(): pass
    app = QApplication(sys.argv)
    try:
        with open(os.path.join(_base_dir(), "settings.json"), encoding="utf-8") as f:
            _lang = json.load(f).get("lang", "en")
    except Exception:
        _lang = "en"
    T = {
        "ru": ["Инициализация ядра...", "Генерация иконки и плеера...",
               "Сборка интерфейса...", "Готово"],
        "en": ["Initializing core...", "Generating icon & player...",
               "Building interface...", "Ready"],
    }.get(_lang, None) or ["Инициализация ядра...", "Генерация иконки и плеера...",
                           "Сборка интерфейса...", "Готово"]
    _pyi_text(T[0])
    app.setStyleSheet(build_style())
    splash = SplashScreen()
    splash.show()
    splash.set_stage(T[1]); splash.set_progress(0.35)
    app.processEvents()
    _pyi_close()
    win = SoundscapeEditor()
    splash.set_stage(T[2]); splash.set_progress(0.8)
    app.processEvents()
    t0 = time.time()
    while time.time() - t0 < 0.6:
        app.processEvents(); time.sleep(0.016)
    splash.set_stage(T[3]); splash.set_progress(1.0)
    app.processEvents()
    t0 = time.time()
    while time.time() - t0 < 0.3:
        app.processEvents(); time.sleep(0.016)
    splash.finish(win)
    win.show()
    sys.exit(app.exec())