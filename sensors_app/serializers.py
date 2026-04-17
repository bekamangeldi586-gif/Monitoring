"""
Serializers for Django REST Framework
"""

from rest_framework import serializers
from .models import SensorType, Sensor, Reading, Alert, AnalysisStrategy, SimulationConfig


class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = ['id', 'name', 'code', 'unit', 'min_value', 'max_value', 'description']


class AnalysisStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisStrategy
        fields = ['id', 'strategy_type', 'moving_avg_window', 'is_active']


class SimulationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationConfig
        fields = [
            'id', 'is_simulating', 'simulation_interval',
            'simulation_min', 'simulation_max', 'noise_level', 'last_simulated'
        ]


class ReadingSerializer(serializers.ModelSerializer):
    unit = serializers.CharField(source='sensor.sensor_type.unit', read_only=True)

    class Meta:
        model = Reading
        fields = ['id', 'sensor', 'value', 'unit', 'is_alert', 'is_critical', 'timestamp', 'notes']
        read_only_fields = ['timestamp']


class SensorDetailSerializer(serializers.ModelSerializer):
    sensor_type = SensorTypeSerializer(read_only=True)
    analysis_strategy = AnalysisStrategySerializer(read_only=True)
    simulation_config = SimulationConfigSerializer(read_only=True)
    recent_readings = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Sensor
        fields = [
            'id', 'sensor_id', 'name', 'sensor_type', 'location',
            'latitude', 'longitude', 'status', 'status_display',
            'is_active', 'threshold_critical', 'threshold_warning',
            'last_reading_value', 'last_reading_time',
            'analysis_strategy', 'simulation_config',
            'recent_readings', 'created_at', 'updated_at'
        ]

    def get_recent_readings(self, obj):
        """Получить последние 10 показаний"""
        recent = obj.readings.order_by('-timestamp')[:10]
        return ReadingSerializer(recent, many=True).data


class SensorListSerializer(serializers.ModelSerializer):
    sensor_type_name = serializers.CharField(source='sensor_type.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Sensor
        fields = [
            'id', 'sensor_id', 'name', 'sensor_type', 'sensor_type_name',
            'location', 'status', 'status_display', 'is_active',
            'last_reading_value', 'last_reading_time'
        ]


class AlertSerializer(serializers.ModelSerializer):
    sensor_id = serializers.CharField(source='sensor.sensor_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'sensor', 'sensor_id', 'value', 'threshold',
            'status', 'status_display', 'description',
            'created_at', 'acknowledged_at', 'resolved_at'
        ]
