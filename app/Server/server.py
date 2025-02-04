from fastapi import FastAPI, WebSocket, HTTPException, Request, WebSocketDisconnect, Query
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Dict
import asyncio
import time
import json
import jwt

from Server.db_wrapper import (
    init_db,
    get_user_hashed_password,
    verify_password,
    log_user_action,
    log_data_change,
    get_document_data,
    update_document_data,
)
from Server.helper import (
    JWT_SECRET_KEY,
    ALGORITHM,
    TOKEN_EXPIRATION,
    DOCUMENT_ID,

    send_login_redirect_response_to_websocket,
)

db_lock = asyncio.Lock()

# { username: set[WebSocket] }
sessions: Dict[str, set[WebSocket]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="UI"), name="static")

@app.get("/")
def root():
    return RedirectResponse("/login")

@app.get("/login")
def get_login_page(request: Request):
    response = FileResponse("UI/login.html")
    if request.cookies.get("jwt"):
        response.delete_cookie("jwt")
    return response

@app.get("/edit_document")
def get_edit_page(request: Request):
    token = request.cookies.get("jwt")
    if not token:
        return RedirectResponse("/login")

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            return RedirectResponse("/login")
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return RedirectResponse("/login")

    return FileResponse("UI/edit_document.html")

@app.post("/login")
def login_user(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing username or password")

    hashed_pw = get_user_hashed_password(username)
    if not hashed_pw or not verify_password(password, hashed_pw):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    log_user_action(username, "login")

    exp_time = int(time.time() + TOKEN_EXPIRATION)
    payload = {"sub": username, "exp": exp_time}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

    response = JSONResponse({"message": "Login successful", "token": token})
    response.set_cookie(
        key="jwt",
        value=token,
        httponly=True,
        samesite="Strict",
        max_age=TOKEN_EXPIRATION
    )
    return response

@app.websocket("/edit_document")
async def edit_document(websocket: WebSocket, token: str = Query(None)):
    if not token:
        await send_login_redirect_response_to_websocket(websocket)
        return

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            await send_login_redirect_response_to_websocket(websocket)
            return
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        await send_login_redirect_response_to_websocket(websocket)
        return

    await websocket.accept()

    document_text = get_document_data(DOCUMENT_ID) or ""
    await websocket.send_text(document_text)

    if username not in sessions:
        sessions[username] = set()
    sessions[username].add(websocket)

    try:
        while True:
            msg = await websocket.receive()

            if "text" in msg:
                try:
                    data = json.loads(msg["text"])
                except:
                    continue
            else:
                continue

            document_text = data.get("text", document_text)
            typed_char = data.get("char", "")
            row = data.get("row", 0)
            col = data.get("col", 0)

            async with db_lock:
                update_document_data(document_text, username, DOCUMENT_ID)
                log_data_change(username, typed_char, row, col, DOCUMENT_ID)

            for user, websocket_set in sessions.items():
                for ws in websocket_set:
                    if ws is not websocket:
                        await ws.send_text(document_text)

    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.send_text("REDIRECT:/login")
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
        if websocket in sessions[username]:
            sessions[username].remove(websocket)
        if sessions[username] == set():
            sessions.pop(username, None)
