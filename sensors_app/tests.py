"""
Tests for sensors_app
"""

from django.test import TestCase
from .models import SensorType, Sensor, Reading, Alert


class SensorTypeTestCase(TestCase):
    def setUp(self):
        self.sensor_type = SensorType.objects.create(
            name='Temperature',
            code='TEMP',
            unit='°C',
            min_value=-30,
            max_value=50
        )

    def test_sensor_type_creation(self):
        self.assertEqual(self.sensor_type.name, 'Temperature')
        self.assertEqual(self.sensor_type.code, 'TEMP')


class SensorTestCase(TestCase):
    def setUp(self):
        self.sensor_type = SensorType.objects.create(
            name='Temperature',
            code='TEMP',
            unit='°C',
            min_value=-30,
            max_value=50
        )
        self.sensor = Sensor.objects.create(
            sensor_id='TEMP_01',
            name='Temperature Sensor #1',
            sensor_type=self.sensor_type,
            location='Main Street',
            threshold_critical=45
        )

    def test_sensor_creation(self):
        self.assertEqual(self.sensor.sensor_id, 'TEMP_01')
        self.assertTrue(self.sensor.is_active)
