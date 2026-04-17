"""
Views for sensors_app REST API
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import random

from .models import SensorType, Sensor, Reading, Alert, AnalysisStrategy, SimulationConfig
from .serializers import (
    SensorTypeSerializer, SensorDetailSerializer, SensorListSerializer,
    ReadingSerializer, AlertSerializer, AnalysisStrategySerializer,
    SimulationConfigSerializer
)


class SensorTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр типов датчиков"""
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class SensorViewSet(viewsets.ModelViewSet):
    """ViewSet для управления датчиками"""
    queryset = Sensor.objects.select_related('sensor_type')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_active', 'sensor_type']
    search_fields = ['sensor_id', 'name', 'location']
    ordering_fields = ['name', 'created_at', 'last_reading_time']
    ordering = ['-is_active', 'sensor_id']

    def get_serializer_class(self):
        """Выбрать нужный сериализатор"""
        if self.action == 'retrieve':
            return SensorDetailSerializer
        return SensorListSerializer

    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """Получить показания для датчика"""
        sensor = self.get_object()
        limit = request.query_params.get('limit', 50)
        
        readings = sensor.readings.order_by('-timestamp')[:int(limit)]
        serializer = ReadingSerializer(readings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Получить тревоги для датчика"""
        sensor = self.get_object()
        limit = request.query_params.get('limit', 50)
        status_filter = request.query_params.get('status')
        
        alerts = sensor.alerts.all()
        if status_filter:
            alerts = alerts.filter(status=status_filter)
        
        alerts = alerts.order_by('-created_at')[:int(limit)]
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def simulate_reading(self, request, pk=None):
        """Сгенерировать одно показание датчика"""
        sensor = self.get_object()
        
        try:
            config = sensor.simulation_config
        except SimulationConfig.DoesNotExist:
            return Response(
                {'error': 'Конфигурация имитации не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Генерировать значение
        value = random.uniform(config.simulation_min, config.simulation_max)
        
        # Добавить шум
        noise = random.uniform(-config.noise_level/100 * (config.simulation_max - config.simulation_min),
                               config.noise_level/100 * (config.simulation_max - config.simulation_min))
        value += noise
        
        # Ограничить диапазоном
        value = max(config.simulation_min, min(config.simulation_max, value))

        # Создать показание
        reading = Reading.objects.create(
            sensor=sensor,
            value=value,
            is_alert=value > sensor.threshold_critical
        )

        # Если критическое, создать тревогу
        if reading.is_alert:
            Alert.objects.create(
                sensor=sensor,
                reading=reading,
                value=value,
                threshold=sensor.threshold_critical,
                description=f"Автоматически созданная тревога: {value:.2f} > {sensor.threshold_critical}"
            )

        config.last_simulated = timezone.now()
        config.save(update_fields=['last_simulated'])

        serializer = ReadingSerializer(reading)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def generate_bulk_readings(self, request):
        """Сгенерировать показания для всех активных датчиков"""
        sensor_ids = request.data.get('sensor_ids', [])
        
        results = []
        
        if sensor_ids:
            sensors = Sensor.objects.filter(id__in=sensor_ids, is_active=True)
        else:
            sensors = Sensor.objects.filter(is_active=True)

        for sensor in sensors:
            try:
                config = sensor.simulation_config
                if not config.is_simulating:
                    continue

                # Генерировать значение
                value = random.uniform(config.simulation_min, config.simulation_max)
                
                # Добавить шум
                noise = random.uniform(-config.noise_level/100 * (config.simulation_max - config.simulation_min),
                                      config.noise_level/100 * (config.simulation_max - config.simulation_min))
                value += noise
                value = max(config.simulation_min, min(config.simulation_max, value))

                # Создать показание
                reading = Reading.objects.create(
                    sensor=sensor,
                    value=value,
                    is_alert=value > sensor.threshold_critical
                )

                # Если критическое, создать тревогу
                if reading.is_alert:
                    Alert.objects.create(
                        sensor=sensor,
                        reading=reading,
                        value=value,
                        threshold=sensor.threshold_critical
                    )

                config.last_simulated = timezone.now()
                config.save(update_fields=['last_simulated'])

                results.append({
                    'sensor_id': sensor.sensor_id,
                    'value': value,
                    'is_alert': reading.is_alert
                })
            except Exception as e:
                results.append({
                    'sensor_id': sensor.sensor_id,
                    'error': str(e)
                })

        return Response({'readings_created': results})


class ReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра показаний"""
    queryset = Reading.objects.select_related('sensor')
    serializer_class = ReadingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sensor', 'is_alert']
    ordering_fields = ['timestamp', 'value']
    ordering = ['-timestamp']

    @action(detail=False, methods=['get'])
    def recent_alerts(self, request):
        """Получить последние тревоги (за последний час)"""
        one_hour_ago = timezone.now() - timedelta(hours=1)
        readings = Reading.objects.filter(
            is_alert=True,
            timestamp__gte=one_hour_ago
        ).order_by('-timestamp')
        
        serializer = ReadingSerializer(readings, many=True)
        return Response(serializer.data)


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet для управления тревогами"""
    queryset = Alert.objects.select_related('sensor')
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sensor', 'status']
    ordering_fields = ['created_at', 'value']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Принять тревогу"""
        alert = self.get_object()
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.save()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Разрешить тревогу"""
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active_alerts(self, request):
        """Получить активные тревоги"""
        alerts = Alert.objects.filter(status__in=['new', 'acknowledged']).order_by('-created_at')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получить статистику по тревогам"""
        total = Alert.objects.count()
        new = Alert.objects.filter(status='new').count()
        acknowledged = Alert.objects.filter(status='acknowledged').count()
        resolved = Alert.objects.filter(status='resolved').count()

        return Response({
            'total': total,
            'new': new,
            'acknowledged': acknowledged,
            'resolved': resolved
        })


class DashboardView(viewsets.ViewSet):
    """ViewSet для статистики приборной панели"""

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получить общую статистику"""
        total_sensors = Sensor.objects.count()
        active_sensors = Sensor.objects.filter(is_active=True).count()
        inactive_sensors = Sensor.objects.filter(is_active=False).count()
        
        total_readings = Reading.objects.count()
        alert_readings = Reading.objects.filter(is_alert=True).count()
        
        total_alerts = Alert.objects.count()
        new_alerts = Alert.objects.filter(status='new').count()
        resolved_alerts = Alert.objects.filter(status='resolved').count()

        return Response({
            'sensors': {
                'total': total_sensors,
                'active': active_sensors,
                'inactive': inactive_sensors
            },
            'readings': {
                'total': total_readings,
                'alerts': alert_readings
            },
            'alerts': {
                'total': total_alerts,
                'new': new_alerts,
                'resolved': resolved_alerts
            }
        })

    @action(detail=False, methods=['get'])
    def sensor_status(self, request):
        """Получить статус всех датчиков"""
        sensors = Sensor.objects.all()
        data = []
        
        for sensor in sensors:
            data.append({
                'id': sensor.id,
                'sensor_id': sensor.sensor_id,
                'name': sensor.name,
                'status': sensor.status,
                'is_active': sensor.is_active,
                'last_reading_value': sensor.last_reading_value,
                'last_reading_time': sensor.last_reading_time,
                'has_critical_threshold': sensor.threshold_critical is not None
            })
        
        return Response(data)


def dashboard(request):
    """Главная страница приборной панели"""
    return render(request, 'sensors_app/dashboard.html')
