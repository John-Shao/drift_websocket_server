import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    
    # 接收X5设备推送视频流的RTMP服务器地址和端口
    video_rtmp_host: str
    video_rtmp_port: int
    
    # 接收VeRTC推送音频流的RTMP服务器地址和端口
    audio_rtmp_host: str
    audio_rtmp_port: int
    # VolcEngine RTC 配置
    volc_rtc_app_id: str
    volc_rtc_app_key: str
    volc_token_expire_seconds: int = 3600  # 默认1小时

    # 音视频互动智能体（Conversational-AI）
    volc_cai_app_id: str
    volc_cai_app_key: str

    # 豆包端到端实时语音大模型
    doubao_s2s_app_id: str
    doubao_s2s_access_token: str

    # AK/SK
    volc_access_key: str
    volc_secret_key: str
    volc_region: str
    
    # 服务器配置
    APP_NAME: str = "DriftSee WebSocket Server"
    APP_VERSION: str = "1.5.0"
    HOST: str = "0.0.0.0"
    PORT: int = 9000  # WebSocket端点与HTTP API端点共用同一端口
    DEBUG: bool = True
    
    # WebSocket 配置
    WEBSOCKET_PING_INTERVAL: int = 20  # 秒
    WEBSOCKET_PING_TIMEOUT: int = 30   # 秒
    HEARTBEAT_TIMEOUT: int = 180       # 3分钟心跳超时
    
    # 安全配置
    SECRET_KEY: str = "your_secret key"
    
    # 数据库配置
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@"
    REDIS_URL: str = "redis://jusi:jusi2025@172.18.245.192:6379"  # 测试环境 172.18.245.192
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png"]
    
    class Config:
        # 指定 .env 文件的编码
        env_file_encoding = 'utf-8'

        # (可选) 如果你的 .env 文件不叫 ".env"，可以在这里指定
        env_file = ".env"

settings = Settings()
