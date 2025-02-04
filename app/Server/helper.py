from fastapi import WebSocket

JWT_SECRET_KEY = "568bf61dd84faf3f142fe20fcbb6bb281f5bb3e9e2a8fc05df4e842adf87da1d"
ALGORITHM = "HS256"
TOKEN_EXPIRATION = 3600
DOCUMENT_ID = 1

async def send_login_redirect_response_to_websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("REDIRECT:/login")
    await websocket.close()
