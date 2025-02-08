import json
import subprocess
import random

from PyQt5.QtWidgets import (
    QApplication, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout,
    QFrame, QGridLayout, QStackedWidget, QProgressBar, QComboBox, QTextEdit
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

# Функция запуска игры
def launch_game(game_path): # передается имя файла игры для её запуска
    subprocess.Popen(["python", game_path])

# Загрузка списка игр
with open("library.json") as file: # тут типо нахожднеие игр и добавление в магазин или билиотеку
    games = json.load(file)

library_games = []
store_games = games.copy()

# Инициализация приложения
app = QApplication([])
window = QWidget()
window.setWindowTitle("Game Launcher")
window.setGeometry(100, 100, 1000, 600)

# Функция применения темы
def apply_theme(dark_mode=True): #В настройка для выбора темы
    if dark_mode:
        window.setStyleSheet("""
            QWidget { background-color: #1c1c1c; color: white; font-family: "Arial"; }
        """)
    else:
        window.setStyleSheet("""
            QWidget { background-color: #f5f5f5; color: black; font-family: "Arial"; }
        """)

apply_theme()

# Главный layout
main_layout = QHBoxLayout(window)

# Боковая панель
sidebar_layout = QVBoxLayout()
buttons = {}

for name in ["Библиотека", "Магазин", "Настройки"]: # перебор для добавление кнопок в понельку с спец стилем
    btn = QPushButton(name)
    btn.setStyleSheet("""
        QPushButton {
            background-color: #1f1f1f;
            color: white;
            border: 2px solid #333333;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
            width: 180px;
        }
        QPushButton:hover { background-color: #333333; border-color: #444444; }
        QPushButton:pressed { background-color: #555555; border-color: #666666; }
    """)
    sidebar_layout.addWidget(btn)
    buttons[name] = btn

# Основной контент
content_area = QStackedWidget()
library_widget = QWidget()
store_widget = QWidget()
settings_widget = QWidget()
downloading = False  # Флаг, контролирующий одновременную загрузку
# Библиотека и Магазин
library_layout = QVBoxLayout(library_widget)
library_grid = QGridLayout()
library_layout.addLayout(library_grid)

store_layout = QVBoxLayout(store_widget)
store_grid = QGridLayout()
store_layout.addLayout(store_grid)

# Функция создания карточки игры
def create_game_frame(game, library):
    frame = QFrame() # ну это типо конейнер с виджетами
    frame.setStyleSheet("""
        QFrame {
            background-color: #2a2a2a;
            border: 2px solid #222222;
            border-radius: 12px;
            padding: 15px;
        }
    """)
    layout = QVBoxLayout(frame)

    icon = QLabel()
    pixmap = QPixmap(game["icon"]) # Ну тут иконка игры из жсон файла
    icon.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio)) # тут дальше все для сохранение пропорций и маста каритонок
    icon.setAlignment(Qt.AlignCenter)

    btn = QPushButton(game["name"]) #ну тут того самого названи игры
    btn.setFont(QFont("Arial", 14, QFont.Bold))

    if library:
        btn.clicked.connect(lambda checked, path=game["file"]: launch_game(path)) # если игра под пункстом билиотека то можно играть
    else:
        progress_bar = QProgressBar() # иначе скачать и только потом играть
        progress_bar.setValue(0)
        btn.setText("Скачать")
        btn.clicked.connect(lambda: add_to_library(game, btn, progress_bar))
        layout.addWidget(progress_bar)

    layout.addWidget(icon)
    layout.addWidget(btn)
    frame.setLayout(layout)
    return frame

# Функция добавления игры в библиотеку (имитация загрузки)
def add_to_library(game, button, progress_bar):
    global downloading
    if downloading:
        return  # Если уже идёт загрузка, прерываем

    downloading = True  # Устанавливаем флаг загрузки    
    def update_progress():
        global downloading
        value = progress_bar.value() + random.randint(5, 15)
        if value <= 100:
            progress_bar.setValue(value) # ну тут вечная проверка загружена ли игра или нет
        if value >= 100:
            timer.stop()
            store_games.remove(game)
            library_games.append(game)
            refresh_library()
            refresh_store()
            downloading = False  # Сбрасываем флаг загрузки

    timer = QTimer()
    timer.timeout.connect(update_progress)
    timer.start(500)

