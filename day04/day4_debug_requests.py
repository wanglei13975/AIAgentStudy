import requests
import json
import time

# 配置
MODEL = "qwen2.5:14b"  # 如果跑不动，请一定要改为 "qwen2.5:7b"
URL = "http://localhost:11434/api/chat"

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市"}
                },
                "required": ["city"]
            }
        }
    }
]

def debug_chat():
    print(f"1. 正在尝试连接本地模型: {MODEL} ...")
    print("   (注意：第一次运行可能需要几十秒加载模型到显存，请耐心)")

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "帮我查一下北京的天气"}],
        "tools": tools,
        "stream": False # 关闭流式输出，方便调试
    }

    try:
        start_time = time.time()
        
        # 核心修改：使用 requests 库，timeout 设置为 None (永不超时) 或者 300秒
        response = requests.post(URL, json=payload, timeout=300)
        
        end_time = time.time()
        print(f"2. 请求耗时: {end_time - start_time:.2f} 秒")

        if response.status_code == 200:
            result = response.json()
            print("3. 成功获取返回内容！")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 检查是否有工具调用
            if result['message'].get('tool_calls'):
                print("\n[成功] 模型成功识别并请求调用工具！")
            else:
                print("\n[注意] 模型回复了，但没有调用工具。")
        else:
            print(f"Error: 状态码 {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("\n[严重错误] 连接被拒绝！")
        print("原因可能是：")
        print("1. Ollama 服务没有启动（请在任务栏确认 Ollama 图标）")
        print("2. 模型加载导致 Ollama 崩溃（显存爆了）")
    except requests.exceptions.ReadTimeout:
        print("\n[错误] 读取超时，但连接是通的。")
    except Exception as e:
        print(f"\n[未知错误] {e}")

if __name__ == "__main__":
    debug_chat()