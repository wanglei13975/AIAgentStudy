import requests
import json
import time
import random  # 用来模拟股票波动
import re

# --- 配置区 ---
TIMEOUT_SECONDS = 600 
MODEL_NAME = "qwen2.5:14b"
API_URL = "http://localhost:11434/api/chat"

# ==========================================
# 1. 定义工具 (这里是 Agent 的“手”)
# ==========================================

def get_weather(city: str):
    return {"city": city, "temperature": "25°C", "condition": "晴天"}

def calculate_investment(principal: float, rate: float, years: int):
    # 简单的复利计算
    total = principal * (1 + rate) ** years
    return {"total": round(total, 2)}

# 【新增工具】模拟查询股票价格
def get_stock_price(symbol: str):
    print(f"  >>> (本地代码执行) 正在联网查询 {symbol} 的股价...")
    # 这里模拟一个随机股价，实际开发中可以接新浪财经/雅虎财经 API
    base_price = 100.0
    current_price = base_price + random.uniform(-10, 10)
    return {"symbol": symbol, "price": round(current_price, 2), "currency": "USD"}

# 工具注册表：将函数名映射到真实的 Python 函数
available_functions = {
    "get_weather": get_weather,
    "calculate_investment": calculate_investment,
    "get_stock_price": get_stock_price, # 【记得在这里注册！】
}

# ==========================================
# 2. 核心逻辑 (这里是 Agent 的“大脑”连接器)
# ==========================================

def chat_with_model(messages):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()['message']
    except Exception as e:
        print(f"[Error] {e}")
        return None

def run_agent():
    # 【重点】在这里修改 Prompt，教模型如何使用新工具，并修复利率的 Bug
    system_prompt = """
    你是一个金融助手。你可以通过生成 JSON 来调用以下工具：

    1. get_weather(city): 查询天气
    2. calculate_investment(principal, rate, years): 计算投资
       - 注意：rate 参数必须是小数。例如 5% 请传 0.05
    3. get_stock_price(symbol): 查询股票价格
       - symbol 例如: AAPL, TSLA, NVDA

    规则：
    - 如果需要使用工具，只输出 JSON：{"function_name": "...", "parameters": {...}}
    - 不需要工具则直接回答。
    """
    
    # 我们测试一个复杂的复合问题：既要查股票，又要算投资
    user_question = "我现在有1000美元，如果买入 AAPL 股票（假设股价不变），并假设每年涨 10%，持有 5 年后大概多少钱？请先帮我查查 AAPL 现在的价格，然后帮我算一下。"
    
    print(f"用户: {user_question}")
    print("-" * 50)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    # --- 第一轮：Agent 思考 ---
    reply = chat_with_model(messages)
    if not reply: return
    
    content = reply['content']
    print(f"[Agent 思考 1]: {content}")

    # --- 处理工具调用 ---
    try:
        # 【核心修复】不再直接 replace，而是用正则查找第一个 { 和最后一个 } 之间的内容
        # 意思就是：不管你前面说了多少废话，我只要 JSON 那一段
        match = re.search(r'\{.*\}', content, re.DOTALL)
        
        if match:
            json_str = match.group()
            tool_call = json.loads(json_str)
            
            if "function_name" in tool_call:
                fn_name = tool_call["function_name"]
                fn_args = tool_call["parameters"]
                
                print(f"\n[Agent] 决定调用工具: {fn_name}")
                
                # 执行工具
                if fn_name in available_functions:
                    func = available_functions[fn_name]
                    result = func(**fn_args)
                    print(f"[工具结果] {result}")
                    
                    # --- 第二轮：把结果给模型 ---
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": f"工具执行结果：{json.dumps(result)}。请继续你的分析。" })
                    
                    print("\n[*] 正在请求 Agent 下一步动作...")
                    final_reply = chat_with_model(messages)
                    print(f"[Agent 思考 2]: {final_reply['content']}")
        else:
            print("[Agent] 回复中未发现 JSON，视为普通对话。")

    except json.JSONDecodeError:
        print("[Agent] JSON 解析失败，可能格式有误。")

if __name__ == "__main__":
    run_agent()