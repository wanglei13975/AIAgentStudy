"""
Day 1 - 项目2: 对话历史管理器
功能：维护对话上下文，让AI记住之前的对话内容
"""

import requests
import json
from typing import List, Dict


class ConversationManager:
    """对话管理器类：管理对话历史和上下文"""
    
    def __init__(self, model: str = "qwen2.5:14b"):
        """
        初始化对话管理器
        
        参数:
            model (str): 使用的模型名称
        """
        self.model = model
        self.history: List[Dict[str, str]] = []  # 存储对话历史
        self.url = "http://localhost:11434/api/chat"
    
    def add_message(self, role: str, content: str):
        """
        添加消息到历史记录
        
        参数:
            role (str): 角色 ('user' 或 'assistant')
            content (str): 消息内容
        """
        self.history.append({
            "role": role,
            "content": content
        })
    
    def get_response(self, user_message: str) -> str:
        """
        发送消息并获取回复（带上下文）
        
        参数:
            user_message (str): 用户消息
        
        返回:
            str: AI的回复
        """
        # 添加用户消息到历史
        self.add_message("user", user_message)
        
        # 构建请求数据
        data = {
            "model": self.model,
            "messages": self.history,
            "stream": False
        }
        
        try:
            # 发送请求
            response = requests.post(self.url, json=data)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            assistant_message = result.get("message", {}).get("content", "")
            
            # 添加AI回复到历史
            if assistant_message:
                self.add_message("assistant", assistant_message)
            
            return assistant_message
        
        except requests.exceptions.ConnectionError:
            return "❌ 错误：无法连接到Ollama。请确保Ollama正在运行。"
        except requests.exceptions.RequestException as e:
            return f"❌ 请求错误：{str(e)}"
        except json.JSONDecodeError:
            return "❌ 响应解析错误"
    
    def clear_history(self):
        """清空对话历史"""
        self.history.clear()
        print("🧹 对话历史已清空")
    
    def show_history(self):
        """显示对话历史"""
        if not self.history:
            print("📝 暂无对话历史")
            return
        
        print("\n" + "=" * 50)
        print("📝 对话历史")
        print("=" * 50)
        for i, msg in enumerate(self.history, 1):
            role = "👤 你" if msg["role"] == "user" else "🤖 AI"
            print(f"{i}. {role}: {msg['content'][:50]}...")
        print("=" * 50 + "\n")
    def export_history(self):
        """导出对话历史"""
        with open('conversation.txt', 'w', encoding='utf-8') as f:
            for msg in self.history:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg['role']}: {msg['content']}\n")
        print("✅ 对话历史已导出到 conversation.txt")
    
    def load_history(self):
        """加载对话历史"""
        with open('conversation.txt', 'r', encoding='utf-8') as f:
            for line in f:
                msg = line.strip()
                self.history.append(msg)
        print("✅ 对话历史已加载")

def main():
    """主函数：带上下文的对话循环"""
    print("=" * 50)
    print("🤖 对话历史管理器 - Day 1 项目2")
    print("=" * 50)
    print("命令说明:")
    print("  - 输入消息即可对话")
    print("  - 'clear' - 清空对话历史")
    print("  - 'history' - 查看对话历史")
    print("  - 'quit' 或 'exit' - 退出程序\n")
    
    # 创建对话管理器
    manager = ConversationManager()
    
    while True:
        # 获取用户输入
        user_input = input("👤 你: ").strip()
        
        # 处理特殊命令
        #扩展 `project2_conversation_manager.py`，添加导出功能：
        #- 添加 'export' 命令，将对话历史保存为纯文本文件
        #- 格式要求：每条消息占一行，包含时间戳
        #- 示例格式：`[2024-01-29 10:30:15] 用户: 你好`
        if user_input.lower() == 'export':
            manager.export_history()
            continue
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("\n👋 再见！")
            break
        elif user_input.lower() == 'clear':
            manager.clear_history()
            continue
        elif user_input.lower() == 'history':
            manager.show_history()
            continue
        
        # 跳过空输入
        if not user_input:
            continue
        
        # 获取AI回复
        print("🤔 思考中...")
        response = manager.get_response(user_input)
        
        # 显示回复
        print(f"🤖 AI: {response}\n")


if __name__ == "__main__":
    main()
