import pygame
import os
import random
pygame.init()

# Получаем абсолютный путь к папке, где находится dino.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Папка с ассетами (ищем её относительно dino.py)
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

# Функция для загрузки изображений (проверяет, есть ли файл)
def load_image(subfolder, filename):
    path = os.path.join(ASSETS_DIR, subfolder, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл {path} не найден!")
    return pygame.image.load(path)

# Глобальные константы
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Загрузка изображений
RUNNING = [load_image("Dino", "DinoRun1.png"),
           load_image("Dino", "DinoRun2.png")]
JUMPING = load_image("Dino", "DinoJump.png")
DUCKING = [load_image("Dino", "DinoDuck1.png"),
           load_image("Dino", "DinoDuck2.png")]

SMALL_CACTUS = [load_image("Cactus", "SmallCactus1.png"),
                load_image("Cactus", "SmallCactus2.png"),
                load_image("Cactus", "SmallCactus3.png")]
LARGE_CACTUS = [load_image("Cactus", "LargeCactus1.png"),
                load_image("Cactus", "LargeCactus2.png"),
                load_image("Cactus", "LargeCactus3.png")]

BIRD = [load_image("Bird", "Bird1.png"),
        load_image("Bird", "Bird2.png")]

CLOUD = load_image("Other", "Cloud.png")
BG = load_image("Other", "Track.png")

# Класс динозавра
class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        # Инициализация изображений
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        # Состояние динозавра
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        # Вспомогательные переменные
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        # Обновление состояния в зависимости от ввода
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        # Перезапуск индекса шагов
        if self.step_index >= 10:
            self.step_index = 0

        # Обработка ввода пользователя
        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        # Анимация приседания
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        # Анимация бега
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        # Анимация прыжка
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, screen):
        # Отрисовка динозавра
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

# Класс облака
class Cloud:
    def __init__(self):
        # Инициализация позиции облака
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        # Обновление позиции облака
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        # Отрисовка облака
        screen.blit(self.image, (self.x, self.y))

# Базовый класс препятствий
class Obstacle:
    def __init__(self, image, obstacle_type):
        self.image = image
        self.type = obstacle_type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        # Обновление позиции препятствия
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, screen):
        # Отрисовка препятствия
        screen.blit(self.image[self.type], self.rect)

# Класс маленького кактуса
class SmallCactus(Obstacle):
    def __init__(self, image):
        super().__init__(image, random.randint(0, 2))
        self.rect.y = 325

# Класс большого кактуса
class LargeCactus(Obstacle):
    def __init__(self, image):
        super().__init__(image, random.randint(0, 2))
        self.rect.y = 300

# Класс птицы
class Bird(Obstacle):
    def __init__(self, image):
        super().__init__(image, 0)
        self.rect.y = 250
        self.index = 0

    def draw(self, screen):
        # Анимация птицы
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[self.index // 5], self.rect)
        self.index += 1

# Основная функция игры
def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font(None, 20)
    obstacles = []
    death_count = 0

    def score():
        # Подсчет очков
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Очочки: " + str(points), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (1000, 40)
        SCREEN.blit(text, text_rect)

    def background():
        # Отрисовка фона
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        user_input = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(user_input)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)
        pygame.display.update()

# Меню игры
def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font(None, 30)

        if death_count == 0:
            text = font.render("Ты просто смотреть или играть?", True, (0, 0, 0))
        else:
            text = font.render("Нажми если хочешь не просто смотреть", True, (0, 0, 0))
            score_text = font.render("Твои Очочки: " + str(points), True, (0, 0, 0))
            score_rect = score_text.get_rect()
            score_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score_text, score_rect)

        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, text_rect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                main()

menu(death_count=0)
