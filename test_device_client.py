import asyncio
import json
import websockets
from datetime import datetime
import time

class DriftSeeDeviceClient:
    """DriftSee 设备客户端模拟器"""
    
    def __init__(self, device_id, device_sn, room_id, token=None):
        self.device_id = device_id
        self.device_sn = device_sn
        self.room_id = room_id
        self.token = token
        self.ws_url = f"ws://localhost:8000/api/ws/v1/manyRoom/{room_id}/{device_sn}/device/{device_id}"
        if token:
            self.ws_url += f"?token={token}"
        self.websocket = None
    
    async def connect(self):
        """连接到服务器"""
        print(f"正在连接到: {self.ws_url}")
        self.websocket = await websockets.connect(self.ws_url)
        print("连接成功")
        
        # 启动心跳任务
        heartbeat_task = asyncio.create_task(self.send_heartbeat())
        
        # 启动消息接收任务
        receive_task = asyncio.create_task(self.receive_messages())
        
        # 发送设备信息
        await self.send_device_info()
        
        # 等待任务完成
        await asyncio.gather(heartbeat_task, receive_task)
    
    async def send_heartbeat(self):
        """发送心跳"""
        while True:
            try:
                heartbeat_msg = {
                    "type": "notify",
                    "event": "join",
                    "deviceId": self.device_id,
                    "code": 0,
                    "data": {}
                }
                await self.websocket.send(json.dumps(heartbeat_msg))
                print(f"发送心跳: {datetime.now().isoformat()}")
                await asyncio.sleep(60)  # 每分钟发送一次
            except Exception as e:
                print(f"发送心跳失败: {e}")
                break
    
    async def send_device_info(self):
        """发送设备信息"""
        device_info = {
            "type": "notify",
            "event": "device_info",
            "deviceId": self.device_id,
            "code": 0,
            "data": {
                "no": self.device_sn,
                "dzoom": 1,
                "rtmp": "stop",
                "rtmp_url": "",
                "rtsp": "stop",
                "rtsp_url": "",
                "stream_res": "720P",
                "stream_bitrate": 1000000,
                "stream_framerate": 30,
                "record": "stop",
                "led": 0,
                "exposure": 1,
                "filter": 0,
                "mic_sensitivity": 3,
                "fov": 140
            }
        }
        await self.websocket.send(json.dumps(device_info))
        print("设备信息已发送")
    
    async def request_rtmp_address(self):
        """请求RTMP地址"""
        request_msg = {
            "type": "device_control",
            "event": "get_rtmp",
            "deviceId": self.device_id
        }
        await self.websocket.send(json.dumps(request_msg))
        print("RTMP地址请求已发送")
    
    async def receive_messages(self):
        """接收消息"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                print(f"收到消息: {data}")
                
                # 处理不同类型的消息
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("连接已关闭")
    
    async def handle_message(self, data):
        """处理收到的消息"""
        msg_type = data.get("type")
        event = data.get("event")
        
        if msg_type == "device_notify" and event == "get_rtmp":
            print(f"收到RTMP地址: {data.get('data', {})}")
        
        elif msg_type == "control":
            print(f"收到控制命令: {event}")
            
            # 模拟设备响应控制命令
            if event == "device_info":
                await self.send_device_info()
            elif event == "start_rtmp":
                # 模拟开始推流
                response = {
                    "type": "notify",
                    "event": "start_rtmp",
                    "deviceId": self.device_id,
                    "playId": data.get("playId"),
                    "code": 0,
                    "data": {"status": "streaming_started"}
                }
                await self.websocket.send(json.dumps(response))

async def main():
    # 测试设备参数
    device_id = "2d1187e853b81574f8021c6f6739e15d"
    device_sn = "DEVICE_SN_123456"
    room_id = "room123"
    token = "test-token"
    
    device = DriftSeeDeviceClient(device_id, device_sn, room_id, token)
    await device.connect()

if __name__ == "__main__":
    asyncio.run(main())