"""
Factory Method Pattern: Sensor Classes
Создает различные типы датчиков на основе строкового кода.
"""

from abc import ABC, abstractmethod
from random import uniform, randint
from datetime import datetime


class Sensor(ABC):
    """
    Абстрактный класс базового датчика.
    Определяет интерфейс для всех конкретных датчиков.
    """

    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id
        self.last_value = 0.0
        self.readings_history = []
        self.is_critical = False

    @abstractmethod
    def read_value(self) -> float:
        """Прочитать значение с датчика."""
        pass

    @abstractmethod
    def get_sensor_type(self) -> str:
        """Получить тип датчика."""
        pass

    def record_reading(self, value: float):
        """Записать показание в историю."""
        self.readings_history.append(value)
        # Хранить только последние 10 значений
        if len(self.readings_history) > 10:
            self.readings_history.pop(0)
        self.last_value = value

    def get_description(self) -> str:
        """Получить описание датчика."""
        return f"Датчик {self.sensor_id} (тип: {self.get_sensor_type()}), Последнее значение: {self.last_value}"


class TemperatureSensor(Sensor):
    """Датчик температуры. Диапазон: -30°C до +50°C"""

    def read_value(self) -> float:
        """Имитация чтения температуры."""
        value = uniform(-30, 50)
        self.record_reading(value)
        return value

    def get_sensor_type(self) -> str:
        return "temperature"


class AirQualitySensor(Sensor):
    """Датчик качества воздуха (CO2). Диапазон: 300-2000 ppm"""

    def read_value(self) -> float:
        """Имитация чтения уровня CO2."""
        value = uniform(300, 2000)
        self.record_reading(value)
        return value

    def get_sensor_type(self) -> str:
        return "air_quality"


class TrafficSensor(Sensor):
    """Датчик трафика (загруженность). Диапазон: 0-100%"""

    def read_value(self) -> float:
        """Имитация чтения уровня трафика."""
        value = uniform(0, 100)
        self.record_reading(value)
        return value

    def get_sensor_type(self) -> str:
        return "traffic"


class SensorFactory:
    """
    Factory Method: создает датчики по типу.
    Позволяет добавлять новые типы датчиков без изменения клиентского кода.
    """

    _sensor_types = {
        "TEMP": TemperatureSensor,
        "AIR": AirQualitySensor,
        "TRAFFIC": TrafficSensor,
    }

    @classmethod
    def create_sensor(cls, sensor_code: str) -> Sensor:
        """
        Создать датчик по коду.
        
        Args:
            sensor_code: Код датчика (например, "TEMP_01", "AIR_02", "TRAFFIC_03")
        
        Returns:
            Экземпляр нужного типа датчика
            
        Raises:
            ValueError: Если тип датчика не найден
        """
        # Извлечь тип из кода
        sensor_type = sensor_code.split("_")[0]
        
        if sensor_type not in cls._sensor_types:
            raise ValueError(
                f"❌ Неизвестный тип датчика: {sensor_type}. "
                f"Доступные типы: {list(cls._sensor_types.keys())}"
            )
        
        sensor_class = cls._sensor_types[sensor_type]
        return sensor_class(sensor_code)

    @classmethod
    def register_sensor_type(cls, type_code: str, sensor_class: type):
        """
        Добавить новый тип датчика в фабрику.
        Позволяет расширять систему без изменения кода Factory.
        """
        cls._sensor_types[type_code] = sensor_class

    @classmethod
    def get_available_types(cls) -> list:
        """Получить список доступных типов датчиков."""
        return list(cls._sensor_types.keys())


# Пример: расширение системы новым типом датчика
class HumiditySetpointor(Sensor):
    """Пример нового датчика влажности для демонстрации расширяемости."""

    def read_value(self) -> float:
        """Имитация чтения влажности (0-100%)."""
        value = uniform(20, 100)
        self.record_reading(value)
        return value

    def get_sensor_type(self) -> str:
        return "humidity"


# Регистрируем новый тип датчика
SensorFactory.register_sensor_type("HUMIDITY", HumiditySetpointor)
