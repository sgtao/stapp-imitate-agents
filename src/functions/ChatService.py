# ChatService.py
import json

from components.ApiClient import ApiClient

from functions.ApiClientCore import ApiClientCore
from functions.AppLogger import AppLogger
from functions.ClientConfigManager import ClientConfigManager
from functions.ResponseOperator import ResponseOperator

APP_TITLE = "ChatService"


class ChatService:
    """
    ChatService クラスは、設定情報・セッション状態・メッセージ群をもとに
    一連の API リクエストやレスポンス抽出を順次実行する統括サービスです。

    各アクションの種類（"request" または "extract"）に応じて
    適切な処理を行い、結果を蓄積・ログ出力・UI表示します。
    """

    def __init__(self):
        self.app_logger = AppLogger(APP_TITLE)
        # instanciation using functions
        self.config_mgr = ClientConfigManager()
        self.client = ApiClientCore(self.app_logger)
        self.response_op = ResponseOperator()
        self.api_client_comp = ApiClient()

    def post_messages_with_configs(
        self,
        messages,
        session_state,
        action_configs,
    ):
        """
        複数のアクション設定を順に処理し、APIリクエストまたはデータ抽出を実行します。

        各アクション設定 (`action_configs`) の "type" に応じて以下を行います:
            - "request": 設定に基づいてAPIをPOSTし、レスポンスを解析。
            - "extract": JSON文字列から指定パスの値を抽出。

        Parameters
        ----------
        messages : list
            送信するメッセージ群（リクエスト本文に相当）。
        session_state : dict
            セッション中の状態情報（動的置換に利用）。
        action_configs : list[dict]
            各アクションの設定情報。type, uri, config_fileなどを含む。

        Returns
        -------
        Any
            最終アクションの結果（成功・抽出結果・または None）。

        Raises
        ------
        Exception
            各アクションの実行中に発生した例外（ログ出力と警告UIを伴う）。
        """
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
                    config_file = action_config.get("config_file", "")
                    uri = action_config.get("uri")

                    response = self.client.post_msgs_with_config(
                        config=action_config,
                        messages=messages,
                    )
                    result = self.response_op.extract_response_value(
                        response,
                        path=action_config.get("user_property_path", "."),
                    )

                    self.api_client_comp.show_success_ui(
                        f"Success Request of {config_file} is {result}.",
                        uri=uri,
                        response=response,
                    )

                except Exception:
                    result = response.json()
                    self.api_client_comp.show_warning_ui(
                        f"Exception occured at {config_file}"
                    )
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
                    self.api_client_comp.show_success_ui(
                        f"Success to extract is {result}.",
                    )
                except Exception:
                    result = _target_text
                    self.api_client_comp.show_warning_ui(
                        f"Exception occured at extract, so set {result}"
                    )

            else:
                result = "Nothing!"

            results.append(result)
            self.app_logger.info_log(f"Action result_{index}: {result}")

        # return results[-1] if results else None
        return results
