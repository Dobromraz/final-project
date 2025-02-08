import json
import subprocess
import random
import os
from PyQt5.QtWidgets import (
    QApplication, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout,
    QFrame, QGridLayout, QStackedWidget, QProgressBar, QComboBox, QTextEdit
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer


# Функция запуска игры
# Запускает файл игры, переданный в аргументе game_path
# Используется subprocess.Popen для выполнения скрипта игры

def launch_game(game_path):
    subprocess.Popen(["python", game_path])

# Загрузка списка игр из файла library.json
# Этот файл содержит информацию о доступных играх

with open("library.json") as file:
    games = json.load(file)

# Файл, в котором хранится библиотека пользователя
LIBRARY_FILE = "library_data.json"

# Проверяем, существует ли файл с библиотекой игр
# Если да, загружаем его, иначе создаём пустой список

if os.path.exists(LIBRARY_FILE):
    with open(LIBRARY_FILE) as file:
        library_games = json.load(file)
else:
    library_games = []

# Определяем список игр, доступных в магазине
# Это те игры, которых ещё нет в библиотеке пользователя

store_games = [game for game in games if game not in library_games]

# Инициализация главного приложения PyQt
app = QApplication([])
window = QWidget()
window.setWindowTitle("Game Launcher")
window.setGeometry(100, 100, 1000, 600)

# Функция смены темы оформления (тёмная или светлая)
# Применяет стили к главному окну

def apply_theme(dark_mode=True):
    if dark_mode:
        window.setStyleSheet("""
            QWidget { background-color: #1c1c1c; color: white; font-family: "Arial"; }
        """
        )
    else:
        window.setStyleSheet("""
            QWidget { background-color: #f5f5f5; color: black; font-family: "Arial"; }
        """
        )

apply_theme()

# Создаём главный layout
main_layout = QHBoxLayout(window)

# Боковая панель с кнопками для навигации
sidebar_layout = QVBoxLayout()
buttons = {}

# Создаём кнопки "Библиотека", "Магазин", "Настройки"
# Добавляем стилизацию кнопок

for name in ["Библиотека", "Магазин", "Настройки"]:
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
    """
    )
    sidebar_layout.addWidget(btn)
    buttons[name] = btn

# Основное содержимое в центральной области
content_area = QStackedWidget()
library_widget = QWidget()
store_widget = QWidget()
settings_widget = QWidget()
downloading = False  # Флаг, предотвращающий одновременные загрузки

# Layout для библиотеки и магазина
library_layout = QVBoxLayout(library_widget)
library_grid = QGridLayout()
library_layout.addLayout(library_grid)

store_layout = QVBoxLayout(store_widget)
store_grid = QGridLayout()
store_layout.addLayout(store_grid)

# Функция удаления игры из библиотеки

def remove_from_library(game):
    global library_games, store_games
    library_games = [g for g in library_games if g != game]
    store_games.append(game)

    save_library()  # Сохранение изменений в библиотеке
    refresh_library()
    refresh_store()

# Функция сохранения библиотеки пользователя в файл

def save_library():
    with open(LIBRARY_FILE, "w") as file:
        json.dump(library_games, file, indent=4)

# Функция создания карточки игры

def create_game_frame(game, library):
    frame = QFrame()
    frame.setStyleSheet("""
        QFrame {
            background-color: #2a2a2a;
            border: 2px solid #222222;
            border-radius: 12px;
            padding: 15px;
        }
    """
    )
    layout = QVBoxLayout(frame)

    # Значок игры
    icon = QLabel()
    pixmap = QPixmap(game["icon"])
    icon.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
    icon.setAlignment(Qt.AlignCenter)

    # Кнопка запуска игры или загрузки
    btn = QPushButton(game["name"])
    btn.setFont(QFont("Arial", 14, QFont.Bold))

    if library:
        # Если игра в библиотеке, кнопка запускает игру
        btn.clicked.connect(lambda checked, path=game["file"]: launch_game(path))
        remove_btn = QPushButton("Удалить из библиотеки")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #aa3333;
                color: white;
                border: 2px solid #992222;
                border-radius: 8px;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #cc4444; }
            QPushButton:pressed { background-color: #dd5555; }
        """
        )
        remove_btn.clicked.connect(lambda: remove_from_library(game))
        layout.addWidget(remove_btn)
    else:
        # Если игра в магазине, кнопка запускает загрузку
        progress_bar = QProgressBar()
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


# Функция обновления прогресса загрузки игры
    def update_progress():
        global downloading  # Флаг, указывающий, что идет загрузка
        value = progress_bar.value() + random.randint(5, 15)  # Увеличиваем значение прогресса на случайное число
        if value <= 100:
            progress_bar.setValue(value)  # Обновляем значение прогресс-бара
        if value >= 100:  # Когда прогресс достигает 100%
            timer.stop()  # Останавливаем таймер
            store_games.remove(game)  # Удаляем игру из магазина
            library_games.append(game)  # Добавляем игру в библиотеку
            save_library()  # Сохраняем библиотеку в JSON-файл
            refresh_library()  # Обновляем отображение библиотеки
            refresh_store()  # Обновляем отображение магазина
            downloading = False  # Сбрасываем флаг загрузки

    # Создание таймера для обновления прогресса загрузки
    timer = QTimer()
    timer.timeout.connect(update_progress)  # Привязываем функцию update_progress к событию таймера
    timer.start(500)  # Устанавливаем интервал в 500 мс

