import json
import requests

# 模拟一个天气查询工具
def get_weather(city: str):
    # 实际项目中这里可以调用 openweather API
    print(f"--- 正在调用本地函数：查询 {city} 的天气 ---")
    return {"city": city, "temperature": "25°C", "condition": "晴天"}

# 模拟一个复杂的数学计算工具
def calculate_investment(principal: float, rate: float, years: int):
    print(f"--- 正在调用本地函数：计算投资收益 ---")
    total = principal * (1 + rate) ** years
    return {"total": round(total, 2)}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如：北京"}
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
                    "rate": {"type": "number", "description": "年化利率（如0.05代表5%）"},
                    "years": {"type": "integer", "description": "投资年限"}
                },
                "required": ["principal", "rate", "years"]
            }
        }
    }
]

import ollama

def run_agent(user_prompt):
    print(f"\n用户提问: {user_prompt}")
    
    # 1. 第一次调用：将问题和工具定义传给模型
    response = ollama.chat(
        model='qwen2.5:14b',
        messages=[{'role': 'user', 'content': user_prompt}],
        tools=tools,
    )

    message = response['message']

    # 2. 判断模型是否决定调用工具
    if message.get('tool_calls'):
        # 建立函数映射表
        available_functions = {
            "get_weather": get_weather,
            "calculate_investment": calculate_investment,
        }

        # 处理模型发出的每一个工具调用请求
        for tool in message['tool_calls']:
            function_name = tool['function']['name']
            arguments = tool['function']['parameters']
            
            # 执行本地代码
            function_to_call = available_functions[function_name]
            function_response = function_to_call(**arguments)

            # 3. 第二次调用：将函数执行结果反馈给模型
            final_response = ollama.chat(
                model='qwen2.5:14b',
                messages=[
                    {'role': 'user', 'content': user_prompt},
                    message, # 模型之前的回复
                    {
                        'role': 'tool',
                        'content': json.dumps(function_response),
                        'name': function_name,
                    }
                ],
            )
            print("Agent 最终回复:", final_response['message']['content'])
    else:
        print("模型认为不需要调用工具:", message['content'])

# 测试运行
if __name__ == "__main__":
    run_agent("我想在上海投资10000元，年化利率6%，放5年，最后能拿多少钱？顺便告诉我上海天气。")