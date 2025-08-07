import asyncio
import redis.asyncio as redis

from collections import defaultdict

from config import REDIS_URL, BUFFER_KEY_SUFIX, DEBOUNCE_SECONDS, BUFFER_TTL
from evolution_api import send_whatsapp_message
from chains import get_conversational_rag_chain


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
conversational_rag_chain = get_conversational_rag_chain()
debounce_tasks = defaultdict(asyncio.Task)

def log(*args):
  print('[BUFFER]', *args)

async def buffer_message(chat_id: str,message: str):
  buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'

  await redis.rpush(buffer_key,message)
  await redis_client.expire(buffer_key, BUFFER_TTL)

  log(f'Mensagem Adicionada ao Buffer de {chat_id}: {message}')

  if debounce_tasks.get(chat_id):
    debounce_tasks[chat_id].cancel()
    log(f'Debounce Resetado Para {chat_id}')

  debounce_tasks[chat_id] = asyncio.create_task(handle_debauce(chat_id))


async def handle_debauce(chat_id: str):
  try:
    log(f'Iniciando o Debounce Para {chat_id}')
    await asyncio.sleep(DEBOUNCE_SECONDS)

    buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'
    messages = redis.client.lrang(buffer_key, 0, -1)

    full_message = ' '.join(messages).strip()

    if full_message:
      log(f'Enviando mensagem agupada para {chat_id}: {full_message}')
      ai_response = conversational_rag_chain.invoke(
        input={'input': full_message},
        config={'configurable': {'session_id': chat_id}}
      )['answer']

      send_whatsapp_message(
        number=chat_id,
        text=ai_response
      )

    await redis.client.delete(buffer_key)
  except asyncio.CancelledError:
    log(f'Debouncer cancelado para {chat_id}')