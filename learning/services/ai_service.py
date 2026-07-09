import os
from openai import AsyncOpenAI
from decouple import config

# Inicializamos el cliente de forma asíncrona usando la clave del .env
client = AsyncOpenAI(api_key=config('OPENAI_API_KEY'))

async def get_ai_response(user_message: str) -> str:
    """
    Envía el mensaje del usuario a la API de OpenAI y retorna la respuesta generada.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres el Tutor IA de JumpUp. Tu objetivo es ayudar al estudiante a practicar "
                        "y aprender idiomas de manera amigable, interactiva y gamificada. "
                        "Corrige los errores con amabilidad y sugiere mejoras. Sé conciso y directo."
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Lo siento, hubo un problema al procesar tu mensaje. Intenta de nuevo más tarde. (Error: {str(e)})"
