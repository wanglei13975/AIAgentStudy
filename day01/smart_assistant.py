import time
from project3_llm_toolkit import OllamaLLM  # 假设你的项目3代码保存在此文件名下

ROLES = {
    "Python老师": "你是一位专业的 Python 编程老师。你会用通俗易懂的语言解释概念，并经常提供简洁的代码示例。如果用户代码有错，你会耐心地指出并给出修改建议。",
    "翻译助手": "你是一个精通多国语言的翻译官。请将用户输入的任何内容翻译成中文（如果是中文则翻译成英文）。你只返回翻译结果，不要有任何多余的解释。",
    "代码审查员": "你是一个资深软件架构师。请审查用户提交的代码，从性能、安全、可读性三个维度给出改进意见。你的回答应该专业且言简意赅。"
}

class SmartAssistant:
    def __init__(self):
        self.current_role_name = "Python老师"
        # 初始化 LLM，默认载入 Python 老师的提示词
        self.llm = OllamaLLM(system_prompt=ROLES[self.current_role_name])
        
    def switch_role(self, role_name: str):
        """切换角色并重置对话历史"""
        if role_name in ROLES:
            self.current_role_name = role_name
            # 更新 System Prompt 需要清空历史并重新设置
            self.llm.system_prompt = ROLES[role_name]
            self.llm.clear_history(keep_system=True)
            print(f"✅ 已成功切换到角色: 【{role_name}】")
        else:
            print(f"❌ 角色 '{role_name}' 不存在。当前可选: {list(ROLES.keys())}")

    def run(self):
        print("=" * 50)
        print("🌟 欢迎使用智能助手 (Day 1 - 练习4)")
        print(f"当前角色: {self.current_role_name}")
        print("命令: /role <角色名> | /list (查看角色) | /save | /quit")
        print("=" * 50)

        while True:
            user_input = input(f"👤 [{self.current_role_name}] 你: ").strip()
            
            if not user_input: continue
            
            # 处理命令
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            elif user_input.startswith('/role '):
                new_role = user_input.split(maxsplit=1)[1]
                self.switch_role(new_role)
                continue
            
            elif user_input == '/list':
                print(f"可选角色: {', '.join(ROLES.keys())}")
                continue

            elif user_input == '/save':
                filename = f"chat_{self.current_role_name}.json"
                self.llm.save_conversation(filename)
                continue

            # 普通对话
            print("🤔 思考中...")
            response = self.llm.chat(user_input, stream=True) # 使用流式增加体验
            # 如果 project3 的 chat 返回的是字符串且在函数内已 print，这里就不需要重复 print
if __name__ == "__main__":
    assistant = SmartAssistant()
    assistant.run()