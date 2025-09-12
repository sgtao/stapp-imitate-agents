# 12_chat_with_config.py
import time

import streamlit as st

# from components.ApiRequestInputs import ApiRequestInputs
# from components.ResponseViewer import ResponseViewer
from components.Messages import Messages
from components.SideMenus import SideMenus

# from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Chat with Config"


def initial_session_state():
    # セッション状態の初期化
    if "use_sys_prompt" not in st.session_state:
        st.session_state.use_sys_prompt = False


def post_messages_with_config(messages=[]):
    time.sleep(3)
    response_messaeg = {"role": "assistant", "content": "Hello again!"}
    if len(messages) > 0:
        return messages[-1]
    else:
        return response_messaeg


def main():
    messages = Messages()

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください:"):
        # 最初のメッセージは`system_prompt`を付与する
        messages.append_system_prompts()

        messages.add_with_display_msg(role="user", content=prompt)

        # アシスタントの応答
        with st.chat_message("assistant"):
            with st.spinner("考え中..."):
                assistant_response = post_messages_with_config(
                    # messages=st.session_state.messages,
                    messages=messages.get_messages(),
                )
                st.markdown(assistant_response)

                messages.add(role="assistant", content=assistant_response)
                st.rerun()


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
