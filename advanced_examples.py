"""
ADVANCED EXAMPLES - Дополнительные возможности системы
======================================================

Этот файл демонстрирует продвинутые техники:
- Кастомные датчики
- Фильтрация уведомлений
- Динамическая регистрация стратегий
- Логирование событий
"""

import json
from datetime import datetime
from sensors import Sensor, SensorFactory
from strategies import AnalysisStrategy
from alerts import AlertSubscriber, get_control_center


# ========== ПРИМЕР 1: Кастомный датчик ==========
class NoiseLevelSensor(Sensor):
    """Пользовательский датчик уровня шума в dB."""

    def read_value(self) -> float:
        """Имитация чтения уровня шума (диапазон 30-100 dB)."""
        from random import uniform
        value = uniform(30, 100)
        self.record_reading(value)
        return value

    def get_sensor_type(self) -> str:
        return "noise"


# Регистрируем новый датчик
SensorFactory.register_sensor_type("NOISE", NoiseLevelSensor)


# ========== ПРИМЕР 2: Продвинутая стратегия ==========
class TriggeredStrategy(AnalysisStrategy):
    """
    Стратегия с срабатыванием (Hysteresis).
    Требует нескольких последовательных превышений для тревоги.
    """

    def __init__(self, trigger_count: int = 2):
        self.trigger_count = trigger_count
        self.consecutive_triggers = 0

    def analyze(self, readings: list, threshold: float) -> bool:
        if not readings:
            return False

        if readings[-1] > threshold:
            self.consecutive_triggers += 1
        else:
            self.consecutive_triggers = 0

        return self.consecutive_triggers >= self.trigger_count

    def get_description(self) -> str:
        return f"Срабатывание: требует {self.trigger_count} последовательных превышений"


# ========== ПРИМЕР 3: Избирательный подписчик ==========
class SpecializedService(AlertSubscriber):
    """Служба, которая реагирует только на определенные типы датчиков."""

    def __init__(self, name: str, interested_sensors: list):
        self.name = name
        self.interested_sensors = interested_sensors
        self.alerts_count = 0

    def update(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        if sensor_type not in self.interested_sensors:
            return

        self.alerts_count += 1
        print(f"\n🎯 {self.name} зафиксировала проблему:")
        print(f"   Датчик: {sensor_id} ({sensor_type})")
        print(f"   Значение: {value:.2f} (лимит: {threshold:.2f})")

    def get_name(self) -> str:
        return self.name


# ========== ПРИМЕР 4: Логирование событий ==========
class EventLogger(AlertSubscriber):
    """
    Централизованный логгер всех событий.
    Сохраняет события в структурированном формате.
    """

    def __init__(self, log_file: str = "monitoring_log.json"):
        self.name = "Event Logger (Централизованный логгер)"
        self.log_file = log_file
        self.events = []
        self.alerts_count = 0

    def update(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        self.alerts_count += 1
        event = {
            "timestamp": datetime.now().isoformat(),
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "value": value,
            "threshold": threshold,
            "severity": "HIGH" if value > threshold * 1.5 else "MEDIUM"
        }
        self.events.append(event)

    def get_name(self) -> str:
        return self.name

    def save_log(self):
        """Сохранить логи в JSON файл."""
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)
        print(f"💾 Логи сохранены в {self.log_file}")

    def print_summary(self):
        """Вывести сводку по событиям."""
        if not self.events:
            print("Логи пусты")
            return

        print(f"\n📝 Сводка логов ({len(self.events)} событий):")
        for event in self.events:
            print(
                f"  [{event['timestamp']}] {event['sensor_id']} "
                f"= {event['value']:.2f} ({event['severity']})"
            )


# ========== ПРИМЕР 5: Демонстрация расширений ==========
def demo_extensions():
    """Демонстрирует расширяемость системы."""

    print("\n" + "="*70)
    print("🚀 ДЕМОНСТРАЦИЯ РАСШИРЕНИЙ СИСТЕМЫ")
    print("="*70)

    from settings import get_settings
    from sensors import SensorFactory

    settings = get_settings()
    control_center = get_control_center()

    # Добавить специализированные службы
    print("\n1. Добавляем специализированные службы:")
    temp_service = SpecializedService("Служба отопления", ["temperature"])
    noise_service = SpecializedService("Служба по борьбе с шумом", ["noise"])
    logger = EventLogger()

    control_center.subscribe(temp_service)
    control_center.subscribe(noise_service)
    control_center.subscribe(logger)

    print(control_center.get_subscribers_info())

    # Создать кастомные датчики
    print("\n2. Создаем кастомные датчики:")
    print(f"   Новые типы датчиков: {SensorFactory.get_available_types()}")

    noise_sensor = SensorFactory.create_sensor("NOISE_01")
    print(f"   ✅ Создан датчик: {noise_sensor.get_description()}")

    # Протестировать стратегию с срабатыванием
    print("\n3. Тестируем продвинутую стратегию:")
    strategy = TriggeredStrategy(trigger_count=2)
    print(f"   {strategy.get_description()}")

    # Симуляция показаний
    test_readings = [40, 42, 48, 52, 55]  # растущие значения
    threshold = 50

    print(f"\n   Значения: {test_readings}")
    print(f"   Порог: {threshold}")

    for i, reading in enumerate(test_readings, 1):
        is_critical = strategy.analyze(test_readings[:i], threshold)
        print(f"   Показание {i} ({reading}): {'🚨 ТРЕВОГА' if is_critical else 'в норме'}")

    # Логирование
    print("\n4. Демонстрируем логирование:")
    print("   Генерируем тестовые события...")

    control_center.notify_subscribers("TEMP_01", "temperature", 47, 45)
    control_center.notify_subscribers("NOISE_01", "noise", 85, 70)

    logger.print_summary()
    # logger.save_log()  # Раскомментируйте для сохранения в файл

    print("\n✅ Демонстрация расширений завершена!")


if __name__ == "__main__":
    demo_extensions()
