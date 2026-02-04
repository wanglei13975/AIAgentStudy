"""
Day 1 - 项目3: LLM工具类
功能：封装完整的LLM交互逻辑，支持流式输出、温度控制等高级功能
"""

import requests
import json
from typing import List, Dict, Optional, Generator
from datetime import datetime

import logging

# 配置日志：同时输出到控制台和文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("llm_tools.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OllamaLLM:
    """Ollama LLM工具类：提供完整的模型交互接口"""
    
    def __init__(
        self, 
        model: str = "qwen2.5:14b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        """
        初始化LLM工具
        
        参数:
            model (str): 模型名称
            base_url (str): Ollama服务地址
            temperature (float): 温度参数（0-1，越高越随机）
            system_prompt (str): 系统提示词
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.history: List[Dict[str, str]] = []
        
        # 如果有系统提示词，添加到历史
        if system_prompt:
            self.history.append({
                "role": "system",
                "content": system_prompt
            })
    
    def chat(
        self, 
        message: str, 
        stream: bool = False,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        发送消息并获取回复
        
        参数:
            message (str): 用户消息
            stream (bool): 是否使用流式输出
            max_tokens (int): 最大token数
        
        返回:
            str: AI的回复
        """
        # 添加用户消息
        self.history.append({"role": "user", "content": message})
        
        # 构建请求
        url = f"{self.base_url}/api/chat"
        data = {
            "model": self.model,
            "messages": self.history,
            "stream": stream,
            "options": {
                "temperature": self.temperature
            }
        }
        
        if max_tokens:
            data["options"]["num_predict"] = max_tokens
        
        try:
            response = requests.post(url, json=data, stream=stream)
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return self._handle_normal_response(response)
        
        except Exception as e:
            error_msg = f"❌ 错误：{str(e)}"
            return error_msg
    
    def _handle_normal_response(self, response) -> str:
        """处理非流式响应"""
        result = response.json()
        assistant_message = result.get("message", {}).get("content", "")
        
        if assistant_message:
            self.history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def _handle_stream_response(self, response) -> str:
        """处理流式响应"""
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    full_response += content
                    print(content, end="", flush=True)
                except json.JSONDecodeError:
                    continue
        
        print()  # 换行
        
        if full_response:
            self.history.append({"role": "assistant", "content": full_response})
        
        return full_response
    
    def clear_history(self, keep_system: bool = True):
        """
        清空对话历史
        
        参数:
            keep_system (bool): 是否保留系统提示词
        """
        if keep_system and self.system_prompt:
            self.history = [{"role": "system", "content": self.system_prompt}]
        else:
            self.history.clear()
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.history.copy()
    
    def save_conversation(self, filename: str):
        """
        保存对话到文件
        
        参数:
            filename (str): 文件名
        """
        data = {
            "model": self.model,
            "timestamp": datetime.now().isoformat(),
            "history": self.history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 对话已保存到: {filename}")
    
    def load_conversation(self, filename: str):
        """
        从文件加载对话
        
        参数:
            filename (str): 文件名
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.history = data.get("history", [])
            print(f"✅ 对话已从 {filename} 加载")
            print(f"📝 加载了 {len(self.history)} 条消息")
        
        except FileNotFoundError:
            print(f"❌ 文件不存在: {filename}")
        except json.JSONDecodeError:
            print(f"❌ 文件格式错误: {filename}")


def demo_basic_usage():
    """演示基本用法"""
    print("\n" + "=" * 50)
    print("📚 演示1: 基本对话")
    print("=" * 50)
    
    llm = OllamaLLM()
    
    response = llm.chat("你好，请用一句话介绍你自己")
    print(f"🤖 AI: {response}\n")


def demo_with_system_prompt():
    """演示系统提示词"""
    print("\n" + "=" * 50)
    print("📚 演示2: 使用系统提示词")
    print("=" * 50)
    
    llm = OllamaLLM(
        system_prompt="你是一个Python编程专家，回答要简洁专业。"
    )
    
    response = llm.chat("什么是列表推导式？")
    print(f"🤖 AI: {response}\n")


def demo_streaming():
    """演示流式输出"""
    print("\n" + "=" * 50)
    print("📚 演示3: 流式输出")
    print("=" * 50)
    
    llm = OllamaLLM()
    
    print("🤖 AI: ", end="")
    llm.chat("用三句话解释什么是AI Agent", stream=True)
    print()


def demo_save_load():
    """演示保存和加载对话"""
    print("\n" + "=" * 50)
    print("📚 演示4: 保存和加载对话")
    print("=" * 50)
    
    llm = OllamaLLM()
    llm.chat("记住这个数字：42")
    llm.chat("我刚才说的数字是多少？")
    
    # 保存对话
    llm.save_conversation("conversation.json")
    
    # 创建新实例并加载
    new_llm = OllamaLLM()
    new_llm.load_conversation("conversation.json")
    
    response = new_llm.chat("再重复一次那个数字")
    print(f"🤖 AI: {response}\n")


def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 50)
    print("🤖 LLM工具类 - 交互模式")
    print("=" * 50)
    print("命令说明:")
    print("  - 输入消息即可对话")
    print("  - 'stream on/off' - 切换流式输出")
    print("  - 'temp <0-1>' - 设置温度")
    print("  - 'save <filename>' - 保存对话")
    print("  - 'load <filename>' - 加载对话")
    print("  - 'clear' - 清空历史")
    print("  - 'history' - 查看历史")
    print("  - 'quit' - 退出\n")
    
    llm = OllamaLLM()
    stream_mode = False
    
    while True:
        user_input = input("👤 你: ").strip()
        
        if not user_input:
            continue
        
        # 处理命令
        if user_input.lower() in ['quit', 'exit']:
            print("👋 再见！")
            break
        
        elif user_input.lower() == 'stream on':
            stream_mode = True
            print("✅ 流式输出已开启")
            continue
        
        elif user_input.lower() == 'stream off':
            stream_mode = False
            print("✅ 流式输出已关闭")
            continue
        
        elif user_input.lower().startswith('temp '):
            try:
                temp = float(user_input.split()[1])
                if 0 <= temp <= 1:
                    llm.temperature = temp
                    print(f"✅ 温度已设置为: {temp}")
                else:
                    print("❌ 温度必须在0-1之间")
            except (ValueError, IndexError):
                print("❌ 格式错误，使用: temp 0.7")
            continue
        
        elif user_input.lower().startswith('save '):
            filename = user_input.split(maxsplit=1)[1]
            llm.save_conversation(filename)
            continue
        
        elif user_input.lower().startswith('load '):
            filename = user_input.split(maxsplit=1)[1]
            llm.load_conversation(filename)
            continue
        
        elif user_input.lower() == 'clear':
            llm.clear_history()
            print("✅ 历史已清空")
            continue
        
        elif user_input.lower() == 'history':
            history = llm.get_history()
            print(f"\n📝 共有 {len(history)} 条消息:")
            for i, msg in enumerate(history, 1):
                role = msg['role']
                content = msg['content'][:50]
                print(f"  {i}. [{role}] {content}...")
            print()
            continue
        
        # 正常对话
        if stream_mode:
            print("🤖 AI: ", end="")
        else:
            print("🤔 思考中...")
        
        response = llm.chat(user_input, stream=stream_mode)
        
        if not stream_mode:
            print(f"🤖 AI: {response}\n")


if __name__ == "__main__":
    # 运行所有演示
    demo_basic_usage()
    demo_with_system_prompt()
    demo_streaming()
    demo_save_load()
    
    # 进入交互模式
    interactive_mode()
