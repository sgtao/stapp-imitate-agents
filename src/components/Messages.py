# Messages.py
from datetime import datetime
import logging

import streamlit as st


class Messages:
    def __init__(self):
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def _get_timestamp(self):
        # ミリ秒単位までの現在の日時を取得
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S.%f")[:-3]
        return current_time

    def display_chat_history(self):
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def has_message(self):
        if len(st.session_state.messages) > 0:
            return True
        else:
            return False

    def available_sys_prompt(self):
        return not self.has_message()

    def add(self, role: str, content: str):
        st.session_state.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": self._get_timestamp(),
            }
        )

    def pop(self):
        st.session_state.messages[-1].pop()

    def clear_messages(self):
        st.session_state.messages = []

    def append_system_prompts(self):
        # システムプロンプト利用時、最初のチャットヒストリーで追加する
        if self.available_sys_prompt() and st.session_state.use_sys_prompt:
            self.add(role="system", content=st.session_state.system_prompt)

    def add_with_display_msg(self, role: str, content: str):
        with st.chat_message(role):
            st.markdown(content)
        self.add(role=role, content=content)

    def get_messages(self):
        messages = []
        for message in st.session_state.messages:
            messages.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )
        return messages

    def set_whole_messages(self, messages):
        _NAME = "set_whole_messages"
        logging.debug(f"[{_NAME}] Start")
        logging.debug(f"set messages is {messages}")
        st.session_state.messages = messages
