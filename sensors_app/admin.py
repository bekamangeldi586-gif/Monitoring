"""
Admin panel configuration for sensors_app
"""

from django.contrib import admin
from .models import SensorType, Sensor, Reading, Alert, AnalysisStrategy, SimulationConfig


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'unit', 'min_value', 'max_value', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'code', 'unit', 'description')
        }),
        ('Диапазон значений', {
            'fields': ('min_value', 'max_value')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['sensor_id', 'name', 'sensor_type', 'location', 'status', 'get_status_emoji', 'last_reading_value', 'is_active']
    list_filter = ['status', 'is_active', 'sensor_type', 'created_at']
    search_fields = ['sensor_id', 'name', 'location']
    readonly_fields = ['created_at', 'updated_at', 'last_reading_time']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('sensor_id', 'name', 'sensor_type', 'location')
        }),
        ('Геолокация', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Пороги срабатывания', {
            'fields': ('threshold_critical', 'threshold_warning')
        }),
        ('Статус и последние показания', {
            'fields': ('status', 'is_active', 'last_reading_value', 'last_reading_time')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_status_emoji(self, obj):
        """Вывести статус с эмодзи"""
        return obj.get_status_display_emoji()
    get_status_emoji.short_description = 'Статус'


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'value', 'get_unit', 'is_alert', 'timestamp']
    list_filter = ['is_alert', 'sensor', 'timestamp']
    search_fields = ['sensor__sensor_id', 'sensor__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def get_unit(self, obj):
        """Получить единицу измерения"""
        return obj.sensor.sensor_type.unit
    get_unit.short_description = 'Единица'

    def has_add_permission(self, request):
        """Показания добавляются автоматически"""
        return False


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'value', 'status', 'created_at', 'get_status_badge']
    list_filter = ['status', 'created_at', 'sensor']
    search_fields = ['sensor__sensor_id', 'sensor__name', 'description']
    readonly_fields = ['created_at', 'acknowledged_at', 'resolved_at', 'sensor', 'reading', 'value', 'threshold']
    
    fieldsets = (
        ('Информация о тревоге', {
            'fields': ('sensor', 'reading', 'value', 'threshold', 'status', 'description')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'acknowledged_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )

    def get_status_badge(self, obj):
        """Получить статус с цветом"""
        colors = {
            'new': '🔴',
            'acknowledged': '🟡',
            'resolved': '🟢',
            'false_alarm': '⚪',
        }
        return f"{colors.get(obj.status, '')} {obj.get_status_display()}"
    get_status_badge.short_description = 'Статус'

    actions = ['mark_acknowledged', 'mark_resolved']

    def mark_acknowledged(self, request, queryset):
        """Действие: Принять тревогу"""
        from django.utils import timezone
        queryset.filter(status='new').update(status='acknowledged', acknowledged_at=timezone.now())
    mark_acknowledged.short_description = "✅ Принять выбранные тревоги"

    def mark_resolved(self, request, queryset):
        """Действие: Разрешить тревогу"""
        from django.utils import timezone
        queryset.update(status='resolved', resolved_at=timezone.now())
    mark_resolved.short_description = "✔️ Разрешить выбранные тревоги"


@admin.register(AnalysisStrategy)
class AnalysisStrategyAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'strategy_type', 'is_active', 'updated_at']
    list_filter = ['strategy_type', 'is_active']
    search_fields = ['sensor__sensor_id', 'sensor__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Стратегия анализа', {
            'fields': ('sensor', 'strategy_type', 'is_active')
        }),
        ('Параметры', {
            'fields': ('moving_avg_window',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SimulationConfig)
class SimulationConfigAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'is_simulating', 'simulation_interval', 'last_simulated']
    list_filter = ['is_simulating', 'simulation_interval']
    search_fields = ['sensor__sensor_id', 'sensor__name']
    readonly_fields = ['last_simulated']
    
    fieldsets = (
        ('Датчик', {
            'fields': ('sensor',)
        }),
        ('Конфигурация имитации', {
            'fields': ('is_simulating', 'simulation_interval')
        }),
        ('Диапазон значений', {
            'fields': ('simulation_min', 'simulation_max', 'noise_level')
        }),
        ('История', {
            'fields': ('last_simulated',),
            'classes': ('collapse',)
        }),
    )

    actions = ['enable_simulation', 'disable_simulation']

    def enable_simulation(self, request, queryset):
        """Включить имитацию"""
        queryset.update(is_simulating=True)
    enable_simulation.short_description = "▶️ Включить имитацию"

    def disable_simulation(self, request, queryset):
        """Отключить имитацию"""
        queryset.update(is_simulating=False)
    disable_simulation.short_description = "⏹️ Отключить имитацию"


# Настройки админ-панели
admin.site.site_header = "🏙️ Smart City Monitoring - Админ-панель"
admin.site.site_title = "Мониторинг города"
admin.site.index_title = "Добро пожаловать в систему мониторинга"
