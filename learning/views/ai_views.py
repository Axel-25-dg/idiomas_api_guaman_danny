from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import serializers
from learning.services.ai_service import get_ai_response


class TestAISerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000, required=True)


class TestAIView(generics.CreateAPIView):
    """
    Endpoint de prueba para Tutor IA (REST).
    Envía un mensaje y recibe la respuesta de GPT-4o.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TestAISerializer

    async def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data['message']
        
        try:
            ai_response = await get_ai_response(user_message)
            return Response({
                'success': True,
                'user_message': user_message,
                'ai_response': ai_response,
            })
        except Exception as e:
            return Response({
                'success': False,
                'detail': f'Error al procesar la IA: {str(e)}'
            }, status=500)
