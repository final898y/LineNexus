from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    專案設定類別，使用 pydantic-settings 自動從環境變數或 .env 讀取。
    """

    # 應用程式設定
    APP_NAME: str = "LineNexus"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # LINE Bot 設定
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str

    # AI 設定
    GEMINI_API_KEY: str

    # 允許讀取 .env 檔案
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# 實例化設定物件
settings = Settings()
