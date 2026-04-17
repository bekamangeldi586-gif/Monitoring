# 🏙️ Smart City Monitoring System
## Архитектура распределенной системы мониторинга городских ресурсов

Полнофункциональная демонстрация четырех ключевых паттернов проектирования на Python.

---

## 📋 Содержание

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Паттерны проектирования](#паттерны-проектирования)
3. [Структура проекта](#структура-проекта)
4. [Установка и запуск](#установка-и-запуск)
5. [Примеры использования](#примеры-использования)
6. [Расширение системы](#расширение-системы)

---

## 🏛️ Обзор архитектуры

Система моделирует контроль экологии и трафика в городе Семей с сотнями датчиков. 
Основные требования:

- ✅ Быстро добавлять новые типы датчиков
- ✅ Мгновенно уведомлять службы об аномалиях  
- ✅ Менять алгоритм анализа данных во время работы
- ✅ Гарантировать единственность критических компонентов

---

## 🎨 Паттерны проектирования

### 1️⃣ **Singleton (Одиночка)**

**Файл:** `settings.py`

**Назначение:** Гарантировать единственный экземпляр настроек системы в памяти.

```python
from settings import get_settings

# Оба вызова возвращают ОДИН и ТОТ ЖЕ объект
settings1 = get_settings()
settings2 = get_settings()
assert settings1 is settings2  # True!
```

**Реализация:** Используется метакласс `SingletonMeta` для контроля создания экземпляров.

**Ключевые параметры:**
- `threshold_temperature` = 45°C
- `threshold_co2` = 400 ppm
- `threshold_traffic` = 85%
- `database_url` = строка подключения БД
- `moving_average_window` = 3 значения

---

### 2️⃣ **Factory Method (Фабричный метод)**

**Файл:** `sensors.py`

**Назначение:** Создавать датчики разных типов по коду без знания их деталей реализации.

```python
from sensors import SensorFactory

# Создание датчиков по коду
temp_sensor = SensorFactory.create_sensor("TEMP_01")
air_sensor = SensorFactory.create_sensor("AIR_02")
traffic_sensor = SensorFactory.create_sensor("TRAFFIC_03")
```

**Доступные типы датчиков:**
- `TEMP` - Датчик температуры (-30°C до +50°C)
- `AIR` - Датчик качества воздуха / CO2 (300-2000 ppm)
- `TRAFFIC` - Датчик трафика (0-100%)
- `HUMIDITY` - Датчик влажности (по умолчанию добавлен как пример)

**Преимущества:**
- Новые типы датчиков добавляются через `register_sensor_type()`
- Нет необходимости изменять клиентский код
- Логика создания инкапсулирована в Factory

---

### 3️⃣ **Observer (Наблюдатель)**

**Файл:** `alerts.py`

**Назначение:** Разделение издателей (датчики) и подписчиков (службы).

```python
from alerts import get_control_center, EmergencyService, PoliceService

center = get_control_center()

# Регистрация служб как подписчиков
center.subscribe(EmergencyService())
center.subscribe(PoliceService())

# Отправка уведомлений
center.notify_subscribers("TEMP_01", "temperature", 47, 45)
```

**Реализованные службы:**
- 🚨 **МЧС (EmergencyService)** - реагирует на все аномалии
- 🚔 **Полиция (PoliceService)** - интересует только трафик
- ♻️ **Экологи (EnvironmentalService)** - следят за воздухом
- 📋 **Архив (CityCouncil)** - логирует все события

**Схема работы:**
```
Датчик с критическим значением
        ↓
Центр управления (Control Center)
        ↓
    ┌───┴────┬────────┬──────────┐
    ↓        ↓        ↓          ↓
   МЧС     Полиция   Экологи   Архив
```

---

### 4️⃣ **Strategy (Стратегия)**

**Файл:** `strategies.py`

**Назначение:** Менять алгоритм анализа данных во время работы.

```python
from strategies import StrategyFactory

# Изменение стратегии на лету
system.change_strategy("TEMP_01", "MOVING_AVG")
system.change_strategy("AIR_02", "TREND")
```

**Доступные стратегии:**

| Стратегия | Описание | Использование |
|-----------|---------|---------------|
| **SIMPLE** | Если значение > X, то тревога | Срочные анализы |
| **MOVING_AVG** | Тревога если среднее 3 значений > X | Скользящая обработка |
| **TREND** | Тревога если растет И > X | Детектирование опасных тенденций |
| **ADAPTIVE** | Разные пороги день/ночь | Гибкая обработка |

---

## 📁 Структура проекта

```
/Monitoring
├── main.py                    # Главная демонстрация всех паттернов
├── settings.py               # Singleton: настройки системы
├── sensors.py                # Factory: создание датчиков
├── alerts.py                 # Observer: система уведомлений
├── strategies.py             # Strategy: алгоритмы анализа
├── advanced_examples.py      # Расширенные возможности
└── README.md                 # Этот файл
```

---

## 🚀 Установка и запуск

### Требования
- Python 3.9+
- Никаких внешних зависимостей! (используются только встроенные модули)

### Запуск базовой демонстрации

```bash
python main.py
```

**Вывод:**
```
🎓 ДЕМОНСТРАЦИЯ ПАТТЕРНОВ ПРОЕКТИРОВАНИЯ
======================================================================

1️⃣  SINGLETON - Настройки системы
✅ settings1 is settings2: True

2️⃣  FACTORY METHOD - Создание датчиков
✅ Добавлен датчик TEMP_01 со стратегией SIMPLE
...

3️⃣  OBSERVER - Подписка служб на уведомления
✅ МЧС (Служба спасения) подписалась на уведомления
...

🚀 ПОЕХАЛИ! Симуляция мониторинга:
```

### Запуск расширенных примеров

```bash
python advanced_examples.py
```

---

## 💡 Примеры использования

### Пример 1: Создание датчика и проверка его значения

```python
from sensors import SensorFactory
from settings import get_settings

# Создать датчик
sensor = SensorFactory.create_sensor("TEMP_01")

# Прочитать значение
value = sensor.read_value()
print(f"Температура: {value}°C")

# Получить тип
print(f"Тип: {sensor.get_sensor_type()}")
print(f"Описание: {sensor.get_description()}")
```

### Пример 2: Использование разных стратегий анализа

```python
from strategies import StrategyFactory

# Создать две стратегии
simple = StrategyFactory.create_strategy("SIMPLE")
moving_avg = StrategyFactory.create_strategy("MOVING_AVG")

# Проанализировать с разными алгоритмами
readings = [48, 49, 51]
threshold = 50

print(simple.analyze(readings, threshold))        # True (51 > 50)
print(moving_avg.analyze(readings, threshold))    # True (49.3 > 50? False)
```

### Пример 3: Регистрация кастомной службы

```python
from alerts import get_control_center, AlertSubscriber

class MyService(AlertSubscriber):
    def __init__(self):
        self.name = "Моя служба"
        self.alerts_count = 0
    
    def update(self, sensor_id, sensor_type, value, threshold):
        self.alerts_count += 1
        print(f"Мое уведомление: {sensor_id} = {value}")
    
    def get_name(self):
        return self.name

# Подписать на уведомления
center = get_control_center()
center.subscribe(MyService())
```

---

## 🔧 Расширение системы

### Добавление нового типа датчика

```python
from sensors import Sensor, SensorFactory
import random

class PressureSensor(Sensor):
    """Датчик давления (900-1100 hPa)"""
    
    def read_value(self) -> float:
        value = random.uniform(900, 1100)
        self.record_reading(value)
        return value
    
    def get_sensor_type(self) -> str:
        return "pressure"

# Регистрируем новый тип
SensorFactory.register_sensor_type("PRESSURE", PressureSensor)

# Теперь можем создавать датчики
sensor = SensorFactory.create_sensor("PRESSURE_01")
```

### Добавление новой стратегии анализа

```python
from strategies import AnalysisStrategy, StrategyFactory

class ThresholdWithHysteresis(AnalysisStrategy):
    """Стратегия с гистерезисом"""
    
    def __init__(self, trigger_threshold: float = 1.1):
        self.trigger_threshold = trigger_threshold
        self.triggered = False
    
    def analyze(self, readings: list, threshold: float) -> bool:
        if not readings:
            return False
        
        value = readings[-1]
        if value > threshold * self.trigger_threshold:
            self.triggered = True
        elif value < threshold * 0.9:
            self.triggered = False
        
        return self.triggered
    
    def get_description(self) -> str:
        return "Гистерезис: с памятью состояния"

# Использование
strategy = ThresholdWithHysteresis()
```

### Добавление новой службы-подписчика

```python
from alerts import AlertSubscriber, get_control_center

class DataCenter(AlertSubscriber):
    """Центр обработки данных"""
    
    def __init__(self):
        self.name = "Центр обработки данных"
        self.alerts_count = 0
    
    def update(self, sensor_id, sensor_type, value, threshold):
        self.alerts_count += 1
        # Логирование, отправка в облако, и т.д.
        print(f"📡 DataCenter: {sensor_id} зафиксировано")
    
    def get_name(self):
        return self.name

# Регистрируем
center = get_control_center()
center.subscribe(DataCenter())
```

---

## 📊 Статистика проекта

| Компонент | Строк кода | Назначение |
|-----------|-----------|-----------|
| **settings.py** | ~80 | Singleton паттерн |
| **sensors.py** | ~150 | Factory паттерн |
| **strategies.py** | ~180 | Strategy паттерн |
| **alerts.py** | ~220 | Observer паттерн |
| **main.py** | ~200 | Демонстрация |
| **advanced_examples.py** | ~150 | Расширения |

**Общее время выполнения симуляции:** ~20 секунд

---

## 🎓 Образовательные цели

При работе с этим проектом вы изучите:

✅ **Singleton** - Как гарантировать единственность объекта
✅ **Factory Method** - Как создавать объекты не зная их типа
✅ **Observer** - Как разделить издателей и подписчиков
✅ **Strategy** - Как менять алгоритмы во время работы

✅ Использование модуля `abc` для абстрактных классов
✅ Расширяемость кода без изменения существующего
✅ Слабую связанность между компонентами
✅ Инкапсуляцию логики в разных слоях

---

## 🐛 Решение проблем

### Проблема: "ModuleNotFoundError"
**Решение:** Убедитесь, что находитесь в правильной папке и все файлы на месте.

### Проблема: Мало тревог в симуляции
**Решение:** Отрегулируйте пороги в `settings.py` или измените стратегии на "SIMPLE".

### Проблема: Нужно логировать события
**Решение:** Смотрите `advanced_examples.py` - там реализован `EventLogger`.

---

## 📚 Дополнительные ресурсы

- **Design Patterns: Elements of Reusable Object-Oriented Software** - Gang of Four
- **Python Design Patterns** - https://refactoring.guru/design-patterns/python
- **Python abc module** - https://docs.python.org/3/library/abc.html

---

## 📞 Контакты и поддержка

Проект создан в образовательных целях для изучения паттернов проектирования.

Версия: 1.0
Дата: 2026
Язык: Python 3.9+

---

**Успехов в изучении паттернов! 🚀**
