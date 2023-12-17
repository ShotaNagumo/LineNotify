from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import yaml
import os


class DisasterTextType(Enum):
    CURERNT = auto()
    PAST = auto()
    PAST_WITH_TIME = auto()


@dataclass
class DisasterTextInfo:
    disaster_text: str
    disaster_text_type: DisasterTextType


class MainClassSetting:
    def __init__(self, setting_file_path: Path):
        # 設定ファイルからデータの読み取り
        with open(setting_file_path, mode='rt', encoding='utf-8') as fp:
            setting_data = yaml.safe_load(fp)

        # 設定ファイルの構造チェック
        config_data = setting_data.get('config', None)
        if config_data is None:
            raise Exception('config.yaml format error.')

        # 設定値の読み取り（variable_dir）
        variable_dir: Path = Path(config_data.get('variable_dir', ''))
        try:
            if not variable_dir.exists():
                os.makedirs(variable_dir)
        except Exception:
            # ディレクトリが存在せず、生成もできない場合は無効設定値と判定してExceptionをraise
            raise Exception('config.yaml: variable_dir could not create.')
        self.variable_dir = variable_dir
