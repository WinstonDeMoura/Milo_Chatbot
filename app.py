from fastapi import FastAPI, Request


app = FastAPI()

@app.post('/webhook')
async def webhook(resquest: Request):
  data = await resquest.json()
  print(data)
  return {'status':'ok'}