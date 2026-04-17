"""
Models for sensors_app.
Модели для управления датчиками и их показаниями.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class SensorType(models.Model):
    """Тип датчика (Температура, CO2, Трафик и т.д.)"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    code = models.CharField(max_length=20, unique=True, verbose_name="Код")
    unit = models.CharField(max_length=50, verbose_name="Единица измерения")
    min_value = models.FloatField(verbose_name="Минимальное значение", default=0)
    max_value = models.FloatField(verbose_name="Максимальное значение", default=100)
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Тип датчика"
        verbose_name_plural = "Типы датчиков"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Sensor(models.Model):
    """Датчик в городской сети мониторинга"""
    
    SENSOR_STATUS_CHOICES = [
        ('active', '🟢 Активен'),
        ('inactive', '🔴 Неактивен'),
        ('error', '⚠️ Ошибка'),
        ('maintenance', '🔧 Техническое обслуживание'),
    ]

    sensor_type = models.ForeignKey(
        SensorType,
        on_delete=models.PROTECT,
        verbose_name="Тип датчика"
    )
    sensor_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID датчика (TEMP_01, AIR_02 и т.д.)"
    )
    name = models.CharField(max_length=200, verbose_name="Название датчика")
    location = models.CharField(max_length=255, verbose_name="Местоположение")
    latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name="Широта"
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name="Долгота"
    )
    status = models.CharField(
        max_length=20,
        choices=SENSOR_STATUS_CHOICES,
        default='active',
        verbose_name="Статус"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    threshold_critical = models.FloatField(
        verbose_name="Критический порог",
        help_text="Значение при котором срабатывает тревога"
    )
    threshold_warning = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Пороговое значение предупреждения"
    )
    last_reading_value = models.FloatField(null=True, blank=True, verbose_name="Последнее показание")
    last_reading_time = models.DateTimeField(null=True, blank=True, verbose_name="Время последнего показания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Датчик"
        verbose_name_plural = "Датчики"
        ordering = ['-is_active', 'sensor_id']
        indexes = [
            models.Index(fields=['sensor_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.sensor_id} - {self.name}"

    def get_status_display_emoji(self):
        """Получить статус с эмодзи"""
        return dict(self.SENSOR_STATUS_CHOICES).get(self.status, self.status)

    def get_last_readings(self, count=10):
        """Получить последние N показаний"""
        return self.readings.order_by('-timestamp')[:count]


class Reading(models.Model):
    """Показание датчика"""
    
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='readings',
        verbose_name="Датчик"
    )
    value = models.FloatField(verbose_name="Значение")
    is_critical = models.BooleanField(default=False, verbose_name="Критическое")
    is_alert = models.BooleanField(
        default=False,
        verbose_name="Тревога",
        help_text="True если значение выше порога критичности"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время измерения"
    )
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Показание"
        verbose_name_plural = "Показания"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
            models.Index(fields=['is_alert', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.sensor.sensor_id}: {self.value} {self.sensor.sensor_type.unit} ({self.timestamp})"

    def save(self, *args, **kwargs):
        """Переопределение сохранения для проверки тревог"""
        # Проверить если значение критическое
        if self.sensor:
            self.is_critical = self.value > self.sensor.threshold_critical
            self.is_alert = self.is_critical
            
            # Обновить последнее показание датчика
            self.sensor.last_reading_value = self.value
            self.sensor.last_reading_time = self.timestamp
            self.sensor.save(update_fields=['last_reading_value', 'last_reading_time'])
        
        super().save(*args, **kwargs)


class Alert(models.Model):
    """Тревога (когда датчик срабатывает)"""
    
    ALERT_STATUS_CHOICES = [
        ('new', '🆕 Новая'),
        ('acknowledged', '✅ Принята'),
        ('resolved', '✔️ Разрешена'),
        ('false_alarm', '❌ Ложная тревога'),
    ]

    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name="Датчик"
    )
    reading = models.ForeignKey(
        Reading,
        on_delete=models.CASCADE,
        verbose_name="Показание"
    )
    value = models.FloatField(verbose_name="Значение при срабатывании")
    threshold = models.FloatField(verbose_name="Превышенный порог")
    status = models.CharField(
        max_length=20,
        choices=ALERT_STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="Принята")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Разрешена")

    class Meta:
        verbose_name = "Тревога"
        verbose_name_plural = "Тревоги"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['sensor', '-created_at']),
        ]

    def __str__(self):
        return f"Тревога {self.sensor.sensor_id}: {self.value} > {self.threshold}"


class AnalysisStrategy(models.Model):
    """Стратегия анализа для датчика"""
    
    STRATEGY_TYPES = [
        ('simple', 'Простая (Simple)'),
        ('moving_avg', 'Скользящее среднее (Moving Average)'),
        ('trend', 'Анализ тренда (Trend)'),
        ('adaptive', 'Адаптивная (Adaptive)'),
    ]

    sensor = models.OneToOneField(
        Sensor,
        on_delete=models.CASCADE,
        related_name='analysis_strategy',
        verbose_name="Датчик"
    )
    strategy_type = models.CharField(
        max_length=20,
        choices=STRATEGY_TYPES,
        default='simple',
        verbose_name="Тип стратегии"
    )
    moving_avg_window = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Окно скользящего среднего"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Стратегия анализа"
        verbose_name_plural = "Стратегии анализа"

    def __str__(self):
        return f"{self.sensor.sensor_id}: {self.get_strategy_type_display()}"


class SimulationConfig(models.Model):
    """Конфигурация имитации показаний"""
    
    sensor = models.OneToOneField(
        Sensor,
        on_delete=models.CASCADE,
        related_name='simulation_config',
        verbose_name="Датчик"
    )
    is_simulating = models.BooleanField(
        default=False,
        verbose_name="Имитировать показания"
    )
    simulation_interval = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(3600)],
        verbose_name="Интервал имитации (секунды)"
    )
    simulation_min = models.FloatField(
        verbose_name="Минимальное значение при имитации"
    )
    simulation_max = models.FloatField(
        verbose_name="Максимальное значение при имитации"
    )
    noise_level = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Уровень шума (%)"
    )
    last_simulated = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последняя имитация"
    )

    class Meta:
        verbose_name = "Конфигурация имитации"
        verbose_name_plural = "Конфигурации имитации"

    def __str__(self):
        return f"Имитация {self.sensor.sensor_id}"
