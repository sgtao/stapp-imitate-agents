# message_controller.py
import json
import os

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from functions.AppLogger import AppLogger
from functions.ChatService import ChatService
from functions.utils.read_yaml_file import read_yaml_file

APP_NAME = "api_server"
router = APIRouter(tags=["Messages"])


def get_apikey():
    # API-KEYの確認
    if os.getenv("API_KEY"):
        return os.getenv("API_KEY")
    else:
        return ""


async def process_message_request(request: Request):
    api_logger = AppLogger(f"{APP_NAME}(process_llm_rqeuests):")
    # --- 1. リクエストと設定読み込み ---

    try:
        body_data = await request.json()
        # api_logger.debug_log(f"request body: {body_data}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    try:
        config_file_path = body_data.get("config_file")
        if not config_file_path:
            raise HTTPException(
                status_code=400, detail="Missing 'config_file'"
            )
        config_data = read_yaml_file(config_file_path)
        config_data["api_key"] = get_apikey()
        action_configs = config_data.get("action_state", [])

        session_state = {}
        num_user_inputs = body_data.get("num_user_inputs", 0)
        user_inputs = body_data.get("user_inputs", {})
        session_state["num_inputs"] = num_user_inputs
        for i in range(num_user_inputs):
            session_state[f"user_input_{i}"] = user_inputs.get(
                f"user_input_{i}", ""
            )

        messages = body_data.get("messages")

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
        chat_service = ChatService()
        # send message:
        response = chat_service.post_messages_with_configs(
            session_state=session_state,
            messages=messages,
            action_configs=action_configs,
        )

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
