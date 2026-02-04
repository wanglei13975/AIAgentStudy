import ollama
import json

# --- 1. 定义工具 (真实的 Python 函数) ---
def get_weather(city: str):
    print(f"  >>> 正在调用天气查询: {city}")
    return {"city": city, "temperature": "25°C", "condition": "晴天"}

def calculate_investment(principal: float, rate: float, years: int):
    print(f"  >>> 正在调用计算器: 本金{principal}, 利率{rate}, 年限{years}")
    total = principal * (1 + rate) ** years
    return {"total": round(total, 2)}

# 工具映射表
available_functions = {
    "get_weather": get_weather,
    "calculate_investment": calculate_investment,
}

# --- 2. 核心：用 System Prompt 替代 tools 参数 ---
# 这是手动实现 ReAct Agent 的关键
SYSTEM_PROMPT = """
你是一个全能助手。你可以通过生成特定的 JSON 格式来调用工具。

【可用工具】:
1. get_weather(city): 查询天气
2. calculate_investment(principal, rate, years): 计算投资

【重要规则】:
- 如果需要使用工具，请只输出一个 JSON 对象，格式必须如下：
  {"function_name": "工具名称", "parameters": {参数键值对}}
- 不要输出任何额外的解释文本，只输出 JSON。
- 如果不需要工具，请直接用自然语言回答。
"""

def run_agent_manual(user_prompt):
    print(f"\n用户: {user_prompt}")
    print("-" * 40)
    
    # 步骤 1: 发送问题给模型 (没有 tools 参数，只有 System Prompt)
    response = ollama.chat(
        model='qwen2.5:14b', # 你的本地模型
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_prompt}
        ],
        options={'temperature': 0} # 让模型更严谨，便于输出 JSON
    )
    
    content = response['message']['content'].strip()
    
    # 步骤 2: 检查模型是否想调用工具 (判断是不是 JSON)
    try:
        # 尝试清理一下 markdown 符号 (有些模型喜欢加 ```json )
        clean_content = content.replace("```json", "").replace("```", "").strip()
        
        # 尝试解析 JSON
        tool_call = json.loads(clean_content)
        
        # 确认是我们的工具调用格式
        if isinstance(tool_call, dict) and "function_name" in tool_call:
            fn_name = tool_call["function_name"]
            fn_args = tool_call.get("parameters", {})
            
            print(f"[Agent 思考] 我需要调用工具: {fn_name}")
            
            # 执行 Python 函数
            if fn_name in available_functions:
                func = available_functions[fn_name]
                tool_result = func(**fn_args)
                print(f"[System 结果] {tool_result}")
                
                # 步骤 3: 把结果传回给模型，进行总结
                final_prompt = f"""
                用户问题: {user_prompt}
                工具执行结果: {json.dumps(tool_result, ensure_ascii=False)}
                请根据工具结果，用自然语言回答用户。
                """
                
                final_response = ollama.chat(
                    model='qwen2.5:14b',
                    messages=[{'role': 'user', 'content': final_prompt}]
                )
                print(f"[Agent 回复] {final_response['message']['content']}")
            else:
                print(f"[Error] 模型想要调用不存在的工具: {fn_name}")
        else:
            # 解析成功但格式不对，或者是普通对话
            print(f"[Agent 回复] {content}")

    except json.JSONDecodeError:
        # 解析失败，说明模型返回的是普通文本，不需要调用工具
        print(f"[Agent 回复] {content}")

if __name__ == "__main__":
    # 测试 1: 需要调用工具
    run_agent_manual("我想存5000块钱，存3年，年利率5%，最后有多少钱？")
    
    # 测试 2: 不需要调用工具
    run_agent_manual("你好，讲个笑话。")