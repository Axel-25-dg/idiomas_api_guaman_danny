from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from learning.models import Catalogo, Carrito, CarritoItem, OrdenCompra, OrdenDetalle
from learning.serializers import (
    CatalogoSerializer, CarritoSerializer, CarritoItemSerializer, OrdenCompraSerializer
)
from learning.permissions import IsTeacherOrAdminOrReadOnly

class CatalogoViewSet(viewsets.ModelViewSet):
    queryset = Catalogo.objects.all()
    serializer_class = CatalogoSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]

class CarritoViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_carrito(self, request):
        carrito, created = Carrito.objects.get_or_create(estudiante=request.user)
        return carrito

    def list(self, request):
        carrito = self.get_carrito(request)
        serializer = CarritoSerializer(carrito, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='agregar')
    def agregar(self, request):
        producto_id = request.data.get('producto_id')
        cantidad = int(request.data.get('cantidad', 1))
        
        try:
            producto = Catalogo.objects.get(id=producto_id)
        except Catalogo.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        carrito = self.get_carrito(request)
        item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            item.cantidad += cantidad
        else:
            item.cantidad = cantidad
        item.save()

        return Response({'message': 'Producto agregado al carrito'})

    @action(detail=False, methods=['post'], url_path='eliminar')
    def eliminar(self, request):
        producto_id = request.data.get('producto_id')
        carrito = self.get_carrito(request)
        
        try:
            item = CarritoItem.objects.get(carrito=carrito, producto_id=producto_id)
            item.delete()
            return Response({'message': 'Producto eliminado del carrito'})
        except CarritoItem.DoesNotExist:
            return Response({'error': 'Item no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='comprar')
    def comprar(self, request):
        carrito = self.get_carrito(request)
        items = carrito.items.all()
        
        if not items.exists():
            return Response({'error': 'El carrito está vacío'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la orden
        total = sum(item.producto.precio * item.cantidad for item in items)
        orden = OrdenCompra.objects.create(estudiante=request.user, total=total, estado='pagada') # Auto-completado/pagado para demostración simplificada

        for item in items:
            OrdenDetalle.objects.create(
                orden=orden,
                producto=item.producto,
                precio_unitario=item.producto.precio
            )

        # Limpiar carrito
        items.delete()

        serializer = OrdenCompraSerializer(orden, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrdenCompraViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrdenCompraSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return OrdenCompra.objects.all()
        return OrdenCompra.objects.filter(estudiante=user)
