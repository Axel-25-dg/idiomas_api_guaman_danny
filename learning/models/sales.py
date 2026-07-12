from django.db import models
from django.conf import settings
from django.utils import timezone
from .course import Course

PRODUCT_TYPE_CHOICES = [
    ('curso', 'Curso'),
    ('libro', 'Libro'),
]

ORDER_STATUS_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('pagada', 'Pagada'),
    ('cancelada', 'Cancelada'),
]

class Catalogo(models.Model):
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='curso')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    contenido_url = models.URLField(max_length=500, blank=True, null=True)
    curso = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    creado_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()}) - ${self.precio}"

class Carrito(models.Model):
    estudiante = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrito')
    creado_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.estudiante.email}"

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Catalogo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.titulo} en {self.carrito}"

class Orden(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordenes_compras')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Orden #{self.id} - {self.estudiante.email} - Status: {self.estado}"

class OrdenDetalle(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Catalogo, on_delete=models.PROTECT)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle Orden #{self.orden.id} - {self.producto.titulo}"
