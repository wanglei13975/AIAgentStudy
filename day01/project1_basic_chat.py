"""
Day 1 - 项目1: 基础对话器
功能：与本地Ollama模型进行简单问答
"""

import requests
import json
import time

def chat_with_ollama(prompt: str, model: str = "qwen2.5:14b") -> str:
    """
    向Ollama发送请求并获取响应
    
    参数:
        prompt (str): 用户输入的问题
        model (str): 使用的模型名称
    
    返回:
        str: 模型的回复
    """
    # Ollama API的默认地址
    url = "http://localhost:11434/api/generate"
    
    # 构建请求数据
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False  # 非流式输出，一次性返回完整结果
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, json=data)
        response.raise_for_status()  # 检查HTTP错误
        
        # 解析响应
        result = response.json()
        return result.get("response", "")
    
    except requests.exceptions.ConnectionError:
        return "❌ 错误：无法连接到Ollama。请确保Ollama正在运行。"
    except requests.exceptions.RequestException as e:
        return f"❌ 请求错误：{str(e)}"
    except json.JSONDecodeError:
        return "❌ 响应解析错误"


def main():
    """主函数：简单的对话循环"""
    print("=" * 50)
    print("🤖 基础对话器 - Day 1 项目1")
    print("=" * 50)
    print("输入 'quit' 或 'exit' 退出程序\n")
    question_count = 0
    while True:
        # 获取用户输入
        #- 统计用户提问次数
        #- 在退出时显示总共的对话次数
        user_input = input("👤 你: ").strip()
        question_count += 1
        # 检查退出命令
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("\n👋 再见！")
            print(f"🤖 总共的对话次数: {question_count}")
            break
        
        # 跳过空输入
        if not user_input:
            continue
        
        # 调用模型
        print("🤔 思考中...")
        # 记录花费的时间
        start_time = time.time()
        response = chat_with_ollama(user_input)
        end_time = time.time()
        # 显示回复
        print(f"🤖 AI: {response}\n")
        print(f"🤖 花费时间: {end_time - start_time:.2f}秒")

if __name__ == "__main__":
    main()
