"""
Singleton Pattern: SystemSettings
Гарантирует, что в памяти существует только один экземпляр конфигурации системы.
"""

import threading


class SingletonMeta(type):
    """
    Метакласс для реализации Singleton паттерна.
    Контролирует создание экземпляров класса.
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with SingletonMeta._lock:
                if cls not in cls._instances:
                    instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class SystemSettings(metaclass=SingletonMeta):
    """
    Установки системы мониторинга.
    Реализована как Singleton - гарантирует единственный экземпляр.
    """

    def __init__(self):
        # Порог температуры для срабатывания тревоги
        self.threshold_temperature = 45
        
        # Порог CO2 (ppm)
        self.threshold_co2 = 400
        
        # Порог трафика (% от максимума)
        self.threshold_traffic = 85
        
        # URL базы данных
        self.database_url = "postgresql://localhost/smart_city"
        
        # Количество последних измерений для Moving Average
        self.moving_average_window = 3
        
        # Интервал между проверками датчиков (секунды)
        self.check_interval = 2
        
        # Минимальное количество критических значений для тревоги
        self.min_critical_readings = 2

    def set_threshold(self, sensor_type: str, value: float):
        """Установить новый порог для типа датчика."""
        if sensor_type == "temperature":
            self.threshold_temperature = value
        elif sensor_type == "co2":
            self.threshold_co2 = value
        elif sensor_type == "traffic":
            self.threshold_traffic = value

    def get_threshold(self, sensor_type: str) -> float:
        """Получить порог для типа датчика."""
        if sensor_type == "temperature":
            return self.threshold_temperature
        elif sensor_type == "co2":
            return self.threshold_co2
        elif sensor_type == "traffic":
            return self.threshold_traffic
        return 0.0

    def display_settings(self):
        """Вывести текущие настройки."""
        print("\n📋 Текущие настройки системы:")
        print(f"   Порог температуры: {self.threshold_temperature}°C")
        print(f"   Порог CO2: {self.threshold_co2} ppm")
        print(f"   Порог трафика: {self.threshold_traffic}%")
        print(f"   БД: {self.database_url}")
        print(f"   Окно Moving Average: {self.moving_average_window}")


# Функция-помощник для быстрого доступа к Singleton
def get_settings() -> SystemSettings:
    """Получить единственный экземпляр SystemSettings."""
    return SystemSettings()
