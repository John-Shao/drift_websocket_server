import os
import sys
import requests
import json
import time
import uuid


GROUP_ID = "f2374f8400a763e03e35745d71b01275"

# 测试配置
BASE_URL = "http://localhost:9000"

ROOM_ID = "f2374f8400a763e03e35745d71b01275"    # 测试房间ID
DEVICE_SN = "74TNABDGNAA0YW01"                  # 测试设备序列号
DEVICE_ID = "00a4b5697e3d16796b818d656ccea433"  # 测试设备ID


def test_start_rtmp_api():
    """测试START_RTMP控制接口"""
    
    # 生成唯一的playId
    play_id = str(uuid.uuid4())
    
    # 构建请求URL
    url = f"{BASE_URL}/api/control/{DEVICE_ID}"
    
    # 构建请求体
    payload = {
        "type": "control",
        "playId": play_id,
        "deviceId": DEVICE_ID,
        "event": "start_rtmp",
        "data": {
            "rtmp_url": f"rtmp://14.103.74.174/{GROUP_ID}/{DEVICE_ID}",
            "stream_res": "720P",
            "stream_bitrate": 2000000,
            "stream_framerate": 30
        }
    }
    
    print(f"测试START_RTMP接口:")
    print(f"请求URL: {url}")
    print(f"请求体: {json.dumps(payload, indent=2)}")
    
    try:
        # 发送POST请求
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("\nSTART_RTMP命令发送成功！")
                return True
            else:
                print(f"\nSTART_RTMP命令执行失败: {result.get('error_msg', '未知错误')}")
                return False
        else:
            print(f"\n请求失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n连接失败，请确保服务器正在运行在 {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print("\n请求超时")
        return False
    except Exception as e:
        print(f"\n发生未知错误: {e}")
        return False


def test_stop_rtmp_api():
    """测试STOP_RTMP控制接口"""
    
    # 生成唯一的playId
    play_id = str(uuid.uuid4())
    
    # 构建请求URL
    url = f"{BASE_URL}/api/control/{DEVICE_ID}"
    
    # 构建请求体
    payload = {
        "playId": play_id,
        "deviceId": DEVICE_ID,
        "event": "stop_rtmp",
    }
    
    print(f"\n\n测试STOP_RTMP接口:")
    print(f"请求URL: {url}")
    print(f"请求体: {json.dumps(payload, indent=2)}")
    
    try:
        # 发送POST请求
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2)}")
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                print("\nSTOP_RTMP命令发送成功！")
                return True
            else:
                print(f"\nSTOP_RTMP命令执行失败: {result.get('error_msg', '未知错误')}")
                return False
        else:
            print(f"\n请求失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n连接失败，请确保服务器正在运行在 {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print("\n请求超时")
        return False
    except Exception as e:
        print(f"\n发生未知错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("RTMP控制接口测试")
    print("=" * 50)
    
    # 测试START_RTMP
    start_success = test_start_rtmp_api()

    # 等待指定秒数后测试STOP_RTMP
    if start_success:
        sec = 60
        print(f"\n等待{sec}秒后测试STOP_RTMP...")
        time.sleep(sec)
        
        # 测试STOP_RTMP
        test_stop_rtmp_api()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
