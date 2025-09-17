import streamlit as st

"""
## Welcome to imitate agents  App.
- implemented with [Streamlit](https://docs.streamlit.io/).

"""

# サイドバーのページに移動
st.page_link(
    "pages/11_config_api_client.py",
    label="Go to API Client App (for create Config.)",
    icon="🧪",
)
st.page_link(
    "pages/12_chat_with_config.py",
    label="Go to Chat with Config App",
    icon="💬",
)
st.page_link("pages/21_logs_viewer.py", label="Go to Log Vieewr", icon="🗒️")
