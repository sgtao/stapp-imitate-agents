# ChatService.py
import json
from components.ApiClient import ApiClient
from components.ClientController import ClientController
from components.ResponseViewer import ResponseViewer
from functions.AppLogger import AppLogger
from functions.ResponseOperator import ResponseOperator

APP_TITLE = "Chat with Config"


class ChatService:
    def __init__(self):
        self.api_client = ApiClient()
        self.client_controller = ClientController()
        self.response_viewer = ResponseViewer()
        self.app_logger = AppLogger(APP_TITLE)

    def post_messages_with_config(self, messages, action_configs):
        action_results = []

        for index, action_config in enumerate(action_configs):
            _type = action_config.get("type", "request")
            _result = ""

            if _type == "request":
                action_config = self.client_controller.replace_action_config(
                    action_config, action_results
                )
                response = self.api_client.post_msg_with_action_config(
                    action_config=action_config, messages=messages
                )
                try:
                    _result = self.response_viewer.extract_response_value(
                        response,
                        path=action_config.get("user_property_path", "."),
                    )
                except Exception:
                    _result = response.json()

            elif _type == "extract":
                _response_op = ResponseOperator()
                action_config = self.client_controller.replace_extract_config(
                    action_config, action_results
                )
                _target_text = action_config.get("target", "")
                _target_obj = json.loads(_target_text)
                try:
                    _result = _response_op.extract_property_from_json(
                        json_data=_target_obj,
                        property_path=action_config.get(
                            "user_property_path", "."
                        ),
                    )
                except Exception:
                    _result = _target_text

            else:
                _result = "Nothing!"

            action_results.append(_result)
            self.app_logger.info_log(f"Action result_{index} : {_result}")

        return action_results[-1] if action_results else None
