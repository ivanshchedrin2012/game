# 🎮 Мульти-жанровая игра - 10 игр в одной!

## 📖 Описание
Уникальная игра, которая объединяет **10 различных игровых жанров** в одном приложении! Каждый уровень представляет собой полноценную мини-игру со своими механиками, управлением и целями. От классических аркад до современных стратегий - испытайте себя во всех популярных жанрах!

## 📋 Содержание
- [Установка и запуск](#-установка-и-запуск)
- [Игровые жанры и уровни](#-игровые-жанры-и-уровни)
- [Система прогрессии](#-система-прогрессии)
- [Управление](#-управление)
- [Игровые механики](#-игровые-механики)
- [Советы для прохождения](#-советы-для-прохождения)
- [Технические требования](#-технические-требования)
- [Разработка](#-разработка)
- [Частые вопросы (FAQ)](#-частые-вопросы-faq)

## 🚀 Установка и запуск

### Системные требования
- **Операционная система:** Windows 10/11, macOS 10.15+, Linux
- **Процессор:** 2.0 GHz или выше
- **Оперативная память:** 2 GB RAM
- **Место на диске:** 100 MB
- **Python:** 3.6 или выше
- **Pygame:** 2.0 или выше

### Быстрая установка
```bash
# 1. Клонируем репозиторий
git clone https://github.com/your-username/multi-genre-game.git
cd multi-genre-game

# 2. Создаем виртуальное окружение
python -m venv venv

# 3. Активируем виртуальное окружение
# Для Windows:
venv\Scripts\activate
# Для macOS/Linux:
source venv/bin/activate

# 4. Устанавливаем зависимости
pip install -r requirements.txt

# 5. Запускаем игру
python space_game.py
```

### ⚠️ ВАЖНО: Настройка клавиатуры
- **Переключите клавиатуру на АНГЛИЙСКИЙ язык** перед запуском игры!
- Иначе управление WASD работать не будет
- Проверьте работу клавиш в меню настроек перед началом игры

## 🎯 Игровые жанры и уровни

### 🚀 Уровень 1: ШУТЕР (Космический бой)
**Вы:** Зеленый космический корабль  
**Цель:** Набрать 20 очков, уворачиваясь от самонаводящихся ракет  
**Управление:** 
- `W` - движение вверх
- `S` - движение вниз
- `A` - движение влево
- `D` - движение вправо
- `Пробел` - стрельба
**Особенности:** 
- Классический shoot'em up с самонаводящимися ракетами
- Система щитов и бонусов
- Уникальные паттерны атак врагов

### 🏃 Уровень 2: ПЛАТФОРМЕР (Прыжки и препятствия)
**Вы:** Синий прямоугольник с глазами  
**Цель:** Добраться до зеленой платформы  
**Управление:** A/D - движение, W/Пробел - прыжок  
**Особенности:** 
- Wall jump (прыжки от стен)
- Шипы и вращающиеся пилы
- Гравитация и физика платформера

### 🏎️ Уровень 3: ГОНКИ (Уворачивание от препятствий)
**Вы:** Красная машина  
**Цель:** Проехать 1000 метров, избегая препятствий  
**Управление:** A/D - поворот влево/вправо  
**Особенности:** 
- Автоматическое движение вперед
- Случайные препятствия
- Система дистанции

### 🧩 Уровень 4: ГОЛОВОЛОМКА (Пошаговая логика)
**Вы:** Фиолетовый кубик  
**Цель:** Собрать все 3 ключа за минимум ходов  
**Управление:** WASD - пошаговое движение (1 клетка за ход)  
**Особенности:** 
- Лабиринт со стенами
- Ограничение на количество ходов (50)
- Логические головоломки

### 🎵 Уровень 5: РИТМ-ИГРА (Музыкальные ноты)
**Цель:** Набрать 500 очков, попадая в ноты  
**Управление:** WASD - нажимайте клавиши когда цветные ноты в белой зоне  
**Особенности:** 
- 4 дорожки с цветными нотами
- Система комбо и множителей
- Точное попадание в такт

### 🏰 Уровень 6: TOWER DEFENSE (Защита базы)
**Вы:** Зеленая башня с пушкой  
**Цель:** Уничтожить 5 волн красных врагов  
**Управление:** WASD - движение башни, Пробел - стрельба  
**Особенности:** 
- Враги движутся по тропе
- Ограниченные жизни (10)
- Стратегическое позиционирование

### 🕵️ Уровень 7: СТЕЛС (Скрытность)
**Вы:** Синий шпион с глазами  
**Цель:** Добраться до зеленой цели, избегая красных охранников  
**Управление:** WASD - скрытное движение  
**Особенности:** 
- Патрулирующие охранники
- Полоса обнаружения
- Препятствия для укрытия

### 👊 Уровень 8: ФАЙТИНГ (Бой один на один)
**Вы:** Красный боец с желтыми перчатками  
**Цель:** Победить в 3 раундах против синего противника  
**Управление:** WASD - движение, Пробел - атака  
**Особенности:** 
- ИИ противник с разными тактиками
- Полосы здоровья
- Система раундов

### ⚔️ Уровень 9: СТРАТЕГИЯ (RTS в стиле StarCraft)
**Вы:** Зеленый командир с погонами  
**Цель:** Уничтожить красную вражескую базу  
**Управление:** 
- 1/2/3 - выбор типа юнита (Рабочий/Морпех/Танк)
- Пробел - создать выбранного юнита
- ЛКМ - выделить юнита
- ПКМ - приказ движения
**Особенности:** 
- Сбор ресурсов (минералы)
- Создание армии (рабочие, морпехи, танки)
- Экономика и стратегия в реальном времени

### 💀 Уровень 10: ФИНАЛЬНЫЙ МИКС (Босс-файт)
**Вы:** Зеленый космический корабль  
**Цель:** Победить финального босса с тремя фазами  
**Управление:** WASD - движение, Пробел - стрельба  
**Особенности:** 
- Огромный красный босс (500 HP)
- 3 фазы с разными атаками
- Комбинация всех изученных навыков

## 🎮 Система прогрессии

### 🔒 Разблокировка уровней
- Первый уровень открыт сразу
- Каждый следующий уровень открывается после прохождения предыдущего
- Прогресс сохраняется автоматически в `game_progress.json`

### 🏆 Цели прохождения
Каждый уровень имеет уникальную цель:
- **Шутер:** Набрать очки, выживая
- **Платформер:** Добраться до цели
- **Гонки:** Проехать дистанцию
- **Головоломка:** Решить за минимум ходов
- **Ритм:** Набрать очки комбо
- **Tower Defense:** Выжить волны атак
- **Стелс:** Остаться незамеченным
- **Файтинг:** Выиграть раунды
- **Стратегия:** Победить в войне
- **Финал:** Победить босса

## 🎯 Управление

### Универсальные клавиши
- **WASD** или **Стрелки** - основное движение
- **Пробел** - основное действие (стрельба/прыжок/атака)
- **Enter** - подтвердить/продолжить
- **R** - перезапуск уровня (при поражении)
- **ESC** - возврат в меню

### Специальные для жанров
- **Ритм-игра:** WASD для разных дорожек
- **Стратегия:** 1/2/3 - выбор юнитов, ЛКМ/ПКМ - команды
- **Головоломка:** Пошаговое движение (1 ход за нажатие)

## 🛡️ Игровые механики

### Система здоровья
- Большинство персонажей имеют 100 HP
- Щиты для временной защиты
- Восстановление между раундами

### Различные враги
- **Самонаводящиеся ракеты** (Шутер)
- **Шипы и пилы** (Платформер)
- **Препятствия** (Гонки)
- **Охранники** (Стелс)
- **ИИ бойцы** (Файтинг)
- **Вражеская армия** (Стратегия)

### Уникальные особенности
- **Wall jump** в платформере
- **Система комбо** в ритм-игре
- **Экономика ресурсов** в стратегии
- **Многофазный босс** в финале

## 💡 Советы для прохождения

### Общие
1. **Практикуйтесь** - можете переигрывать пройденные уровни
2. **Изучайте паттерны** - у каждого жанра свои особенности
3. **Переключите клавиатуру** на английский язык!

### По жанрам
- **Шутер:** Постоянно двигайтесь, используйте углы экрана
- **Платформер:** Освойте wall jump для сложных участков
- **Гонки:** Предсказывайте движение препятствий
- **Головоломка:** Планируйте маршрут заранее
- **Ритм:** Слушайте ритм и смотрите на цвета
- **Tower Defense:** Позиционируйтесь стратегически
- **Стелс:** Изучите паттерны охранников
- **Файтинг:** Изучите дистанцию атаки
- **Стратегия:** Баланс между экономикой и армией
- **Финал:** Комбинируйте все изученные навыки

## 💻 Технические требования

### Минимальные требования
```python
# requirements.txt
pygame==2.0.0
numpy==1.19.5
pillow==8.0.0
```

### Рекомендуемые настройки
- **Разрешение экрана:** 1920x1080 (поддерживается масштабирование)
- **Частота обновления:** 60+ Hz
- **Звуковая карта:** Совместимая с DirectSound или OpenAL

## 🛠 Разработка

### Структура проекта
```
game/
├── assets/
│   ├── images/
│   ├── sounds/
│   └── fonts/
├── src/
│   ├── levels/
│   ├── entities/
│   └── utils/
├── tests/
├── game_progress.json
├── requirements.txt
├── README.md
└── space_game.py
```

### Запуск тестов
```bash
# Установка зависимостей для тестирования
pip install pytest pytest-cov

# Запуск тестов
pytest tests/
```

### Сборка и дистрибуция
```bash
# Создание исполняемого файла
pyinstaller --onefile space_game.py
```

## ❓ Частые вопросы (FAQ)

### Общие вопросы
1. **В: Игра не запускается, что делать?**
   О: Проверьте версию Python и установку всех зависимостей

2. **В: Как сохранить прогресс?**
   О: Прогресс сохраняется автоматически в `game_progress.json`

3. **В: Можно ли изменить управление?**
   О: Да, в меню настроек (клавиша `ESC`)

### Технические проблемы
1. **В: Низкая производительность**
   О: Попробуйте:
   - Закрыть фоновые приложения
   - Обновить драйверы видеокарты
   - Уменьшить разрешение в настройках

2. **В: Не работает звук**
   О: Проверьте:
   - Настройки звука в системе
   - Установку звуковых драйверов
   - Настройки звука в игре

## 📝 Лицензия
Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

### Вы можете:
- **Делиться** — копировать и распространять материал на любом носителе и в любом формате
- **Адаптировать** — делать ремиксы, видоизменять и создавать новое, опираясь на этот материал

### При соблюдении следующих условий:
- **Некоммерческое использование** — Вы не можете использовать материал в коммерческих целях
- **Attribution** — Вы должны указать авторство, предоставить ссылку на лицензию и обозначить изменения, если таковые были сделаны

### Запрещено:
- Коммерческое использование
- Распространение без указания авторства
- Закрытие исходного кода
- Изменение условий лицензии

Полный текст лицензии доступен по ссылке: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)


**Сделано с ❤️ в России**
