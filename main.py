import json
import logging
from datetime import datetime
from typing import Optional, AsyncGenerator
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from config import settings
from manager import manager
from device_handler import DeviceMessageHandler
from control_handler import ControlMessageHandler
from auth_handler import authenticate_device
from models import MessageType, EventType

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 定义Lifespan事件
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期事件"""

    # 启动事件
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 连接 Redis
    await manager.connect_redis()
    
    # 启动心跳监控
    #await manager.start_heartbeat_monitor()
    
    logger.info("应用启动完成")
    
    yield  # 应用运行中
    
    # 关闭事件
    logger.info("应用正在关闭...")
    
    # 关闭所有 WebSocket 连接
    for connection_id in list(manager.active_connections.keys()):
        await manager.disconnect(connection_id, reason="服务器关闭")
    
    logger.info("应用已关闭")

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,  # 应用名称
    version=settings.APP_VERSION,  # API的版本
    docs_url="/docs" if settings.DEBUG else None,    # 仅在调试模式下启用Swagger UI文档的访问路径
    redoc_url="/redoc" if settings.DEBUG else None,  # 仅在调试模式下启用ReDoc文档的访问路径
    lifespan=lifespan  # 定义一个 lifespan 函数来处理应用启动时和关闭时需要执行的代码，如连接和断开数据库，启动和停止心跳监控任务等
)

# CORS (Cross-Origin Resource Sharing 跨域资源共享)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''
WebSocket 端点
'''

# 设备 WebSocket 连接端点，websocket_server_url=ws://jusiai.cn:8000
# /api/ws/v1/manyRoom/f2374f8400a763e03e35745d71b01275/74TNABDGNAA0YW01/device/00a4b5697e3d16796b818d656ccea433/zh-CN
@app.websocket("/api/ws/v1/manyRoom/{room_id}/{device_sn}/device/{device_id}/{language}")
async def device_websocket(
    websocket: WebSocket,
    room_id: str,
    device_sn: str,
    device_id: str,
    language: Optional[str] = None
    ):
    """设备 WebSocket 连接端点"""
    '''
    # 设备认证
    is_authenticated = await authenticate_device(token, device_id, device_sn, room_id)
    if not is_authenticated:
        await websocket.close(code=1008, reason="认证失败")
        return
    '''

    # 建立连接
    connection_id = await manager.connect(websocket, room_id, device_sn, device_id)
    
    try:
        while True:
            # 接收消息
            message_data = await websocket.receive_json()
            logger.debug(f"收到消息: {json.dumps(message_data, indent=2)}")
            
            # 处理消息
            response = await DeviceMessageHandler.handle_message(
                message_data, connection_id, websocket
            )
            
            # 发送响应
            if response:
                await websocket.send_json(response)
                logger.debug(f"发送响应: {json.dumps(response, indent=2)}")
            
    except WebSocketDisconnect as e:
        logger.info(f"设备断开连接: {connection_id}, 代码: {e.code}")
        await manager.disconnect(connection_id)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}")
        await manager.disconnect(
            connection_id,
            code=1007,
            reason="消息格式错误"
        )
    except Exception as e:
        logger.error(f"处理 WebSocket 时出错: {e}")
        await manager.disconnect(
            connection_id,
            code=1011,
            reason="服务器内部错误"
        )

'''
HTTP API 端点
'''

# 设备控制
@app.post("/api/control/{device_id}")
async def send_control_command(device_id: str, request: dict):
    """发送控制命令到设备"""
    try:
        connection_id = await manager.get_device_connection(device_id)
        if not connection_id:
            raise ValueError(f"设备 {device_id} 未连接")

        logger.debug(f"发送控制消息: {json.dumps(request, indent=2)}")
        
        # 处理控制消息
        response = await ControlMessageHandler.handle_control_message(connection_id, request)
        
        logger.debug(f"控制命令响应: {json.dumps(response, indent=2)}")
        
        if response and response.get("code") == -1:
            raise HTTPException(
                status_code=400,
                detail=response.get("error_msg", "控制命令执行失败")
            )
        
        return JSONResponse(content=response or {})
        
    except Exception as e:
        logger.error(f"发送控制命令时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 获取在线设备列表
@app.get("/api/devices")
async def get_online_devices(room_id: Optional[str] = None):
    """获取在线设备列表"""
    devices = manager.get_online_devices(room_id)
    return {
        "code": 0,
        "data": devices,
        "count": len(devices)
    }

# 健康检查
@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "connected_devices": len(manager.active_connections)
    }

# 截图上传端点（用于接收设备上传的截图）
@app.post("/api/upload/screenshot")
async def upload_screenshot_endpoint(data: dict):
    """接收设备上传的截图"""
    try:
        # 这里可以添加额外的验证逻辑
        # 例如验证 deviceId 是否合法等
        
        # 简单示例：直接返回成功
        return {
            "code": 0,
            "message": "截图上传成功",
            "data": {
                "url": f"/screenshots/{data.get('deviceId')}/{data.get('screenName', 'screenshot.jpg')}",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"处理截图上传时出错: {e}")
        return {
            "code": -1,
            "error_msg": str(e)
        }

# 单元测试
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=["./app/"],
        ws_ping_interval=settings.WEBSOCKET_PING_INTERVAL,
        ws_ping_timeout=settings.WEBSOCKET_PING_TIMEOUT,
        log_level="info" if settings.DEBUG else "warning"
    )
