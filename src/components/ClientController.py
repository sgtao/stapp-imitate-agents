# ClientController.py
from datetime import datetime
import urllib.parse

# import json
import time
import yaml

import streamlit as st


class ClientController:
    def __init__(self) -> None:
        if "api_running" not in st.session_state:
            st.session_state.api_running = False

    @st.dialog("Setting Info.")
    def modal(self, type):
        st.write(f"Modal for {type}:")
        if type == "save_state":
            self.save_action_state()
            self._modal_closer()
        elif type == "load_state":
            self.load_action_state()
            self._modal_closer()
        else:
            st.write("No Definition.")

    def _modal_closer(self):
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    # 『保存』モーダル：
    def _header_df_to_dict(self, header_df):
        dict_list = []
        records_list = header_df.to_dict(orient="records")
        for item in records_list:
            if item["Property"] == "Authorization":
                # auth_value = item["Value"].replace(
                #     "Bearer .*", "Bearer ＜API_KEY＞"
                # )
                auth_value = item["Value"].replace(
                    st.session_state.api_key, "＜API_KEY＞"
                )
                # dict_list.append({item["Property"]: auth_value})
                dict_list.append(
                    {"Property": item["Property"], "Value": auth_value}
                )
            else:
                # dict_list.append({item["Property"]: item["Value"]})
                dict_list.append(
                    {"Property": item["Property"], "Value": item["Value"]}
                )

        return dict_list

    def save_action_state(self):
        with st.expander("Save Session State ?", expanded=False):
            pad = "stappApiClientState.yaml"
            time_stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name_conf = (
                f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{pad}"
            )
            pad = "stappApiClientMessages.yaml"

            # --- 保存データを構築 ---
            _action_state = []
            _action_item = {
                "uri": st.session_state.get("uri", ""),
                # "method": st.session_state.get("method", ""),
                "method": "POST",
                "config_file": st.session_state["config_file"],
                "use_dynamic_inputs": st.session_state.get(
                    "use_dynamic_inputs", True
                ),
                "user_property_path": st.session_state.get(
                    "user_property_path", ""
                ),
                "num_inputs": st.session_state.get("num_inputs", 0),
            }
            for i in range(_action_item["num_inputs"]):
                _action_item[f"user_input_{i}"] = st.session_state.get(
                    f"user_input_{i}", ""
                )
            _action_state.append(_action_item)
            conf_data = {
                "title": file_name_conf,
                "action_state": _action_state,
                "time_stamp": time_stamp,
            }

            # YAMLに変換
            conf_yaml = yaml.dump(
                conf_data, allow_unicode=True, default_flow_style=False
            )

            # ダウンロードボタンを表示
            st.download_button(
                label="Download YAML for config",
                data=conf_yaml,
                file_name=file_name_conf,
                mime="text/yaml",
            )

    # 『読込み』モーダル：
    def _on_file_upload(self):
        # st.session_state.config = None
        pass

    def _load_config(self, uploaded_yaml):
        """
        YAMLファイルを読み込み、ユーザー入力を初期化する

        Args:
            uploaded_file: Streamlitのfile_uploaderから受け取るファイルオブジェクト

        Returns:
            Dict[str, Any]: 処理済みの設定データ
        """
        try:
            config = yaml.safe_load(uploaded_yaml, "r", encoding="utf-8")
            # st.session_state.user_inputs = []
            # st.session_state.min_user_inputs =
            # _initialize_user_inputs(config)
            return config
        except yaml.YAMLError as e:
            st.error(f"YAML解析エラー: {str(e)}")
            return {}
        except Exception as e:
            st.error(f"設定ファイルの処理に失敗しました: {str(e)}")
            return {}

    def set_action_config(self, config, index=0):
        _action_states = config.get("action_state", [])
        if len(_action_states) <= 0:
            raise "Action State not defined!"
        _cfg_action_state = _action_states[index]
        # print(f"_cfg_aciton: {_cfg_action_state}")
        st.session_state.action_config = _cfg_action_state

    def get_action_config(self):
        return st.session_state.action_config

    def replace_placeholder(self, session_state, target_str: str) -> str:
        """
        プレースホルダー（例: ＜user_input_0＞）を
        session_state 内のユーザー入力値で置換する。

        Args:
            session_state (dict): Streamlitのセッション状態
            target_str (str): プレースホルダーを含む文字列

        Returns:
            str: プレースホルダーが置換された文字列
        """
        replaced_str = target_str
        num_inputs = session_state.get("num_inputs", 0)

        for i in range(num_inputs):
            key = f"user_input_{i}"
            if key in session_state:
                value = urllib.parse.quote(str(session_state[key]))
                replaced_str = replaced_str.replace(f"＜{key}＞", value)

        return replaced_str

    def replace_action_config(self, action_config):
        """
        指定されたアクション設定（action_config）を置換する。

        Args:
            action_config (dict): YAML設定ファイルなどから読み込まれた
        Side Effects:
            - `action_state`の値の特定キーワードを置換する
            - 置換対象：
                - config_file
                - user_input_{i}
            - 対象外：
                - method, uri, num_inputs
                - use_dynamic_inputs, user_property_path
        """
        _replaced_config = {}
        if "method" in action_config:
            _replaced_config["method"] = action_config.get("method", "")
        if "uri" in action_config:
            _replaced_config["uri"] = action_config.get("uri", "")
        if "config_file" in action_config:
            # _replaced_config["config_file"] = action_config.get(
            #     "config_file", ""
            # )
            _replaced_config["config_file"] = self.replace_placeholder(
                session_state=st.session_state,
                target_str=action_config.get("config_file", ""),
            )

        _num_inputs = action_config.get("num_inputs", 0)
        _replaced_config["num_inputs"] = _num_inputs
        for i in range(_num_inputs):
            key = f"user_input_{i}"
            if key in action_config:
                # _replaced_config[key] = action_config.get(key, "")
                _replaced_config[key] = self.replace_placeholder(
                    session_state=st.session_state,
                    target_str=action_config.get(key, ""),
                )

        if "use_dynamic_inputs" in action_config:
            if action_config.get("use_dynamic_inputs") == "false":
                _replaced_config["use_dynamic_inputs"] = False
            else:
                _replaced_config["use_dynamic_inputs"] = True
        if "user_property_path" in action_config:
            _replaced_config["user_property_path"] = action_config.get(
                "user_property_path", "."
            )
        return _replaced_config

    def load_action_state(self):
        uploaded_file = st.file_uploader(
            label="Choose a YAML config file",
            type="yaml",
            on_change=self._on_file_upload,
        )

        # if uploaded_file is not None and st.session_state.config is None:
        if uploaded_file is not None:
            try:
                config = self._load_config(uploaded_file)
                if config:
                    # st.session_state.config = config
                    self.set_action_state(config)
                    # main_viewer.config_viewer(st.session_state.config)
                    st.rerun()
            except yaml.YAMLError as e:
                st.error(f"Error loading YAML file: {e}")

    def _clear_states(self):
        st.session_state.api_running = False

    def render_buttons(self):
        st.write("##### Runner Ctrl.")
        (
            col1,
            col2,
            col3,
            col4,
            col5,
        ) = st.columns(5)
        with col1:
            if st.button(
                help="Stop Running",
                label="⏹️",
                disabled=(st.session_state.api_running is False),
            ):
                self._clear_states()
                st.rerun()
        with col2:
            if st.button(
                help="Save Session States",
                label="📥",
                disabled=st.session_state.api_running,
            ):
                self.modal("save_state")
        with col3:
            if st.button(
                help="Clear Session States",
                label="🔄",
            ):
                # 全てのセッション状態をクリアする場合はこちらを使用
                st.session_state.clear()
                st.rerun()
        with col4:
            pass
        with col5:
            pass
