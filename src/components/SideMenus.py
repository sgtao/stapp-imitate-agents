# SideMenus.py
import streamlit as st

from components.ClientController import ClientController
from components.UserInputs import UserInputs


class SideMenus:
    def __init__(self):
        # インスタンス化
        self.client_controller = ClientController()
        self.user_inputs_component = UserInputs(user_property_path="results")

    def render_api_client_menu(self):
        with st.sidebar:
            self.user_inputs_component.render_dynamic_inputs()
            self.user_inputs_component.render_property_path()
            with st.expander("session_state", expanded=False):
                st.write(st.session_state)
            self.client_controller.render_buttons()

    def set_user_property_path(self, response_path):
        # st.session_state.user_property_path = response_path
        self.user_inputs_component.set_user_property_path(response_path)
