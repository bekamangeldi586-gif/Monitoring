"""
Django app configuration for sensors_app
"""

from django.apps import AppConfig


class SensorsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sensors_app'
    verbose_name = '🏙️ Система мониторинга датчиков'
