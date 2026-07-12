from rest_framework import serializers
from learning.models import Catalogo, Carrito, CarritoItem, OrdenCompra, OrdenDetalle
from learning.serializers.course_serializer import CourseSerializer

class CatalogoSerializer(serializers.ModelSerializer):
    curso_info = CourseSerializer(source='curso', read_only=True)

    class Meta:
        model = Catalogo
        fields = ['id', 'titulo', 'tipo', 'precio', 'contenido_url', 'curso', 'curso_info', 'creado_at']

class CarritoItemSerializer(serializers.ModelSerializer):
    producto_info = CatalogoSerializer(source='producto', read_only=True)

    class Meta:
        model = CarritoItem
        fields = ['id', 'producto', 'producto_info', 'cantidad']

class CarritoSerializer(serializers.ModelSerializer):
    items = CarritoItemSerializer(many=True, read_only=True)
    estudiante_email = serializers.EmailField(source='estudiante.email', read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'estudiante_email', 'items', 'creado_at']

class OrdenDetalleSerializer(serializers.ModelSerializer):
    producto_info = CatalogoSerializer(source='producto', read_only=True)

    class Meta:
        model = OrdenDetalle
        fields = ['id', 'producto', 'producto_info', 'precio_unitario']

class OrdenCompraSerializer(serializers.ModelSerializer):
    detalles = OrdenDetalleSerializer(many=True, read_only=True)
    estudiante_email = serializers.EmailField(source='estudiante.email', read_only=True)

    class Meta:
        model = OrdenCompra
        fields = ['id', 'estudiante_email', 'total', 'estado', 'detalles', 'fecha_creacion']
