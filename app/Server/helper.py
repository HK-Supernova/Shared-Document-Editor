from cryptography.fernet import Fernet
from fastapi import WebSocket

DOCUMENT_ENCRYPTION_KEY = b'pPUT2KROK8lr1cM_D_YGLpI-wFVMyCiEGVm-EVTsC6U=' # Used `Fernet.generate_key()` to generate a key
JWT_SECRET_KEY = "568bf61dd84faf3f142fe20fcbb6bb281f5bb3e9e2a8fc05df4e842adf87da1d"
ALGORITHM = "HS256"
TOKEN_EXPIRATION = 3600
DOCUMENT_ID = 1

async def send_login_redirect_response_to_websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("REDIRECT:/login")
    await websocket.close()

def encrypt_document_data(plain_text: str):
    f = Fernet(DOCUMENT_ENCRYPTION_KEY)
    return f.encrypt(plain_text.encode('utf-8'))

def decrypt_document_data(encrypted_data: bytes):
    f = Fernet(DOCUMENT_ENCRYPTION_KEY)
    return f.decrypt(encrypted_data).decode('utf-8')