# Функция обновления библиотеки игр
def refresh_library():
    global library_games
    # Загружаем библиотеку из JSON-файла, если он существует
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE) as file:
            library_games = json.load(file)

    # Очищаем сетку библиотеки от старых виджетов
    for i in reversed(range(library_grid.count())):
        library_grid.itemAt(i).widget().setParent(None)

    row, col = 0, 0  # Начальные координаты сетки
    for game in library_games:  # Добавляем игры в сетку библиотеки
        frame = create_game_frame(game, library=True)
        library_grid.addWidget(frame, row, col)
        col += 1
        if col == 3:  # Переход на новую строку при заполнении трех колонок
            col = 0
            row += 1

# Функция обновления магазина игр
def refresh_store():
    # Очищаем сетку магазина от старых виджетов
    for i in reversed(range(store_grid.count())):
        store_grid.itemAt(i).widget().setParent(None)

    row, col = 0, 0  # Начальные координаты сетки
    for game in store_games:  # Добавляем игры в сетку магазина
        frame = create_game_frame(game, library=False)
        store_grid.addWidget(frame, row, col)
        col += 1
        if col == 3:  # Переход на новую строку при заполнении трех колонок
            col = 0
            row += 1

# Первоначальное обновление библиотеки и магазина при запуске
refresh_library()
refresh_store()

# === Вкладка "Настройки" ===
settings_layout = QVBoxLayout(settings_widget)  # Главный вертикальный лэйаут

# Создание фрейма для настроек
settings_frame = QFrame()
settings_frame.setStyleSheet("""
    QFrame {
        background-color: #2c2c2c;
        border: 2px solid #444444;
        border-radius: 12px;
        padding: 20px;
    }
""")

frame_layout = QVBoxLayout(settings_frame)  # Лэйаут внутри фрейма

# Виджеты для изменения темы
theme_label = QLabel("Тема:")
theme_combo = QComboBox()
theme_combo.addItems(["Тёмная", "Светлая"])

# Виджеты для изменения разрешения экрана
resolution_label = QLabel("Разрешение экрана:")
resolution_combo = QComboBox()
resolution_combo.addItems(["1000x600", "1024x768", "1280x720"])

# Кнопка "Применить"
apply_btn = QPushButton("Применить")

# Функция применения настроек
def apply_settings():
    apply_theme(theme_combo.currentText() == "Тёмная")  # Применение темы
    resolution = resolution_combo.currentText().split("x")  # Разбираем строку с разрешением
    window.setGeometry(100, 100, int(resolution[0]), int(resolution[1]))  # Изменяем размеры окна

apply_btn.clicked.connect(apply_settings)  # Привязываем кнопку к функции

# Добавление всех элементов в лэйаут настроек
frame_layout.addWidget(theme_label)
frame_layout.addWidget(theme_combo)
frame_layout.addWidget(resolution_label)
frame_layout.addWidget(resolution_combo)
frame_layout.addWidget(apply_btn)

settings_layout.addWidget(settings_frame)  # Добавляем фрейм настроек в лэйаут настроек

# === Блок новостей ===
news_frame = QFrame()  # Создаём фрейм новостей
news_frame.setStyleSheet("""
    QFrame {
        background-color: #1e1e1e;
        border: 2px solid #555555;
        border-radius: 12px;
        padding: 10px;
    }
""")
news_layout = QVBoxLayout(news_frame)  # Лэйаут внутри блока новостей

# Заголовок новостей
news_label = QLabel("Новости игр:")
news_label.setFont(QFont("Arial", 16, QFont.Bold))
news_label.setAlignment(Qt.AlignCenter)

# Текстовое поле с новостями
news_text = QTextEdit()
news_text.setReadOnly(True)  # Делаем поле только для чтения
news_text.setPlainText("""• Обновление 1.22 для Minecraft вышло!
• Новая игра 'Cyber Storm' скоро выйдет!
• Steam распродажа началась!
• По словам создателей Dota 2 НИКОГДА не станет нормальной
• GTA 6 выйдет уже в этом году
• Baldur's gate 3 уже надоела? Она опять получила награду за лучшую РПГ игру
• Steam снова облажался? В КС 2 невозможно играть? В Dota 2 нет баланса? Ну а чего вы ожидали""")

# Добавление элементов в лэйаут новостей
news_layout.addWidget(news_label)
news_layout.addWidget(news_text)
news_frame.setLayout(news_layout)

settings_layout.addWidget(news_frame)  # Добавляем блок новостей в настройки

settings_widget.setLayout(settings_layout)  # Устанавливаем лэйаут в виджет настроек

# === Добавление вкладок в область контента ===
content_area.addWidget(library_widget)  # Вкладка "Библиотека"
content_area.addWidget(store_widget)  # Вкладка "Магазин"
content_area.addWidget(settings_widget)  # Вкладка "Настройки"

# Функции для переключения между вкладками
buttons["Библиотека"].clicked.connect(lambda: content_area.setCurrentWidget(library_widget))
buttons["Магазин"].clicked.connect(lambda: content_area.setCurrentWidget(store_widget))
buttons["Настройки"].clicked.connect(lambda: content_area.setCurrentWidget(settings_widget))

# Компоновка основного интерфейса
main_layout.addLayout(sidebar_layout)  # Добавляем боковое меню
main_layout.addWidget(content_area)  # Добавляем область контента

window.setLayout(main_layout)  # Устанавливаем основной лэйаут на окно
content_area.setCurrentWidget(store_widget)  # По умолчанию открываем магазин

window.show()  # Отображаем окно приложения
app.exec_()  # Запускаем главный цикл обработки событий
