# 12_chat_with_config.py
import time

import streamlit as st

# from components.ApiRequestInputs import ApiRequestInputs
# from components.ResponseViewer import ResponseViewer
from components.ChatMessage import ChatMessage
from components.ClientController import ClientController
from components.ConfigFiles import ConfigFiles
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
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"💬 {APP_TITLE}")
    # インスタンス化
    chat_message = ChatMessage()
    client_controller = ClientController()
    config_files = ConfigFiles()

    # assets/privatesフォルダからyamlファイルを選択
    if not config_files:
        st.warning(
            "No YAML config files in assets and private. Please add some."
        )
        return

    selected_config_file = config_files.render_config_selector()

    # 選択されたコンフィグファイルを読み込む
    if st.button("Load Config."):
        config = config_files.load_config_from_yaml(selected_config_file)
        config_files.render_config_viewer(selected_config_file, config)
        client_controller.set_action_state(config)

    # Chat with Config
    chat_message.display_chat_history()

    # ユーザー入力
    if prompt := st.chat_input("メッセージを入力してください:"):
        # # 最初のメッセージは`system_prompt`を付与する
        # chat_message.append_system_prompts()

        chat_message.add(role="user", content=prompt)

        # アシスタントの応答
        with st.chat_message("assistant"):
            with st.spinner("考え中..."):
                action_state = client_controller.get_action_state()
                client_controller.prepare_api_request(action_state)
                assistant_response = post_messages_with_config(
                    # messages=st.session_state.messages,
                    messages=chat_message.get_messages(),
                )
                st.markdown(assistant_response.get("content"),)

                # chat_message.add(role="assistant", content=assistant_response)
                chat_message.add(
                    # role=assistant_response.get("role"),
                    role="assistant",
                    content=assistant_response.get("content"),
                )
                st.rerun()


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
