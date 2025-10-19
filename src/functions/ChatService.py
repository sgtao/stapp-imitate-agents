# ChatService.py
import json

from functions.ApiClientCore import ApiClientCore
from functions.AppLogger import AppLogger
from functions.ClientConfigManager import ClientConfigManager
from functions.ResponseOperator import ResponseOperator

APP_TITLE = "ChatService"


class ChatService:
    def __init__(self):
        self.app_logger = AppLogger(APP_TITLE)
        # instanciation using functions
        self.config_mgr = ClientConfigManager()
        self.client = ApiClientCore(self.app_logger)
        self.response_op = ResponseOperator()

    def post_messages_with_configs(
        self,
        messages,
        session_state,
        action_configs,
    ):
        results = []
        result = ""

        for index, cfg in enumerate(action_configs):
            # print(cfg)
            _type = cfg.get("type", "request")

            if _type == "request":
                try:
                    action_config = self.config_mgr.replace_action_config(
                        session_state, cfg, results
                    )
                    # print(action_config)
                    response = self.client.post_msgs_with_config(
                        config=action_config,
                        messages=messages,
                    )
                    result = self.response_op.extract_response_value(
                        response,
                        path=action_config.get("user_property_path", "."),
                    )
                except Exception:
                    result = response.json()

            elif _type == "extract":
                action_config = self.config_mgr.replace_extract_config(
                    session_state=session_state,
                    action_config=cfg,
                    results=results,
                )
                _target_text = action_config.get("target", "")
                _target_obj = json.loads(_target_text)
                try:
                    result = self.response_op.extract_property_from_json(
                        json_data=_target_obj,
                        property_path=action_config.get(
                            "user_property_path", "."
                        ),
                    )
                except Exception:
                    result = _target_text

            else:
                result = "Nothing!"

            results.append(result)
            self.app_logger.info_log(f"Action result_{index}: {result}")

        return results[-1] if results else None
