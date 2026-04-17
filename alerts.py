"""
Observer Pattern: Alert System
Датчики - издатели (Publishers), Службы - подписчики (Subscribers).
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class AlertSubscriber(ABC):
    """
    Абстрактный класс подписчика (Observer).
    Все службы должны наследовать этот класс.
    """

    @abstractmethod
    def update(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        """
        Получить уведомление об аномалии.
        
        Args:
            sensor_id: ID датчика
            sensor_type: Тип датчика
            value: Измеренное значение
            threshold: Пороговое значение
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Получить название службы."""
        pass


class EmergencyService(AlertSubscriber):
    """МЧС (служба спасения). Реагирует на все критические ситуации."""

    def __init__(self):
        self.name = "МЧС (Служба спасения)"
        self.alerts_count = 0

    def update(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        self.alerts_count += 1
        print(f"\n🚨 {self.name} получила тревогу!")
        print(f"   ⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   📍 Датчик: {sensor_id} ({sensor_type})")
        print(f"   📊 Значение: {value:.2f} (порог: {threshold:.2f})")
        print(f"   ⚠️  КРИТИЧЕСКАЯ СИТУАЦИЯ - Отправляем спасательную группу!")

    def get_name(self) -> str:
        return self.name


class PoliceService(AlertSubscriber):
    """Полиция. Реагирует на аномальный трафик."""

    def __init__(self):
        self.name = "Полиция (Отдел трафика)"
        self.alerts_count = 0

    def update(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        if sensor_type != "traffic":
            return  # Полиция интересует только трафик
        
        self.alerts_count += 1
        print(f"\n🚔 {self.name} получила тревогу!")
        print(f"   ⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   📍 Датчик: {sensor_id}")
        print(f"   📊 Загруженность: {value:.1f}% (порог: {threshold:.1f}%)")
        print(f"   🚨 Направляем дополнительные посты на перекресток!")

    def get_name(self) -> str:
        return self.name


class EnvironmentalService(AlertSubscriber):
    """Экологическая служба. Реагирует на загрязнение воздуха."""

    def __init__(self):
        self.name = "Экологическая инспекция"
        self.alerts_count = 0

    def update(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        if sensor_type != "air_quality":
            return  # Экологов интересует только качество воздуха
        
        self.alerts_count += 1
        print(f"\n♻️  {self.name} получила тревогу!")
        print(f"   ⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   📍 Датчик: {sensor_id}")
        print(f"   📊 Уровень CO2: {value:.0f} ppm (норма: {threshold:.0f} ppm)")
        print(f"   🌍 Начинаем мониторинг и ищем источник загрязнения!")

    def get_name(self) -> str:
        return self.name


class CityCouncil(AlertSubscriber):
    """Городской совет. Получает все уведомления для отчетности."""

    def __init__(self):
        self.name = "Городской совет (Архив)"
        self.alerts_count = 0
        self.all_alerts = []

    def update(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        self.alerts_count += 1
        alert_info = {
            "timestamp": datetime.now().isoformat(),
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "value": value,
            "threshold": threshold,
        }
        self.all_alerts.append(alert_info)
        
        print(f"\n📋 {self.name} зафиксировала событие #{self.alerts_count}")
        print(f"   ⏰ Время: {alert_info['timestamp']}")
        print(f"   📍 Датчик: {sensor_id} ({sensor_type})")

    def get_name(self) -> str:
        return self.name

    def get_report(self) -> str:
        """Получить отчет по всем тревогам."""
        if not self.all_alerts:
            return "Тревог не было"
        
        report = f"📊 Отчет {self.name}: {len(self.all_alerts)} тревог\n"
        for i, alert in enumerate(self.all_alerts, 1):
            report += (
                f"  {i}. {alert['timestamp']} - {alert['sensor_id']} "
                f"({alert['sensor_type']}) = {alert['value']:.2f}\n"
            )
        return report


class ControlCenter:
    """
    Центр управления (Control Center).
    Это издатель (Publisher) в паттерне Observer.
    Управляет подписчиками и уведомляет их об аномалиях.
    """

    def __init__(self):
        self._subscribers: List[AlertSubscriber] = []
        self.total_alerts = 0

    def subscribe(self, subscriber: AlertSubscriber):
        """Зарегистрировать подписчика (службу)."""
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
            print(f"✅ {subscriber.get_name()} подписалась на уведомления")

    def unsubscribe(self, subscriber: AlertSubscriber):
        """Отписать подписчика."""
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)
            print(f"❌ {subscriber.get_name()} отписалась от уведомлений")

    def notify_subscribers(self, sensor_id: str, sensor_type: str, value: float, threshold: float):
        """Уведомить всех подписчиков об аномалии."""
        self.total_alerts += 1
        print(f"\n🔔 ЦЕНТР УПРАВЛЕНИЯ: Обнаружена аномалия #{self.total_alerts}!")
        
        for subscriber in self._subscribers:
            subscriber.update(sensor_id, sensor_type, value, threshold)

    def get_subscribers_info(self) -> str:
        """Получить информацию о зарегистрированных подписчиках."""
        info = f"📱 Зарегистрировано подписчиков: {len(self._subscribers)}\n"
        for sub in self._subscribers:
            info += f"   - {sub.get_name()}\n"
        return info

    def get_statistics(self) -> str:
        """Получить статистику по тревогам."""
        stats = "📈 Статистика тревог:\n"
        stats += f"   Всего тревог обработано: {self.total_alerts}\n"
        for subscriber in self._subscribers:
            stats += f"   - {subscriber.get_name()}: {subscriber.alerts_count} тревог\n"
        return stats


# Глобальный центр управления
_control_center = None


def get_control_center() -> ControlCenter:
    """Получить глобальный Центр управления (Singleton)."""
    global _control_center
    if _control_center is None:
        _control_center = ControlCenter()
    return _control_center
