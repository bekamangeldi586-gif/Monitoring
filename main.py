"""
Smart City Monitoring System - Главная демонстрация
===============================================

Архитектура демонстрирует 4 основных паттерна проектирования:
1. Singleton - SystemSettings (только один экземпляр настроек)
2. Factory Method - SensorFactory (создание датчиков по коду)
3. Observer - ControlCenter + AlertSubscriber (уведомление служб об аномалиях)
4. Strategy - AnalysisStrategy (переключение алгоритмов анализа)
"""

import time
from settings import get_settings
from sensors import SensorFactory, Sensor
from strategies import StrategyFactory, AnalysisStrategy
from alerts import (
    get_control_center, EmergencyService, PoliceService,
    EnvironmentalService, CityCouncil
)


class MonitoringSystem:
    """Главная система мониторинга города."""

    def __init__(self):
        self.settings = get_settings()
        self.control_center = get_control_center()
        self.sensors: dict[str, Sensor] = {}
        self.sensor_strategies: dict[str, AnalysisStrategy] = {}

    def add_sensor(self, sensor_code: str, strategy_type: str = "SIMPLE"):
        """
        Добавить новый датчик в систему.
        
        Args:
            sensor_code: Код датчика (например "TEMP_01", "AIR_02")
            strategy_type: Тип стратегии анализа
        """
        try:
            sensor = SensorFactory.create_sensor(sensor_code)
            strategy = StrategyFactory.create_strategy(strategy_type)
            
            self.sensors[sensor_code] = sensor
            self.sensor_strategies[sensor_code] = strategy
            
            print(f"✅ Добавлен датчик {sensor_code} со стратегией {strategy_type}")
            return sensor
        except ValueError as e:
            print(f"❌ Ошибка: {e}")
            return None

    def change_strategy(self, sensor_code: str, new_strategy_type: str):
        """Изменить стратегию анализа для датчика во время работы."""
        if sensor_code not in self.sensors:
            print(f"❌ Датчик {sensor_code} не найден")
            return
        
        try:
            new_strategy = StrategyFactory.create_strategy(new_strategy_type)
            old_strategy = self.sensor_strategies[sensor_code]
            self.sensor_strategies[sensor_code] = new_strategy
            
            print(f"\n🔄 Датчик {sensor_code}:")
            print(f"   Старая стратегия: {old_strategy.get_description()}")
            print(f"   Новая стратегия: {new_strategy.get_description()}")
        except ValueError as e:
            print(f"❌ Ошибка: {e}")

    def check_sensor(self, sensor_code: str):
        """Проверить значение датчика и применить стратегию анализа."""
        if sensor_code not in self.sensors:
            print(f"❌ Датчик {sensor_code} не найден")
            return

        sensor = self.sensors[sensor_code]
        strategy = self.sensor_strategies[sensor_code]

        # Прочитать значение
        value = sensor.read_value()

        # Применить стратегию
        sensor_type = sensor.get_sensor_type()
        threshold = self.settings.get_threshold(sensor_type)
        is_critical = strategy.analyze(sensor.readings_history, threshold)

        # Вывести информацию
        status = "🚨 КРИТИЧЕСКОЕ" if is_critical else "✅ в норме"
        print(f"\n[{sensor_code}] {sensor_type}: {value:.2f} - {status}")
        print(f"   Стратегия: {strategy.get_description()}")
        print(f"   История: {[f'{x:.1f}' for x in sensor.readings_history[-5:]]}")

        # Если критическое - отправить уведомление
        if is_critical:
            self.control_center.notify_subscribers(
                sensor_code, sensor_type, value, threshold
            )

    def simulate_monitoring(self, duration_seconds: int = 20):
        """Симуляция работы системы мониторинга."""
        print(f"\n{'='*70}")
        print("🌆 ЗАПУСК СИМУЛЯЦИИ СИСТЕМЫ МОНИТОРИНГА ГОРОДА СЕМЕЙ")
        print(f"{'='*70}")
        print(f"Продолжительность: {duration_seconds} секунд")

        start_time = time.time()
        iteration = 0

        while time.time() - start_time < duration_seconds:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"⏱️  Итерация {iteration} ({int(time.time() - start_time)}с)")
            print(f"{'='*70}")

            # Проверить все датчики
            for sensor_code in self.sensors:
                self.check_sensor(sensor_code)

            time.sleep(self.settings.check_interval)

    def print_final_report(self):
        """Вывести финальный отчет."""
        print(f"\n{'='*70}")
        print("📊 ФИНАЛЬНЫЙ ОТЧЕТ")
        print(f"{'='*70}")

        print(self.control_center.get_statistics())
        
        # Найти и вывести отчет архива
        for subscriber in self.control_center._subscribers:
            if isinstance(subscriber, CityCouncil):
                print("\n" + subscriber.get_report())


def main():
    """Главная функция - демонстрация всех паттернов."""
    
    print("\n🎓 ДЕМОНСТРАЦИЯ ПАТТЕРНОВ ПРОЕКТИРОВАНИЯ")
    print("="*70)

    # ============ 1. SINGLETON ============
    print("\n1️⃣  SINGLETON - Настройки системы")
    print("-" * 70)
    settings1 = get_settings()
    settings2 = get_settings()
    print(f"✅ settings1 is settings2: {settings1 is settings2}")
    print(f"   (Доказывает, что существует только один экземпляр)")
    settings1.display_settings()

    # ============ 2. FACTORY METHOD ============
    print("\n2️⃣  FACTORY METHOD - Создание датчиков")
    print("-" * 70)
    system = MonitoringSystem()

    # Добавить датчики разных типов
    print(f"\nДоступные типы датчиков: {SensorFactory.get_available_types()}")
    print(f"Доступные стратегии: {StrategyFactory.get_available_strategies()}")

    system.add_sensor("TEMP_01", "SIMPLE")
    system.add_sensor("AIR_02", "MOVING_AVG")
    system.add_sensor("TRAFFIC_03", "TREND")
    system.add_sensor("HUMIDITY_04", "ADAPTIVE")

    # ============ 3. OBSERVER ============
    print("\n3️⃣  OBSERVER - Подписка служб на уведомления")
    print("-" * 70)
    # Создать и зарегистрировать службы
    emergency = EmergencyService()
    police = PoliceService()
    ecology = EnvironmentalService()
    archive = CityCouncil()

    system.control_center.subscribe(emergency)
    system.control_center.subscribe(police)
    system.control_center.subscribe(ecology)
    system.control_center.subscribe(archive)

    print(system.control_center.get_subscribers_info())

    # ============ 4. STRATEGY ============
    print("\n4️⃣  STRATEGY - Изменение стратегии анализа во время работы")
    print("-" * 70)
    print("Демонстрируем смену стратегии:")
    system.change_strategy("TEMP_01", "MOVING_AVG")
    system.change_strategy("AIR_02", "TREND")

    # ============ СИМУЛЯЦИЯ ============
    print("\n" + "="*70)
    print("🚀 ПОЕХАЛИ! Симуляция мониторинга: ")
    print("="*70)
    
    # Запустить симуляцию на 20 секунд
    system.simulate_monitoring(duration_seconds=20)

    # Вывести итоговый отчет
    system.print_final_report()

    print("\n✅ Демонстрация завершена!")


if __name__ == "__main__":
    main()
