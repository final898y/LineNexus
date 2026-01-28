from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    應用程式設定，透過 pydantic-settings 自動從 .env 讀取。
    """
    # 伺服器設定
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # LINE Bot 設定
    LINE_CHANNEL_ACCESS_TOKEN: str = "your_token"
    LINE_CHANNEL_SECRET: str = "your_secret"

    # Google Gemini API 設定
    GEMINI_API_KEY: str = "your_key"

    # 允許讀取 .env 檔案
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# 實例化設定物件
settings = Settings()
