"""
Strategy Pattern: Analysis Strategies
Позволяет менять алгоритм анализа данных во время работы.
"""

from abc import ABC, abstractmethod
from statistics import mean


class AnalysisStrategy(ABC):
    """
    Абстрактная стратегия анализа данных датчика.
    Определяет интерфейс для всех конкретных стратегий.
    """

    @abstractmethod
    def analyze(self, readings: list, threshold: float) -> bool:
        """
        Проанализировать данные и определить, критичное ли значение.
        
        Args:
            readings: История последних показаний датчика
            threshold: Пороговое значение для тревоги
            
        Returns:
            True если критическое значение, False иначе
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Получить описание стратегии."""
        pass


class SimpleStrategy(AnalysisStrategy):
    """
    Strategy A: Простая стратегия.
    Поднять тревогу, если последнее значение > порога.
    """

    def analyze(self, readings: list, threshold: float) -> bool:
        if not readings:
            return False
        return readings[-1] > threshold

    def get_description(self) -> str:
        return "Простая (Simple): тревога если значение > порога"


class MovingAverageStrategy(AnalysisStrategy):
    """
    Strategy B: Скользящее среднее.
    Поднять тревогу, только если среднее последних N значений > порога.
    """

    def __init__(self, window_size: int = 3):
        self.window_size = window_size

    def analyze(self, readings: list, threshold: float) -> bool:
        if len(readings) < self.window_size:
            return False
        
        recent_readings = readings[-self.window_size:]
        average = mean(recent_readings)
        return average > threshold

    def get_description(self) -> str:
        return f"Скользящее среднее: тревога если среднее {self.window_size} значений > порога"


class TrendStrategy(AnalysisStrategy):
    """
    Strategy C (Бонус): Анализ тренда.
    Поднять тревогу если значения растут и последнее > порога.
    Используется для детектирования опасных тенденций.
    """

    def analyze(self, readings: list, threshold: float) -> bool:
        if len(readings) < 2:
            return readings[-1] > threshold if readings else False
        
        # Проверить, растут ли последние значения
        is_increasing = all(
            readings[i] < readings[i + 1]
            for i in range(max(0, len(readings) - 4), len(readings) - 1)
        )
        
        # Тревога если растет И превышено значение
        return is_increasing and readings[-1] > threshold

    def get_description(self) -> str:
        return "Анализ тренда: тревога если значения растут и > порога"


class AdaptiveStrategy(AnalysisStrategy):
    """
    Strategy D (Бонус): Адаптивная стратегия.
    Использует разные пороги в зависимости от времени суток.
    (Днем строже, ночью мягче)
    """

    def __init__(self, base_threshold_multiplier_day: float = 1.0,
                 base_threshold_multiplier_night: float = 1.2):
        self.day_multiplier = base_threshold_multiplier_day
        self.night_multiplier = base_threshold_multiplier_night

    def analyze(self, readings: list, threshold: float) -> bool:
        if not readings:
            return False
        
        # Получить текущий час (упрощенно)
        from datetime import datetime
        current_hour = datetime.now().hour
        
        # Применить разные коэффициенты
        if 7 <= current_hour < 22:  # День
            adjusted_threshold = threshold * self.day_multiplier
        else:  # Ночь
            adjusted_threshold = threshold * self.night_multiplier
        
        return readings[-1] > adjusted_threshold

    def get_description(self) -> str:
        return f"Адаптивная: день (x{self.day_multiplier}), ночь (x{self.night_multiplier})"


class StrategyFactory:
    """Фабрика для создания стратегий анализа."""

    _strategies = {
        "SIMPLE": SimpleStrategy,
        "MOVING_AVG": lambda: MovingAverageStrategy(3),
        "TREND": TrendStrategy,
        "ADAPTIVE": AdaptiveStrategy,
    }

    @classmethod
    def create_strategy(cls, strategy_type: str) -> AnalysisStrategy:
        """Создать стратегию по типу."""
        if strategy_type not in cls._strategies:
            raise ValueError(
                f"❌ Неизвестная стратегия: {strategy_type}. "
                f"Доступные: {list(cls._strategies.keys())}"
            )
        
        strategy = cls._strategies[strategy_type]
        # Если это функция (lambda), вызов вернет экземпляр
        return strategy() if callable(strategy) and not isinstance(strategy, type) else strategy()

    @classmethod
    def get_available_strategies(cls) -> list:
        """Получить список доступных стратегий."""
        return list(cls._strategies.keys())
