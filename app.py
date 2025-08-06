from fastapi import FastAPI, Request

from evolution_api import send_whatsapp_message


app = FastAPI()

@app.post('/webhook')
async def webhook(resquest: Request):
  data = await resquest.json()
  chat_id = data.get('data').get('key').get('remoteJid')
  message = data.get('data').get('message').get('conversation')
  
  if chat_id and message and not '@g.us' in chat_id:
    send_whatsapp_message(
      number=chat_id,
      text='Opa! Recebi!'
    )
  
  return {'status':'ok'}