from pathlib import Path
import yaml
import os


class MainClassSetting:
    def __init__(self, setting_file_path: Path):
        try:
            # 設定ファイルが存在するかを確認
            if not setting_file_path.exists():
                raise FileNotFoundError('config file does not exist.')

            # 設定ファイルからデータの読み取り
            setting_data = yaml.safe_load(setting_file_path.read_text(encoding='utf-8'))

            # 設定ファイルの構造チェック
            if (config_data := setting_data.get('config', None)) is None:
                raise ValueError('config file illegal format.')

            # 設定値の読み取り（variable_dir）
            if not (variable_dir := Path(config_data.get('variable_dir', ''))):
                raise ValueError('config file illegal format.')

            # ディレクトリ確認、生成
            if not variable_dir.exists():
                os.makedirs(variable_dir)

            # 読み取った値をインスタンス変数に保存
            self.variable_dir: Path = variable_dir

        except Exception as err:
            raise err
