# message_controller.py
import json

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from functions.AppLogger import AppLogger
from functions.ChatService import ChatService

APP_NAME = "api_server"
router = APIRouter(tags=["Messages"])


async def process_message_request(request: Request):
    api_logger = AppLogger(f"{APP_NAME}(process_llm_rqeuests):")
    # --- 1. リクエストと設定読み込み ---

    try:
        body_data = await request.json()
        # api_logger.debug_log(f"request body: {body_data}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    chat_service = ChatService()

    try:
        post_data = chat_service.prepare_post_data(body_data)
        session_state = post_data["session_state"]
        messages = post_data["messages"]
        action_configs = post_data["action_configs"]

    except Exception as e:
        api_logger.error_log(f"APIリクエスト作成失敗: {e}")
        raise HTTPException(
            status_code=400, detail=f"APIリクエスト作成失敗: {e}"
        )

    if not messages:
        raise HTTPException(
            status_code=400, detail="messages not found in request body"
        )

    # --- 2. ChatServiceを使ったリクエスト ---
    try:
        # send message:
        results = chat_service.post_messages_with_configs(
            session_state=session_state,
            messages=messages,
            action_configs=action_configs,
        )
        response = results[-1] if results else None

        # 結果の返却
        return JSONResponse(content={"results": response})

    except Exception as e:
        api_logger.error_log(f"APIリクエスト失敗: {e}")
        raise HTTPException(status_code=502, detail=f"APIリクエスト失敗: {e}")


@router.post("/messages")
async def post_messages(request: Request):
    """
    messagesを含むリクエストを受け取り、
    config_file で指定したAPIを実行し、
    JSON形式で`{"results": [user_property value]}`を返します。
    """
    # --- 1. Logger setting and Instanciation ---
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    # --- 2. ChatServiceを使った変換とリクエスト ---
    try:
        return await process_message_request(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
