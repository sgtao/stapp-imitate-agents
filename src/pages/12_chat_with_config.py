# 12_chat_with_config.py
# import time

import streamlit as st

from components.ApiClient import ApiClient
from components.ChatMessage import ChatMessage
from components.ClientController import ClientController
from components.ConfigFiles import ConfigFiles
from components.ResponseViewer import ResponseViewer
from components.SideMenus import SideMenus

# from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Chat with Config"


def initial_session_state():
    # セッション状態の初期化
    if "use_sys_prompt" not in st.session_state:
        st.session_state.use_sys_prompt = False


def post_messages_with_config(
    uri="http://localhost:3000/api/v0/messages",
    messages=[],
):
    # time.sleep(3)
    # response_messaeg = {"role": "assistant", "content": "Hello again!"}
    # if len(messages) > 0:
    #     return messages[-1]
    # else:
    #     return response_messaeg
    # APIリクエスト送信
    api_client = ApiClient()
    client_controller = ClientController()
    response_viewer = ResponseViewer()
    action_config = client_controller.get_action_config()
    # client_controller.prepare_api_request(action_config)
    action_config = client_controller.replace_action_config(action_config)

    response = api_client.post_msg_with_action_config(
        action_config=action_config,
        messages=messages,
    )

    api_response = response_viewer.extract_response_value(response)
    # print(f"api_response: {api_response}")
    return api_response


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
        client_controller.set_action_config(config, 0)
        chat_message.reset()

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
                assistant_response = post_messages_with_config(
                    messages=chat_message.get_messages(),
                )
                # st.markdown(
                #     # assistant_response.get("results"),
                #     assistant_response.json().get("results"),
                # )

                chat_message.add(
                    # role=assistant_response.get("role"),
                    role="assistant",
                    # content=assistant_response.get("results"),
                    # content=assistant_response.json().get("results"),
                    content=assistant_response,
                )
                st.rerun()


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
