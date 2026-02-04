import json
import ollama
from ollama import Client

# --- 1. 定义工具函数 (保持不变) ---
def get_weather(city: str):
    """查询天气的模拟函数"""
    return {"city": city, "temperature": "25°C", "condition": "晴天", "remark": "适合出去写代码"}

def calculate_investment(principal: float, rate: float, years: int):
    """计算投资的模拟函数"""
    total = principal * (1 + rate) ** years
    return {"total": round(total, 2), "yield_rate": f"{round((total-principal)/principal*100, 2)}%"}

# --- 2. 核心 Agent 类 (修复并优化) ---
class RealLLMAgent:
    def __init__(self, model="qwen2.5:14b"):
        self.model = model
        # 关键修复：实例化 Client 并设置更长的超时时间（单位：秒）
        # 如果你的电脑慢，可以把 timeout 改成 300 (5分钟)
        self.client = Client(host='http://localhost:11434', timeout=120)
        
        # 注册工具：这里建立函数名到实际函数的映射
        self.available_functions = {
            "get_weather": get_weather,
            "calculate_investment": calculate_investment,
        }
        
        # 定义工具描述（发给模型的说明书）
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "查询指定城市的当前天气",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "城市名称"}
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_investment",
                    "description": "计算复利投资收益",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "principal": {"type": "number", "description": "本金"},
                            "rate": {"type": "number", "description": "年化利率(小数)"},
                            "years": {"type": "integer", "description": "年限"}
                        },
                        "required": ["principal", "rate", "years"]
                    }
                }
            }
        ]

    def chat(self, user_prompt):
        print(f"[*] 正在思考: {user_prompt} ... (请耐心等待)")
        messages = [{'role': 'user', 'content': user_prompt}]

        try:
            # 第一次调用：让模型判断是否使用工具
            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=self.tools_schema, # 直接使用原生 tools 参数
            )
            
            msg = response['message']
            
            # 如果模型没有返回 tool_calls，直接输出回答
            if not msg.get('tool_calls'):
                print(f"[Agent]: {msg['content']}")
                return

            # 如果模型决定使用工具
            messages.append(msg) # 把模型的“思考过程”加到历史记录中
            
            for tool in msg['tool_calls']:
                fn_name = tool['function']['name']
                fn_args = tool['function']['parameters']
                
                print(f"[系统] 检测到工具调用: {fn_name} | 参数: {fn_args}")
                
                # 执行对应的 Python 函数
                if fn_name in self.available_functions:
                    func = self.available_functions[fn_name]
                    tool_result = func(**fn_args)
                    print(f"[系统] 工具运行结果: {tool_result}")
                    
                    # 把结果通过 'tool' 角色传回给模型
                    messages.append({
                        'role': 'tool',
                        'content': json.dumps(tool_result),
                        'name': fn_name
                    })

            # 第二次调用：让模型根据工具结果生成最终回答
            print("[*] 正在整理最终回复...")
            final_response = self.client.chat(
                model=self.model,
                messages=messages,
            )
            print(f"[Agent]: {final_response['message']['content']}")

        except Exception as e:
            print(f"\n[Error] 发生错误: {e}")
            print("建议：如果是因为超时(504)，请尝试换用 qwen2.5:7b 模型测试，或者进一步增加 timeout 时间。")

# --- 3. 运行测试 ---
if __name__ == "__main__":
    # 实例化 Agent
    agent = RealLLMAgent(model="qwen2.5:14b")
    
    # 测试 1: 简单对话
    # agent.chat("你好，你是谁？")
    
    print("-" * 50)
    
    # 测试 2: 复杂任务（通过工具）
    agent.chat("我要存50000块钱，存10年，年化4%，最后能拿多少？顺便看看北京天气怎么样。")