from fastapi import FastAPI, Request

from config import IGNORED_NUMBERS

app = FastAPI()

@app.get('/health')
async def health():
  return {'status': 'ok', 'message': 'FastAPI is running'}

@app.post('/webhook')
async def webhook(resquest: Request):
  # Import lazy loading to avoid loading embeddings at startup
  from message_buffer import buffer_message
  
  data = await resquest.json()
  chat_id = data.get('data').get('key').get('remoteJid')
  message = data.get('data').get('message').get('conversation')
  
  is_group = '@g.us' in chat_id if chat_id else False
  clean_chat_id = chat_id.replace('@s.whatsapp.net', '') if chat_id else ''
  is_ignored = clean_chat_id in IGNORED_NUMBERS
  
  if chat_id and message and not is_group and not is_ignored:
    await buffer_message(
      chat_id=chat_id,
      message=message
    )

  
  return {'status':'ok'}