# Функция обновления библиотеки
def refresh_library():
    for i in reversed(range(library_grid.count())):
        library_grid.itemAt(i).widget().setParent(None)
    row, col = 0, 0
    for game in library_games:
        frame = create_game_frame(game, library=True)
        library_grid.addWidget(frame, row, col)
        col += 1
        if col == 3:
            col = 0
            row += 1

# Функция обновления магазина
def refresh_store():
    for i in reversed(range(store_grid.count())):
        store_grid.itemAt(i).widget().setParent(None)
    row, col = 0, 0
    for game in store_games:
        frame = create_game_frame(game, library=False)
        store_grid.addWidget(frame, row, col)
        col += 1
        if col == 3:
            col = 0
            row += 1

# Заполняем данные в первый раз
refresh_library()
refresh_store()

# === Улучшенная вкладка "Настройки" ===
settings_layout = QVBoxLayout(settings_widget)

settings_frame = QFrame()
settings_frame.setStyleSheet("""
    QFrame {
        background-color: #2c2c2c;
        border: 2px solid #444444;
        border-radius: 12px;
        padding: 20px;
    }
""")

frame_layout = QVBoxLayout(settings_frame)

theme_label = QLabel("Тема:")
theme_combo = QComboBox()
theme_combo.addItems(["Тёмная", "Светлая"])

resolution_label = QLabel("Разрешение экрана:")
resolution_combo = QComboBox()
resolution_combo.addItems(["1000x600", "1024x768", "1280x720"])

apply_btn = QPushButton("Применить")

def apply_settings():
    apply_theme(theme_combo.currentText() == "Тёмная")
    resolution = resolution_combo.currentText().split("x")
    window.setGeometry(100, 100, int(resolution[0]), int(resolution[1]))

apply_btn.clicked.connect(apply_settings)

frame_layout.addWidget(theme_label)
frame_layout.addWidget(theme_combo)
frame_layout.addWidget(resolution_label)
frame_layout.addWidget(resolution_combo)
frame_layout.addWidget(apply_btn)

settings_layout.addWidget(settings_frame)

# === Блок новостей ===
news_frame = QFrame()
news_frame.setStyleSheet("""
    QFrame {
        background-color: #1e1e1e;
        border: 2px solid #555555;
        border-radius: 12px;
        padding: 10px;
    }
""")
news_layout = QVBoxLayout(news_frame)

news_label = QLabel("Новости игр:")
news_label.setFont(QFont("Arial", 16, QFont.Bold))
news_label.setAlignment(Qt.AlignCenter)

news_text = QTextEdit()
news_text.setReadOnly(True)
news_text.setPlainText("• Обновление 1.22 для Minecraft вышло!\n• Новая игра 'Cyber Storm' скоро выйдет!\n• Steam распродажа началась!\n• По словам создателей Dota 2 НИКОГДА не станет нормальной\n• GTA 6 выйдет уже в этом году\n• Baldur's gate 3 уже надоела? Она опять получила награду за лучшую РПГ игру\n• Steam сново обасралось? В КС 2 не возможно играть? В Dota 2 нет баланса? Ну а чего вы ожидали")

news_layout.addWidget(news_label)
news_layout.addWidget(news_text)
news_frame.setLayout(news_layout)

settings_layout.addWidget(news_frame)

settings_widget.setLayout(settings_layout)

# Добавление виджетов во вкладки
content_area.addWidget(library_widget)
content_area.addWidget(store_widget)
content_area.addWidget(settings_widget)

# Функции переключения вкладок
buttons["Библиотека"].clicked.connect(lambda: content_area.setCurrentWidget(library_widget))
buttons["Магазин"].clicked.connect(lambda: content_area.setCurrentWidget(store_widget))
buttons["Настройки"].clicked.connect(lambda: content_area.setCurrentWidget(settings_widget))

main_layout.addLayout(sidebar_layout)
main_layout.addWidget(content_area)

window.setLayout(main_layout)
content_area.setCurrentWidget(store_widget)


window.show()
app.exec_()
