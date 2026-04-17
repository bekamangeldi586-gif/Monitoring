"""
QUICK START - Быстрый старт с примерами
========================================

Примеры для быстрого начала работы с системой.
Скопируйте, модифицируйте и используйте как шаблоны.
"""

# ========== ПРИМЕР 1: Минималистичный ==========
def example_1_minimal():
    """Самый простой способ начать."""
    from sensors import SensorFactory
    from alerts import EmergencyService, get_control_center

    # Создали датчик
    sensor = SensorFactory.create_sensor("TEMP_01")

    # Прочитали значение
    value = sensor.read_value()
    print(f"📊 Значение: {value:.1f}°C")

    # Если срочно, отправляем уведомление
    if value > 45:
        center = get_control_center()
        center.subscribe(EmergencyService())
        center.notify_subscribers(
            "TEMP_01", "temperature", value, 45
        )


# ========== ПРИМЕР 2: Работа с стратегиями ==========
def example_2_strategies():
    """Демонстрация смены стратегий анализа."""
    from sensors import SensorFactory
    from strategies import StrategyFactory
    from settings import get_settings

    # Получить настройки (Singleton!)
    settings = get_settings()

    # Создать датчик
    sensor = SensorFactory.create_sensor("AIR_02")

    # Создать две стратегии
    simple = StrategyFactory.create_strategy("SIMPLE")
    moving_avg = StrategyFactory.create_strategy("MOVING_AVG")

    # Несколько измерений
    readings = []
    for _ in range(5):
        value = sensor.read_value()
        readings.append(value)

    threshold = settings.get_threshold("air_quality")

    print(f"📊 Показания: {[f'{x:.0f}' for x in readings]}")
    print(f"🎯 Порог: {threshold:.0f} ppm")
    print(f"📈 SIMPLE: {simple.analyze(readings, threshold)}")
    print(f"📈 MOVING_AVG: {moving_avg.analyze(readings, threshold)}")


# ========== ПРИМЕР 3: Демонстрация Singleton ==========
def example_3_singleton():
    """Доказательство работы Singleton паттерна."""
    from settings import SystemSettings, get_settings

    # Способ 1: Прямое создание
    s1 = SystemSettings()
    s2 = SystemSettings()

    # Способ 2: Функция-помощник
    s3 = get_settings()
    s4 = get_settings()

    # Все одно и то же!
    print(f"✅ s1 is s2: {s1 is s2}")
    print(f"✅ s3 is s4: {s3 is s4}")
    print(f"✅ s1 is s3: {s1 is s3}")

    # ID в памяти
    print(f"📍 ID объекта: {id(s1)}")

    # Меняем в одном месте - видим везде
    s1.threshold_temperature = 50
    print(f"🌡️  s2.threshold_temperature = {s2.threshold_temperature}")
    print(f"🌡️  s3.threshold_temperature = {s3.threshold_temperature}")


# ========== ПРИМЕР 4: Отслеживание тревог ==========
def example_4_tracking_alerts():
    """Отслеживание всех тревог через архив."""
    from sensors import SensorFactory
    from settings import get_settings
    from strategies import StrategyFactory
    from alerts import get_control_center, CityCouncil

    settings = get_settings()
    center = get_control_center()

    # Создать архив-подписчик
    archive = CityCouncil()
    center.subscribe(archive)

    # Создать датчик
    sensor = SensorFactory.create_sensor("TRAFFIC_03")

    # Сгенерировать тревоги
    for i in range(5):
        value = sensor.read_value()
        threshold = settings.get_threshold("traffic")
        
        if value > threshold:
            center.notify_subscribers(
                "TRAFFIC_03", "traffic", value, threshold
            )

    # Вывести отчет
    print(archive.get_report())


# ========== ПРИМЕР 5: Кастомная служба ==========
def example_5_custom_service():
    """Создание собственной службы-подписчика."""
    from alerts import AlertSubscriber, get_control_center

    class TelegramBot(AlertSubscriber):
        """Бот, отправляющий уведомления в Telegram"""

        def __init__(self, chat_id: str):
            self.name = f"Telegram Bot (chat: {chat_id})"
            self.chat_id = chat_id
            self.alerts_count = 0

        def update(self, sensor_id, sensor_type, value, threshold):
            self.alerts_count += 1
            # Здесь был бы запрос к Telegram API
            message = (
                f"⚠️  ALERT\\n"
                f"Датчик: {sensor_id}\\n"
                f"Значение: {value:.2f}\\n"
                f"Порог: {threshold:.2f}"
            )
            print(f"📱 Отправляю в Telegram ({self.chat_id}): {message}")

        def get_name(self):
            return self.name

    # Использование
    center = get_control_center()
    bot = TelegramBot("123456789")
    center.subscribe(bot)

    # Тревога
    center.notify_subscribers("TEMP_01", "temperature", 46, 45)


