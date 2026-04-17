"""
Команда для инициализации базы данных с примерами
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from sensors_app.models import SensorType, Sensor, AnalysisStrategy, SimulationConfig
import random


class Command(BaseCommand):
    help = 'Initialize database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-migrations',
            action='store_true',
            help='Create migrations before initialization'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Инициализация базы данных...'))

        # Создать миграции если нужно
        if options['create_migrations']:
            self.stdout.write('📝 Создание миграций...')
            call_command('makemigrations', 'sensors_app')
            call_command('migrate')

        # Проверить миграции
        self.stdout.write('🔄 Применение миграций...')
        call_command('migrate')

        # Создать типы датчиков
        self.stdout.write('📊 Создание типов датчиков...')
        sensor_types = [
            {
                'name': 'Датчик температуры',
                'code': 'TEMP',
                'unit': '°C',
                'min_value': -30,
                'max_value': 50,
                'description': 'Измеряет температуру окружающей среды'
            },
            {
                'name': 'Датчик качества воздуха',
                'code': 'AIR',
                'unit': 'ppm',
                'min_value': 300,
                'max_value': 2000,
                'description': 'Измеряет уровень CO2 в воздухе'
            },
            {
                'name': 'Датчик трафика',
                'code': 'TRAFFIC',
                'unit': '%',
                'min_value': 0,
                'max_value': 100,
                'description': 'Измеряет загруженность дороги'
            },
            {
                'name': 'Датчик влажности',
                'code': 'HUMIDITY',
                'unit': '%',
                'min_value': 0,
                'max_value': 100,
                'description': 'Измеряет уровень влажности'
            },
        ]

        created_types = {}
        for type_data in sensor_types:
            sensor_type, created = SensorType.objects.get_or_create(
                code=type_data['code'],
                defaults=type_data
            )
            created_types[type_data['code']] = sensor_type
            status = 'создан' if created else 'уже существует'
            self.stdout.write(self.style.SUCCESS(f"✅ {type_data['name']} ({status})"))

        # Создать датчики
        self.stdout.write('🔧 Создание датчиков...')
        sensors_data = [
            {
                'sensor_id': 'TEMP_01',
                'name': 'Датчик температуры на Центральной площади',
                'type_code': 'TEMP',
                'location': 'Площадь Центральная',
                'latitude': 49.6821,
                'longitude': 84.9397,
                'threshold_critical': 45,
                'threshold_warning': 40,
                'sim_min': -30,
                'sim_max': 50
            },
            {
                'sensor_id': 'AIR_01',
                'name': 'Датчик CO2 возле ТЭЦ',
                'type_code': 'AIR',
                'location': 'ТЭЦ промышленная',
                'latitude': 49.6800,
                'longitude': 84.9400,
                'threshold_critical': 600,
                'threshold_warning': 400,
                'sim_min': 300,
                'sim_max': 2000
            },
            {
                'sensor_id': 'TRAFFIC_01',
                'name': 'Датчик трафика на главной дороге',
                'type_code': 'TRAFFIC',
                'location': 'Проспект Независимости',
                'latitude': 49.6850,
                'longitude': 84.9350,
                'threshold_critical': 90,
                'threshold_warning': 70,
                'sim_min': 0,
                'sim_max': 100
            },
            {
                'sensor_id': 'HUMIDITY_01',
                'name': 'Датчик влажности в парке',
                'type_code': 'HUMIDITY',
                'location': 'Центральный парк',
                'latitude': 49.6825,
                'longitude': 84.9425,
                'threshold_critical': 90,
                'threshold_warning': 75,
                'sim_min': 20,
                'sim_max': 100
            },
            {
                'sensor_id': 'TEMP_02',
                'name': 'Датчик температуры в школе',
                'type_code': 'TEMP',
                'location': 'Школа №1',
                'latitude': 49.6820,
                'longitude': 84.9410,
                'threshold_critical': 35,
                'threshold_warning': 30,
                'sim_min': -30,
                'sim_max': 50
            },
        ]

        for sensor_data in sensors_data:
            sensor, created = Sensor.objects.get_or_create(
                sensor_id=sensor_data['sensor_id'],
                defaults={
                    'name': sensor_data['name'],
                    'sensor_type': created_types[sensor_data['type_code']],
                    'location': sensor_data['location'],
                    'latitude': sensor_data['latitude'],
                    'longitude': sensor_data['longitude'],
                    'threshold_critical': sensor_data['threshold_critical'],
                    'threshold_warning': sensor_data['threshold_warning'],
                    'status': 'active',
                    'is_active': True
                }
            )

            if created:
                # Создать стратегию анализа
                strategy = AnalysisStrategy.objects.create(
                    sensor=sensor,
                    strategy_type='simple' if random.random() > 0.5 else 'moving_avg',
                    is_active=True
                )

                # Создать конфигурацию имитации
                SimulationConfig.objects.create(
                    sensor=sensor,
                    is_simulating=True,
                    simulation_interval=5,
                    simulation_min=sensor_data['sim_min'],
                    simulation_max=sensor_data['sim_max'],
                    noise_level=5.0
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Датчик {sensor_data['sensor_id']} создан с стратегией {strategy.get_strategy_type_display()}"
                    )
                )
            else:
                self.stdout.write(f"⏭️ Датчик {sensor_data['sensor_id']} уже существует")

        self.stdout.write(
            self.style.SUCCESS(
                '\n✨ Инициализация завершена! Откройте http://localhost:8000/admin/ для управления'
            )
        )
