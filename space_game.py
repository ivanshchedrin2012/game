import pygame
import math
import random
import sys
import json
import os

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
PINK = (255, 192, 203)
BROWN = (139, 69, 19)

# Файл для сохранения прогресса
SAVE_FILE = "game_progress.json"

class GameProgress:
    def __init__(self):
        self.unlocked_levels = [1]  # Первый уровень всегда открыт
        self.load_progress()
    
    def load_progress(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.unlocked_levels = data.get('unlocked_levels', [1])
            except:
                self.unlocked_levels = [1]
    
    def save_progress(self):
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump({'unlocked_levels': self.unlocked_levels}, f)
        except:
            pass
    
    def unlock_level(self, level):
        if level not in self.unlocked_levels and level <= 10:
            self.unlocked_levels.append(level)
            self.save_progress()
    
    def is_level_unlocked(self, level):
        return level in self.unlocked_levels

class Player:
    def __init__(self, x, y, level_type="shooter"):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.shield_active = False
        self.shield_timer = 0
        self.level_type = level_type
        self.rotation_angle = 0  # Угол поворота для survival режима
        
        # Специальные параметры для разных жанров
        if level_type == "platformer":
            self.velocity_y = 0
            self.on_ground = False
            self.jump_power = -15
            self.jump_charge = 0  # Заряд прыжка от удержания пробела
            self.max_jump_charge = 20  # Максимальное время зарядки
            self.min_jump_power = -8   # Минимальная сила прыжка
            self.max_jump_power = -18  # Максимальная сила прыжка
            self.is_charging_jump = False
            self.jump_released = True  # Для контроля одного прыжка за нажатие
        elif level_type == "racing":
            self.velocity_x = 0
            self.max_speed = 8
        elif level_type == "puzzle":
            self.moves = 0
            self.target_moves = 50
        
    def update(self, level_type="shooter"):
        keys = pygame.key.get_pressed()
        
        if level_type == "shooter":
            # Обычное управление для шутера
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
                self.x -= self.speed
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < SCREEN_WIDTH - self.width:
                self.x += self.speed
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > 0:
                self.y -= self.speed
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y < SCREEN_HEIGHT - self.height:
                self.y += self.speed
                
        elif level_type == "platformer":
            # Платформер - только горизонтальное движение и прыжки с зарядкой
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
                self.x -= self.speed
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < SCREEN_WIDTH - self.width:
                self.x += self.speed
            
            # Система автоматического определения силы прыжка
            jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w]
            
            if jump_pressed and self.on_ground and self.jump_released:
                # Начинаем отсчет времени нажатия
                self.is_charging_jump = True
                self.jump_released = False
                self.jump_charge = 0
                
            if self.is_charging_jump and jump_pressed and self.on_ground:
                # Увеличиваем заряд пока зажат пробел
                self.jump_charge = min(self.jump_charge + 1, self.max_jump_charge)
                
            if not jump_pressed and self.is_charging_jump:
                # Прыгаем СРАЗУ когда отпускаем пробел с накопленной силой
                charge_ratio = self.jump_charge / self.max_jump_charge
                jump_power = self.min_jump_power + (self.max_jump_power - self.min_jump_power) * charge_ratio
                self.velocity_y = jump_power
                self.on_ground = False
                self.is_charging_jump = False
                self.jump_charge = 0
                
            if not jump_pressed:
                self.jump_released = True
            
            # Гравитация
            self.velocity_y += 0.8
            self.y += self.velocity_y
                
        elif level_type == "racing":
            # Гонки - реальное движение по трассе
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                self.velocity_x = max(-self.max_speed, self.velocity_x - 0.5)
            elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                self.velocity_x = min(self.max_speed, self.velocity_x + 0.5)
            else:
                self.velocity_x *= 0.9  # Трение
            
            # Движение по X (влево-вправо по полосам)
            self.x += self.velocity_x
            self.x = max(100, min(600, self.x))  # Ограничиваем движение полосами трассы
            
            # Автоматическое движение вперед (по Y)
            self.y -= 3  # Постоянно едем вперед
            
            # Если выехали за верх экрана, возвращаемся вниз (эффект движения по кругу)
            if self.y < -50:
                self.y = SCREEN_HEIGHT + 50
            
        elif level_type == "puzzle":
            # Пошаговое движение для головоломки - только один ход за нажатие
            pass  # Движение обрабатывается в событиях
        
        elif level_type == "tower_defense" or level_type == "stealth" or level_type == "fighting" or level_type == "strategy" or level_type == "final_mix" or level_type == "survival":
            # Обычное управление для tower defense, stealth, fighting, strategy, final_mix и survival
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
                self.x -= self.speed
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < SCREEN_WIDTH - self.width:
                self.x += self.speed
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > 0:
                self.y -= self.speed
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y < SCREEN_HEIGHT - self.height:
                self.y += self.speed
        
        # Обновление поворота к мыши для survival
        if level_type == "survival":
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - (self.x + self.width//2)
            dy = mouse_y - (self.y + self.height//2)
            self.rotation_angle = math.atan2(dy, dx)
        
        # Уменьшаем кулдауны
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
    
    def can_shoot(self):
        return self.shoot_cooldown <= 0
    
    def shoot(self, level_type="shooter"):
        if self.can_shoot():
            self.shoot_cooldown = 15
            if level_type == "survival":
                # Для survival стреляем в направлении мыши
                center_x = self.x + self.width//2
                center_y = self.y + self.height//2
                return PlayerBullet(center_x - 2, center_y - 5, speed=8, angle=self.rotation_angle)
            else:
                return PlayerBullet(self.x + self.width//2 - 2, self.y)
        return None
    
    def activate_shield(self, duration=300):
        self.shield_active = True
        self.shield_timer = duration
    
    def take_damage(self, damage):
        if not self.shield_active:
            self.health -= damage
            return True
        return False
    
    def draw(self, screen, level_type="shooter"):
        # Рисуем щит если активен
        if self.shield_active:
            pygame.draw.circle(screen, CYAN, 
                             (self.x + self.width//2, self.y + self.height//2), 
                             self.width, 2)
        
        if level_type == "shooter" or level_type == "final_mix":
            # ПРОДВИНУТЫЙ КОСМИЧЕСКИЙ КОРАБЛЬ
            center_x = self.x + self.width//2
            center_y = self.y + self.height//2
            
            # Основной корпус корабля - серебристый
            main_body = [
                (center_x, self.y),  # Нос
                (center_x - 8, self.y + 8),  # Левое крыло
                (center_x - 12, self.y + self.height - 8),
                (center_x - 6, self.y + self.height),  # Левый хвост
                (center_x + 6, self.y + self.height),  # Правый хвост  
                (center_x + 12, self.y + self.height - 8),
                (center_x + 8, self.y + 8),  # Правое крыло
            ]
            pygame.draw.polygon(screen, (180, 180, 200), main_body)
            pygame.draw.polygon(screen, (220, 220, 240), main_body, 2)
            
            # Кабина пилота - тёмно-синее стекло
            cockpit = [
                (center_x, self.y + 2),
                (center_x - 4, self.y + 8),
                (center_x - 3, self.y + 12),
                (center_x + 3, self.y + 12),
                (center_x + 4, self.y + 8),
            ]
            pygame.draw.polygon(screen, (20, 40, 80), cockpit)
            pygame.draw.polygon(screen, (60, 100, 160), cockpit, 1)
            
            # Двигатели - светящиеся сопла
            # Левый двигатель
            pygame.draw.circle(screen, (100, 100, 120), (center_x - 8, self.y + self.height - 3), 4)
            pygame.draw.circle(screen, (255, 100, 0), (center_x - 8, self.y + self.height - 3), 2)
            # Правый двигатель  
            pygame.draw.circle(screen, (100, 100, 120), (center_x + 8, self.y + self.height - 3), 4)
            pygame.draw.circle(screen, (255, 100, 0), (center_x + 8, self.y + self.height - 3), 2)
            
            # Центральный двигатель
            pygame.draw.circle(screen, (120, 120, 140), (center_x, self.y + self.height - 2), 3)
            pygame.draw.circle(screen, (255, 150, 50), (center_x, self.y + self.height - 2), 1)
            
            # Пламя из двигателей (анимированное)
            flame_offset = (pygame.time.get_ticks() // 50) % 4
            flame_colors = [(255, 200, 0), (255, 100, 0), (255, 50, 0), (200, 0, 0)]
            
            for i in range(4):
                flame_y = self.y + self.height + i * 2 + flame_offset
                flame_alpha = 255 - i * 60
                if flame_alpha > 0:
                    # Левое пламя
                    pygame.draw.circle(screen, flame_colors[i], 
                                     (center_x - 8, flame_y), max(1, 3 - i))
                    # Правое пламя
                    pygame.draw.circle(screen, flame_colors[i], 
                                     (center_x + 8, flame_y), max(1, 3 - i))
                    # Центральное пламя
                    pygame.draw.circle(screen, flame_colors[i], 
                                     (center_x, flame_y - 1), max(1, 2 - i//2))
            
            # Детали корабля
            # Боковые лазеры
            pygame.draw.rect(screen, (150, 150, 170), (center_x - 10, self.y + 6, 2, 8))
            pygame.draw.rect(screen, (150, 150, 170), (center_x + 8, self.y + 6, 2, 8))
            
            # Антенны/сенсоры
            pygame.draw.circle(screen, (0, 255, 0), (center_x - 5, self.y + 5), 1)  # Левый сенсор
            pygame.draw.circle(screen, (255, 0, 0), (center_x + 5, self.y + 5), 1)  # Правый сенсор
            
            # Центральная полоса
            pygame.draw.line(screen, (100, 255, 100), 
                           (center_x, self.y + 3), (center_x, self.y + self.height - 8), 2)
        elif level_type == "platformer":
            # Персонаж платформера с индикацией зарядки
            player_color = BLUE
            if hasattr(self, 'is_charging_jump') and self.is_charging_jump:
                # Меняем цвет во время зарядки
                charge_intensity = self.jump_charge / self.max_jump_charge
                player_color = (int(255 * charge_intensity), int(100 + 155 * charge_intensity), 255)
            
            pygame.draw.rect(screen, player_color, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 5), 3)  # Глаз
            pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 5), 3)  # Глаз
            
            # Индикатор зарядки прыжка
            if hasattr(self, 'is_charging_jump') and self.is_charging_jump:
                bar_width = 40
                bar_height = 6
                bar_x = self.x + self.width//2 - bar_width//2
                bar_y = self.y - 15
                
                # Фон полоски
                pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
                
                # Заполнение по заряду
                charge_ratio = self.jump_charge / self.max_jump_charge
                fill_width = int(bar_width * charge_ratio)
                fill_color = (255, int(255 * (1 - charge_ratio)), 0)  # От красного к желтому
                pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height))
                
                # Рамка
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        elif level_type == "racing":
            # Гоночная машина
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x + 5, self.y - 5, 5, 5))  # Колесо
            pygame.draw.rect(screen, BLACK, (self.x + 20, self.y - 5, 5, 5))  # Колесо
        elif level_type == "puzzle":
            # Кубик для головоломки
            pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, WHITE, (self.x + 2, self.y + 2, self.width - 4, self.height - 4), 2)
        elif level_type == "tower_defense":
            # Башня - большая и заметная
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, DARK_GRAY, (self.x + 5, self.y - 10, self.width - 10, 10))  # Пушка
            pygame.draw.circle(screen, YELLOW, (self.x + self.width//2, self.y + self.height//2), 5)  # Центр
        elif level_type == "stealth":
            # Шпион - синий с белыми глазами
            pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 5), 3)  # Левый глаз
            pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 5), 3)  # Правый глаз
            pygame.draw.rect(screen, BLACK, (self.x + 10, self.y + 15, 10, 3))  # Рот
        elif level_type == "fighting":
            # Боец - красный с желтыми перчатками
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 5), 3)  # Левый глаз
            pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 5), 3)  # Правый глаз
            pygame.draw.rect(screen, YELLOW, (self.x - 5, self.y + 10, 8, 8))  # Левая перчатка
            pygame.draw.rect(screen, YELLOW, (self.x + self.width - 3, self.y + 10, 8, 8))  # Правая перчатка
        elif level_type == "strategy":
            # Командир - зеленый с золотыми знаками отличия
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 5), 3)  # Левый глаз
            pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 5), 3)  # Правый глаз
            pygame.draw.rect(screen, YELLOW, (self.x + 5, self.y + 2, 20, 3))  # Погоны
            pygame.draw.circle(screen, YELLOW, (self.x + 15, self.y + 12), 4)  # Медаль
        elif level_type == "survival":
            # Выживший с поворотом к мыши
            center_x = self.x + self.width//2
            center_y = self.y + self.height//2
            
            # Основное тело - зеленый прямоугольник
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, DARK_GRAY, (self.x + 2, self.y + 2, self.width - 4, self.height - 4), 2)
            
            # Глаза
            pygame.draw.circle(screen, WHITE, (self.x + 8, self.y + 6), 3)
            pygame.draw.circle(screen, WHITE, (self.x + 22, self.y + 6), 3)
            pygame.draw.circle(screen, BLACK, (self.x + 8, self.y + 6), 1)  # Зрачки
            pygame.draw.circle(screen, BLACK, (self.x + 22, self.y + 6), 1)
            
            # Оружие (направлено в сторону мыши)
            weapon_length = 25
            weapon_end_x = center_x + math.cos(self.rotation_angle) * weapon_length
            weapon_end_y = center_y + math.sin(self.rotation_angle) * weapon_length
            
            # Ствол оружия
            pygame.draw.line(screen, BLACK, (center_x, center_y), (weapon_end_x, weapon_end_y), 4)
            pygame.draw.line(screen, GRAY, (center_x, center_y), (weapon_end_x, weapon_end_y), 2)
            
            # Рукоятка
            grip_offset = 8
            grip_x = center_x - math.cos(self.rotation_angle) * grip_offset
            grip_y = center_y - math.sin(self.rotation_angle) * grip_offset
            pygame.draw.circle(screen, BROWN, (int(grip_x), int(grip_y)), 4)
            
            # Дуло оружия
            pygame.draw.circle(screen, BLACK, (int(weapon_end_x), int(weapon_end_y)), 3)
            pygame.draw.circle(screen, DARK_GRAY, (int(weapon_end_x), int(weapon_end_y)), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Missile:
    def __init__(self, x, y, target, speed=2):
        self.x = x
        self.y = y
        self.target = target
        self.speed = speed
        self.width = 8
        self.height = 15
        
    def update(self):
        # Самонаведение на игрока
        dx = self.target.x + self.target.width//2 - self.x
        dy = self.target.y + self.target.height//2 - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, ORANGE, (int(self.x + self.width//2), int(self.y + self.height)), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class PlayerBullet:
    def __init__(self, x, y, speed=8, angle=None):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = speed
        self.angle = angle
        if angle is not None:
            # Направленная пуля (для survival)
            self.dx = math.cos(angle) * speed
            self.dy = math.sin(angle) * speed
        else:
            # Обычная пуля вверх
            self.dx = 0
            self.dy = -speed
        
    def update(self):
        if self.angle is not None:
            # Направленная пуля
            self.x += self.dx
            self.y += self.dy
        else:
            # Обычная пуля вверх
            self.y -= self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 80
        self.health = 500
        self.max_health = 500
        self.speed = 1
        self.direction_x = 1
        self.direction_y = 1
        self.attack_timer = 0
        self.phase = 1  # Фазы босса: 1, 2, 3
        self.special_attack_timer = 0
        self.boss_bullets = []
        
    def update(self, player):
        # Движение босса
        self.x += self.speed * self.direction_x
        self.y += self.speed * self.direction_y * 0.5
        
        # Отскок от границ
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.direction_x *= -1
        if self.y <= 0 or self.y >= 200:
            self.direction_y *= -1
        
        # Определяем фазу по здоровью
        health_percent = self.health / self.max_health
        if health_percent > 0.66:
            self.phase = 1
        elif health_percent > 0.33:
            self.phase = 2
        else:
            self.phase = 3
        
        # Увеличиваем скорость в зависимости от фазы
        base_speed = self.phase
        self.speed = base_speed
        
        # Атаки босса
        self.attack_timer += 1
        self.special_attack_timer += 1
        
        # Обычная атака - стрельба по игроку
        if self.attack_timer >= max(30 - self.phase * 5, 10):  # Быстрее с каждой фазой
            # Стреляем в сторону игрока
            dx = player.x - (self.x + self.width//2)
            dy = player.y - (self.y + self.height)
            distance = math.sqrt(dx*dx + dy*dy)
            if distance > 0:
                bullet_speed = 3 + self.phase
                self.boss_bullets.append({
                    "x": self.x + self.width//2,
                    "y": self.y + self.height,
                    "dx": (dx / distance) * bullet_speed,
                    "dy": (dy / distance) * bullet_speed,
                    "type": "normal"
                })
            self.attack_timer = 0
        
        # Специальные атаки
        if self.special_attack_timer >= 120:  # Каждые 2 секунды
            if self.phase == 2:
                # Фаза 2: Веерная стрельба
                for angle in range(-45, 46, 15):
                    rad = math.radians(angle)
                    self.boss_bullets.append({
                        "x": self.x + self.width//2,
                        "y": self.y + self.height,
                        "dx": math.sin(rad) * 4,
                        "dy": math.cos(rad) * 4,
                        "type": "spread"
                    })
            elif self.phase == 3:
                # Фаза 3: Круговая атака + веерная
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    self.boss_bullets.append({
                        "x": self.x + self.width//2,
                        "y": self.y + self.height//2,
                        "dx": math.cos(rad) * 3,
                        "dy": math.sin(rad) * 3,
                        "type": "circle"
                    })
                # Плюс веерная атака
                for angle in range(-60, 61, 10):
                    rad = math.radians(angle)
                    self.boss_bullets.append({
                        "x": self.x + self.width//2,
                        "y": self.y + self.height,
                        "dx": math.sin(rad) * 5,
                        "dy": math.cos(rad) * 5,
                        "type": "spread"
                    })
            self.special_attack_timer = 0
        
        # Обновление пуль босса
        for bullet in self.boss_bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]
            
            # Удаляем пули за границами экрана
            if (bullet["x"] < -10 or bullet["x"] > SCREEN_WIDTH + 10 or
                bullet["y"] < -10 or bullet["y"] > SCREEN_HEIGHT + 10):
                self.boss_bullets.remove(bullet)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        # Основное тело босса - большой красный корабль
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, DARK_GRAY, (self.x + 10, self.y + 10, self.width - 20, self.height - 20), 3)
        
        # Детали босса
        # Пушки
        pygame.draw.rect(screen, BLACK, (self.x + 20, self.y + self.height, 15, 20))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 35, self.y + self.height, 15, 20))
        pygame.draw.rect(screen, BLACK, (self.x + self.width//2 - 10, self.y + self.height, 20, 25))
        
        # Глаза/огни
        pygame.draw.circle(screen, YELLOW, (self.x + 30, self.y + 20), 8)
        pygame.draw.circle(screen, YELLOW, (self.x + self.width - 30, self.y + 20), 8)
        pygame.draw.circle(screen, RED, (self.x + 30, self.y + 20), 4)
        pygame.draw.circle(screen, RED, (self.x + self.width - 30, self.y + 20), 4)
        
        # Центральное ядро
        pygame.draw.circle(screen, ORANGE, (self.x + self.width//2, self.y + self.height//2), 15)
        pygame.draw.circle(screen, YELLOW, (self.x + self.width//2, self.y + self.height//2), 8)
        
        # Полоса здоровья босса
        bar_width = 200
        bar_height = 15
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 20
        
        # Фон полосы
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Здоровье
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = GREEN if self.health > self.max_health * 0.5 else (YELLOW if self.health > self.max_health * 0.25 else RED)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Рамка
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Текст босса
        font = pygame.font.Font(None, 24)
        boss_text = font.render(f"БОСС - ФАЗА {self.phase}", True, WHITE)
        screen.blit(boss_text, (bar_x, bar_y - 25))
        
        # Пули босса
        for bullet in self.boss_bullets:
            color = RED if bullet["type"] == "normal" else (ORANGE if bullet["type"] == "spread" else PURPLE)
            pygame.draw.circle(screen, color, (int(bullet["x"]), int(bullet["y"])), 4)
            pygame.draw.circle(screen, WHITE, (int(bullet["x"]), int(bullet["y"])), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_bullet_rects(self):
        return [pygame.Rect(bullet["x"] - 4, bullet["y"] - 4, 8, 8) for bullet in self.boss_bullets]

class Platform:
    def __init__(self, x, y, width, height, is_wall=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_wall = is_wall
    
    def draw(self, screen):
        if self.is_wall:
            # Стены для wall jump - темно-серые с текстурой
            pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
            # Добавляем текстуру стены
            for i in range(0, self.height, 20):
                pygame.draw.line(screen, GRAY, (self.x, self.y + i), (self.x + self.width, self.y + i), 1)
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        else:
            # Обычные платформы - коричневые
            pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class RacingObstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 5
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class PuzzleBlock:
    def __init__(self, x, y, block_type="wall"):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.block_type = block_type  # "wall", "goal", "key"
        self.collected = False
    
    def draw(self, screen):
        if self.block_type == "wall":
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        elif self.block_type == "goal":
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        elif self.block_type == "key" and not self.collected:
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class RhythmNote:
    def __init__(self, x, y, note_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 20
        self.speed = 3
        self.note_type = note_type  # "left", "right", "up", "down"
        self.hit = False
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        colors = {"left": RED, "right": BLUE, "up": GREEN, "down": YELLOW}
        color = colors.get(self.note_type, WHITE)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 2, self.y + 2, self.width - 4, self.height - 4), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Spike:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
    
    def draw(self, screen):
        # Рисуем шип как треугольник
        points = [
            (self.x + self.width//2, self.y),  # Верхушка
            (self.x, self.y + self.height),    # Левый угол
            (self.x + self.width, self.y + self.height)  # Правый угол
        ]
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.polygon(screen, DARK_GRAY, points, 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Saw:
    def __init__(self, x, y, direction, range_distance):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.direction = direction  # "horizontal" или "vertical"
        self.range = range_distance
        self.speed = 2
        self.move_direction = 1
        self.rotation = 0
        self.time = 0  # Для плавного синусоидального движения
    
    def update(self):
        # Плавное синусоидальное движение пилы
        self.time += 0.03  # Медленнее для более плавного движения
        
        if self.direction == "horizontal":
            # Плавное горизонтальное движение
            self.x = self.start_x + math.sin(self.time) * (self.range / 2)
        else:  # vertical
            # Плавное вертикальное движение
            self.y = self.start_y + math.sin(self.time) * (self.range / 2)
        
        # Плавное вращение пилы
        self.rotation += 4
        if self.rotation >= 360:
            self.rotation = 0
    
    def draw(self, screen):
        # Рисуем пилу как вращающийся круг с зубцами
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        radius = self.width // 2
        
        # Основной круг пилы
        pygame.draw.circle(screen, GRAY, (center_x, center_y), radius)
        
        # Зубцы пилы
        for i in range(8):
            angle = (self.rotation + i * 45) * math.pi / 180
            end_x = center_x + int((radius + 5) * math.cos(angle))
            end_y = center_y + int((radius + 5) * math.sin(angle))
            pygame.draw.line(screen, DARK_GRAY, (center_x, center_y), (end_x, end_y), 3)
        
        # Центр пилы
        pygame.draw.circle(screen, BLACK, (center_x, center_y), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Zombie:
    def __init__(self, x, y, zombie_type="basic"):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.zombie_type = zombie_type
        self.speed = 0.8
        self.health = 30
        self.max_health = 30
        self.damage = 10
        self.attack_cooldown = 0
        
        # Разные типы зомби
        if zombie_type == "fast":
            self.speed = 1.5
            self.health = 20
            self.max_health = 20
            self.damage = 8
            self.color = YELLOW
        elif zombie_type == "tank":
            self.speed = 0.4
            self.health = 80
            self.max_health = 80
            self.damage = 20
            self.color = PURPLE
        elif zombie_type == "runner":
            self.speed = 2.0
            self.health = 15
            self.max_health = 15
            self.damage = 5
            self.color = GREEN
        else:  # basic
            self.color = RED
    
    def update(self, player):
        # Движение к игроку
        dx = player.x - self.x
        dy = player.y - self.y
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        
        # Нормализуем направление и применяем скорость
        self.x += (dx / distance) * self.speed
        self.y += (dy / distance) * self.speed
        
        # Кулдаун атаки
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def can_attack(self, player):
        distance = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        return distance < 30 and self.attack_cooldown <= 0
    
    def attack(self, player):
        if self.can_attack(player):
            player.take_damage(self.damage)
            self.attack_cooldown = 60  # 1 секунда кулдаун
            return True
        return False
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    def draw(self, screen):
        # Тело зомби
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, DARK_GRAY, (self.x + 2, self.y + 2, self.width - 4, self.height - 4), 2)
        
        # Глаза зомби
        pygame.draw.circle(screen, RED, (int(self.x + 8), int(self.y + 8)), 3)
        pygame.draw.circle(screen, RED, (int(self.x + 17), int(self.y + 8)), 3)
        
        # Рот зомби
        pygame.draw.rect(screen, BLACK, (self.x + 8, self.y + 15, 9, 3))
        
        # Полоса здоровья
        if self.health < self.max_health:
            health_width = int((self.health / self.max_health) * self.width)
            pygame.draw.rect(screen, RED, (self.x, self.y - 8, self.width, 4))
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 8, health_width, 4))
        
        # Детали разных типов зомби
        if self.zombie_type == "tank":
            # Броня
            pygame.draw.rect(screen, GRAY, (self.x + 5, self.y + 5, 15, 15), 2)
        elif self.zombie_type == "fast":
            # Когти
            pygame.draw.line(screen, BLACK, (self.x, self.y + 12), (self.x - 5, self.y + 8), 2)
            pygame.draw.line(screen, BLACK, (self.x + self.width, self.y + 12), (self.x + self.width + 5, self.y + 8), 2)
        elif self.zombie_type == "runner":
            # Следы движения
            pygame.draw.circle(screen, (0, 255, 0, 100), (int(self.x - 5), int(self.y + 12)), 3)
            pygame.draw.circle(screen, (0, 255, 0, 50), (int(self.x - 10), int(self.y + 12)), 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class TowerDefenseBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80
        self.health = 1000  # Уменьшено в 2 раза
        self.max_health = 1000
        self.speed = 0.5
        self.direction_x = 1
        self.attack_timer = 0
        self.special_attack_timer = 0
        self.minion_spawn_timer = 0
        self.boss_bullets = []
        self.minions = []
        self.phase = 1
        self.rage_mode = False
        self.shield_active = False
        self.shield_timer = 0
        self.teleport_timer = 0
        
    def update(self, towers, enemies):
        # Определяем фазу босса
        health_percent = self.health / self.max_health
        if health_percent > 0.75:
            self.phase = 1
        elif health_percent > 0.5:
            self.phase = 2
        elif health_percent > 0.25:
            self.phase = 3
        else:
            self.phase = 4
            self.rage_mode = True
        
        # Движение босса по экрану
        self.x += self.speed * self.direction_x
        if self.x <= 50 or self.x >= SCREEN_WIDTH - self.width - 50:
            self.direction_x *= -1
        
        # Щит в последней фазе
        if self.phase == 4:
            self.shield_timer += 1
            if self.shield_timer >= 180:  # Каждые 3 секунды
                self.shield_active = not self.shield_active
                self.shield_timer = 0
        
        # Телепортация в фазе 3+
        if self.phase >= 3:
            self.teleport_timer += 1
            if self.teleport_timer >= 300:  # Каждые 5 секунд
                self.x = random.randint(100, SCREEN_WIDTH - self.width - 100)
                self.teleport_timer = 0
        
        # Основные атаки - МЕДЛЕННЕЕ
        self.attack_timer += 1
        attack_rate = max(45, 120 - self.phase * 15)  # В 3 раза медленнее стрельба
        
        if self.attack_timer >= attack_rate:
            # Лазерные лучи к башням - РЕЖЕ
            if towers and random.random() < 0.3:  # Уменьшено с 70% до 30%
                target_tower = random.choice(towers)
                dx = target_tower.x - (self.x + self.width//2)
                dy = target_tower.y - (self.y + self.height)
                distance = math.sqrt(dx*dx + dy*dy)
                if distance > 0:
                    speed = 4 + self.phase
                    self.boss_bullets.append({
                        "x": self.x + self.width//2,
                        "y": self.y + self.height,
                        "dx": (dx / distance) * speed,
                        "dy": (dy / distance) * speed,
                        "type": "laser",
                        "damage": 25  # Уменьшено в 2 раза
                    })
            
            # Случайные ракеты - МЕНЬШЕ
            for _ in range(max(1, self.phase // 2)):  # В 2 раза меньше ракет
                angle = random.uniform(0, 2 * math.pi)
                self.boss_bullets.append({
                    "x": self.x + self.width//2,
                    "y": self.y + self.height//2,
                    "dx": math.cos(angle) * 2,
                    "dy": math.sin(angle) * 2,
                    "type": "rocket",
                    "damage": 15  # Уменьшено в 2 раза
                })
            
            self.attack_timer = 0
        
        # Специальные атаки - РЕЖЕ
        self.special_attack_timer += 1
        if self.special_attack_timer >= 480:  # Каждые 8 секунд (в 2 раза реже)
            if self.phase == 2:
                # Огненная волна - МЕНЬШЕ
                for i in range(6):  # В 2 раза меньше снарядов
                    angle = (i * 30) * math.pi / 180
                    self.boss_bullets.append({
                        "x": self.x + self.width//2,
                        "y": self.y + self.height//2,
                        "dx": math.cos(angle) * 3,
                        "dy": math.sin(angle) * 3,
                        "type": "fire",
                        "damage": 20  # Уменьшено в 2 раза
                    })
            elif self.phase == 3:
                # Кислотные бомбы - МЕНЬШЕ
                for _ in range(4):  # В 2 раза меньше бомб
                    x = random.randint(50, SCREEN_WIDTH - 50)
                    y = random.randint(50, SCREEN_HEIGHT - 50)
                    self.boss_bullets.append({
                        "x": self.x + self.width//2,
                        "y": self.y + self.height//2,
                        "dx": (x - (self.x + self.width//2)) / 30,
                        "dy": (y - (self.y + self.height//2)) / 30,
                        "type": "acid",
                        "damage": 30  # Уменьшено в 2 раза
                    })
            elif self.phase == 4:
                # Хаос - все виды атак, НО МЕНЬШЕ
                for attack_type in ["laser", "rocket", "fire", "acid"]:
                    for _ in range(1):  # В 3 раза меньше снарядов
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(2, 5)
                        self.boss_bullets.append({
                            "x": self.x + self.width//2,
                            "y": self.y + self.height//2,
                            "dx": math.cos(angle) * speed,
                            "dy": math.sin(angle) * speed,
                            "type": attack_type,
                            "damage": 35  # Уменьшено в 2 раза
                        })
            
            self.special_attack_timer = 0
        
        # Спавн миньонов - ГОРАЗДО РЕЖЕ
        self.minion_spawn_timer += 1
        if self.minion_spawn_timer >= max(600, 900 - self.phase * 60):  # В 3-4 раза реже
            for _ in range(max(1, self.phase // 2)):  # В 2 раза меньше миньонов
                minion = {
                    "x": random.randint(50, SCREEN_WIDTH - 50),
                    "y": 50,
                    "health": 15,  # Уменьшено в 2 раза
                    "max_health": 15,
                    "speed": 1.5,
                    "path_index": 0,
                    "path_progress": 0,
                    "reward": 5,
                    "damage": 1,
                    "type": "minion",
                    "color": ORANGE,
                    "frozen": 0
                }
                self.minions.append(minion)
            self.minion_spawn_timer = 0
        
        # Обновление пуль босса
        for bullet in self.boss_bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]
            
            # Удаляем пули за границами экрана
            if (bullet["x"] < -50 or bullet["x"] > SCREEN_WIDTH + 50 or
                bullet["y"] < -50 or bullet["y"] > SCREEN_HEIGHT + 50):
                self.boss_bullets.remove(bullet)
        
        # Обновление миньонов (простое движение вниз)
        for minion in self.minions[:]:
            minion["y"] += minion["speed"]
            if minion["y"] > SCREEN_HEIGHT:
                self.minions.remove(minion)
    
    def take_damage(self, damage):
        if not self.shield_active:
            self.health -= damage
            return self.health <= 0
        return False
    
    def draw(self, screen):
        # Эффект телепортации
        if self.phase >= 3 and self.teleport_timer > 280:
            # Мерцание перед телепортацией
            if (self.teleport_timer // 5) % 2:
                return
        
        # Основное тело босса - ОГРОМНЫЙ
        boss_color = RED
        if self.rage_mode:
            boss_color = (255, 100, 100) if (pygame.time.get_ticks() // 100) % 2 else RED
        
        pygame.draw.rect(screen, boss_color, (self.x, self.y, self.width, self.height))
        
        # Щит
        if self.shield_active:
            pygame.draw.circle(screen, CYAN, (self.x + self.width//2, self.y + self.height//2), self.width//2 + 10, 5)
            pygame.draw.circle(screen, WHITE, (self.x + self.width//2, self.y + self.height//2), self.width//2 + 15, 3)
        
        # Детали босса
        # Глаза-лазеры
        eye_color = YELLOW if self.phase < 4 else RED
        pygame.draw.circle(screen, eye_color, (self.x + 20, self.y + 20), 8)
        pygame.draw.circle(screen, eye_color, (self.x + self.width - 20, self.y + 20), 8)
        pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 20), 4)
        pygame.draw.circle(screen, WHITE, (self.x + self.width - 20, self.y + 20), 4)
        
        # Пушки
        pygame.draw.rect(screen, BLACK, (self.x + 10, self.y + self.height, 12, 20))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 22, self.y + self.height, 12, 20))
        pygame.draw.rect(screen, BLACK, (self.x + self.width//2 - 8, self.y + self.height, 16, 25))
        
        # Реактивные двигатели
        if self.rage_mode:
            flame_colors = [RED, ORANGE, YELLOW]
            for i, color in enumerate(flame_colors):
                pygame.draw.circle(screen, color, (self.x + 15, self.y + self.height + 5 + i*3), 6 - i*2)
                pygame.draw.circle(screen, color, (self.x + self.width - 15, self.y + self.height + 5 + i*3), 6 - i*2)
        
        # Центральное ядро - пульсирующее
        core_size = 20 + int(5 * math.sin(pygame.time.get_ticks() * 0.01))
        pygame.draw.circle(screen, PURPLE, (self.x + self.width//2, self.y + self.height//2), core_size)
        pygame.draw.circle(screen, WHITE, (self.x + self.width//2, self.y + self.height//2), core_size - 5)
        
        # Полоса здоровья босса
        bar_width = 300
        bar_height = 20
        bar_x = SCREEN_WIDTH//2 - bar_width//2
        bar_y = 10
        
        # Фон полосы
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Здоровье с градиентом
        health_width = int((self.health / self.max_health) * bar_width)
        if health_width > 0:
            if self.health > self.max_health * 0.6:
                health_color = GREEN
            elif self.health > self.max_health * 0.3:
                health_color = YELLOW
            else:
                health_color = RED
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Фазовые индикаторы
        for i in range(4):
            phase_color = YELLOW if i < self.phase else GRAY
            pygame.draw.circle(screen, phase_color, (bar_x + i * 80 + 40, bar_y + bar_height + 15), 8)
            pygame.draw.circle(screen, WHITE, (bar_x + i * 80 + 40, bar_y + bar_height + 15), 6, 2)
        
        # Рамка
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)
        
        # Текст босса
        font = pygame.font.Font(None, 32)
        boss_text = font.render(f"МЕГА-БОСС - ФАЗА {self.phase}", True, WHITE)
        text_rect = boss_text.get_rect(center=(SCREEN_WIDTH//2, bar_y - 25))
        screen.blit(boss_text, text_rect)
        
        # Пули босса с разными эффектами
        for bullet in self.boss_bullets:
            x, y = int(bullet["x"]), int(bullet["y"])
            if bullet["type"] == "laser":
                pygame.draw.circle(screen, RED, (x, y), 6)
                pygame.draw.circle(screen, WHITE, (x, y), 3)
            elif bullet["type"] == "rocket":
                pygame.draw.circle(screen, ORANGE, (x, y), 5)
                pygame.draw.circle(screen, YELLOW, (x, y), 2)
            elif bullet["type"] == "fire":
                pygame.draw.circle(screen, (255, 150, 0), (x, y), 4)
                pygame.draw.circle(screen, YELLOW, (x, y), 2)
            elif bullet["type"] == "acid":
                pygame.draw.circle(screen, GREEN, (x, y), 7)
                pygame.draw.circle(screen, (150, 255, 150), (x, y), 4)
        
        # Миньоны
        for minion in self.minions:
            pygame.draw.circle(screen, minion["color"], (int(minion["x"]), int(minion["y"])), 12)
            pygame.draw.circle(screen, WHITE, (int(minion["x"]), int(minion["y"])), 8, 2)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_bullet_rects(self):
        return [pygame.Rect(bullet["x"] - 6, bullet["y"] - 6, 12, 12) for bullet in self.boss_bullets]

class Tower:
    def __init__(self, x, y, tower_type="basic"):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.width = 40
        self.height = 40
        self.shoot_cooldown = 0
        self.bullets = []
        self.level = 1
        self.kill_count = 0
        self.show_range = False
        
        # Параметры в зависимости от типа башни
        if tower_type == "basic":
            self.range = 100
            self.damage = 25
            self.rate = 30  # Кулдаун между выстрелами
            self.cost = 50
            self.color = GREEN
        elif tower_type == "rapid":
            self.range = 80
            self.damage = 15
            self.rate = 10  # Быстрая стрельба
            self.cost = 75
            self.color = YELLOW
        elif tower_type == "heavy":
            self.range = 120
            self.damage = 50
            self.rate = 60  # Медленная но мощная
            self.cost = 100
            self.color = RED
        elif tower_type == "freeze":
            self.range = 90
            self.damage = 10
            self.rate = 20
            self.cost = 80
            self.color = CYAN
    
    def update(self, enemies):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Обновляем пули башни
        for bullet in self.bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]
            if bullet["y"] < 0 or bullet["y"] > SCREEN_HEIGHT or bullet["x"] < 0 or bullet["x"] > SCREEN_WIDTH:
                self.bullets.remove(bullet)
        
        # Ищем ближайшего врага в радиусе
        if self.shoot_cooldown <= 0:
            closest_enemy = None
            min_distance = self.range
            
            for enemy in enemies:
                distance = math.sqrt((self.x + self.width//2 - enemy["x"])**2 + (self.y + self.height//2 - enemy["y"])**2)
                if distance <= min_distance:
                    min_distance = distance
                    closest_enemy = enemy
            
            if closest_enemy:
                self.shoot_at_enemy(closest_enemy)
                self.shoot_cooldown = self.rate
    
    def shoot_at_enemy(self, enemy):
        # Создаем пулю направленную в сторону врага
        dx = enemy["x"] - (self.x + self.width//2)
        dy = enemy["y"] - (self.y + self.height//2)
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            speed = 5
            bullet = {
                "x": self.x + self.width//2,
                "y": self.y + self.height//2,
                "dx": (dx / distance) * speed,
                "dy": (dy / distance) * speed,
                "damage": self.damage,
                "type": self.tower_type
            }
            self.bullets.append(bullet)
    
    def can_upgrade(self):
        return self.level < 3 and self.kill_count >= self.level * 3
    
    def upgrade(self):
        if self.can_upgrade():
            self.level += 1
            self.damage += 10
            self.range += 15
            if self.tower_type == "rapid":
                self.rate = max(5, self.rate - 3)
            return True
        return False
    
    def draw(self, screen):
        # Рисуем радиус действия (полупрозрачный)
        if hasattr(self, 'show_range') and self.show_range:
            pygame.draw.circle(screen, (*self.color, 50), (self.x + self.width//2, self.y + self.height//2), self.range, 2)
        
        # Основание башни
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, DARK_GRAY, (self.x + 2, self.y + 2, self.width - 4, self.height - 4), 2)
        
        # Пушка/оружие в зависимости от типа
        center_x = self.x + self.width//2
        center_y = self.y + self.height//2
        
        if self.tower_type == "basic":
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 8)
            pygame.draw.rect(screen, DARK_GRAY, (center_x - 2, center_y - 15, 4, 15))
        elif self.tower_type == "rapid":
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 6)
            pygame.draw.rect(screen, DARK_GRAY, (center_x - 3, center_y - 12, 2, 12))
            pygame.draw.rect(screen, DARK_GRAY, (center_x + 1, center_y - 12, 2, 12))
        elif self.tower_type == "heavy":
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 10)
            pygame.draw.rect(screen, DARK_GRAY, (center_x - 4, center_y - 20, 8, 20))
        elif self.tower_type == "freeze":
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 7)
            pygame.draw.circle(screen, WHITE, (center_x, center_y - 10), 3)
        
        # Индикатор уровня
        for i in range(self.level):
            pygame.draw.circle(screen, YELLOW, (self.x + 5 + i * 8, self.y + 5), 2)
        
        # Пули башни
        for bullet in self.bullets:
            color = self.color if self.tower_type != "freeze" else CYAN
            pygame.draw.circle(screen, color, (int(bullet["x"]), int(bullet["y"])), 3)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Menu:
    def __init__(self, progress):
        self.progress = progress
        self.selected_level = 1
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and self.selected_level > 1:
                self.selected_level -= 1
            elif event.key == pygame.K_RIGHT and self.selected_level < 10:
                self.selected_level += 1
            elif event.key == pygame.K_RETURN:
                if self.progress.is_level_unlocked(self.selected_level):
                    return self.selected_level
        return None
    
    def draw(self, screen):
        # Полностью статичный фон без анимации
        screen.fill((20, 20, 40))  # Темно-синий фон
        
        # Статичные декоративные элементы
        pygame.draw.circle(screen, (60, 60, 80), (100, 100), 30)
        pygame.draw.circle(screen, (60, 60, 80), (700, 150), 25)
        pygame.draw.circle(screen, (60, 60, 80), (200, 400), 20)
        pygame.draw.circle(screen, (60, 60, 80), (600, 450), 35)
        
        # Заголовок
        title = self.font_large.render("МУЛЬТИ-ЖАНРОВАЯ ИГРА", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        subtitle = self.font_medium.render("Выберите уровень", True, WHITE)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 120))
        
        # Сетка уровней
        for i in range(1, 11):
            row = (i - 1) // 5
            col = (i - 1) % 5
            x = 150 + col * 120
            y = 200 + row * 100
            
            # Определяем цвет кнопки
            if self.progress.is_level_unlocked(i):
                if i == self.selected_level:
                    color = YELLOW
                    border_color = WHITE
                else:
                    color = GREEN
                    border_color = WHITE
            else:
                color = GRAY
                border_color = DARK_GRAY
            
            # Рисуем кнопку уровня
            pygame.draw.rect(screen, color, (x, y, 80, 60))
            pygame.draw.rect(screen, border_color, (x, y, 80, 60), 3)
            
            # Номер уровня
            level_text = self.font_medium.render(str(i), True, BLACK if color != GRAY else WHITE)
            text_rect = level_text.get_rect(center=(x + 40, y + 30))
            screen.blit(level_text, text_rect)
        
        # Описание выбранного уровня
        level_descriptions = {
            1: "ШУТЕР - Классический космический бой",
            2: "ПЛАТФОРМЕР - Доберитесь до вершины с wall jump!",
            3: "ГОНКИ - Уворачивайтесь от препятствий",
            4: "ГОЛОВОЛОМКА - Соберите ключи за минимум ходов",
            5: "РИТМ-ИГРА - Нажимайте кнопки в такт",
            6: "TOWER DEFENSE - Защищайте базу",
            7: "СТЕЛС - Избегайте охранников",
            8: "SURVIVAL - Выживание против зомби",
            9: "СТРАТЕГИЯ - Управляйте армией",
            10: "ФИНАЛЬНЫЙ МИКС - Все жанры вместе!"
        }
        
        desc = level_descriptions.get(self.selected_level, "")
        if self.progress.is_level_unlocked(self.selected_level):
            desc_text = self.font_small.render(desc, True, WHITE)
        else:
            desc_text = self.font_small.render("ЗАБЛОКИРОВАНО - пройдите предыдущий уровень", True, RED)
        
        screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 450))
        
        # Дисклеймер о раскладке клавиатуры
        disclaimer = self.font_small.render("⚠️ ВАЖНО: Переключите клавиатуру на АНГЛИЙСКИЙ язык!", True, YELLOW)
        screen.blit(disclaimer, (SCREEN_WIDTH//2 - disclaimer.get_width()//2, 480))
        
        disclaimer2 = self.font_small.render("Иначе управление WASD работать не будет!", True, YELLOW)
        screen.blit(disclaimer2, (SCREEN_WIDTH//2 - disclaimer2.get_width()//2, 500))
        
        # Инструкции
        controls = self.font_small.render("Стрелки - выбор, Enter - играть, ESC - выход", True, WHITE)
        screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, 540))

class Game:
    def __init__(self, level=1):
        # НЕ создаем новый экран - используем уже созданный
        self.screen = pygame.display.get_surface()
        if self.screen is None:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = level
        
        # Определяем тип уровня
        self.level_types = {
            1: "shooter",
            2: "platformer", 
            3: "racing",
            4: "puzzle",
            5: "rhythm",
            6: "tower_defense",
            7: "stealth",
            8: "survival",
            9: "strategy",
            10: "final_mix"
        }
        
        self.level_type = self.level_types.get(level, "shooter")
        pygame.display.set_caption(f"Уровень {level}: {self.level_type.upper()}")
        
        # Инициализация игрока
        if self.level_type == "platformer":
            self.player = Player(50, SCREEN_HEIGHT - 50, self.level_type)
        elif self.level_type == "puzzle":
            # Для головоломки - безопасная стартовая позиция
            self.player = Player(80, 80, self.level_type)
        elif self.level_type == "stealth":
            # Для стелс миссии - начинаем в подвале
            self.player = Player(50, 590, self.level_type)
        elif self.level_type == "final_mix":
            # Для финального уровня - правильная позиция
            self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, "shooter")
        else:
            self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50, self.level_type)
        
        # Общие переменные
        self.score = 0
        self.game_over = False
        self.level_complete = False
        self.timer = 0
        
        # Система помощи
        self.help_expanded = True  # Показываем помощь по умолчанию
        self.help_button_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, 120, 30)  # Кнопка в левом нижнем углу
        
        # Специфичные для жанра переменные
        self.setup_level_specific()
        
        # Шрифты
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
    
    def setup_level_specific(self):
        if self.level_type == "shooter":
            self.missiles = []
            self.player_bullets = []
            self.missile_spawn_timer = 0
            self.target_score = 20
            
        elif self.level_type == "platformer":
            # ЛИНЕЙНЫЙ ВЕРТИКАЛЬНЫЙ ПУТЬ К ВЕРШИНЕ - БЕЗ ОБХОДНЫХ ПУТЕЙ!
            center_x = SCREEN_WIDTH // 2  # Центр экрана
            
            self.platforms = [
                # ЗЕМЛЯ - ОСНОВАНИЕ
                Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),  # Земля
                Platform(center_x - 60, SCREEN_HEIGHT - 120, 120, 20),  # Стартовая платформа
                
                # УРОВЕНЬ 1: Обучение коротким прыжкам (маленькие расстояния)
                Platform(center_x - 50, 400, 100, 20),    # Первая платформа - нужен короткий прыжок
                Platform(center_x - 40, 340, 80, 20),     # Вторая платформа - короткий прыжок
                
                # УРОВЕНЬ 2: Обучение средним прыжкам (средние расстояния)
                Platform(center_x - 70, 260, 90, 20),     # Нужен средний прыжок
                Platform(center_x + 20, 190, 90, 20),     # Зигзаг - средний прыжок в сторону
                
                # УРОВЕНЬ 3: Обучение высоким прыжкам (большие расстояния)
                Platform(center_x - 60, 100, 80, 20),     # Нужен высокий прыжок!
                Platform(center_x + 10, 0, 80, 20),       # Очень высокий прыжок!
                
                # УРОВЕНЬ 4: Максимальные прыжки (вместо wall jump)
                Platform(center_x - 80, -120, 80, 20),    # Платформа слева - нужен супер высокий прыжок!
                Platform(center_x + 30, -180, 80, 20),    # Платформа справа - еще выше и в сторону!
                
                # ФИНАЛ: Грандиозный финальный прыжок
                Platform(center_x - 60, -260, 160, 20),   # Очень широкая финальная платформа - максимальный прыжок с дальним расстоянием!
                
                # Границы уровня
                Platform(0, -350, 20, SCREEN_HEIGHT + 350, True),  # Левая стена
                Platform(SCREEN_WIDTH - 20, -350, 20, SCREEN_HEIGHT + 350, True),  # Правая стена
                Platform(0, -350, SCREEN_WIDTH, 20, True),  # Потолок
            ]
            
            # ЦЕЛЬ - НА ФИНАЛЬНОЙ ПЛАТФОРМЕ!
            self.goal = Platform(center_x - 10, -280, 20, 20)  # Цель на огромной финальной платформе
            
            # Шипы только на земле - логично и безопасно
            self.spikes = [
                # Только на земле между стартовой платформой и краями
                Spike(center_x - 150, SCREEN_HEIGHT - 60),  # На земле слева от старта
                Spike(center_x + 130, SCREEN_HEIGHT - 60),  # На земле справа от старта
                # Никаких шипов в воздухе или на платформах!
            ]
            
            # Пилы далеко от основного пути - только для атмосферы
            self.saws = [
                # Слева от пути - декорация
                Saw(center_x - 150, 400, "horizontal", 30),  # Низко слева
                Saw(center_x - 140, 200, "vertical", 25),    # Средне слева
                
                # Справа от пути - декорация  
                Saw(center_x + 150, 350, "horizontal", 30),  # Низко справа
                Saw(center_x + 140, 100, "vertical", 25),    # Средне справа
            ]
            
            # Убираем переменные wall jump
            
            # Переменная для отслеживания высоты (для изменения фона)
            self.max_height_reached = SCREEN_HEIGHT
            
            # КАМЕРА ДЛЯ СЛЕДОВАНИЯ ЗА ИГРОКОМ
            self.camera_y = 0  # Смещение камеры по Y
            
        elif self.level_type == "racing":
            self.racing_obstacles = []  # Переименовываем для правильной типизации
            self.obstacle_spawn_timer = 0
            self.distance = 0
            self.target_distance = 1000
            # Добавляем недостающие атрибуты для гонок
            self.bots = []
            self.current_lap = 1
            self.target_laps = 3
            self.player_position = 1
            self.lap_progress = 0
            
        elif self.level_type == "puzzle":
            self.puzzle_blocks = []
            self.keys_collected = 0
            self.total_keys = 3
            
            # Создаем СЛОЖНЫЙ лабиринт с внутренними стенами
            # Внешние границы
            for x in range(0, SCREEN_WIDTH, 40):
                for y in range(0, SCREEN_HEIGHT, 40):
                    if x == 0 or x == SCREEN_WIDTH - 40 or y == 0 or y == SCREEN_HEIGHT - 40:
                        self.puzzle_blocks.append(PuzzleBlock(x, y, "wall"))
            
            # ВНУТРЕННИЕ СТЕНЫ - создаем настоящий лабиринт!
            # Горизонтальные стены
            for x in range(160, 320, 40):  # Стена сверху слева
                self.puzzle_blocks.append(PuzzleBlock(x, 120, "wall"))
            
            for x in range(480, 640, 40):  # Стена сверху справа
                self.puzzle_blocks.append(PuzzleBlock(x, 120, "wall"))
                
            for x in range(120, 280, 40):  # Стена в центре слева
                self.puzzle_blocks.append(PuzzleBlock(x, 280, "wall"))
                
            for x in range(440, 600, 40):  # Стена в центре справа
                self.puzzle_blocks.append(PuzzleBlock(x, 280, "wall"))
                
            for x in range(280, 520, 40):  # Длинная стена внизу
                self.puzzle_blocks.append(PuzzleBlock(x, 440, "wall"))
            
            # Вертикальные стены
            for y in range(160, 240, 40):  # Стена слева вертикальная 1
                self.puzzle_blocks.append(PuzzleBlock(320, y, "wall"))
                
            for y in range(320, 400, 40):  # Стена слева вертикальная 2
                self.puzzle_blocks.append(PuzzleBlock(160, y, "wall"))
                
            for y in range(160, 280, 40):  # Стена справа вертикальная 1
                self.puzzle_blocks.append(PuzzleBlock(560, y, "wall"))
                
            for y in range(360, 440, 40):  # Стена справа вертикальная 2
                self.puzzle_blocks.append(PuzzleBlock(600, y, "wall"))
                
            for y in range(200, 320, 40):  # Стена в центре
                self.puzzle_blocks.append(PuzzleBlock(400, y, "wall"))
                
            # Дополнительные блокирующие стены
            self.puzzle_blocks.append(PuzzleBlock(240, 200, "wall"))  # Одиночная стена 1
            self.puzzle_blocks.append(PuzzleBlock(520, 360, "wall"))  # Одиночная стена 2
            self.puzzle_blocks.append(PuzzleBlock(360, 160, "wall"))  # Одиночная стена 3
            self.puzzle_blocks.append(PuzzleBlock(280, 360, "wall"))  # Одиночная стена 4
            self.puzzle_blocks.append(PuzzleBlock(480, 200, "wall"))  # Одиночная стена 5
            
            # КЛЮЧИ - размещаем в труднодоступных местах
            self.puzzle_blocks.append(PuzzleBlock(120, 160, "key"))   # Ключ 1 - в верхнем левом углу за стеной
            self.puzzle_blocks.append(PuzzleBlock(680, 240, "key"))   # Ключ 2 - в правом верхнем углу
            self.puzzle_blocks.append(PuzzleBlock(200, 520, "key"))   # Ключ 3 - в нижнем левом углу
            
            # ЦЕЛЬ - в самом труднодоступном месте
            self.puzzle_blocks.append(PuzzleBlock(640, 520, "goal"))  # Цель в правом нижнем углу
            
        elif self.level_type == "rhythm":
            self.rhythm_notes = []
            self.note_spawn_timer = 0
            self.hit_zone_y = SCREEN_HEIGHT - 100
            self.score_multiplier = 1
            self.combo = 0
            
        elif self.level_type == "tower_defense":
            # УЛУЧШЕННЫЙ TOWER DEFENSE С БОССОМ
            self.towers = []
            self.enemies = []
            self.enemy_spawn_timer = 0
            self.lives = 20
            self.money = 300  # Еще больше денег для усиленных врагов
            self.wave = 1
            self.target_score = 5  # 5 волн перед боссом
            self.enemies_in_wave = 6  # Больше врагов в волне
            self.enemies_spawned = 0
            self.wave_complete = False
            self.wave_delay = 0
            
            # БОСС ФАЗА
            self.boss_spawned = False
            self.tower_defense_boss = None
            self.boss_fight = False
            
            # Система строительства башен
            self.selected_tower_type = "basic"
            self.build_mode = False
            self.valid_build_spots = []
            
            # Создаем валидные места для строительства (сетка)
            for x in range(100, SCREEN_WIDTH - 100, 60):
                for y in range(100, SCREEN_HEIGHT - 200, 60):
                    # Не строим на пути врагов
                    if not (SCREEN_HEIGHT//2 - 50 <= y <= SCREEN_HEIGHT//2 + 50):
                        self.valid_build_spots.append({"x": x, "y": y, "occupied": False})
            
            # Путь для врагов
            self.enemy_path = [
                {"x": -30, "y": SCREEN_HEIGHT//2},
                {"x": 200, "y": SCREEN_HEIGHT//2},
                {"x": 200, "y": 200},
                {"x": 400, "y": 200},
                {"x": 400, "y": SCREEN_HEIGHT//2 + 20},
                {"x": 600, "y": SCREEN_HEIGHT//2 + 20},
                {"x": 600, "y": 300},
                {"x": SCREEN_WIDTH + 30, "y": 300}
            ]
            
        elif self.level_type == "stealth":
            # ДЖЕЙМС БОНД СТИЛЬ - ТАЙНАЯ МИССИЯ
            self.guards = []
            self.guard_spawn_timer = 0
            self.detection_level = 0
            self.max_detection = 100
            self.target_x = 350  # Центр VIP зоны
            self.target_y = 80   # Финальный этаж здания
            self.stealth_timer = 0
            self.mission_phase = 1  # 1-проникновение, 2-середина, 3-побег
            self.alarm_active = False
            self.alarm_timer = 0
            
            # ДЛИННАЯ АРХИТЕКТУРА ЗДАНИЯ (УВЕЛИЧЕННЫЙ УРОВЕНЬ)
            self.obstacles = [
                # ПОДВАЛ - новая секция (НАЧАЛО МИССИИ)
                Platform(50, 560, 80, 40),     # Ящики на складе
                Platform(200, 580, 120, 30),   # Длинный ящик
                Platform(400, 570, 90, 40),    # Бочки
                Platform(600, 560, 100, 50),   # Большие контейнеры
                
                # Нижний этаж - ОХРАНЯЕМЫЙ ВЕСТИБЮЛЬ
                Platform(80, 480, 140, 60),    # СТОЙКА РЕСЕПШЕН (очень длинная)
                Platform(280, 450, 80, 40),    # Кресло охранника
                Platform(420, 470, 60, 50),    # Колонна
                Platform(540, 460, 120, 70),   # Диван для ожидания
                Platform(720, 480, 80, 60),    # Информационная стойка
                
                # Средний этаж - ОФИСЫ С МНОЖЕСТВОМ УКРЫТИЙ
                Platform(40, 370, 70, 50),     # Принтер
                Platform(150, 350, 100, 70),   # Стол переговоров 1
                Platform(300, 330, 80, 60),    # Офисный стол
                Platform(420, 360, 90, 80),    # Большой стол руководителя
                Platform(560, 340, 70, 50),    # Шкаф с документами
                Platform(680, 350, 90, 70),    # Еще один стол
                
                # Средне-верхний этаж - ДОПОЛНИТЕЛЬНАЯ СЕКЦИЯ
                Platform(100, 250, 80, 60),    # Сервер
                Platform(220, 240, 110, 70),   # Длинный стол
                Platform(380, 260, 70, 50),    # Сейф среднего уровня
                Platform(500, 230, 120, 80),   # Стол с компьютерами
                Platform(660, 250, 80, 60),    # Техническая стойка
                
                # ВЕРХНИЙ ЭТАЖ - VIP ЗОНА (ФИНАЛЬНАЯ ЦЕЛЬ)
                Platform(120, 130, 90, 70),    # Барная стойка
                Platform(280, 110, 160, 90),   # ОГРОМНЫЙ стол директора
                Platform(500, 120, 100, 80),   # Стол заместителя
                Platform(650, 100, 90, 70),    # Личный бар
                
                # ЛЕСТНИЦЫ И ПЕРЕХОДЫ (больше путей)
                Platform(30, 520, 25, 80),     # Лестница из подвала
                Platform(750, 520, 25, 80),    # Лестница 2
                Platform(30, 410, 25, 90),     # Лестница на средний этаж
                Platform(750, 400, 25, 100),   # Лестница 3  
                Platform(400, 300, 25, 80),    # Центральная лестница
                Platform(30, 290, 25, 80),     # Лестница на верх
                Platform(750, 280, 25, 90),    # Финальная лестница
            ]
            
            # НАМНОГО БОЛЬШЕ ОПАСНЫХ ОХРАННИКОВ
            self.guards = [
                # ПОДВАЛ - склад с охраной
                {"x": 150, "y": 580, "direction": 1, "patrol_range": 200, "start_x": 150,
                 "speed": 1.5, "vision_range": 95, "type": "patrol", "alert_level": 0},
                {"x": 500, "y": 570, "direction": -1, "patrol_range": 180, "start_x": 500,
                 "speed": 1.3, "vision_range": 90, "type": "patrol", "alert_level": 0},
                
                # Нижний этаж - УСИЛЕННАЯ ОХРАНА ВЕСТИБЮЛЯ
                {"x": 120, "y": 500, "direction": 1, "patrol_range": 160, "start_x": 120,
                 "speed": 1.8, "vision_range": 110, "type": "office", "alert_level": 0},
                {"x": 350, "y": 490, "direction": -1, "patrol_range": 140, "start_x": 350,
                 "speed": 1.6, "vision_range": 105, "type": "office", "alert_level": 0},
                {"x": 580, "y": 480, "direction": 1, "patrol_range": 150, "start_x": 580,
                 "speed": 1.7, "vision_range": 100, "type": "office", "alert_level": 0},
                {"x": 720, "y": 495, "direction": -1, "patrol_range": 80, "start_x": 720,
                 "speed": 2.0, "vision_range": 115, "type": "elite", "alert_level": 0},
                
                # Средний этаж - ОФИСНЫЕ ОХРАННИКИ (больше и быстрее)
                {"x": 80, "y": 380, "direction": 1, "patrol_range": 120, "start_x": 80,
                 "speed": 2.2, "vision_range": 120, "type": "office", "alert_level": 0},
                {"x": 200, "y": 370, "direction": -1, "patrol_range": 100, "start_x": 200,
                 "speed": 2.0, "vision_range": 110, "type": "office", "alert_level": 0},
                {"x": 350, "y": 360, "direction": 1, "patrol_range": 130, "start_x": 350,
                 "speed": 1.9, "vision_range": 115, "type": "office", "alert_level": 0},
                {"x": 500, "y": 375, "direction": -1, "patrol_range": 140, "start_x": 500,
                 "speed": 2.1, "vision_range": 125, "type": "elite", "alert_level": 0},
                {"x": 650, "y": 365, "direction": 1, "patrol_range": 90, "start_x": 650,
                 "speed": 2.3, "vision_range": 130, "type": "elite", "alert_level": 0},
                
                # Средне-верхний этаж - ТЕХНИЧЕСКАЯ ОХРАНА
                {"x": 150, "y": 270, "direction": 1, "patrol_range": 120, "start_x": 150,
                 "speed": 2.5, "vision_range": 140, "type": "elite", "alert_level": 0},
                {"x": 350, "y": 260, "direction": -1, "patrol_range": 100, "start_x": 350,
                 "speed": 2.4, "vision_range": 135, "type": "elite", "alert_level": 0},
                {"x": 550, "y": 255, "direction": 1, "patrol_range": 110, "start_x": 550,
                 "speed": 2.6, "vision_range": 145, "type": "elite", "alert_level": 0},
                
                # ВЕРХНИЙ ЭТАЖ - ЭЛИТНАЯ VIP ОХРАНА (ОЧЕНЬ ОПАСНАЯ)
                {"x": 200, "y": 150, "direction": 1, "patrol_range": 150, "start_x": 200,
                 "speed": 3.0, "vision_range": 160, "type": "elite", "alert_level": 0},
                {"x": 400, "y": 140, "direction": -1, "patrol_range": 120, "start_x": 400,
                 "speed": 2.8, "vision_range": 150, "type": "elite", "alert_level": 0},
                {"x": 600, "y": 135, "direction": 1, "patrol_range": 140, "start_x": 600,
                 "speed": 2.9, "vision_range": 155, "type": "elite", "alert_level": 0},
                
                # СНАЙПЕРЫ НА КЛЮЧЕВЫХ ПОЗИЦИЯХ (САМЫЕ ОПАСНЫЕ)
                {"x": 100, "y": 200, "direction": 0, "patrol_range": 0, "start_x": 100,
                 "speed": 0, "vision_range": 250, "type": "sniper", "alert_level": 0},
                {"x": 400, "y": 300, "direction": 0, "patrol_range": 0, "start_x": 400,
                 "speed": 0, "vision_range": 280, "type": "sniper", "alert_level": 0},
                {"x": 700, "y": 180, "direction": 0, "patrol_range": 0, "start_x": 700,
                 "speed": 0, "vision_range": 260, "type": "sniper", "alert_level": 0},
                
                # ДОПОЛНИТЕЛЬНЫЕ ПАТРУЛИ НА ЛЕСТНИЦАХ
                {"x": 50, "y": 450, "direction": 1, "patrol_range": 60, "start_x": 50,
                 "speed": 1.5, "vision_range": 80, "type": "patrol", "alert_level": 0},
                {"x": 750, "y": 320, "direction": -1, "patrol_range": 70, "start_x": 750,
                 "speed": 1.6, "vision_range": 85, "type": "patrol", "alert_level": 0},
            ]
            
        elif self.level_type == "survival":
            # SURVIVAL - выживание против зомби
            self.zombies = []
            self.zombie_spawn_timer = 0
            self.wave = 1
            self.zombies_to_spawn = 5
            self.zombies_spawned = 0
            self.wave_complete = False
            self.wave_delay = 0
            self.target_score = 5  # Выжить 5 волн
            self.ammo = 100
            self.max_ammo = 100
            self.reload_timer = 0
            self.barricades = []
            self.player_bullets = []  # Добавляем инициализацию пуль игрока
            
            # Создаем баррикады для укрытия
            self.barricades = [
                Platform(150, 200, 60, 40),
                Platform(400, 300, 60, 40),
                Platform(600, 150, 60, 40),
                Platform(200, 450, 60, 40),
                Platform(500, 500, 60, 40),
            ]
            
        elif self.level_type == "strategy":
            # StarCraft-стиль стратегия
            self.minerals = 50
            self.gas = 0
            self.supply_used = 0
            self.supply_max = 10
            
            # Ресурсы врага
            self.enemy_minerals = 50
            self.enemy_supply_used = 0
            self.enemy_supply_max = 10
            
            # Здания
            self.buildings = [
                {"type": "command_center", "x": 100, "y": 400, "health": 500, "max_health": 500}
            ]
            self.enemy_buildings = [
                {"type": "command_center", "x": 650, "y": 400, "health": 500, "max_health": 500}
            ]
            
            # Юниты
            self.units = [
                {"type": "worker", "x": 120, "y": 420, "health": 40, "target": None, "carrying": 0}
            ]
            self.enemy_units = []
            
            # Ресурсы на карте
            self.mineral_patches = [
                {"x": 50, "y": 350, "minerals": 500},
                {"x": 700, "y": 350, "minerals": 500}
            ]
            
            self.selected_building = None
            self.selected_unit_type = "worker"
            self.selected_units = []  # Выделенные юниты
            self.enemy_spawn_timer = 0
            self.target_score = 1  # Уничтожить вражескую базу
            
        elif self.level_type == "final_mix":
            # Финальный уровень с боссом
            self.missiles = []
            self.player_bullets = []
            self.missile_spawn_timer = 0
            self.boss = Boss(SCREEN_WIDTH//2 - 60, 50)  # Босс в центре вверху
            self.target_score = 1  # Победить босса
            
        # Остальные жанры пока упрощенные
        else:
            self.missiles = []
            self.player_bullets = []
            self.missile_spawn_timer = 0
            self.target_score = 15
    
    def update(self):
        if self.game_over or self.level_complete:
            return
        
        self.timer += 1
        # В tower defense игрок не двигается - это стратегическая игра
        if self.level_type != "tower_defense":
            self.player.update(self.level_type)
        
        if self.level_type == "shooter":
            self.update_shooter()
        elif self.level_type == "platformer":
            self.update_platformer()
        elif self.level_type == "racing":
            self.update_racing()
        elif self.level_type == "puzzle":
            self.update_puzzle()
        elif self.level_type == "rhythm":
            self.update_rhythm()
        elif self.level_type == "tower_defense":
            self.update_tower_defense()
        elif self.level_type == "stealth":
            self.update_stealth()
        elif self.level_type == "survival":
            self.update_survival()
        elif self.level_type == "strategy":
            self.update_strategy()
        elif self.level_type == "final_mix":
            self.update_final_mix()
        else:
            # Упрощенная версия для остальных жанров - инициализируем переменные если их нет
            if not hasattr(self, 'missile_spawn_timer'):
                self.missile_spawn_timer = 0
                self.missiles = []
                self.player_bullets = []
                self.target_score = 15
            self.update_shooter()
    
    def update_shooter(self):
        # Стрельба (пробел или мышь)
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Левая кнопка мыши
        
        if keys[pygame.K_SPACE] or mouse_pressed:
            bullet = self.player.shoot()
            if bullet:
                self.player_bullets.append(bullet)
        
        # Спавн ракет
        self.missile_spawn_timer += 1
        if self.missile_spawn_timer >= 60:
            x = random.randint(0, SCREEN_WIDTH - 8)
            y = -15
            self.missiles.append(Missile(x, y, self.player, 2))
            self.missile_spawn_timer = 0
        
        # Обновление объектов
        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.player_bullets.remove(bullet)
                continue
            
            # Проверка столкновений пуль с ракетами
            bullet_rect = bullet.get_rect()
            for missile in self.missiles[:]:
                if bullet_rect.colliderect(missile.get_rect()):
                    # Уничтожаем и ракету и пулю
                    self.missiles.remove(missile)
                    self.player_bullets.remove(bullet)
                    self.score += 1  # Даём очки за уничтожение ракеты
                    break
        
        for missile in self.missiles[:]:
            missile.update()
            if missile.get_rect().colliderect(self.player.get_rect()):
                self.game_over = True
            if missile.y > SCREEN_HEIGHT:
                self.missiles.remove(missile)
        
        if self.score >= self.target_score:
            self.level_complete = True
    
    def update_platformer(self):
        # Обновление пил
        for saw in self.saws:
            saw.update()
        
        # Проверка столкновений с платформами
        player_rect = self.player.get_rect()
        self.player.on_ground = False
        
        # Убираем wall jump - слишком сложно с новым управлением
        # Теперь стены просто блокируют горизонтальное движение
        
        # Обычные столкновения с платформами
        for platform in self.platforms:
            platform_rect = platform.get_rect()
            
            if player_rect.colliderect(platform_rect):
                # Обычные платформы (не стены)
                if not platform.is_wall:
                    if self.player.velocity_y > 0 and self.player.y < platform.y:
                        self.player.y = platform.y - self.player.height
                        self.player.velocity_y = 0
                        self.player.on_ground = True
                    elif self.player.velocity_y < 0 and self.player.y > platform.y:
                        self.player.y = platform.y + platform.height
                        self.player.velocity_y = 0
                # Стены - блокируем горизонтальное движение
                else:
                    if self.player.x < platform.x:
                        self.player.x = platform.x - self.player.width
                    else:
                        self.player.x = platform.x + platform.width
        
        # Убираем логику wall jump
        
        # Проверка столкновений с шипами
        for spike in self.spikes:
            if player_rect.colliderect(spike.get_rect()):
                self.game_over = True
        
        # Проверка столкновений с пилами
        for saw in self.saws:
            if player_rect.colliderect(saw.get_rect()):
                self.game_over = True
        
        # Отслеживаем максимальную достигнутую высоту для эффекта фона
        if self.player.y < self.max_height_reached:
            self.max_height_reached = self.player.y
        
        # ОБНОВЛЕНИЕ КАМЕРЫ - следует за игроком по вертикали
        target_camera_y = self.player.y - SCREEN_HEIGHT // 2  # Игрок в центре экрана
        # Плавное следование камеры
        self.camera_y += (target_camera_y - self.camera_y) * 0.1
        
        # Проверка достижения цели
        if player_rect.colliderect(self.goal.get_rect()):
            self.level_complete = True
        
        # Проверка падения
        if self.player.y > SCREEN_HEIGHT:
            self.game_over = True
        
        # Инструкции управления на экране
        instruction1 = self.font_small.render("A/D - движение влево/вправо", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 140))
        instruction2 = self.font_small.render("W/ПРОБЕЛ - прыжок (время нажатия = высота прыжка)", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 120))
        instruction3 = self.font_small.render("Быстрый тап = низкий прыжок, долгое нажатие = высокий прыжок", True, YELLOW)
        self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 100))
        instruction4 = self.font_small.render("Достигните ВЕРШИНЫ - используйте максимальные прыжки!", True, YELLOW)
        self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 80))
        
        # Показываем прогресс высоты
        height_progress = (SCREEN_HEIGHT - self.max_height_reached) / (SCREEN_HEIGHT + 350)
        height_progress_percent = int(height_progress * 100)
        progress_text = self.font_small.render(f"Высота: {height_progress_percent}%", True, WHITE)
        self.screen.blit(progress_text, (10, SCREEN_HEIGHT - 60))
    
    def update_racing(self):
        # Спавн препятствий
        self.obstacle_spawn_timer += 1
        if self.obstacle_spawn_timer >= 40:
            x = random.randint(0, SCREEN_WIDTH - 30)
            self.racing_obstacles.append(RacingObstacle(x, -30))
            self.obstacle_spawn_timer = 0
        
        # Обновление препятствий
        for obstacle in self.racing_obstacles[:]:
            obstacle.update()
            if obstacle.get_rect().colliderect(self.player.get_rect()):
                self.game_over = True
            if obstacle.y > SCREEN_HEIGHT:
                self.racing_obstacles.remove(obstacle)
                self.distance += 10
        
        self.distance += 1
        if self.distance >= self.target_distance:
            self.level_complete = True
    
    def update_puzzle(self):
        # Проверка сбора ключей
        player_rect = self.player.get_rect()
        for block in self.puzzle_blocks:
            if block.block_type == "key" and not block.collected:
                if player_rect.colliderect(block.get_rect()):
                    block.collected = True
                    self.keys_collected += 1
            elif block.block_type == "goal":
                if player_rect.colliderect(block.get_rect()) and self.keys_collected >= self.total_keys:
                    self.level_complete = True
            elif block.block_type == "wall":
                if player_rect.colliderect(block.get_rect()):
                    # Возвращаем игрока на предыдущую позицию
                    self.player.x -= 40 if self.player.x > block.x else -40
                    self.player.y -= 40 if self.player.y > block.y else -40
        
        if self.player.moves > self.player.target_moves:
            self.game_over = True
    
    def update_rhythm(self):
        # Спавн нот
        self.note_spawn_timer += 1
        if self.note_spawn_timer >= 60:
            note_type = random.choice(["left", "right", "up", "down"])
            x = 100 + (["left", "right", "up", "down"].index(note_type) * 150)
            self.rhythm_notes.append(RhythmNote(x, -20, note_type))
            self.note_spawn_timer = 0
        
        # Обновление нот
        keys = pygame.key.get_pressed()
        for note in self.rhythm_notes[:]:
            note.update()
            
            # Проверка попадания в зону
            if abs(note.y - self.hit_zone_y) < 30 and not note.hit:
                hit = False
                if note.note_type == "left" and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                    hit = True
                elif note.note_type == "right" and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                    hit = True
                elif note.note_type == "up" and (keys[pygame.K_UP] or keys[pygame.K_w]):
                    hit = True
                elif note.note_type == "down" and (keys[pygame.K_DOWN] or keys[pygame.K_s]):
                    hit = True
                
                if hit:
                    note.hit = True
                    self.score += 10 * self.score_multiplier
                    self.combo += 1
                    if self.combo > 10:
                        self.score_multiplier = 2
            
            if note.y > SCREEN_HEIGHT:
                if not note.hit:
                    self.combo = 0
                    self.score_multiplier = 1
                self.rhythm_notes.remove(note)
        
        if self.score >= 500:
            self.level_complete = True
    
    def update_tower_defense(self):
        # УЛУЧШЕННАЯ ЛОГИКА TOWER DEFENSE С БОССОМ
        
        # Переключение типов башен
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.selected_tower_type = "basic"
        elif keys[pygame.K_2]:
            self.selected_tower_type = "rapid"
        elif keys[pygame.K_3]:
            self.selected_tower_type = "heavy"
        elif keys[pygame.K_4]:
            self.selected_tower_type = "freeze"
        
        # БОСС ФАЗА - после всех волн
        if self.wave > self.target_score and not self.boss_spawned:
            self.tower_defense_boss = TowerDefenseBoss(SCREEN_WIDTH//2 - 40, 50)
            self.boss_spawned = True
            self.boss_fight = True
            self.money += 500  # Бонусные деньги для финальной битвы
        
        if self.boss_fight and hasattr(self, 'tower_defense_boss') and self.tower_defense_boss:
            # Обновление босса (TowerDefenseBoss)
            self.tower_defense_boss.update(self.towers, self.enemies)
            
            # Добавляем миньонов босса к обычным врагам
            for minion in self.tower_defense_boss.minions[:]:
                self.enemies.append(minion)
                self.tower_defense_boss.minions.remove(minion)
            
            # Проверка попаданий пуль башен по боссу
            for tower in self.towers:
                for bullet in tower.bullets[:]:
                    bullet_rect = pygame.Rect(bullet["x"] - 3, bullet["y"] - 3, 6, 6)
                    if bullet_rect.colliderect(self.tower_defense_boss.get_rect()):
                        if self.tower_defense_boss.take_damage(bullet["damage"]):
                            self.level_complete = True  # Босс побежден!
                        tower.bullets.remove(bullet)
                        break
            
            # Проверка попаданий пуль босса по башням
            for bullet in self.tower_defense_boss.boss_bullets[:]:
                bullet_rect = pygame.Rect(bullet["x"] - 6, bullet["y"] - 6, 12, 12)
                for tower in self.towers[:]:
                    if bullet_rect.colliderect(tower.get_rect()):
                        # Уничтожаем башню
                        self.towers.remove(tower)
                        self.tower_defense_boss.boss_bullets.remove(bullet)
                        # Находим место строительства и освобождаем его
                        for spot in self.valid_build_spots:
                            if abs(spot["x"] - tower.x) < 30 and abs(spot["y"] - tower.y) < 30:
                                spot["occupied"] = False
                        break
        
        # Обычная логика волн (только если босс не появился)
        elif not self.boss_fight:
            if self.wave_delay > 0:
                self.wave_delay -= 1
            elif not self.wave_complete:
                # Спавн врагов в текущей волне
                self.enemy_spawn_timer += 1
                spawn_rate = max(20, 80 - self.wave * 4)  # Еще быстрее спавн
                
                if self.enemy_spawn_timer >= spawn_rate and self.enemies_spawned < self.enemies_in_wave:
                    # Более разнообразные и сильные враги
                    if self.wave <= 2:
                        enemy_type = "basic"
                    elif self.wave <= 4:
                        enemy_type = "fast" if random.random() < 0.4 else "basic"
                    elif self.wave <= 8:
                        enemy_type = random.choice(["basic", "fast", "tank", "elite"])
                    else:
                        # В поздних волнах больше элитных врагов
                        enemy_type = random.choice(["fast", "tank", "elite", "elite"])
                    
                    enemy = self.create_enemy(enemy_type)
                    self.enemies.append(enemy)
                    self.enemies_spawned += 1
                    self.enemy_spawn_timer = 0
                
                # Проверяем завершение волны
                if self.enemies_spawned >= self.enemies_in_wave and len(self.enemies) == 0:
                    self.wave_complete = True
                    self.wave += 1
                    self.money += 150 + self.wave * 30  # Еще больше денег за волну для баланса
                    
                    if self.wave > self.target_score:
                        # Переходим к босс-фазе
                        pass
                    else:
                        # Готовим следующую волну
                        self.enemies_in_wave += 3 + self.wave // 2  # Больше врагов
                        self.enemies_spawned = 0
                        self.wave_complete = False
                        self.wave_delay = 150  # Меньше времени между волнами
        
        # Обновление врагов (движение по пути и регенерация)
        for enemy in self.enemies[:]:
            # Регенерация для элитных врагов
            if enemy.get("regenerates") and enemy["health"] < enemy["max_health"]:
                enemy["health"] = min(enemy["max_health"], enemy["health"] + 1)
            
            self.move_enemy_along_path(enemy)
            
            # Проверка достижения конца пути
            if enemy["path_index"] >= len(self.enemy_path) - 1:
                self.lives -= enemy.get("damage", 1)
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.game_over = True
        
        # Обновление башен
        for tower in self.towers:
            # Обновляем против обычных врагов и босса
            all_targets = self.enemies[:]
            if self.boss_fight and hasattr(self, 'tower_defense_boss') and self.tower_defense_boss:
                # Босс как дополнительная цель (но башни предпочитают обычных врагов)
                if len(self.enemies) == 0:  # Только если нет других врагов
                    all_targets.append({
                        "x": self.tower_defense_boss.x + self.tower_defense_boss.width//2,
                        "y": self.tower_defense_boss.y + self.tower_defense_boss.height//2,
                        "type": "boss"
                    })
            
            tower.update(all_targets)
            
            # Проверка попаданий пуль башен по обычным врагам
            for bullet in tower.bullets[:]:
                bullet["x"] += bullet["dx"]
                bullet["y"] += bullet["dy"]
                
                hit = False
                for enemy in self.enemies[:]:
                    enemy_rect = pygame.Rect(enemy["x"] - 15, enemy["y"] - 15, 30, 30)
                    bullet_rect = pygame.Rect(bullet["x"] - 3, bullet["y"] - 3, 6, 6)
                    
                    if bullet_rect.colliderect(enemy_rect):
                        # Наносим урон
                        enemy["health"] -= bullet["damage"]
                        
                        # Особые эффекты башен
                        if bullet["type"] == "freeze":
                            enemy["frozen"] = 60  # Заморозка на 1 секунду
                        
                        if enemy["health"] <= 0:
                            self.money += enemy.get("reward", 10)
                            tower.kill_count += 1
                            self.enemies.remove(enemy)
                        
                        tower.bullets.remove(bullet)
                        hit = True
                        break
                
                if not hit and (bullet["x"] < 0 or bullet["x"] > SCREEN_WIDTH or 
                               bullet["y"] < 0 or bullet["y"] > SCREEN_HEIGHT):
                    tower.bullets.remove(bullet)
    
    def create_enemy(self, enemy_type):
        if enemy_type == "basic":
            return {
                "x": self.enemy_path[0]["x"],
                "y": self.enemy_path[0]["y"],
                "health": 160 + self.wave * 30,  # В 2 РАЗА больше здоровья
                "max_health": 160 + self.wave * 30,
                "speed": 1.4,  # Еще быстрее
                "path_index": 0,
                "path_progress": 0,
                "reward": 30,  # В 2 раза больше награды
                "damage": 4,  # В 2 раза больше урона
                "type": "basic",
                "color": RED,
                "frozen": 0
            }
        elif enemy_type == "fast":
            return {
                "x": self.enemy_path[0]["x"],
                "y": self.enemy_path[0]["y"],
                "health": 120 + self.wave * 20,  # В 2 раза больше здоровья
                "max_health": 120 + self.wave * 20,
                "speed": 3.0,  # Еще быстрее
                "path_index": 0,
                "path_progress": 0,
                "reward": 40,  # В 2 раза больше награды
                "damage": 2,  # В 2 раза больше урона
                "type": "fast",
                "color": YELLOW,
                "frozen": 0
            }
        elif enemy_type == "tank":
            return {
                "x": self.enemy_path[0]["x"],
                "y": self.enemy_path[0]["y"],
                "health": 400 + self.wave * 50,  # В 2 РАЗА больше здоровья
                "max_health": 400 + self.wave * 50,
                "speed": 1.0,  # Быстрее
                "path_index": 0,
                "path_progress": 0,
                "reward": 80,  # В 2 раза большая награда
                "damage": 6,  # В 2 раза больше урона
                "type": "tank",
                "color": PURPLE,
                "frozen": 0
            }
        elif enemy_type == "elite":
            return {
                "x": self.enemy_path[0]["x"],
                "y": self.enemy_path[0]["y"],
                "health": 300 + self.wave * 40,  # В 2 раза больше здоровья
                "max_health": 300 + self.wave * 40,
                "speed": 2.2,  # Быстрее
                "path_index": 0,
                "path_progress": 0,
                "reward": 60,  # В 2 раза больше
                "damage": 4,  # В 2 раза больше урона
                "type": "elite",
                "color": (255, 0, 255),  # Магента
                "frozen": 0,
                "regenerates": True  # Особенность элитных врагов
            }
    
    def move_enemy_along_path(self, enemy):
        if enemy["frozen"] > 0:
            enemy["frozen"] -= 1
            return
        
        if enemy["path_index"] < len(self.enemy_path) - 1:
            current_point = self.enemy_path[enemy["path_index"]]
            next_point = self.enemy_path[enemy["path_index"] + 1]
            
            # Движение к следующей точке пути
            dx = next_point["x"] - current_point["x"]
            dy = next_point["y"] - current_point["y"]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                move_x = (dx / distance) * enemy["speed"]
                move_y = (dy / distance) * enemy["speed"]
                
                enemy["x"] += move_x
                enemy["y"] += move_y
                
                # Проверяем достижение следующей точки
                dist_to_next = math.sqrt((enemy["x"] - next_point["x"])**2 + (enemy["y"] - next_point["y"])**2)
                if dist_to_next < 10:
                    enemy["path_index"] += 1
    
    def update_stealth(self):
        # Обновляем таймеры миссии
        self.stealth_timer += 1
        if self.alarm_active:
            self.alarm_timer += 1
            if self.alarm_timer > 300:  # 5 секунд тревоги
                self.alarm_active = False
                self.alarm_timer = 0
        
        # Определяем фазу миссии (5 фаз для длинного уровня)
        if self.player.y > 550:
            self.mission_phase = 1  # Подвал
        elif self.player.y > 420:
            self.mission_phase = 2  # Вестибюль
        elif self.player.y > 300:
            self.mission_phase = 3  # Офисы
        elif self.player.y > 200:
            self.mission_phase = 4  # Техническая зона
        else:
            self.mission_phase = 5  # VIP зона
        
        # УЛУЧШЕННАЯ ЛОГИКА ОХРАННИКОВ
        for guard in self.guards:
            # Базовое движение зависит от типа
            if guard["type"] == "sniper":
                # Снайпер поворачивается медленно
                if self.stealth_timer % 120 == 0:  # Каждые 2 секунды
                    guard["direction"] = 1 if guard["direction"] <= 0 else -1
            else:
                # Обычное патрулирование с разной скоростью
                guard["x"] += guard["direction"] * guard["speed"]
                if abs(guard["x"] - guard["start_x"]) > guard["patrol_range"]:
                    guard["direction"] *= -1
            
            # Увеличиваем скорость при тревоге
            if self.alarm_active and guard["type"] != "sniper":
                guard["speed"] = min(guard["speed"] * 1.5, 3.0)
            elif not self.alarm_active:
                # Восстанавливаем нормальную скорость
                if guard["type"] == "patrol":
                    guard["speed"] = 1.0 if guard["speed"] > 1.2 else guard["speed"]
                elif guard["type"] == "office":
                    guard["speed"] = 1.1 if guard["speed"] > 1.3 else guard["speed"]
                elif guard["type"] == "elite":
                    guard["speed"] = 1.4 if guard["speed"] > 1.6 else guard["speed"]
        
        # ПРОВЕРКА УКРЫТИЯ
        player_hidden = False
        for obstacle in self.obstacles:
            if (obstacle.x - 5 <= self.player.x <= obstacle.x + obstacle.width + 5 and
                obstacle.y - 5 <= self.player.y <= obstacle.y + obstacle.height + 5):
                player_hidden = True
                break
        
        # СЛОЖНАЯ СИСТЕМА ОБНАРУЖЕНИЯ
        if not player_hidden:
            for guard in self.guards:
                distance = math.sqrt((guard["x"] - self.player.x)**2 + (guard["y"] - self.player.y)**2)
                
                # Разная дальность видимости у разных типов
                vision_range = guard["vision_range"]
                if self.alarm_active:
                    vision_range *= 1.5  # Увеличенная бдительность при тревоге
                
                if distance < vision_range:
                    # Проверка линии видимости (не через препятствия)
                    can_see = True
                    for obstacle in self.obstacles:
                        # Простая проверка препятствий между охранником и игроком
                        if (min(guard["x"], self.player.x) < obstacle.x + obstacle.width and
                            max(guard["x"], self.player.x) > obstacle.x and
                            min(guard["y"], self.player.y) < obstacle.y + obstacle.height and
                            max(guard["y"], self.player.y) > obstacle.y):
                            can_see = False
                            break
                    
                    if can_see:
                        # Скорость обнаружения зависит от типа охранника
                        detection_speed = 1
                        if guard["type"] == "elite":
                            detection_speed = 3
                        elif guard["type"] == "sniper":
                            detection_speed = 4  # Снайпер замечает быстрее всех
                        elif guard["type"] == "office":
                            detection_speed = 2
                        
                        self.detection_level += detection_speed
                        guard["alert_level"] = min(guard["alert_level"] + 2, 100)
                        
                        # При высоком уровне тревоги включается общая тревога
                        if guard["alert_level"] > 50 and not self.alarm_active:
                            self.alarm_active = True
                            # Все охранники становятся более бдительными
                            for g in self.guards:
                                g["alert_level"] = max(g["alert_level"], 30)
        else:
            # В укрытии - медленное снижение тревоги
            for guard in self.guards:
                guard["alert_level"] = max(guard["alert_level"] - 0.3, 0)
        
        # Снижение общего уровня обнаружения
        if self.detection_level > 0:
            self.detection_level -= 0.3 if player_hidden else 0.1
        
        # ПОРАЖЕНИЕ ПРИ ПОЛНОМ ОБНАРУЖЕНИИ
        if self.detection_level >= self.max_detection:
            # Игрок пойман - перезапуск уровня
            self.player.x = 50
            self.player.y = 590  # Начинаем в подвале
            self.detection_level = 0
            self.alarm_active = False
            self.alarm_timer = 0
            # Сбрасываем состояние всех охранников
            for guard in self.guards:
                guard["alert_level"] = 0
                guard["x"] = guard["start_x"]
        
        # Проверка достижения цели
        if abs(self.player.x - self.target_x) < 30 and abs(self.player.y - self.target_y) < 30:
            self.level_complete = True
    
    def update_survival(self):
        # SURVIVAL - выживание против зомби
        keys = pygame.key.get_pressed()
        
        # Перезарядка
        if self.reload_timer > 0:
            self.reload_timer -= 1
        
        # Стрельба
        if keys[pygame.K_SPACE] and self.ammo > 0 and self.reload_timer <= 0:
            bullet = self.player.shoot("survival")
            if bullet:
                self.player_bullets.append(bullet)
                self.ammo -= 1
        
        # Перезарядка при нажатии R
        if keys[pygame.K_r] and self.ammo < self.max_ammo and self.reload_timer <= 0:
            self.reload_timer = 120  # 2 секунды перезарядка
            self.ammo = self.max_ammo
        
        # Управление волнами зомби
        if self.wave_delay > 0:
            self.wave_delay -= 1
        elif not self.wave_complete:
            # Спавн зомби
            self.zombie_spawn_timer += 1
            spawn_rate = max(30, 90 - self.wave * 5)
            
            if self.zombie_spawn_timer >= spawn_rate and self.zombies_spawned < self.zombies_to_spawn:
                # Выбираем тип зомби в зависимости от волны
                if self.wave <= 2:
                    zombie_type = "basic"
                elif self.wave <= 5:
                    zombie_type = "fast" if random.random() < 0.3 else "basic"
                elif self.wave <= 8:
                    types = ["basic", "fast", "tank"]
                    zombie_type = random.choice(types)
                else:
                    types = ["basic", "fast", "tank", "runner"]
                    zombie_type = random.choice(types)
                
                # Спавн с краев экрана
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x, y = random.randint(0, SCREEN_WIDTH), -25
                elif side == "bottom":
                    x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 25
                elif side == "left":
                    x, y = -25, random.randint(0, SCREEN_HEIGHT)
                else:  # right
                    x, y = SCREEN_WIDTH + 25, random.randint(0, SCREEN_HEIGHT)
                
                zombie = Zombie(x, y, zombie_type)
                self.zombies.append(zombie)
                self.zombies_spawned += 1
                self.zombie_spawn_timer = 0
            
            # Проверка завершения волны
            if self.zombies_spawned >= self.zombies_to_spawn and len(self.zombies) == 0:
                self.wave_complete = True
                self.wave += 1
                self.score += 10
                
                if self.wave > self.target_score:
                    self.level_complete = True
                else:
                    # Подготовка следующей волны
                    self.zombies_to_spawn += 3 + self.wave // 2
                    self.zombies_spawned = 0
                    self.wave_complete = False
                    self.wave_delay = 180  # 3 секунды перерыв
                    # Восстанавливаем немного здоровья и патронов
                    self.player.health = min(100, self.player.health + 20)
                    self.ammo = self.max_ammo
        
        # Обновление зомби
        for zombie in self.zombies[:]:
            zombie.update(self.player)
            
            # Атака зомби
            if zombie.attack(self.player):
                pass  # Урон уже нанесен в методе attack
            
            if self.player.health <= 0:
                self.game_over = True
        
        # Обновление пуль игрока
        for bullet in self.player_bullets[:]:
            bullet.update()
            # Удаляем пули за границами экрана
            if (bullet.x < -10 or bullet.x > SCREEN_WIDTH + 10 or 
                bullet.y < -10 or bullet.y > SCREEN_HEIGHT + 10):
                self.player_bullets.remove(bullet)
                continue
            
            # Проверка попаданий в зомби
            bullet_rect = bullet.get_rect()
            for zombie in self.zombies[:]:
                if bullet_rect.colliderect(zombie.get_rect()):
                    if zombie.take_damage(25):  # Убили зомби
                        self.zombies.remove(zombie)
                        self.score += 5
                    self.player_bullets.remove(bullet)
                    break
        
        # Проверка столкновений с баррикадами
        player_rect = self.player.get_rect()
        for barricade in self.barricades:
            if player_rect.colliderect(barricade.get_rect()):
                # Простая физика отталкивания
                if self.player.x < barricade.x:
                    self.player.x = barricade.x - self.player.width
                else:
                    self.player.x = barricade.x + barricade.width
    
    def update_strategy(self):
        # StarCraft-стиль стратегия
        keys = pygame.key.get_pressed()
        
        # Переключение типа юнитов
        if keys[pygame.K_1]:
            self.selected_unit_type = "worker"
        elif keys[pygame.K_2]:
            self.selected_unit_type = "marine"
        elif keys[pygame.K_3]:
            self.selected_unit_type = "tank"
        
        # Создание юнитов из командного центра
        if keys[pygame.K_SPACE]:
            unit_costs = {"worker": 50, "marine": 100, "tank": 150}
            supply_costs = {"worker": 1, "marine": 2, "tank": 3}
            
            if (self.minerals >= unit_costs[self.selected_unit_type] and 
                self.supply_used + supply_costs[self.selected_unit_type] <= self.supply_max):
                
                # Создаем юнита БЕЗОПАСНО рядом с командным центром
                command_center = self.buildings[0]
                spawn_x = command_center["x"] + 90  # Дальше от базы
                spawn_y = command_center["y"] + 70  # Ниже базы
                self.units.append({
                    "type": self.selected_unit_type,
                    "x": spawn_x,
                    "y": spawn_y,
                    "health": {"worker": 40, "marine": 45, "tank": 150}[self.selected_unit_type],
                    "target": None,
                    "carrying": 0 if self.selected_unit_type == "worker" else 0,
                    "attack_cooldown": 0,
                    "move_target": None
                })
                self.minerals -= unit_costs[self.selected_unit_type]
                self.supply_used += supply_costs[self.selected_unit_type]
        
        # Обновление рабочих - сбор минералов
        for unit in self.units[:]:
            if unit["type"] == "worker":
                if unit["target"] is None:
                    # Ищем ближайший минеральный патч
                    closest_patch = None
                    min_distance = float('inf')
                    for patch in self.mineral_patches:
                        if patch["minerals"] > 0:
                            distance = math.sqrt((unit["x"] - patch["x"])**2 + (unit["y"] - patch["y"])**2)
                            if distance < min_distance:
                                min_distance = distance
                                closest_patch = patch
                    unit["target"] = closest_patch
                
                if unit["target"] and unit["carrying"] == 0:
                    # Идем к минералам
                    dx = unit["target"]["x"] - unit["x"]
                    dy = unit["target"]["y"] - unit["y"]
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < 20:
                        # Собираем минералы
                        if unit["target"]["minerals"] > 0:
                            unit["carrying"] = 8
                            unit["target"]["minerals"] -= 8
                    else:
                        # Движемся к минералам
                        unit["x"] += (dx / distance) * 1
                        unit["y"] += (dy / distance) * 1
                
                elif unit["carrying"] > 0:
                    # Возвращаемся к командному центру
                    command_center = self.buildings[0]
                    dx = command_center["x"] - unit["x"]
                    dy = command_center["y"] - unit["y"]
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < 30:
                        # Сдаем минералы
                        self.minerals += unit["carrying"]
                        unit["carrying"] = 0
                        unit["target"] = None
                    else:
                        # Движемся к базе
                        unit["x"] += (dx / distance) * 1
                        unit["y"] += (dy / distance) * 1
            
            elif unit["type"] in ["marine", "tank"]:
                # Боевые юниты - сначала проверяем команды игрока
                if unit["attack_cooldown"] > 0:
                    unit["attack_cooldown"] -= 1
                
                # Если есть цель движения от игрока
                if unit.get("move_target"):
                    target = unit["move_target"]
                    dx = target["x"] - unit["x"]
                    dy = target["y"] - unit["y"]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < 10:  # Достигли цели
                        unit["move_target"] = None
                    else:
                        # Движемся к цели
                        speed = {"marine": 2, "tank": 1}[unit["type"]]
                        unit["x"] += (dx / distance) * speed
                        unit["y"] += (dy / distance) * speed
                else:
                    # Автоматическое поведение - ищем ближайшего врага
                    closest_enemy = None
                    min_distance = float('inf')
                    for enemy in self.enemy_units:
                        distance = math.sqrt((unit["x"] - enemy["x"])**2 + (unit["y"] - enemy["y"])**2)
                        if distance < min_distance:
                            min_distance = distance
                            closest_enemy = enemy
                    
                    # Ищем ближайшую цель (враги или здания)
                    closest_target = None
                    min_distance = float('inf')
                    
                    # Проверяем вражеские юниты
                    for enemy in self.enemy_units:
                        distance = math.sqrt((unit["x"] - enemy["x"])**2 + (unit["y"] - enemy["y"])**2)
                        if distance < min_distance:
                            min_distance = distance
                            closest_target = enemy
                    
                    # Проверяем вражеские здания
                    for building in self.enemy_buildings:
                        distance = math.sqrt((unit["x"] - building["x"])**2 + (unit["y"] - building["y"])**2)
                        if distance < min_distance:
                            min_distance = distance
                            closest_target = building
                    
                    if closest_target:
                        if min_distance < 100:  # Дальность атаки
                            if unit["attack_cooldown"] <= 0:
                                damage = {"marine": 6, "tank": 20}[unit["type"]]
                                closest_target["health"] -= damage
                                unit["attack_cooldown"] = 30
                                if closest_target["health"] <= 0:
                                    if closest_target in self.enemy_units:
                                        self.enemy_units.remove(closest_target)
                                        self.score += 1
                                    elif closest_target in self.enemy_buildings:
                                        self.enemy_buildings.remove(closest_target)
                                        self.score += 10  # Больше очков за здания
                        else:
                            # Движемся к цели
                            dx = closest_target["x"] - unit["x"]
                            dy = closest_target["y"] - unit["y"]
                            distance = math.sqrt(dx*dx + dy*dy)
                            speed = {"marine": 2, "tank": 1}[unit["type"]]
                            unit["x"] += (dx / distance) * speed
                            unit["y"] += (dy / distance) * speed
        
        # Спавн вражеских юнитов - ТОЛЬКО ЗА РЕСУРСЫ
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= 180:  # Каждые 3 секунды
            if len(self.enemy_buildings) > 0:  # Только если база еще жива
                enemy_base = self.enemy_buildings[0]
                
                # Враг создает юнитов ТОЛЬКО если есть ресурсы
                unit_costs = {"worker": 50, "marine": 100}
                supply_costs = {"worker": 1, "marine": 2}
                
                # Определяем что создавать
                unit_type = "worker" if len(self.enemy_units) < 2 else "marine"
                
                # Проверяем ресурсы и население
                if (self.enemy_minerals >= unit_costs[unit_type] and 
                    self.enemy_supply_used + supply_costs[unit_type] <= self.enemy_supply_max):
                    
                    spawn_x = enemy_base["x"] - 40
                    spawn_y = enemy_base["y"] + 70
                    self.enemy_units.append({
                        "type": unit_type,
                        "x": spawn_x,
                        "y": spawn_y,
                        "health": {"worker": 40, "marine": 45}[unit_type],
                        "attack_cooldown": 0,
                        "target": None,
                        "carrying": 0 if unit_type == "worker" else 0
                    })
                    
                    # Тратим ресурсы врага
                    self.enemy_minerals -= unit_costs[unit_type]
                    self.enemy_supply_used += supply_costs[unit_type]
            
            self.enemy_spawn_timer = 0
        
        # Обновление вражеских юнитов
        for enemy in self.enemy_units[:]:
            if enemy["attack_cooldown"] > 0:
                enemy["attack_cooldown"] -= 1
            
            # Вражеские рабочие добывают минералы
            if enemy["type"] == "worker":
                if enemy["target"] is None:
                    # Ищем ближайший минеральный патч
                    closest_patch = None
                    min_distance = float('inf')
                    for patch in self.mineral_patches:
                        if patch["minerals"] > 0:
                            distance = math.sqrt((enemy["x"] - patch["x"])**2 + (enemy["y"] - patch["y"])**2)
                            if distance < min_distance:
                                min_distance = distance
                                closest_patch = patch
                    enemy["target"] = closest_patch
                
                if enemy["target"] and enemy["carrying"] == 0:
                    # Идем к минералам
                    dx = enemy["target"]["x"] - enemy["x"]
                    dy = enemy["target"]["y"] - enemy["y"]
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance < 20:
                        # Собираем минералы
                        if enemy["target"]["minerals"] > 0:
                            enemy["carrying"] = 8
                            enemy["target"]["minerals"] -= 8
                    else:
                        # Движемся к минералам
                        enemy["x"] += (dx / distance) * 1
                        enemy["y"] += (dy / distance) * 1
                
                elif enemy["carrying"] > 0:
                    # Возвращаемся к вражескому командному центру
                    if len(self.enemy_buildings) > 0:
                        enemy_command_center = self.enemy_buildings[0]
                        dx = enemy_command_center["x"] - enemy["x"]
                        dy = enemy_command_center["y"] - enemy["y"]
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance < 30:
                            # Сдаем минералы врагу
                            self.enemy_minerals += enemy["carrying"]
                            enemy["carrying"] = 0
                            enemy["target"] = None
                        else:
                            # Движемся к базе
                            enemy["x"] += (dx / distance) * 1
                            enemy["y"] += (dy / distance) * 1
            
            else:  # Боевые юниты
                # Атакуют ближайшую цель - ПРИОРИТЕТ ЗДАНИЯМ
                closest_target = None
                min_distance = float('inf')
                
                # СНАЧАЛА проверяем здания (высший приоритет)
                for building in self.buildings:
                    distance = math.sqrt((enemy["x"] - building["x"])**2 + (enemy["y"] - building["y"])**2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_target = building
                
                # Если зданий нет рядом, проверяем юниты
                if min_distance > 200:  # Только если здания далеко
                    for unit in self.units:
                        distance = math.sqrt((enemy["x"] - unit["x"])**2 + (enemy["y"] - unit["y"])**2)
                        if distance < min_distance:
                            min_distance = distance
                            closest_target = unit
                
                # Игрока атакуем только в крайнем случае
                if min_distance > 300:  # Только если все остальное очень далеко
                    player_distance = math.sqrt((enemy["x"] - self.player.x)**2 + (enemy["y"] - self.player.y)**2)
                    if player_distance < min_distance:
                        min_distance = player_distance
                        closest_target = "player"
                
                if closest_target:
                    if min_distance < 50:  # Дальность атаки
                        if enemy["attack_cooldown"] <= 0:
                            if closest_target == "player":
                                self.player.health -= 6
                                if self.player.health <= 0:
                                    self.game_over = True
                            elif isinstance(closest_target, dict):
                                if "health" in closest_target:
                                    closest_target["health"] -= 6
                                    if closest_target["health"] <= 0:
                                        if closest_target in self.units:
                                            self.supply_used -= {"worker": 1, "marine": 2, "tank": 3}.get(closest_target["type"], 1)
                                            self.units.remove(closest_target)
                                        elif closest_target in self.buildings:
                                            self.buildings.remove(closest_target)
                                            if closest_target["type"] == "command_center":
                                                self.game_over = True
                            enemy["attack_cooldown"] = 30
                    else:
                        # Движемся к цели
                        if closest_target == "player":
                            dx = self.player.x - enemy["x"]
                            dy = self.player.y - enemy["y"]
                        else:
                            dx = closest_target["x"] - enemy["x"]
                            dy = closest_target["y"] - enemy["y"]
                        
                        distance = math.sqrt(dx*dx + dy*dy)
                        enemy["x"] += (dx / distance) * 1.5
                        enemy["y"] += (dy / distance) * 1.5
        
        # Проверка победы - уничтожить вражескую базу
        if len(self.enemy_buildings) == 0:
            self.level_complete = True
    
    def update_final_mix(self):
        # Финальный уровень с боссом
        keys = pygame.key.get_pressed()
        
        # Стрельба игрока
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet:
                self.player_bullets.append(bullet)
        
        # Обновление пуль игрока
        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.player_bullets.remove(bullet)
                continue
            
            # Проверка попадания в босса
            if hasattr(self, 'boss') and self.boss and bullet.get_rect().colliderect(self.boss.get_rect()):
                if self.boss.take_damage(10):  # Босс побежден
                    self.level_complete = True
                self.player_bullets.remove(bullet)
                self.score += 1
        
        # Обновление босса
        if hasattr(self, 'boss') and self.boss:
            self.boss.update(self.player)
        
        # Проверка столкновений с пулями босса
        if hasattr(self, 'boss') and self.boss:
            player_rect = self.player.get_rect()
            for bullet_rect in self.boss.get_bullet_rects():
                if player_rect.colliderect(bullet_rect):
                    self.player.health -= 15
                    if self.player.health <= 0:
                        self.game_over = True
                    # Удаляем пулю босса после попадания
                    for bullet in self.boss.boss_bullets[:]:
                        if pygame.Rect(bullet["x"] - 4, bullet["y"] - 4, 8, 8).colliderect(player_rect):
                            self.boss.boss_bullets.remove(bullet)
                            break
            
            # Проверка столкновения с самим боссом
            if player_rect.colliderect(self.boss.get_rect()):
                self.player.health -= 1  # Постоянный урон от касания
                if self.player.health <= 0:
                    self.game_over = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.level_type == "shooter":
            self.draw_shooter()
        elif self.level_type == "platformer":
            self.draw_platformer()
        elif self.level_type == "racing":
            self.draw_racing()
        elif self.level_type == "puzzle":
            self.draw_puzzle()
        elif self.level_type == "rhythm":
            self.draw_rhythm()
        elif self.level_type == "tower_defense":
            self.draw_tower_defense()
        elif self.level_type == "stealth":
            self.draw_stealth()
        elif self.level_type == "survival":
            self.draw_survival()
        elif self.level_type == "strategy":
            self.draw_strategy()
        elif self.level_type == "final_mix":
            self.draw_final_mix()
        else:
            self.draw_shooter()
        
        # Общий UI
        self.draw_ui()
        self.draw_help()  # Добавляем помощь поверх всего
        pygame.display.flip()
    
    def draw_shooter(self):
        # КРАСИВЫЙ КОСМИЧЕСКИЙ ФОН
        
        # Градиентное космическое небо
        for y in range(SCREEN_HEIGHT):
            intensity = y / SCREEN_HEIGHT
            # От темно-синего вверху к черному внизу
            blue = int(50 - (30 * intensity))
            green = int(20 - (15 * intensity))
            red = int(10 - (5 * intensity))
            color = (red, green, blue)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # ЗВЕЗДЫ РАЗНЫХ РАЗМЕРОВ И ЯРКОСТИ
        star_data = []
        for i in range(80):
            x = (i * 47) % SCREEN_WIDTH
            y = (i * 31) % SCREEN_HEIGHT
            size = 1 + (i % 3)
            brightness = 150 + (i % 105)  # От 150 до 255
            
            # Мерцающие звезды
            twinkle = (pygame.time.get_ticks() // (100 + i % 200)) % 4
            if twinkle == 0:
                brightness = min(255, brightness + 50)
            
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (x, y), size)
            
            # Крестообразные блики у ярких звезд
            if size > 1 and brightness > 200:
                pygame.draw.line(self.screen, color, (x-4, y), (x+4, y), 1)
                pygame.draw.line(self.screen, color, (x, y-4), (x, y+4), 1)
        
        # ДАЛЕКИЕ ПЛАНЕТЫ И ТУМАННОСТИ
        
        # Большая планета справа
        planet_x, planet_y, planet_radius = 650, 150, 60
        pygame.draw.circle(self.screen, (100, 80, 120), (planet_x, planet_y), planet_radius)
        pygame.draw.circle(self.screen, (120, 100, 140), (planet_x - 15, planet_y - 15), planet_radius - 10)
        # Кольца планеты
        for i in range(3):
            ring_radius = planet_radius + 15 + i * 8
            pygame.draw.circle(self.screen, (80, 70, 90), (planet_x, planet_y), ring_radius, 2)
        
        # Малая планета слева
        small_planet_x, small_planet_y, small_radius = 120, 80, 25
        pygame.draw.circle(self.screen, (80, 120, 100), (small_planet_x, small_planet_y), small_radius)
        pygame.draw.circle(self.screen, (100, 140, 120), (small_planet_x - 8, small_planet_y - 8), small_radius - 5)
        
        # Туманность (цветное облако)
        nebula_points = [
            (300, 100), (400, 80), (480, 120), (450, 180), (350, 200), (280, 160)
        ]
        pygame.draw.polygon(self.screen, (60, 20, 80), nebula_points)
        pygame.draw.polygon(self.screen, (80, 30, 100), nebula_points, 3)
        
        # АСТЕРОИДЫ
        asteroids = [
            (200, 300, 15),
            (500, 250, 12),
            (350, 400, 18),
            (650, 350, 14),
        ]
        
        for ast_x, ast_y, ast_size in asteroids:
            # Неровная форма астероида
            points = []
            for i in range(8):
                angle = i * 45 * math.pi / 180
                radius = ast_size + random.randint(-3, 3)  # Неровные края
                x = ast_x + int(radius * math.cos(angle))
                y = ast_y + int(radius * math.sin(angle))
                points.append((x, y))
            
            pygame.draw.polygon(self.screen, (80, 70, 60), points)
            pygame.draw.polygon(self.screen, (100, 90, 80), points, 2)
            
            # Кратеры на астероидах
            pygame.draw.circle(self.screen, (60, 50, 40), (ast_x - 3, ast_y + 2), 3)
            pygame.draw.circle(self.screen, (60, 50, 40), (ast_x + 4, ast_y - 3), 2)
        
        # ИГРОВЫЕ ОБЪЕКТЫ
        
        self.player.draw(self.screen, self.level_type)
        
        # Ракеты с улучшенными эффектами
        for missile in self.missiles:
            missile.draw(self.screen)
            
            # Плазменный след
            for i in range(8):
                trail_x = missile.x - i * 2
                trail_y = missile.y + missile.height + i
                trail_size = max(1, 4 - i//2)
                trail_alpha = 255 - i * 30
                
                if trail_alpha > 0:
                    trail_color = (255, 100 + i*10, 50)
                    pygame.draw.circle(self.screen, trail_color, (int(trail_x), int(trail_y)), trail_size)
        
        # Пули игрока с энергетическими эффектами
        for bullet in self.player_bullets:
            bullet.draw(self.screen)
            
            # Энергетическое свечение
            glow_size = 8
            for i in range(3):
                glow_alpha = 100 - i * 30
                glow_color = (0, 255 - i*50, 255)
                glow_radius = glow_size - i * 2
                if glow_radius > 0:
                    pygame.draw.circle(self.screen, glow_color, (int(bullet.x + 2), int(bullet.y + 5)), glow_radius)
    
    def draw_platformer(self):
        # ДИНАМИЧЕСКИЙ ФОН НА ОСНОВЕ ВЫСОТЫ ИГРОКА
        # Вычисляем прогресс подъема с учетом высокой вершины
        # Общий диапазон: от SCREEN_HEIGHT (внизу) до -350 (на вершине) = 950 пикселей
        total_height_range = SCREEN_HEIGHT + 350
        height_progress = max(0.0, min(1.0, (SCREEN_HEIGHT - self.max_height_reached) / total_height_range))
        
        # ПЛАВНЫЕ ГРАДИЕНТНЫЕ ПЕРЕХОДЫ НЕБА С ВЫСОТОЙ
        for y in range(SCREEN_HEIGHT):
            local_intensity = y / SCREEN_HEIGHT
            
            # ПЛАВНЫЕ переходы между 5 этапами:
            # 0.0-0.2: Земля - светло-голубое небо
            # 0.2-0.4: Средние высоты - насыщенное голубое
            # 0.4-0.6: Высокие горы - темно-синее
            # 0.6-0.8: Облака - фиолетовое небо
            # 0.8-1.0: Космос - черное с звездами
            
            if height_progress <= 0.2:  # Земные высоты
                progress_in_stage = height_progress / 0.2
                # От светло-голубого к более насыщенному
                blue = int(255 - (50 * local_intensity) - (20 * progress_in_stage))
                green = int(255 - (30 * local_intensity) - (30 * progress_in_stage))
                red = int(200 + (30 * local_intensity) - (20 * progress_in_stage))
                
            elif height_progress <= 0.4:  # Средние высоты
                progress_in_stage = (height_progress - 0.2) / 0.2
                # От голубого к синему
                blue = int(235 - (60 * local_intensity) - (40 * progress_in_stage))
                green = int(225 - (50 * local_intensity) - (50 * progress_in_stage))
                red = int(180 + (20 * local_intensity) - (30 * progress_in_stage))
                
            elif height_progress <= 0.6:  # Высокие горы
                progress_in_stage = (height_progress - 0.4) / 0.2
                # От синего к темно-синему
                blue = int(195 - (80 * local_intensity) - (50 * progress_in_stage))
                green = int(175 - (60 * local_intensity) - (60 * progress_in_stage))
                red = int(150 + (10 * local_intensity) - (40 * progress_in_stage))
                
            elif height_progress <= 0.8:  # Облачные высоты
                progress_in_stage = (height_progress - 0.6) / 0.2
                # От темно-синего к фиолетовому
                blue = int(145 - (60 * local_intensity) - (60 * progress_in_stage))
                green = int(115 - (40 * local_intensity) - (50 * progress_in_stage))
                red = int(110 + (20 * local_intensity) - (30 * progress_in_stage))
                
            else:  # Космические высоты (0.8-1.0)
                progress_in_stage = (height_progress - 0.8) / 0.2
                # От фиолетового к черному космосу
                blue = int(85 - (60 * local_intensity) - (70 * progress_in_stage))
                green = int(65 - (50 * local_intensity) - (60 * progress_in_stage))
                red = int(80 - (30 * local_intensity) - (70 * progress_in_stage))
            
            color = (max(0, red), max(0, green), max(0, blue))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # ЗВЕЗДЫ ПОЯВЛЯЮТСЯ ПОСТЕПЕННО НА БОЛЬШОЙ ВЫСОТЕ
        if height_progress > 0.5:  # Звезды начинают появляться выше
            # Плавное появление звезд от 50% до 100% высоты
            star_intensity = (height_progress - 0.5) / 0.5
            star_brightness = int(star_intensity * 255)
            
            # Количество звезд увеличивается с высотой
            num_stars = int(50 * star_intensity)
            
            for i in range(num_stars):
                star_x = (i * 47 + 100) % SCREEN_WIDTH
                star_y = (i * 31 + 50) % (SCREEN_HEIGHT // 2)
                
                # Звезды ярче на большей высоте
                star_alpha = int(star_brightness * (0.5 + 0.5 * star_intensity))
                star_color = (star_alpha, star_alpha, star_alpha)
                
                pygame.draw.circle(self.screen, star_color, (star_x, star_y), 1)
                
                # Большие мерцающие звезды на очень большой высоте
                if height_progress > 0.7 and i % 4 == 0:
                    twinkle = int(abs(math.sin(pygame.time.get_ticks() * 0.01 + i)) * star_intensity * 150)
                    bright_star_color = (min(255, star_alpha + twinkle), min(255, star_alpha + twinkle), min(255, star_alpha + twinkle))
                    pygame.draw.circle(self.screen, bright_star_color, (star_x, star_y), 2)
                
                # СУПЕР яркие звезды в космосе (выше 90%)
                if height_progress > 0.9 and i % 8 == 0:
                    cosmic_twinkle = int(abs(math.sin(pygame.time.get_ticks() * 0.005 + i)) * 255)
                    cosmic_color = (cosmic_twinkle, cosmic_twinkle, min(255, cosmic_twinkle + 100))
                    pygame.draw.circle(self.screen, cosmic_color, (star_x, star_y), 3)
        
        # ЭВОЛЮЦИЯ ОБЛАКОВ НА РАЗНЫХ ВЫСОТАХ
        if height_progress < 0.8:  # Облака видны до космических высот
            # Низкие облака (0-40% высоты)
            if height_progress < 0.4:
                cloud_alpha = int((1.0 - height_progress * 2.5) * 255)
                low_clouds = [
                    (100, 250, 60), (300, 280, 45), (500, 240, 70),
                    (650, 290, 50), (200, 320, 40), (450, 260, 55),
                ]
                cloud_color_base = max(150, 255 - int(height_progress * 100))
                
                for cloud in low_clouds:
                    x, y, size = cloud
                    cloud_y_adjusted = y + int(height_progress * 50)
                    if cloud_y_adjusted < SCREEN_HEIGHT:
                        for i, (offset_x, offset_y, radius) in enumerate([
                            (0, 0, size//2), (size//3, 0, size//3), (-size//3, 0, size//3),
                            (0, -size//4, size//2.5), (size//4, size//4, size//4)
                        ]):
                            intensity = cloud_color_base if i < 3 else cloud_color_base - 20
                            cloud_color = (intensity, intensity, intensity)
                            pygame.draw.circle(self.screen, cloud_color, (x + offset_x, cloud_y_adjusted + offset_y), radius)
            
            # Средние облака (25-65% высоты)
            if 0.25 < height_progress < 0.65:
                cloud_intensity = 1.0 - abs(height_progress - 0.45) / 0.2  # Пик в середине
                mid_clouds = [
                    (150, 150, 40), (400, 180, 35), (600, 140, 50),
                    (200, 200, 30), (550, 170, 45),
                ]
                cloud_color_base = int(200 - height_progress * 100)
                
                for cloud in mid_clouds:
                    x, y, size = cloud
                    cloud_y_adjusted = y + int(height_progress * 80)
                    if cloud_y_adjusted < SCREEN_HEIGHT:
                        alpha_intensity = int(cloud_intensity * cloud_color_base)
                        for i, (offset_x, offset_y, radius) in enumerate([
                            (0, 0, size//2), (size//3, 0, size//3), (-size//3, 0, size//3)
                        ]):
                            cloud_color = (alpha_intensity, alpha_intensity, alpha_intensity)
                            pygame.draw.circle(self.screen, cloud_color, (x + offset_x, cloud_y_adjusted + offset_y), radius)
            
            # Высокие облака (50-80% высоты) - более разреженные
            if 0.5 < height_progress < 0.8:
                cloud_intensity = (0.8 - height_progress) / 0.3  # Исчезают к космосу
                high_clouds = [
                    (250, 100, 25), (500, 120, 30), (100, 130, 20), (650, 110, 35)
                ]
                cloud_color_base = int(150 - height_progress * 80)
                
                for cloud in high_clouds:
                    x, y, size = cloud
                    alpha_intensity = int(cloud_intensity * cloud_color_base)
                    for i, (offset_x, offset_y, radius) in enumerate([
                        (0, 0, size//2), (size//4, 0, size//3)
                    ]):
                        cloud_color = (alpha_intensity, alpha_intensity, alpha_intensity)
                        pygame.draw.circle(self.screen, cloud_color, (x + offset_x, y + offset_y), radius)
        
        # МНОГОСЛОЙНЫЕ ГОРЫ НА РАЗНЫХ ВЫСОТАХ
        # Дальние горы (видны с 15% высоты)
        if height_progress > 0.15:
            far_mountain_visibility = min(1.0, (height_progress - 0.15) / 0.25)
            far_intensity = int(far_mountain_visibility * 80)
            far_mountains = [
                (0, 500), (200, 400), (400, 450), (600, 380), (800, 420), (800, 600), (0, 600)
            ]
            far_color = (max(30, far_intensity), max(40, far_intensity + 10), max(60, far_intensity + 20))
            pygame.draw.polygon(self.screen, far_color, far_mountains)
        
        # Средние горы (видны с 30% высоты)
        if height_progress > 0.3:
            mid_mountain_visibility = min(1.0, (height_progress - 0.3) / 0.3)
            mid_intensity = int(mid_mountain_visibility * 100)
            mid_mountains = [
                (0, 450), (150, 350), (300, 400), (450, 320), (600, 370), (750, 300), (800, 350), (800, 600), (0, 600)
            ]
            mid_color = (max(40, mid_intensity), max(50, mid_intensity + 15), max(70, mid_intensity + 25))
            pygame.draw.polygon(self.screen, mid_color, mid_mountains)
        
        # Ближние горы (видны с 45% высоты)
        if height_progress > 0.45:
            near_mountain_visibility = min(1.0, (height_progress - 0.45) / 0.35)
            near_intensity = int(near_mountain_visibility * 120)
            near_mountains = [
                (0, 400), (100, 300), (250, 350), (400, 280), (550, 330), (700, 260), (800, 300), (800, 600), (0, 600)
            ]
            near_color = (max(50, near_intensity), max(60, near_intensity + 20), max(80, near_intensity + 40))
            pygame.draw.polygon(self.screen, near_color, near_mountains)
        
        # ДЕРЕВЬЯ ТОЛЬКО ВНИЗУ
        if height_progress < 0.5:
            tree_alpha = int((1.0 - height_progress * 2) * 255)
            trees = [(80, 450), (180, 480), (350, 470), (480, 460), (620, 475), (720, 465)]
            for tree_x, tree_y in trees:
                if tree_y < SCREEN_HEIGHT:  # Только видимые деревья
                    tree_trunk_color = (max(50, 101 - int(height_progress * 50)), max(30, 67 - int(height_progress * 37)), max(15, 33 - int(height_progress * 18)))
                    tree_crown_color = (max(15, 34 - int(height_progress * 20)), max(80, 139 - int(height_progress * 59)), max(15, 34 - int(height_progress * 20)))
                    
                    # Ствол
                    pygame.draw.rect(self.screen, tree_trunk_color, (tree_x, tree_y, 8, 40))
                    # Крона
                    pygame.draw.circle(self.screen, tree_crown_color, (tree_x + 4, tree_y - 5), 20)
                    pygame.draw.circle(self.screen, (max(0, tree_crown_color[0] - 30), max(30, tree_crown_color[1] - 30), max(0, tree_crown_color[2] - 30)), (tree_x + 4, tree_y - 5), 15)
        
        # Платформы с улучшенной графикой (С УЧЕТОМ КАМЕРЫ)
        for platform in self.platforms:
            # Применяем смещение камеры
            platform_x = platform.x
            platform_y = platform.y - self.camera_y
            
            # Рисуем только видимые платформы
            if platform_y + platform.height >= 0 and platform_y <= SCREEN_HEIGHT:
                if platform.is_wall:
                    # Каменные стены с текстурой
                    pygame.draw.rect(self.screen, (80, 80, 90), (platform_x, platform_y, platform.width, platform.height))
                    # Каменная текстура
                    for i in range(0, platform.height, 25):
                        for j in range(0, platform.width, 20):
                            stone_x = platform_x + j
                            stone_y = platform_y + i
                            pygame.draw.rect(self.screen, (90, 90, 100), (stone_x, stone_y, 18, 23), 1)
                            pygame.draw.rect(self.screen, (70, 70, 80), (stone_x + 1, stone_y + 1, 16, 21), 1)
                    pygame.draw.rect(self.screen, (60, 60, 70), (platform_x, platform_y, platform.width, platform.height), 3)
                else:
                    # Деревянные платформы с досками
                    pygame.draw.rect(self.screen, (139, 69, 19), (platform_x, platform_y, platform.width, platform.height))
                    # Доски
                    for i in range(0, platform.width, 12):
                        board_x = platform_x + i
                        pygame.draw.line(self.screen, (160, 82, 45), (board_x, platform_y), (board_x, platform_y + platform.height), 2)
                        pygame.draw.line(self.screen, (101, 67, 33), (board_x + 6, platform_y), (board_x + 6, platform_y + platform.height), 1)
                    # Гвозди
                    for i in range(10, platform.width, 20):
                        pygame.draw.circle(self.screen, (80, 80, 80), (platform_x + i, platform_y + 5), 2)
                        pygame.draw.circle(self.screen, (80, 80, 80), (platform_x + i, platform_y + platform.height - 5), 2)
        
        # Шипы с улучшенной графикой (С УЧЕТОМ КАМЕРЫ)
        for spike in self.spikes:
            spike_y = spike.y - self.camera_y
            # Рисуем только видимые шипы
            if spike_y + spike.height >= 0 and spike_y <= SCREEN_HEIGHT:
                # Основание шипа
                pygame.draw.rect(self.screen, (100, 100, 100), (spike.x, spike_y + spike.height - 5, spike.width, 5))
                # Металлический шип
                points = [
                    (spike.x + spike.width//2, spike_y),  # Острый верх
                    (spike.x + 2, spike_y + spike.height - 5),  # Левый низ
                    (spike.x + spike.width - 2, spike_y + spike.height - 5)  # Правый низ
                ]
                pygame.draw.polygon(self.screen, (120, 120, 120), points)
                pygame.draw.polygon(self.screen, (80, 80, 80), points, 2)
                # Блик на шипе
                pygame.draw.line(self.screen, (200, 200, 200), 
                               (spike.x + spike.width//2 - 2, spike_y + 3), 
                               (spike.x + spike.width//2 - 1, spike_y + spike.height//2), 2)
        
        # Пилы с улучшенной графикой (С УЧЕТОМ КАМЕРЫ)
        for saw in self.saws:
            saw_y = saw.y - self.camera_y
            # Рисуем только видимые пилы
            if saw_y + saw.height >= 0 and saw_y <= SCREEN_HEIGHT:
                center_x = saw.x + saw.width // 2
                center_y = saw_y + saw.height // 2
                radius = saw.width // 2
                
                # Основной круг пилы с градиентом
                pygame.draw.circle(self.screen, (150, 150, 150), (center_x, center_y), radius)
                pygame.draw.circle(self.screen, (180, 180, 180), (center_x, center_y), radius - 3)
                
                # Зубцы пилы
                for i in range(12):
                    angle = (saw.rotation + i * 30) * math.pi / 180
                    # Внешние зубцы
                    outer_x = center_x + int((radius + 6) * math.cos(angle))
                    outer_y = center_y + int((radius + 6) * math.sin(angle))
                    inner_x = center_x + int((radius - 2) * math.cos(angle))
                    inner_y = center_y + int((radius - 2) * math.sin(angle))
                    
                    pygame.draw.line(self.screen, (100, 100, 100), (inner_x, inner_y), (outer_x, outer_y), 3)
                    pygame.draw.line(self.screen, (200, 200, 200), (inner_x, inner_y), (outer_x, outer_y), 1)
                
                # Центр пилы
                pygame.draw.circle(self.screen, (80, 80, 80), (center_x, center_y), 5)
                pygame.draw.circle(self.screen, (120, 120, 120), (center_x, center_y), 3)
        
        # Цель с красивой анимацией (С УЧЕТОМ КАМЕРЫ)
        goal_y = self.goal.y - self.camera_y
        if goal_y + self.goal.height >= 0 and goal_y <= SCREEN_HEIGHT:
            goal_color = (0, 255, 0) if (pygame.time.get_ticks() // 300) % 2 else (0, 200, 0)
            pygame.draw.rect(self.screen, goal_color, (self.goal.x, goal_y, self.goal.width, self.goal.height))
            pygame.draw.rect(self.screen, (255, 255, 255), (self.goal.x + 2, goal_y + 2, self.goal.width - 4, self.goal.height - 4), 2)
            
            # Звездочки вокруг цели
            star_time = pygame.time.get_ticks() // 100
            for i in range(8):
                angle = (star_time + i * 45) * math.pi / 180
                star_x = self.goal.x + self.goal.width//2 + int(40 * math.cos(angle))
                star_y = goal_y + self.goal.height//2 + int(40 * math.sin(angle))
                pygame.draw.circle(self.screen, (255, 255, 0), (star_x, star_y), 3)
        
        # Игрок (С УЧЕТОМ КАМЕРЫ)
        player_y = self.player.y - self.camera_y
        # Временно сохраняем оригинальную Y координату игрока
        original_player_y = self.player.y
        self.player.y = player_y
        self.player.draw(self.screen, self.level_type)
        # Восстанавливаем оригинальную координату
        self.player.y = original_player_y
        
        # Инструкции управления на экране
        instruction1 = self.font_small.render("A/D - движение влево/вправо", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 140))
        instruction2 = self.font_small.render("W/ПРОБЕЛ - прыжок (время нажатия = высота прыжка)", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 120))
        instruction3 = self.font_small.render("Быстрый тап = низкий прыжок, долгое нажатие = высокий прыжок", True, YELLOW)
        self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 100))
        instruction4 = self.font_small.render("Достигните ВЕРШИНЫ - используйте максимальные прыжки!", True, YELLOW)
        self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 80))
        
        # Показываем прогресс высоты
        height_progress_percent = int(height_progress * 100)
        progress_text = self.font_small.render(f"Высота: {height_progress_percent}%", True, WHITE)
        self.screen.blit(progress_text, (10, SCREEN_HEIGHT - 60))
    
    def draw_racing(self):
        # Трасса с тремя полосами
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Разделители полос
        pygame.draw.line(self.screen, WHITE, (200, 0), (200, SCREEN_HEIGHT), 3)
        pygame.draw.line(self.screen, WHITE, (400, 0), (400, SCREEN_HEIGHT), 3)
        pygame.draw.line(self.screen, WHITE, (600, 0), (600, SCREEN_HEIGHT), 3)
        
        # Разметка дороги (пунктирные линии)
        for i in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.rect(self.screen, YELLOW, (300 - 5, i, 10, 20))
            pygame.draw.rect(self.screen, YELLOW, (500 - 5, i, 10, 20))
        
        # Препятствия на дороге
        for obstacle in self.racing_obstacles:
            obstacle.draw(self.screen)
        
        # Боты-соперники
        for i, bot in enumerate(self.bots):
            if 0 <= bot["y"] <= SCREEN_HEIGHT:  # Рисуем только видимых ботов
                # Машина бота
                pygame.draw.rect(self.screen, bot["color"], (bot["x"], bot["y"], 30, 20))
                pygame.draw.rect(self.screen, BLACK, (bot["x"] + 5, bot["y"] - 5, 5, 5))  # Колесо
                pygame.draw.rect(self.screen, BLACK, (bot["x"] + 20, bot["y"] - 5, 5, 5))  # Колесо
                
                # Номер бота
                bot_text = self.font_small.render(str(i+1), True, WHITE)
                self.screen.blit(bot_text, (bot["x"] + 10, bot["y"] + 5))
        
        # Игрок
        self.player.draw(self.screen, self.level_type)
        
        # UI гонок
        # Информация о круге
        lap_text = self.font.render(f"Круг: {self.current_lap}/{self.target_laps}", True, WHITE)
        self.screen.blit(lap_text, (10, 10))
        
        # Позиция в гонке
        position_text = self.font.render(f"Позиция: {self.player_position}/4", True, WHITE)
        self.screen.blit(position_text, (10, 50))
        
        # Прогресс круга
        progress_percent = int((self.lap_progress / 1000) * 100)
        progress_text = self.font_small.render(f"Прогресс: {progress_percent}%", True, WHITE)
        self.screen.blit(progress_text, (10, 90))
        
        # Инструкции
        instruction1 = self.font_small.render("A/D - поворот влево/вправо", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 100))
        instruction2 = self.font_small.render("Финишируйте ПЕРВЫМ в 3 кругах!", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 80))
        instruction3 = self.font_small.render("Соревнуйтесь с 3 ботами!", True, YELLOW)
        self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 60))
    
    def draw_puzzle(self):
        # Фон
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Блоки
        for block in self.puzzle_blocks:
            block.draw(self.screen)
        
        self.player.draw(self.screen, self.level_type)
        
        # Инструкции для сложного лабиринта
        instruction1 = self.font_small.render("WASD/СТРЕЛКИ - пошаговое движение по лабиринту", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 120))
        instruction2 = self.font_small.render("СОБЕРИТЕ все 3 ЖЕЛТЫХ ключа в труднодоступных местах!", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 100))
        instruction3 = self.font_small.render("Затем доберитесь до ЗЕЛЕНОЙ цели в правом нижнем углу", True, YELLOW)
        self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 80))
        instruction4 = self.font_small.render("Серые блоки - стены. Планируйте маршрут!", True, YELLOW)
        self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 60))
        instruction4 = self.font_small.render("Серые блоки - стены. Планируйте маршрут!", True, YELLOW)
        self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 60))
    
    def draw_rhythm(self):
        # Фон
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Дорожки для нот
        for i in range(4):
            x = 100 + i * 150
            pygame.draw.rect(self.screen, DARK_GRAY, (x, 0, 30, SCREEN_HEIGHT))
        
        # Зона попадания
        pygame.draw.rect(self.screen, WHITE, (50, self.hit_zone_y - 30, 650, 60), 3)
        
        # Ноты
        for note in self.rhythm_notes:
            note.draw(self.screen)
        
        # Индикаторы клавиш
        keys = pygame.key.get_pressed()
        indicators = [
            ("A", keys[pygame.K_LEFT] or keys[pygame.K_a]),
            ("D", keys[pygame.K_RIGHT] or keys[pygame.K_d]),
            ("W", keys[pygame.K_UP] or keys[pygame.K_w]),
            ("S", keys[pygame.K_DOWN] or keys[pygame.K_s])
        ]
        
        for i, (key, pressed) in enumerate(indicators):
            x = 100 + i * 150
            color = YELLOW if pressed else WHITE
            text = self.font.render(key, True, color)
            self.screen.blit(text, (x + 5, self.hit_zone_y - 10))
    
    def draw_tower_defense(self):
        # Фон поля боя
        pygame.draw.rect(self.screen, (40, 60, 40), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))  # Темно-зеленый
        
        # Рисуем путь врагов
        for i in range(len(self.enemy_path) - 1):
            start = self.enemy_path[i]
            end = self.enemy_path[i + 1]
            pygame.draw.line(self.screen, BROWN, (start["x"], start["y"]), (end["x"], end["y"]), 30)
        
        # Валидные места для строительства
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for spot in self.valid_build_spots:
            if not spot["occupied"]:
                distance = math.sqrt((mouse_x - spot["x"])**2 + (mouse_y - spot["y"])**2)
                if distance < 50:  # Подсвечиваем близкие места
                    color = GREEN if self.money >= Tower(0, 0, self.selected_tower_type).cost else RED
                    pygame.draw.circle(self.screen, color, (spot["x"] + 20, spot["y"] + 20), 25, 2)
                else:
                    pygame.draw.circle(self.screen, GRAY, (spot["x"] + 20, spot["y"] + 20), 20, 1)
        
        # Башни и их радиусы
        for tower in self.towers:
            # Показываем радиус при наведении
            tower_rect = tower.get_rect()
            if tower_rect.collidepoint(mouse_x, mouse_y):
                tower.show_range = True
            else:
                tower.show_range = False
            tower.draw(self.screen)
        
        # БОСС - рисуем первым чтобы он был на заднем плане
        if self.boss_fight and hasattr(self, 'tower_defense_boss') and self.tower_defense_boss:
            self.tower_defense_boss.draw(self.screen)
        
        # Враги с полосами здоровья
        for enemy in self.enemies:
            # Основное тело врага с улучшенной графикой
            base_size = 15
            if enemy["type"] == "elite":
                base_size = 18  # Элитные враги крупнее
            elif enemy["type"] == "tank":
                base_size = 20  # Танки самые крупные
            
            pygame.draw.circle(self.screen, enemy["color"], (int(enemy["x"]), int(enemy["y"])), base_size)
            pygame.draw.circle(self.screen, WHITE, (int(enemy["x"]), int(enemy["y"])), base_size - 3, 2)
            
            # Эффект заморозки
            if enemy["frozen"] > 0:
                pygame.draw.circle(self.screen, CYAN, (int(enemy["x"]), int(enemy["y"])), base_size + 3, 3)
            
            # Эффект регенерации для элитных врагов
            if enemy.get("regenerates") and enemy["health"] < enemy["max_health"]:
                pygame.draw.circle(self.screen, GREEN, (int(enemy["x"]), int(enemy["y"])), base_size + 1, 1)
            
            # Полоса здоровья над врагом
            health_width = int((enemy["health"] / enemy["max_health"]) * 30)
            pygame.draw.rect(self.screen, RED, (enemy["x"] - 15, enemy["y"] - 30, 30, 5))
            pygame.draw.rect(self.screen, GREEN, (enemy["x"] - 15, enemy["y"] - 30, health_width, 5))
            
            # Специальные детали для разных типов врагов
            if enemy["type"] == "tank":
                pygame.draw.rect(self.screen, BLACK, (enemy["x"] - 4, enemy["y"] - 10, 8, 10))  # Пушка
                pygame.draw.circle(self.screen, DARK_GRAY, (int(enemy["x"]), int(enemy["y"])), 5)  # Башня
            elif enemy["type"] == "elite":
                # Энергетическое поле
                pygame.draw.circle(self.screen, (255, 0, 255, 50), (int(enemy["x"]), int(enemy["y"])), base_size + 2, 2)
                # Корона
                for i in range(8):
                    angle = i * 45 * math.pi / 180
                    crown_x = enemy["x"] + math.cos(angle) * 8
                    crown_y = enemy["y"] + math.sin(angle) * 8
                    pygame.draw.circle(self.screen, YELLOW, (int(crown_x), int(crown_y)), 2)
            elif enemy["type"] == "fast":
                # Следы движения
                pygame.draw.circle(self.screen, (255, 255, 0, 100), (int(enemy["x"] - 5), int(enemy["y"])), 8)
                pygame.draw.circle(self.screen, (255, 255, 0, 50), (int(enemy["x"] - 10), int(enemy["y"])), 6)
        
        # UI панель
        pygame.draw.rect(self.screen, BLACK, (10, 10, 300, 120))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 300, 120), 2)
        
        # Ресурсы
        money_text = self.font_small.render(f"Деньги: {self.money}", True, YELLOW)
        self.screen.blit(money_text, (15, 15))
        
        lives_text = self.font_small.render(f"Жизни: {self.lives}", True, RED)
        self.screen.blit(lives_text, (15, 35))
        
        wave_text = self.font_small.render(f"Волна: {self.wave}/{self.target_score}", True, WHITE)
        self.screen.blit(wave_text, (15, 55))
        
        # Выбранный тип башни
        tower_costs = {"basic": 50, "rapid": 75, "heavy": 100, "freeze": 80}
        selected_text = self.font_small.render(f"Башня: {self.selected_tower_type.upper()} ({tower_costs[self.selected_tower_type]}$)", True, GREEN)
        self.screen.blit(selected_text, (15, 75))
        
        # Прогресс волны или статус босса
        if self.boss_fight:
            boss_status = self.font_small.render("⚡ БИТВА С МЕГА-БОССОМ! ⚡", True, RED)
            self.screen.blit(boss_status, (15, 95))
        elif not self.wave_complete:
            progress_text = self.font_small.render(f"Врагов: {self.enemies_spawned}/{self.enemies_in_wave}", True, WHITE)
            self.screen.blit(progress_text, (15, 95))
        else:
            delay_text = self.font_small.render(f"Следующая волна через: {self.wave_delay // 60 + 1}с", True, YELLOW)
            self.screen.blit(delay_text, (15, 95))
        
        # Инструкции
        instruction1 = self.font_small.render("1-Базовая(50$), 2-Скорострел(75$), 3-Тяжелая(100$), 4-Заморозка(80$)", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 120))
        instruction2 = self.font_small.render("ЛКМ - построить башню, ПКМ - улучшить", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 100))
        
        if self.boss_fight:
            instruction3 = self.font_small.render("БОСС УНИЧТОЖАЕТ БАШНИ! СТРОЙТЕ БОЛЬШЕ!", True, RED)
            self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 80))
            instruction4 = self.font_small.render("Побейте МЕГА-БОССА чтобы пройти уровень!", True, RED)
            self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 60))
        else:
            instruction3 = self.font_small.render("Усиленные враги: Танки(💜), Элиты(🟣), Быстрые(🟡)", True, YELLOW)
            self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 80))
            instruction4 = self.font_small.render(f"ЦЕЛЬ: Выжить {self.target_score} волн усиленных врагов, затем ПОБИТЬ БОССА!", True, YELLOW)
            self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 60))
    
    def draw_stealth(self):
        # ДЖЕЙМС БОНД СТИЛЬ - ЭЛЕГАНТНОЕ ЗДАНИЕ КАЗИНО/КОРПОРАЦИИ
        
        # Градиентный фон ночного неба
        for y in range(SCREEN_HEIGHT):
            intensity = 1 - (y / SCREEN_HEIGHT)
            dark_blue = int(15 + (25 * intensity))  # От 40 до 15
            midnight = int(20 + (30 * intensity))  # От 50 до 20
            black = int(35 + (25 * intensity))     # От 60 до 35
            color = (dark_blue, midnight, black)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Силуэты городских зданий на заднем плане
        city_buildings = [
            {"x": -50, "y": 300, "width": 100, "height": 300},
            {"x": 100, "y": 250, "width": 80, "height": 350},
            {"x": 200, "y": 280, "width": 120, "height": 320},
            {"x": 350, "y": 200, "width": 90, "height": 400},
            {"x": 480, "y": 240, "width": 110, "height": 360},
            {"x": 620, "y": 220, "width": 100, "height": 380},
            {"x": 750, "y": 260, "width": 80, "height": 340},
        ]
        
        for building in city_buildings:
            pygame.draw.rect(self.screen, (25, 25, 40), 
                           (building["x"], building["y"], building["width"], building["height"]))
            
            # Окна с редкими огнями в ночном городе
            for row in range(2, building["height"]//25):
                for col in range(1, building["width"]//20):
                    window_x = building["x"] + col * 20
                    window_y = building["y"] + row * 25
                    
                    # Только некоторые окна светятся
                    window_hash = (window_x + window_y * 3) % 8
                    if window_hash == 0:  # Желтый свет офиса
                        pygame.draw.rect(self.screen, (80, 70, 30), (window_x, window_y, 12, 15))
                    elif window_hash == 1:  # Синий свет экрана
                        pygame.draw.rect(self.screen, (30, 50, 80), (window_x, window_y, 12, 15))
        
        # ЧЁТКИЕ ЭТАЖИ ЗДАНИЯ С ПОДПИСЯМИ
        
        # Этажи с яркими разделительными линиями и подписями
        floor_levels = [
            {"y": 600, "name": "ПОДВАЛ", "color": (60, 40, 30)},      # Коричневый
            {"y": 520, "name": "ВЕСТИБЮЛЬ", "color": (40, 50, 60)},  # Серо-синий  
            {"y": 410, "name": "ОФИСЫ", "color": (50, 50, 50)},      # Серый
            {"y": 300, "name": "ТЕХОТДЕЛ", "color": (40, 60, 40)},   # Зеленоватый
            {"y": 200, "name": "VIP ЗОНА", "color": (60, 50, 40)},   # Золотистый
            {"y": 100, "name": "СЕЙФ", "color": (80, 60, 40)},       # Роскошный
        ]
        
        for i, floor in enumerate(floor_levels):
            # Основной пол этажа
            floor_height = 25 if i == 0 else 20
            pygame.draw.rect(self.screen, floor["color"], (0, floor["y"], SCREEN_WIDTH, floor_height))
            
            # Яркая разделительная линия между этажами
            pygame.draw.line(self.screen, (200, 200, 200), (0, floor["y"]), (SCREEN_WIDTH, floor["y"]), 3)
            
            # Подпись этажа
            floor_text = self.font_small.render(floor["name"], True, (255, 255, 255))
            self.screen.blit(floor_text, (SCREEN_WIDTH - 100, floor["y"] - 15))
            
            # Номер этажа слева
            floor_num = self.font.render(str(len(floor_levels) - i), True, (255, 255, 100))
            self.screen.blit(floor_num, (5, floor["y"] - 20))
            
            # Узор пола в зависимости от этажа
            if floor["name"] == "ПОДВАЛ":
                # Бетонные плиты
                for x in range(0, SCREEN_WIDTH, 60):
                    pygame.draw.line(self.screen, (80, 60, 50), (x, floor["y"]), (x, floor["y"] + floor_height), 2)
            elif floor["name"] == "ВЕСТИБЮЛЬ":
                # Мраморные прожилки
                for x in range(0, SCREEN_WIDTH, 40):
                    pygame.draw.line(self.screen, (70, 80, 90), (x, floor["y"]), (x + 20, floor["y"] + floor_height), 2)
            elif floor["name"] == "VIP ЗОНА" or floor["name"] == "СЕЙФ":
                # Роскошный паркет
                for x in range(0, SCREEN_WIDTH, 30):
                    pygame.draw.rect(self.screen, (100, 80, 60), (x, floor["y"], 25, floor_height))
                    pygame.draw.rect(self.screen, (120, 100, 80), (x + 25, floor["y"], 5, floor_height))
        
        # Роскошные препятствия для укрытия
        for obstacle in self.obstacles:
            x, y, w, h = obstacle.x, obstacle.y, obstacle.width, obstacle.height
            
            # Определяем тип препятствия по позиции
            if y > 450:  # Нижний этаж - вестибюль
                if w > 100:  # Стойка ресепшен
                    pygame.draw.rect(self.screen, (60, 30, 20), (x, y, w, h))  # Темное дерево
                    pygame.draw.rect(self.screen, (80, 60, 40), (x, y, w, 10))  # Столешница
                    # Золотая отделка
                    pygame.draw.line(self.screen, (200, 180, 100), (x, y), (x + w, y), 3)
                else:  # Диваны и колонны
                    pygame.draw.rect(self.screen, (70, 20, 20), (x, y, w, h))  # Красная кожа/мрамор
                    pygame.draw.rect(self.screen, (90, 40, 40), (x + 5, y + 5, w - 10, h - 10))
                    
            elif y > 300:  # Средний этаж - офисы
                # Офисная мебель
                pygame.draw.rect(self.screen, (40, 40, 45), (x, y, w, h))  # Современная мебель
                pygame.draw.rect(self.screen, (50, 50, 55), (x, y, w, 5))  # Глянцевая поверхность
                # Встроенные мониторы
                if w > 100:
                    for i in range(1, w//30):
                        screen_x = x + i * 30
                        pygame.draw.rect(self.screen, (10, 10, 15), (screen_x, y - 15, 20, 12))
                        pygame.draw.rect(self.screen, (0, 50, 100), (screen_x + 2, y - 13, 16, 8))
                        
            else:  # Верхний этаж - VIP зона
                # Роскошная мебель
                pygame.draw.rect(self.screen, (80, 50, 30), (x, y, w, h))  # Позолоченное дерево
                pygame.draw.rect(self.screen, (120, 100, 60), (x, y, w, 8))  # Золотая отделка
                # Хрустальные украшения
                if w > 120:  # Большой стол руководителя
                    pygame.draw.circle(self.screen, (150, 200, 255), (x + w//2, y - 10), 8)
                    for i in range(6):
                        angle = i * 60 * math.pi / 180
                        crystal_x = x + w//2 + math.cos(angle) * 12
                        crystal_y = y - 10 + math.sin(angle) * 12
                        pygame.draw.circle(self.screen, (100, 150, 200), (int(crystal_x), int(crystal_y)), 3)
        
        # Элегантное освещение
        light_sources = [
            {"x": 150, "y": 450, "power": 100},  # Лобби
            {"x": 350, "y": 320, "power": 80},   # Офис
            {"x": 550, "y": 330, "power": 80},   # Офис
            {"x": 250, "y": 180, "power": 120},  # VIP
            {"x": 500, "y": 190, "power": 120},  # VIP
        ]
        
        for light in light_sources:
            # Мягкое освещение
            for radius in range(light["power"], 0, -20):
                alpha = int(15 * (light["power"] - radius) / light["power"])
                color = (80 + alpha, 80 + alpha, 100 + alpha)
                pygame.draw.circle(self.screen, color, (light["x"], light["y"]), radius, 3)
        
        # ПРОДВИНУТЫЕ ОХРАННИКИ
        for guard in self.guards:
            x, y = int(guard["x"]), int(guard["y"])
            guard_type = guard["type"]
            alert_level = guard["alert_level"]
            
            # Размер и цвет зависят от типа
            if guard_type == "patrol":
                size = 25
                body_color = (100, 100, 150)  # Синяя форма
                weapon_color = (80, 80, 80)
            elif guard_type == "office":
                size = 28
                body_color = (80, 80, 120)   # Темно-синяя форма
                weapon_color = (60, 60, 60)
            elif guard_type == "elite":
                size = 32
                body_color = (120, 80, 80)   # Красная элитная форма
                weapon_color = (40, 40, 40)
            else:  # sniper
                size = 30
                body_color = (60, 60, 60)    # Черная форма снайпера
                weapon_color = (30, 30, 30)
            
            # Усиление цвета при тревоге
            if alert_level > 30:
                body_color = tuple(min(255, c + int(alert_level * 0.5)) for c in body_color)
            
            # Тело охранника
            pygame.draw.circle(self.screen, body_color, (x, y), size)
            pygame.draw.circle(self.screen, (200, 180, 160), (x, y - 5), size//3)  # Голова
            
            # Оружие
            if guard_type == "sniper":
                # Снайперская винтовка
                rifle_end_x = x + guard["direction"] * 40
                rifle_end_y = y - 5
                pygame.draw.line(self.screen, weapon_color, (x, y), (rifle_end_x, rifle_end_y), 4)
                pygame.draw.circle(self.screen, weapon_color, (rifle_end_x, rifle_end_y), 6)
            else:
                # Обычное оружие
                weapon_end_x = x + guard["direction"] * 20
                weapon_end_y = y
                pygame.draw.line(self.screen, weapon_color, (x, y), (weapon_end_x, weapon_end_y), 3)
            
            # Радиус обнаружения (только если настороже)
            if alert_level > 20 or self.alarm_active:
                vision_range = guard["vision_range"]
                if self.alarm_active:
                    vision_range = int(vision_range * 1.5)
                    
                # Красный конус видимости при высокой тревоге
                if alert_level > 50:
                    color = (255, 100, 100, 30)
                elif alert_level > 20:
                    color = (255, 200, 100, 20)
                else:
                    color = (200, 200, 200, 10)
                    
                pygame.draw.circle(self.screen, color[:3], (x, y), vision_range, 2)
        
        # ЦЕЛЬ МИССИИ - ОЧЕНЬ ЗАМЕТНЫЙ СЕЙФ
        target_x, target_y = self.target_x, self.target_y
        
        # БОЛЬШОЙ ЯРКИЙ СЕЙФ С АНИМАЦИЕЙ
        seiф_size = 60
        time_factor = pygame.time.get_ticks() * 0.003
        
        # Пульсирующий фон сейфа
        pulse = abs(math.sin(time_factor)) * 20 + 10
        pygame.draw.circle(self.screen, (255, 215, 0, int(pulse)), (target_x, target_y), seiф_size + 15)
        
        # Основной корпус сейфа - очень заметный
        pygame.draw.rect(self.screen, (60, 60, 70), (target_x - seiф_size//2, target_y - seiф_size//2, seiф_size, seiф_size))
        pygame.draw.rect(self.screen, (100, 100, 110), (target_x - seiф_size//2 + 5, target_y - seiф_size//2 + 5, seiф_size - 10, seiф_size - 10))
        
        # Золотая отделка
        pygame.draw.rect(self.screen, (255, 215, 0), (target_x - seiф_size//2, target_y - seiф_size//2, seiф_size, seiф_size), 4)
        
        # Большой круглый замок в центре
        pygame.draw.circle(self.screen, (255, 215, 0), (target_x, target_y), 20)
        pygame.draw.circle(self.screen, (200, 170, 0), (target_x, target_y), 15)
        pygame.draw.circle(self.screen, (150, 120, 0), (target_x, target_y), 10)
        pygame.draw.circle(self.screen, (100, 80, 0), (target_x, target_y), 5)
        
        # Вращающиеся цифры на замке
        for i in range(12):
            angle = (i * 30) + (time_factor * 50) % 360
            angle_rad = math.radians(angle)
            digit_x = target_x + math.cos(angle_rad) * 12
            digit_y = target_y + math.sin(angle_rad) * 12
            digit = str(i % 10)
            digit_surface = self.font_small.render(digit, True, (255, 255, 255))
            self.screen.blit(digit_surface, (digit_x - 5, digit_y - 5))
        
        # Мерцающие огни безопасности вокруг сейфа
        blink_fast = (pygame.time.get_ticks() // 200) % 2
        blink_slow = (pygame.time.get_ticks() // 800) % 2
        
        # Красные лазеры
        if blink_fast:
            pygame.draw.circle(self.screen, (255, 0, 0), (target_x + 35, target_y - 20), 5)
            pygame.draw.circle(self.screen, (255, 0, 0), (target_x - 35, target_y + 20), 5)
        
        # Зелёные сенсоры
        if blink_slow:
            pygame.draw.circle(self.screen, (0, 255, 0), (target_x - 25, target_y - 30), 4)
            pygame.draw.circle(self.screen, (0, 255, 0), (target_x + 25, target_y + 30), 4)
        
        # Текст "ЦЕЛЬ" над сейфом
        target_text = self.font.render("ЦЕЛЬ!", True, (255, 255, 0))
        text_rect = target_text.get_rect(center=(target_x, target_y - 50))
        
        # Мерцающий текст
        if (pygame.time.get_ticks() // 300) % 2:
            self.screen.blit(target_text, text_rect)
        
        # Стрелка указывающая на сейф
        arrow_points = [
            (target_x, target_y - 70),
            (target_x - 10, target_y - 55),
            (target_x + 10, target_y - 55)
        ]
        pygame.draw.polygon(self.screen, (255, 255, 0), arrow_points)
        
        # Игрок-шпион
        self.player.draw(self.screen, self.level_type)
        
        # АТМОСФЕРНЫЕ ЭФФЕКТЫ
        
        # Система тревоги
        if self.alarm_active:
            # Мигающий красный свет
            alarm_alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 100)
            alarm_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            alarm_surface.set_alpha(alarm_alpha)
            alarm_surface.fill((255, 0, 0))
            self.screen.blit(alarm_surface, (0, 0))
            
            # Текст тревоги
            alarm_text = self.font.render("! ТРЕВОГА !", True, (255, 255, 255))
            self.screen.blit(alarm_text, (SCREEN_WIDTH//2 - 80, 50))
        
        # UI для stealth в стиле шпионских фильмов
        # Темная панель
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (5, 5, 250, 140))
        pygame.draw.rect(self.screen, (100, 150, 200), (5, 5, 250, 140), 2)
        
        # Информация о миссии
        phase_names = ["ПОДВАЛ", "ВЕСТИБЮЛЬ", "ОФИСЫ", "ТЕХОТДЕЛ", "VIP ЗОНА"]
        phase_colors = [(150, 100, 50), (100, 150, 200), (150, 150, 150), (100, 200, 100), (255, 200, 100)]
        phase_text = self.font_small.render(f"Этаж: {phase_names[self.mission_phase - 1]}", True, phase_colors[self.mission_phase - 1])
        self.screen.blit(phase_text, (10, 10))
        
        detection_text = self.font_small.render(f"Обнаружение: {int(self.detection_level)}/{self.max_detection}", True, WHITE)
        self.screen.blit(detection_text, (10, 30))
        
        # Стильная полоса обнаружения
        bar_width = 200
        bar_height = 12
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, (100, 150, 200), (10, 50, bar_width, bar_height), 2)
        
        fill_width = int((self.detection_level / self.max_detection) * bar_width)
        if fill_width > 0:
            if self.detection_level > 75:
                color = (255, 0, 0)      # Критическая опасность
            elif self.detection_level > 50:
                color = (255, 100, 0)    # Высокая опасность
            elif self.detection_level > 25:
                color = (255, 200, 0)    # Средняя опасность
            else:
                color = (0, 200, 0)      # Безопасно
            pygame.draw.rect(self.screen, color, (10, 50, fill_width, bar_height))
        
        # Статус тревоги
        if self.alarm_active:
            alarm_status = self.font_small.render("СТАТУС: ТРЕВОГА АКТИВНА", True, (255, 100, 100))
        else:
            alarm_status = self.font_small.render("СТАТУС: СКРЫТНОСТЬ", True, (100, 255, 100))
        self.screen.blit(alarm_status, (10, 70))
        
        # Инструкции в стиле шпионского брифинга
        instruction1 = self.font_small.render("МИССИЯ: Пройти все 5 этажей и взломать ЗОЛОТОЙ СЕЙФ", True, (200, 200, 255))
        self.screen.blit(instruction1, (10, 100))
        instruction2 = self.font_small.render("WASD - скрытное перемещение | Используйте укрытия!", True, (150, 200, 255))
        self.screen.blit(instruction2, (10, 120))
        
        # Прогресс миссии
        progress_text = self.font_small.render(f"Прогресс: {self.mission_phase}/5 этажей", True, (255, 255, 100))
        self.screen.blit(progress_text, (270, 10))
        
        # Статус охранников
        alert_guards = sum(1 for g in self.guards if g['alert_level'] > 30)
        guard_info = self.font_small.render(f"Охранников в тревоге: {alert_guards}/{len(self.guards)}", True, 
                                          (255, 100, 100) if alert_guards > 5 else YELLOW)
        self.screen.blit(guard_info, (270, 30))
        
        # Краткие инструкции по типам охранников
        type_info = [
            "🔵 Патруль - медленный",
            "🔷 Офисный - быстрый", 
            "🔴 Элитный - ОПАСНЫЙ!",
            "⚫ Снайпер - дальнобойный"
        ]
        
        for i, info in enumerate(type_info):
            info_text = self.font_small.render(info, True, YELLOW)
            self.screen.blit(info_text, (270, 50 + i * 15))
        
        # Подсказка для новичков
        if self.mission_phase == 1:
            tip_text = self.font_small.render("СОВЕТ: Ждите когда охранники отвернутся!", True, (100, 255, 100))
            self.screen.blit(tip_text, (270, 110))
    
    def draw_survival(self):
        # КРАСИВАЯ АПОКАЛИПТИЧЕСКАЯ АТМОСФЕРА
        
        # Градиентное небо - от темно-красного вверху до темно-серого внизу
        for y in range(SCREEN_HEIGHT):
            intensity = y / SCREEN_HEIGHT
            red = int(60 + (20 * (1 - intensity)))  # От 80 до 60
            green = int(20 + (30 * intensity))      # От 20 до 50
            blue = int(20 + (30 * intensity))       # От 20 до 50
            color = (red, green, blue)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # СТАТИЧНЫЕ ДЕКОРАЦИИ ГОРОДА
        
        # Разрушенные здания на заднем плане
        buildings = [
            {"x": 50, "y": 150, "width": 80, "height": 200, "broken": True},
            {"x": 180, "y": 100, "width": 60, "height": 250, "broken": False},
            {"x": 280, "y": 120, "width": 90, "height": 230, "broken": True},
            {"x": 420, "y": 80, "width": 70, "height": 270, "broken": False},
            {"x": 520, "y": 110, "width": 85, "height": 240, "broken": True},
            {"x": 650, "y": 90, "width": 75, "height": 260, "broken": False},
        ]
        
        for building in buildings:
            # Основное здание
            color = (40, 35, 30) if building["broken"] else (50, 45, 40)
            pygame.draw.rect(self.screen, color, (building["x"], building["y"], building["width"], building["height"]))
            
            # Окна в зданиях
            for row in range(3, building["height"]//20):
                for col in range(1, building["width"]//15):
                    window_x = building["x"] + col * 15
                    window_y = building["y"] + row * 20
                    
                    # Случайные разбитые/целые окна
                    window_hash = (window_x + window_y * 7) % 5
                    if window_hash == 0:  # Разбитое окно
                        pygame.draw.rect(self.screen, (20, 20, 20), (window_x, window_y, 8, 12))
                        # Трещины
                        pygame.draw.line(self.screen, (60, 60, 60), (window_x, window_y), (window_x + 8, window_y + 12), 1)
                        pygame.draw.line(self.screen, (60, 60, 60), (window_x + 8, window_y), (window_x, window_y + 12), 1)
                    elif window_hash == 1:  # Горит огонь
                        pygame.draw.rect(self.screen, (100, 40, 0), (window_x, window_y, 8, 12))
                        pygame.draw.rect(self.screen, (150, 80, 0), (window_x + 1, window_y + 1, 6, 10))
                        pygame.draw.rect(self.screen, (200, 120, 20), (window_x + 2, window_y + 2, 4, 8))
                    elif window_hash == 2:  # Темное окно
                        pygame.draw.rect(self.screen, (15, 15, 25), (window_x, window_y, 8, 12))
                    elif window_hash == 3:  # Мерцающий свет
                        flicker = (pygame.time.get_ticks() // 100) % 3
                        if flicker == 0:
                            pygame.draw.rect(self.screen, (80, 80, 60), (window_x, window_y, 8, 12))
                        else:
                            pygame.draw.rect(self.screen, (40, 40, 30), (window_x, window_y, 8, 12))
            
            # Повреждения на разрушенных зданиях
            if building["broken"]:
                # Большая дыра сверху
                hole_width = building["width"] // 3
                hole_height = building["height"] // 4
                pygame.draw.rect(self.screen, (30, 25, 20), 
                               (building["x"] + hole_width, building["y"], hole_width, hole_height))
                
                # Трещины на стенах
                for i in range(3):
                    crack_x = building["x"] + (i + 1) * building["width"] // 4
                    crack_start_y = building["y"] + building["height"] // 3
                    crack_end_y = building["y"] + building["height"]
                    
                    # Зигзагообразная трещина
                    points = [(crack_x, crack_start_y)]
                    for j in range(1, 8):
                        y_pos = crack_start_y + j * (crack_end_y - crack_start_y) // 8
                        x_offset = (-1 if j % 2 == 0 else 1) * (j % 3)
                        points.append((crack_x + x_offset, y_pos))
                    
                    if len(points) > 2:
                        pygame.draw.lines(self.screen, (20, 20, 20), False, points, 2)
        
        # ОБЛОМКИ И МУСОР НА ЗЕМЛЕ
        debris_positions = [
            (120, 380, 25, 15, (60, 50, 40)),    # Кирпичи
            (250, 420, 30, 20, (50, 45, 45)),    # Обломок бетона
            (380, 450, 20, 12, (40, 35, 30)),    # Мелкие камни
            (500, 400, 35, 25, (55, 50, 50)),    # Большой обломок
            (620, 430, 15, 10, (45, 40, 35)),    # Мусор
            (150, 480, 40, 8, (70, 65, 60)),     # Металлическая балка
            (320, 470, 25, 25, (45, 40, 40)),    # Куча щебня
            (580, 460, 20, 15, (50, 45, 45)),    # Обломки
        ]
        
        for debris in debris_positions:
            x, y, w, h, color = debris
            pygame.draw.ellipse(self.screen, color, (x, y, w, h))
            # Добавляем тени
            pygame.draw.ellipse(self.screen, (color[0]-10, color[1]-10, color[2]-10), (x+2, y+2, w, h))
        
        # ЗАБРОШЕННЫЕ АВТОМОБИЛИ
        cars = [
            {"x": 200, "y": 520, "color": (80, 20, 20), "burned": True},   # Сгоревшая красная машина
            {"x": 450, "y": 510, "color": (40, 40, 60), "burned": False},  # Синяя машина
            {"x": 600, "y": 525, "color": (60, 60, 20), "burned": True},   # Желтая сгоревшая
        ]
        
        for car in cars:
            # Основа машины
            pygame.draw.rect(self.screen, car["color"], (car["x"], car["y"], 50, 25))
            
            # Колеса
            wheel_color = (20, 20, 20) if not car["burned"] else (10, 10, 10)
            pygame.draw.circle(self.screen, wheel_color, (car["x"] + 10, car["y"] + 25), 6)
            pygame.draw.circle(self.screen, wheel_color, (car["x"] + 40, car["y"] + 25), 6)
            
            # Окна
            if car["burned"]:
                # Разбитые окна с огнем
                pygame.draw.rect(self.screen, (20, 20, 20), (car["x"] + 5, car["y"] + 5, 40, 10))
                # Огонь внутри
                flame_color = [(120, 60, 20), (150, 80, 30), (100, 50, 10)]
                flame_idx = (pygame.time.get_ticks() // 150) % len(flame_color)
                pygame.draw.rect(self.screen, flame_color[flame_idx], (car["x"] + 10, car["y"] + 6, 30, 8))
            else:
                # Целые, но темные окна
                pygame.draw.rect(self.screen, (30, 30, 40), (car["x"] + 5, car["y"] + 5, 40, 10))
        
        # УЛУЧШЕННЫЕ БАРРИКАДЫ С ДЕТАЛЯМИ
        for barricade in self.barricades:
            # Основная баррикада
            pygame.draw.rect(self.screen, BROWN, (barricade.x, barricade.y, barricade.width, barricade.height))
            pygame.draw.rect(self.screen, (100, 70, 50), (barricade.x + 2, barricade.y + 2, barricade.width - 4, barricade.height - 4), 2)
            
            # Доски и гвозди
            for i in range(3):
                board_y = barricade.y + i * (barricade.height // 3)
                pygame.draw.line(self.screen, (120, 90, 70), 
                               (barricade.x, board_y + 5), (barricade.x + barricade.width, board_y + 5), 3)
                
                # Гвозди
                for j in range(0, barricade.width, 15):
                    nail_x = barricade.x + j + 5
                    pygame.draw.circle(self.screen, (80, 80, 80), (nail_x, board_y + 5), 2)
            
            # Колючая проволока сверху
            wire_y = barricade.y - 3
            for x in range(barricade.x, barricade.x + barricade.width, 5):
                pygame.draw.circle(self.screen, (120, 120, 120), (x, wire_y), 1)
                if x % 10 == 0:  # Колючки
                    pygame.draw.line(self.screen, (100, 100, 100), (x, wire_y - 3), (x, wire_y + 3), 1)
        
        # АТМОСФЕРНЫЕ ЭФФЕКТЫ
        
        # Дым от пожаров (статичные облака)
        smoke_clouds = [
            (160, 80, 25),   # От горящего здания
            (300, 90, 20),   # От другого здания
            (220, 480, 15),  # От сгоревшей машины
            (620, 490, 12),  # От другой машины
        ]
        
        for smoke in smoke_clouds:
            x, y, size = smoke
            # Несколько слоев дыма разной прозрачности
            for i in range(4):
                smoke_size = size + i * 8
                gray_value = 100 - i * 15
                pygame.draw.circle(self.screen, (gray_value, gray_value, gray_value), (x + i*3, y - i*5), smoke_size)
        
        # Летающая пыль и пепел
        dust_particles = []
        current_time = pygame.time.get_ticks()
        for i in range(30):
            # Создаем "псевдослучайные" позиции на основе времени
            x = (i * 47 + current_time // 50) % SCREEN_WIDTH
            y = (i * 31 + current_time // 80) % SCREEN_HEIGHT
            size = 1 + (i % 3)
            
            # Медленно падающий пепел
            fall_speed = 0.5 + (i % 10) * 0.1
            final_y = (y + (current_time * fall_speed // 100)) % SCREEN_HEIGHT
            
            gray = 120 + (i % 40)
            pygame.draw.circle(self.screen, (gray, gray, gray), (int(x), int(final_y)), size)
        
        # ИГРОВЫЕ ОБЪЕКТЫ
        
        # Игрок (выживший) - теперь правильно как survival
        self.player.draw(self.screen, "survival")
        
        # Зомби с улучшенными эффектами
        for zombie in self.zombies:
            zombie.draw(self.screen)
            
            # Кровавые следы позади зомби
            for i in range(3):
                trail_x = zombie.x - (i + 1) * 8
                trail_y = zombie.y + 10 + i * 2
                trail_size = 3 - i
                if trail_size > 0:
                    pygame.draw.circle(self.screen, (60, 10, 10), (int(trail_x), int(trail_y)), trail_size)
        
        # Пули игрока с трассерами
        for bullet in self.player_bullets:
            bullet.draw(self.screen)
            
            # Трассирующий след
            trail_length = 15
            for i in range(trail_length):
                trail_alpha = 255 - (i * 255 // trail_length)
                trail_x = bullet.x - bullet.dx * i * 0.3
                trail_y = bullet.y - bullet.dy * i * 0.3
                
                if 0 <= trail_x <= SCREEN_WIDTH and 0 <= trail_y <= SCREEN_HEIGHT:
                    trail_color = (255, 255 - i*10, 100)
                    pygame.draw.circle(self.screen, trail_color, (int(trail_x), int(trail_y)), max(1, 3 - i//5))
        
        # UI выживания
        # Панель статуса
        pygame.draw.rect(self.screen, BLACK, (10, 10, 350, 100))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 350, 100), 2)
        
        # Здоровье игрока
        health_width = int((self.player.health / self.player.max_health) * 150)
        pygame.draw.rect(self.screen, RED, (15, 15, 150, 15))
        pygame.draw.rect(self.screen, GREEN, (15, 15, health_width, 15))
        pygame.draw.rect(self.screen, WHITE, (15, 15, 150, 15), 2)
        health_text = self.font_small.render(f"HP: {self.player.health}/100", True, WHITE)
        self.screen.blit(health_text, (170, 15))
        
        # Патроны
        ammo_width = int((self.ammo / self.max_ammo) * 150)
        pygame.draw.rect(self.screen, DARK_GRAY, (15, 35, 150, 15))
        pygame.draw.rect(self.screen, YELLOW, (15, 35, ammo_width, 15))
        pygame.draw.rect(self.screen, WHITE, (15, 35, 150, 15), 2)
        ammo_text = self.font_small.render(f"Патроны: {self.ammo}/{self.max_ammo}", True, WHITE)
        self.screen.blit(ammo_text, (170, 35))
        
        # Волна и счет
        wave_text = self.font_small.render(f"Волна: {self.wave}/{self.target_score}", True, WHITE)
        self.screen.blit(wave_text, (15, 55))
        
        zombies_left = len(self.zombies) + (self.zombies_to_spawn - self.zombies_spawned)
        zombies_text = self.font_small.render(f"Зомби: {zombies_left}", True, WHITE)
        self.screen.blit(zombies_text, (15, 75))
        
        score_text = self.font_small.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (170, 75))
        
        # Статус перезарядки
        if self.reload_timer > 0:
            reload_text = self.font_small.render("ПЕРЕЗАРЯДКА...", True, RED)
            self.screen.blit(reload_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))
        
        # Инструкции
        instruction1 = self.font_small.render("WASD - движение, МЫШЬ - прицеливание, ПРОБЕЛ - стрельба, R - перезарядка", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 120))
        instruction2 = self.font_small.render("Красные - базовые зомби, Желтые - быстрые, Фиолетовые - танки", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 100))
        instruction3 = self.font_small.render("Зеленые - бегуны. Используйте баррикады для укрытия!", True, YELLOW)
        self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 80))
        instruction4 = self.font_small.render(f"ЦЕЛЬ: Выжить {self.target_score} волн зомби-апокалипсиса!", True, YELLOW)
        self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 60))
    
    def draw_strategy(self):
        # Мрачное поле боя
        # Темное небо
        pygame.draw.rect(self.screen, (40, 40, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT//2))  # Темно-серое небо
        # Темная земля
        pygame.draw.rect(self.screen, (60, 50, 40), (0, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT//2))  # Коричневая земля
        
        # Линия фронта - более заметная
        pygame.draw.line(self.screen, RED, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT), 4)
        
        # Добавляем мрачную текстуру земли
        for i in range(0, SCREEN_WIDTH, 40):
            for j in range(SCREEN_HEIGHT//2, SCREEN_HEIGHT, 30):
                pygame.draw.circle(self.screen, (40, 30, 20), (i, j), 2)  # Темно-коричневые точки
        
        # Темные облака на небе
        pygame.draw.circle(self.screen, (80, 80, 90), (100, 80), 20)
        pygame.draw.circle(self.screen, (70, 70, 80), (120, 75), 25)
        pygame.draw.circle(self.screen, (80, 80, 90), (140, 80), 20)
        
        pygame.draw.circle(self.screen, (80, 80, 90), (600, 60), 15)
        pygame.draw.circle(self.screen, (70, 70, 80), (615, 55), 20)
        pygame.draw.circle(self.screen, (80, 80, 90), (630, 60), 15)
        
        # Минеральные патчи
        for patch in self.mineral_patches:
            if patch["minerals"] > 0:
                pygame.draw.circle(self.screen, CYAN, (patch["x"], patch["y"]), 15)
                pygame.draw.circle(self.screen, BLUE, (patch["x"], patch["y"]), 10)
                # Показываем количество минералов
                minerals_text = self.font_small.render(str(patch["minerals"]), True, WHITE)
                self.screen.blit(minerals_text, (patch["x"] - 10, patch["y"] - 25))
        
        # Здания
        for building in self.buildings:
            if building["type"] == "command_center":
                pygame.draw.rect(self.screen, GREEN, (building["x"], building["y"], 80, 60))
                pygame.draw.rect(self.screen, DARK_GRAY, (building["x"] + 5, building["y"] + 5, 70, 50), 2)
                # Полоса здоровья здания
                health_width = int((building["health"] / building["max_health"]) * 70)
                pygame.draw.rect(self.screen, RED, (building["x"] + 5, building["y"] - 10, 70, 5))
                pygame.draw.rect(self.screen, GREEN, (building["x"] + 5, building["y"] - 10, health_width, 5))
        
        # Вражеские здания
        for building in self.enemy_buildings:
            if building["type"] == "command_center":
                pygame.draw.rect(self.screen, RED, (building["x"], building["y"], 80, 60))
                pygame.draw.rect(self.screen, DARK_GRAY, (building["x"] + 5, building["y"] + 5, 70, 50), 2)
                # Полоса здоровья здания
                health_width = int((building["health"] / building["max_health"]) * 70)
                pygame.draw.rect(self.screen, RED, (building["x"] + 5, building["y"] - 10, 70, 5))
                pygame.draw.rect(self.screen, GREEN, (building["x"] + 5, building["y"] - 10, health_width, 5))
        
        # Игрок (командир)
        self.player.draw(self.screen, self.level_type)
        
        # Союзные юниты
        for unit in self.units:
            if unit["type"] == "worker":
                color = YELLOW if unit["carrying"] > 0 else BLUE
                pygame.draw.circle(self.screen, color, (unit["x"], unit["y"]), 8)
                pygame.draw.circle(self.screen, WHITE, (unit["x"], unit["y"]), 6, 2)
            elif unit["type"] == "marine":
                pygame.draw.rect(self.screen, GREEN, (unit["x"], unit["y"], 15, 12))
                pygame.draw.rect(self.screen, DARK_GRAY, (unit["x"] + 3, unit["y"] - 3, 9, 3))  # Винтовка
            elif unit["type"] == "tank":
                pygame.draw.rect(self.screen, DARK_GRAY, (unit["x"], unit["y"], 20, 15))
                pygame.draw.rect(self.screen, BLACK, (unit["x"] + 5, unit["y"] - 5, 15, 5))  # Пушка
                pygame.draw.circle(self.screen, GREEN, (unit["x"] + 10, unit["y"] + 7), 3)  # Центр
            
            # Показываем выделение
            if unit in self.selected_units:
                pygame.draw.circle(self.screen, WHITE, (unit["x"], unit["y"]), 12, 2)
            
            # Показываем цель движения
            if unit.get("move_target"):
                target = unit["move_target"]
                pygame.draw.line(self.screen, YELLOW, (unit["x"], unit["y"]), (target["x"], target["y"]), 2)
                pygame.draw.circle(self.screen, YELLOW, (target["x"], target["y"]), 5, 2)
        
        # Вражеские юниты
        for enemy in self.enemy_units:
            if enemy["type"] == "marine":
                pygame.draw.rect(self.screen, RED, (enemy["x"], enemy["y"], 15, 12))
                pygame.draw.rect(self.screen, DARK_GRAY, (enemy["x"] + 3, enemy["y"] - 3, 9, 3))  # Винтовка
        
        # UI стратегии в стиле StarCraft
        # Панель ресурсов
        pygame.draw.rect(self.screen, BLACK, (10, 10, 300, 80))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 300, 80), 2)
        
        minerals_text = self.font_small.render(f"Минералы: {self.minerals}", True, CYAN)
        self.screen.blit(minerals_text, (15, 15))
        
        supply_text = self.font_small.render(f"Население: {self.supply_used}/{self.supply_max}", True, WHITE)
        self.screen.blit(supply_text, (15, 35))
        
        selected_text = self.font_small.render(f"Выбран: {self.selected_unit_type.upper()}", True, YELLOW)
        self.screen.blit(selected_text, (15, 55))
        
        # Стоимость юнитов
        costs = {"worker": 50, "marine": 100, "tank": 150}
        cost_text = self.font_small.render(f"Стоимость: {costs[self.selected_unit_type]}", True, WHITE)
        self.screen.blit(cost_text, (15, 75))
        
        # Инструкции - размещаем внизу экрана
        instruction1 = self.font_small.render("1-Рабочий(50), 2-Морпех(100), 3-Танк(150)", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 120))
        instruction2 = self.font_small.render("ПРОБЕЛ - создать юнита", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 100))
        instruction3 = self.font_small.render("ЛКМ - выделить, ПКМ - приказ движения", True, YELLOW)
        self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 80))
        instruction4 = self.font_small.render("ЦЕЛЬ: Уничтожить красную базу!", True, YELLOW)
        self.screen.blit(instruction4, (10, SCREEN_HEIGHT - 60))
    
    def draw_final_mix(self):
        # Финальный уровень - комбинация всех жанров
        # Космический фон как в шутере
        for i in range(50):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 23) % SCREEN_HEIGHT
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        # Игрок всегда видимый
        self.player.draw(self.screen, "shooter")
        
        # Если есть ракеты - рисуем их
        if hasattr(self, 'missiles'):
            for missile in self.missiles:
                missile.draw(self.screen)
        
        # Если есть пули - рисуем их
        if hasattr(self, 'player_bullets'):
            for bullet in self.player_bullets:
                bullet.draw(self.screen)
        
        # Рисуем босса
        if hasattr(self, 'boss') and self.boss:
            self.boss.draw(self.screen)
        
        # Полоса здоровья игрока
        player_health_width = int((self.player.health / self.player.max_health) * 200)
        pygame.draw.rect(self.screen, RED, (10, 50, 200, 15))
        pygame.draw.rect(self.screen, GREEN, (10, 50, player_health_width, 15))
        pygame.draw.rect(self.screen, WHITE, (10, 50, 200, 15), 2)
        player_text = self.font_small.render("ИГРОК", True, WHITE)
        self.screen.blit(player_text, (10, 30))
        
        # Инструкции для финального уровня
        instruction1 = self.font_small.render("ФИНАЛЬНЫЙ БОСС - УНИЧТОЖЬТЕ КРАСНЫЙ КОРАБЛЬ!", True, YELLOW)
        self.screen.blit(instruction1, (10, SCREEN_HEIGHT - 120))
        instruction2 = self.font_small.render("WASD - движение, ПРОБЕЛ - стрельба", True, YELLOW)
        self.screen.blit(instruction2, (10, SCREEN_HEIGHT - 100))
        instruction3 = self.font_small.render("Избегайте пуль босса! У него 3 фазы!", True, YELLOW)
        self.screen.blit(instruction3, (10, SCREEN_HEIGHT - 80))
    
    def draw_help(self):
        """Отображает подробную помощь для текущего уровня"""
        
        # Определяем инструкции для каждого уровня
        level_instructions = {
            "shooter": {
                "title": "КОСМИЧЕСКИЙ ШУТЕР",
                "goal": "Наберите 20 очков, уничтожая красные ракеты",
                "controls": [
                    "A/D или стрелки - движение влево/вправо",
                    "ПРОБЕЛ - стрельба (жёлтые пули)",
                    "ЛКМ - стрельба (альтернатива)"
                ],
                "tips": [
                    "Красные ракеты летят прямо на вас",
                    "Уклоняйтесь от ракет и стреляйте в них",
                    "За каждую ракету +1 очко",
                    "Серебристый истребитель с анимированными двигателями"
                ]
            },
            "platformer": {
                "title": "ПЛАТФОРМЕР",
                "goal": "Добирайтесь до ЗОЛОТОЙ цели на вершине",
                "controls": [
                    "A/D - движение влево/вправо",
                    "W/ПРОБЕЛ - прыжок (время нажатия = высота)",
                    "Короткий тап = низкий прыжок",
                    "Долгое нажатие = высокий прыжок"
                ],
                "tips": [
                    "Изучайте высоту прыжка для разных расстояний",
                    "Избегайте треугольных шипов и вращающихся пил",
                    "Синие платформы безопасны для приземления"
                ]
            },
            "racing": {
                "title": "ГОНКИ",
                "goal": "Проедьте 1000 метров, избегая препятствий",
                "controls": [
                    "A/D или стрелки - поворот влево/вправо",
                    "W/S - газ/тормоз (опционально)"
                ],
                "tips": [
                    "Серые препятствия падают сверху",
                    "Оставайтесь в пределах жёлтых полос дороги",
                    "Чем дальше проедете, тем больше очков"
                ]
            },
            "puzzle": {
                "title": "ЛАБИРИНТ",
                "goal": "Соберите 3 зелёных ключа и дойдите до красной цели",
                "controls": [
                    "WASD или стрелки - пошаговое движение",
                    "Один клик = один шаг в любом направлении"
                ],
                "tips": [
                    "Серые блоки - стены, нельзя пройти",
                    "У вас ограниченное количество ходов",
                    "Планируйте маршрут заранее"
                ]
            },
            "rhythm": {
                "title": "РИТМ-ИГРА",
                "goal": "Наберите 500 очков, попадая в такт",
                "controls": [
                    "A/ВЛЕВО - левая нота",
                    "D/ВПРАВО - правая нота", 
                    "W/ВВЕРХ - верхняя нота",
                    "S/ВНИЗ - нижняя нота"
                ],
                "tips": [
                    "Нажимайте клавиши когда ноты в белой зоне",
                    "Точное попадание даёт больше очков",
                    "Комбо увеличивает множитель очков"
                ]
            },
            "tower_defense": {
                "title": "ЗАЩИТА БАШНЯМИ",
                "goal": "Отбейте все волны врагов и победите БОССА",
                "controls": [
                    "1-4 - выбор типа башни",
                    "ЛКМ - построить башню в жёлтом месте",
                    "ПКМ - улучшить башню"
                ],
                "tips": [
                    "Базовая(50$), Скорострел(75$), Тяжёлая(100$), Заморозка(80$)",
                    "Враги идут по коричневой тропе",
                    "Улучшайте башни для большего урона"
                ]
            },
            "stealth": {
                "title": "СТЕЛС-МИССИЯ",
                "goal": "Проникните на все 5 этажей и взломайте ЗОЛОТОЙ СЕЙФ",
                "controls": [
                    "WASD - скрытное перемещение",
                    "Прячьтесь за коричневые препятствия"
                ],
                "tips": [
                    "Разные типы охранников: Патруль(синий), Офисный(темно-синий), Элитный(красный), Снайпер(чёрный)",
                    "Когда вас видят - растёт красная полоса обнаружения",
                    "При 100% обнаружения - перезапуск уровня"
                ]
            },
            "survival": {
                "title": "ВЫЖИВАНИЕ",
                "goal": "Переживите 10 волн зомби-апокалипсиса",
                "controls": [
                    "WASD - движение",
                    "Мышь - прицеливание",
                    "ЛКМ/ПРОБЕЛ - стрельба",
                    "R - перезарядка"
                ],
                "tips": [
                    "Зомби: Обычные(зелёные), Быстрые(жёлтые), Танки(красные), Бегуны(розовые)",
                    "Прячьтесь за серые баррикады",
                    "Следите за патронами и здоровьем"
                ]
            },
            "strategy": {
                "title": "СТРАТЕГИЯ (RTS)",
                "goal": "Соберите 1000 минералов, создавая армию",
                "controls": [
                    "1-3 - выбор типа юнита (Рабочий/Морпех/Танк)",
                    "ПРОБЕЛ - создать выбранного юнита",
                    "ЛКМ - выделить юнита",
                    "ПКМ - приказ движения/атаки"
                ],
                "tips": [
                    "Рабочие собирают синие минералы",
                    "Морпехи и танки сражаются с красными врагами",
                    "У каждого юнита есть стоимость и требования снабжения"
                ]
            },
            "final_mix": {
                "title": "ФИНАЛЬНЫЙ МИКС",
                "goal": "Победите финального СУПЕР-БОССА со 1000 HP",
                "controls": [
                    "A/D - движение",
                    "ПРОБЕЛ - стрельба",
                    "Все навыки предыдущих уровней"
                ],
                "tips": [
                    "Босс имеет 3 фазы с разными атаками",
                    "Используйте весь опыт предыдущих уровней",
                    "Это самый сложный вызов!",
                    "Ваш серебристый истребитель против супер-босса"
                ]
            }
        }
        
        # Получаем инструкции для текущего уровня
        instructions = level_instructions.get(self.level_type, {
            "title": "НЕИЗВЕСТНЫЙ УРОВЕНЬ",
            "goal": "Следуйте инструкциям на экране",
            "controls": ["WASD - движение"],
            "tips": ["Удачи!"]
        })
        
        # Рисуем кнопку помощи
        button_color = (100, 200, 100) if self.help_expanded else (200, 100, 100)
        button_text = "СВЕРНУТЬ" if self.help_expanded else "ПОМОЩЬ"
        
        pygame.draw.rect(self.screen, button_color, self.help_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.help_button_rect, 2)
        
        button_surface = self.font_small.render(button_text, True, WHITE)
        button_text_rect = button_surface.get_rect(center=self.help_button_rect.center)
        self.screen.blit(button_surface, button_text_rect)
        
        # Показываем полную помощь только если развёрнуто
        if self.help_expanded:
            # Тёмный фон для помощи - панель снизу
            help_height = min(350, SCREEN_HEIGHT - 80)
            help_bg_rect = pygame.Rect(140, SCREEN_HEIGHT - help_height - 50, SCREEN_WIDTH - 150, help_height)
            pygame.draw.rect(self.screen, (0, 0, 0, 200), help_bg_rect)
            pygame.draw.rect(self.screen, (100, 150, 200), help_bg_rect, 3)
            
            y_offset = SCREEN_HEIGHT - help_height - 30
            
            # Заголовок
            title_surface = self.font.render(instructions["title"], True, (255, 255, 100))
            self.screen.blit(title_surface, (150, y_offset))
            y_offset += 35
            
            # Цель
            goal_surface = self.font_small.render(f"ЦЕЛЬ: {instructions['goal']}", True, (100, 255, 100))
            self.screen.blit(goal_surface, (150, y_offset))
            y_offset += 25
            
            # Управление
            controls_title = self.font_small.render("УПРАВЛЕНИЕ:", True, (255, 200, 100))
            self.screen.blit(controls_title, (150, y_offset))
            y_offset += 20
            
            for control in instructions["controls"]:
                if y_offset < SCREEN_HEIGHT - 80:  # Проверяем, что не выходим за границы
                    control_surface = self.font_small.render(f"• {control}", True, WHITE)
                    self.screen.blit(control_surface, (160, y_offset))
                    y_offset += 18
            
            y_offset += 10
            
            # Советы
            if y_offset < SCREEN_HEIGHT - 60:
                tips_title = self.font_small.render("СОВЕТЫ:", True, (255, 200, 100))
                self.screen.blit(tips_title, (150, y_offset))
                y_offset += 20
                
                for tip in instructions["tips"]:
                    if y_offset >= SCREEN_HEIGHT - 80:  # Не выходим за границы
                        break
                        
                    # Разбиваем длинные строки
                    if len(tip) > 65:  # Уменьшаем ширину для нижней панели
                        words = tip.split(' ')
                        line = ""
                        for word in words:
                            if len(line + word) > 65:
                                if y_offset < SCREEN_HEIGHT - 80:
                                    tip_surface = self.font_small.render(f"• {line}", True, (200, 200, 255))
                                    self.screen.blit(tip_surface, (160, y_offset))
                                    y_offset += 18
                                line = word + " "
                            else:
                                line += word + " "
                        if line and y_offset < SCREEN_HEIGHT - 80:
                            tip_surface = self.font_small.render(f"• {line}", True, (200, 200, 255))
                            self.screen.blit(tip_surface, (160, y_offset))
                            y_offset += 18
                    else:
                        tip_surface = self.font_small.render(f"• {tip}", True, (200, 200, 255))
                        self.screen.blit(tip_surface, (160, y_offset))
                        y_offset += 18

    def draw_ui(self):
        # Счет
        if self.level_type == "puzzle":
            score_text = self.font.render(f"Ходы: {self.player.moves}/{self.player.target_moves}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            keys_text = self.font.render(f"Ключи: {self.keys_collected}/{self.total_keys}", True, WHITE)
            self.screen.blit(keys_text, (10, 50))
        elif self.level_type == "racing":
            # UI для гонок уже отрисован в draw_racing()
            pass
        elif self.level_type == "rhythm":
            score_text = self.font.render(f"Счет: {self.score}/500", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            combo_text = self.font.render(f"Комбо: {self.combo} x{self.score_multiplier}", True, WHITE)
            self.screen.blit(combo_text, (10, 50))
        else:
            score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
        
        # Тип уровня
        level_text = self.font.render(f"Уровень {self.level}: {self.level_type.upper()}", True, WHITE)
        self.screen.blit(level_text, (10, SCREEN_HEIGHT - 40))
        
        # Обозначение игрока на каждом уровне
        player_indicators = {
            "shooter": "ВЫ - СЕРЕБРИСТЫЙ КОСМИЧЕСКИЙ ИСТРЕБИТЕЛЬ",
            "platformer": "ВЫ - СИНИЙ ПРЯМОУГОЛЬНИК (WASD+wall jump к вершине!)", 
            "racing": "ВЫ - КРАСНАЯ МАШИНА ВНИЗУ",
            "puzzle": "ВЫ - ФИОЛЕТОВЫЙ КУБИК",
            "rhythm": "НАЖИМАЙТЕ КЛАВИШИ ПО ЦВЕТНЫМ НОТАМ",
            "tower_defense": "СТРОЙТЕ БАШНИ ДЛЯ ЗАЩИТЫ ОТ ВРАГОВ",
            "stealth": "ВЫ - СИНИЙ ШПИОН С ГЛАЗАМИ",
            "survival": "ВЫ - ЗЕЛЕНЫЙ ВЫЖИВШИЙ (оружие поворачивается к мыши)",
            "strategy": "ВЫ - ЗЕЛЕНЫЙ КОМАНДИР С ПОГОНАМИ",
            "final_mix": "ВЫ - СЕРЕБРИСТЫЙ КОСМИЧЕСКИЙ ИСТРЕБИТЕЛЬ"
        }
        
        if self.level_type in player_indicators:
            indicator_text = self.font_small.render(player_indicators[self.level_type], True, CYAN)
            self.screen.blit(indicator_text, (SCREEN_WIDTH - indicator_text.get_width() - 10, 10))
        
        # Сообщения о завершении
        if self.game_over:
            game_over_text = self.font.render("ПОРАЖЕНИЕ! R - перезапуск, ESC - меню", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
        
        if self.level_complete:
            victory_text = self.font.render("УРОВЕНЬ ПРОЙДЕН! ENTER - продолжить, ESC - меню", True, GREEN)
            text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(victory_text, text_rect)
    
    def restart(self):
        self.__init__(self.level)
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'menu'
                    elif event.key == pygame.K_r and self.game_over:
                        self.restart()
                    elif event.key == pygame.K_RETURN and self.level_complete:
                        return 'next_level'
                    
                    # Пошаговое движение для головоломки
                    elif self.level_type == "puzzle" and not self.game_over and not self.level_complete:
                        moved = False
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            if self.player.x > 40:
                                self.player.x -= 40
                                moved = True
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            if self.player.x < SCREEN_WIDTH - 80:
                                self.player.x += 40
                                moved = True
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            if self.player.y > 40:
                                self.player.y -= 40
                                moved = True
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            if self.player.y < SCREEN_HEIGHT - 80:
                                self.player.y += 40
                                moved = True
                        
                        if moved:
                            self.player.moves += 1
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Проверяем клик по кнопке помощи
                    if event.button == 1 and self.help_button_rect.collidepoint(mouse_x, mouse_y):
                        self.help_expanded = not self.help_expanded
                    
                    elif self.level_type == "tower_defense":
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        if event.button == 1:  # Левая кнопка мыши - строительство башни
                            tower = Tower(0, 0, self.selected_tower_type)
                            if self.money >= tower.cost:
                                # Ищем ближайшее валидное место
                                closest_spot = None
                                min_distance = float('inf')
                                
                                for spot in self.valid_build_spots:
                                    if not spot["occupied"]:
                                        distance = math.sqrt((mouse_x - spot["x"])**2 + (mouse_y - spot["y"])**2)
                                        if distance < min_distance and distance < 50:  # В радиусе 50 пикселей
                                            min_distance = distance
                                            closest_spot = spot
                                
                                if closest_spot:
                                    new_tower = Tower(closest_spot["x"], closest_spot["y"], self.selected_tower_type)
                                    self.towers.append(new_tower)
                                    self.money -= new_tower.cost
                                    closest_spot["occupied"] = True
                        
                        elif event.button == 3:  # Правая кнопка мыши - улучшение башни
                            for tower in self.towers:
                                tower_rect = tower.get_rect()
                                if tower_rect.collidepoint(mouse_x, mouse_y):
                                    if tower.can_upgrade():
                                        upgrade_cost = 25 + tower.level * 15
                                        if self.money >= upgrade_cost:
                                            tower.upgrade()
                                            self.money -= upgrade_cost
                                    break
                    
                    elif self.level_type == "strategy":
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        if event.button == 1:  # Левая кнопка мыши
                            # Выделяем юнитов
                            self.selected_units = []
                            for unit in self.units:
                                unit_rect = pygame.Rect(unit["x"] - 10, unit["y"] - 10, 20, 20)
                                if unit_rect.collidepoint(mouse_x, mouse_y):
                                    self.selected_units.append(unit)
                                    break
                        
                        elif event.button == 3:  # Правая кнопка мыши
                            # Командуем выделенным юнитам
                            for unit in self.selected_units:
                                if unit["type"] in ["marine", "tank"]:
                                    unit["move_target"] = {"x": mouse_x, "y": mouse_y}
            
            self.update()
            self.draw()
            self.clock.tick(FPS)

class GameManager:
    def __init__(self):
        self.progress = GameProgress()
        self.menu = Menu(self.progress)
        self.current_state = 'menu'
        self.current_level = 1
        self.clock = pygame.time.Clock()
        # Создаем экран только ОДИН раз с правильными флагами!
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption("Мульти-жанровая игра")
        
    def run(self):
        running = True
        while running:
            if self.current_state == 'menu':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        else:
                            selected_level = self.menu.handle_input(event)
                            if selected_level:
                                self.current_level = selected_level
                                self.current_state = 'game'
                
                # Используем уже созданный экран
                self.menu.draw(self.screen)
                pygame.display.update()  # Более стабильная альтернатива flip()
                self.clock.tick(FPS)
                
            elif self.current_state == 'game':
                game = Game(self.current_level)
                result = game.run()
                
                if result == 'quit':
                    running = False
                elif result == 'menu':
                    self.current_state = 'menu'
                elif result == 'next_level':
                    # Разблокируем следующий уровень
                    next_level = self.current_level + 1
                    if next_level <= 10:
                        self.progress.unlock_level(next_level)
                        self.current_level = next_level
                        # Продолжаем играть на следующем уровне
                    else:
                        # Игра пройдена полностью
                        self.current_state = 'menu'
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()