# ========== ПРИМЕР 6: Работа с историей датчика ==========
def example_6_sensor_history():
    """Работа с историей измерений датчика."""
    from sensors import SensorFactory

    # Создать датчик
    sensor = SensorFactory.create_sensor("TEMP_01")

    # Снять 10 измерений
    print("📊 Снимаю 10 измерений температуры:\n")
    for i in range(10):
        value = sensor.read_value()
        avg = sum(sensor.readings_history) / len(sensor.readings_history)
        min_val = min(sensor.readings_history)
        max_val = max(sensor.readings_history)

        print(
            f"  {i+1:2d}. Значение: {value:6.2f}°C | "
            f"Средн: {avg:6.2f} | Min: {min_val:6.2f} | Max: {max_val:6.2f}"
        )


# ========== ПРИМЕР 7: Полная демонстрация ==========
def example_7_full_demo():
    """Полная демонстрация всех компонентов вместе."""
    from sensors import SensorFactory
    from settings import get_settings
    from strategies import StrategyFactory
    from alerts import (
        get_control_center, EmergencyService,
        PoliceService, EnvironmentalService, CityCouncil
    )

    print("\n" + "="*70)
    print("🎯 ПОЛНАЯ ДЕМОНСТРАЦИЯ СИСТЕМЫ")
    print("="*70)

    # 1. Настройки (Singleton)
    settings = get_settings()
    print("\n1️⃣  Настройки системы:")
    settings.display_settings()

    # 2. Центр управления
    center = get_control_center()
    print("\n2️⃣  Регистрируем службы:")
    center.subscribe(EmergencyService())
    center.subscribe(PoliceService())
    center.subscribe(EnvironmentalService())
    center.subscribe(CityCouncil())
    print(center.get_subscribers_info())

    # 3. Создаем датчики с разными стратегиями
    print("\n3️⃣  Создаем датчики:")
    sensors = {
        "TEMP_01": StrategyFactory.create_strategy("MOVING_AVG"),
        "AIR_02": StrategyFactory.create_strategy("SIMPLE"),
        "TRAFFIC_03": StrategyFactory.create_strategy("TREND"),
    }

    for sensor_code, strategy in sensors.items():
        print(f"   {sensor_code} -> {strategy.get_description()}")

    # 4. Симуляция наблюдений
    print("\n4️⃣  Симуляция наблюдений (5 итераций):")
    for iteration in range(5):
        print(f"\n   Итерация {iteration + 1}:")
        
        for sensor_code, strategy in sensors.items():
            sensor = SensorFactory.create_sensor(sensor_code)
            value = sensor.read_value()
            sensor_type = sensor.get_sensor_type()
            threshold = settings.get_threshold(sensor_type)

            is_critical = strategy.analyze(sensor.readings_history, threshold)

            if is_critical:
                center.notify_subscribers(sensor_code, sensor_type, value, threshold)

    # 5. Статистика
    print("\n5️⃣  Статистика:")
    print(center.get_statistics())


# ========== МЕНЮ ПРИМЕРОВ ==========
def main():
    """Главное меню с примерами."""
    examples = {
        "1": ("Минимальный пример", example_1_minimal),
        "2": ("Работа со стратегиями", example_2_strategies),
        "3": ("Demонстрация Singleton", example_3_singleton),
        "4": ("Отслеживание тревог", example_4_tracking_alerts),
        "5": ("Кастомная служба", example_5_custom_service),
        "6": ("История датчика", example_6_sensor_history),
        "7": ("Полная демонстрация", example_7_full_demo),
    }

    print("\n" + "="*70)
    print("🚀 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ СИСТЕМЫ МОНИТОРИНГА")
    print("="*70)
    print("\nВыберите пример:")

    for key, (description, _) in examples.items():
        print(f"  {key}. {description}")
    print("  0. Выйти")

    print("\n" + "-"*70)
    choice = input("Введите номер (0-7): ").strip()

    if choice in examples:
        description, func = examples[choice]
        print(f"\n▶️  Запуск: {description}")
        print("-"*70)
        func()
        print("\n✅ Пример завершен!")
    elif choice == "0":
        print("До встречи!")
    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    # Для прямого запуска примера: раскомментируйте нужный
    
    # example_1_minimal()
    # example_2_strategies()
    # example_3_singleton()
    # example_4_tracking_alerts()
    # example_5_custom_service()
    # example_6_sensor_history()
    example_7_full_demo()
    
    # Или запустите меню:
    # main()
