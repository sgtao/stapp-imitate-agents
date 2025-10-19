# ApiClientCore.py
# logic/ApiClientCore.py
import requests

from components.ApiClient import ApiClient
from functions.AppLogger import AppLogger
from functions.ApiRequestor import ApiRequestor

APP_TITLE = "ApiClientCore"


class ApiClientCore:
    def __init__(self, logger: AppLogger = None):
        self.logger = logger or AppLogger(APP_TITLE)
        self.api_client_comp = ApiClient()

    def post(self, uri, headers=None, json_body=None):
        self.logger.api_start_log(uri, "POST", headers, json_body)
        response = requests.post(uri, headers=headers, json=json_body)
        self.logger.api_success_log(response)
        return response

    def post_msgs_with_config(self, config, messages=[]):
        """
        APIサーバーへ`config`のPOSTリクエストを発行します
        - 内部は、ApiRequestor.send_api_request を呼び出すラッパー
        """
        # st.session_state.api_response = None
        # print(f"config: {config}")
        uri = config.get("uri", "")
        num_inputs = config.get("num_inputs", 0)
        config_file = config.get("config_file", "")
        user_inputs = {}

        for i in range(num_inputs):
            user_key = f"user_input_{i}"
            if user_key in config:
                user_inputs[user_key] = config.get(user_key, "")
            else:
                self.api_client_comp.show_warning_ui(
                    f"Session state key '{user_key}' not found."
                )

        try:
            api_requestor = ApiRequestor()
            response = api_requestor.send_api_request(
                uri=uri,
                method="POST",
                config_file=config_file,
                num_inputs=num_inputs,
                user_inputs=user_inputs,
                messages=messages,
            )
            # if success, set parameters to session_state for save YAML
            self.api_client_comp.show_success_ui(
                "Successfully connected to API Server.",
                uri=uri,
                response=response,
            )
            self.logger.info_log(f"Request Success of {config_file}.")
            return response
        except Exception as e:
            self.logger.error_log(f"Error occur: {e}")
            raise e
