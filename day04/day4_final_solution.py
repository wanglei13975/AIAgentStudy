import requests
import json
import time

# --- 配置区 ---
# 既然 14b 慢，我们给它足够的时间（10分钟），绝不让它超时断开
TIMEOUT_SECONDS = 600 
MODEL_NAME = "qwen2.5:14b"
API_URL = "http://localhost:11434/api/chat"

# --- 1. 定义本地工具 ---
def get_weather(city: str):
    return {"city": city, "temperature": "25°C", "condition": "晴天"}

def calculate_investment(principal: float, rate: float, years: int):
    total = principal * (1 + rate) ** years
    return {"total": round(total, 2)}

available_functions = {
    "get_weather": get_weather,
    "calculate_investment": calculate_investment,
}

# --- 2. 核心函数：手动发送 HTTP 请求 ---
def chat_with_model(messages):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,  # 关闭流式，一次性拿回结果
        "options": {
            "temperature": 0.1 # 低温度，保证输出格式稳定
        }
    }
    
    print(f"[*] 正在发送请求给 {MODEL_NAME}，请耐心等待（最长等待 {TIMEOUT_SECONDS} 秒）...")
    start = time.time()
    
    try:
        # 关键点：timeout 设置为 600 秒
        response = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
        response.raise_for_status() # 如果状态码不是 200，抛出异常
        
        print(f"[*] 请求耗时: {time.time() - start:.2f} 秒")
        return response.json()['message']
        
    except requests.exceptions.Timeout:
        print("[X] 错误：模型推理超时！这说明 14b 对你的机器来说太重了。")
        return None
    except Exception as e:
        print(f"[X] 请求发生错误: {e}")
        return None

# --- 3. 编排 Agent 逻辑 ---
def run_agent():
    # 构造 System Prompt：强行教模型输出 JSON，绕过 tools 参数限制
    system_prompt = """
    你是一个智能助手。你可以调用以下工具：
    1. get_weather(city): 查询天气
    2. calculate_investment(principal, rate, years): 计算投资
    
    规则：
    - 如果用户问题需要使用工具，请**只输出**一个 JSON 格式，不要包含任何其他废话。
    - JSON 格式必须为：{"function_name": "工具名", "parameters": {参数字典}}
    - 如果不需要工具，直接用自然语言回答。
    """
    
    user_question = "我想存5000块钱，存3年，年利率5%，最后有多少钱？"
    print(f"用户问题: {user_question}")
    print("-" * 50)

    # 初始化对话历史
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    # 第一轮交互：获取模型意图
    reply_message = chat_with_model(messages)
    
    if not reply_message:
        return

    content = reply_message['content']
    print(f"[模型原始回复]: {content}")

    # 尝试解析 JSON
    try:
        # 清理可能存在的 markdown 符号
        clean_json = content.replace("```json", "").replace("```", "").strip()
        tool_call = json.loads(clean_json)
        
        if "function_name" in tool_call:
            fn_name = tool_call["function_name"]
            fn_args = tool_call["parameters"]
            
            print(f"\n[Agent] 决定调用工具: {fn_name}")
            print(f"[Agent] 参数: {fn_args}")
            
            # 执行本地 Python 代码
            if fn_name in available_functions:
                func = available_functions[fn_name]
                result = func(**fn_args)
                print(f"[System] 工具运行结果: {result}")
                
                # 第二轮交互：把结果给模型总结
                # 注意：手动模式下，我们把结果伪装成 system 提示或者 user 提示发回去
                summary_prompt = f"工具 {fn_name} 的执行结果是：{json.dumps(result)}。请根据此结果回答用户之前的问题。"
                
                messages.append({"role": "assistant", "content": content}) # 存入模型之前的思考
                messages.append({"role": "user", "content": summary_prompt}) # 存入结果
                
                print("\n[*] 正在请求模型进行最终总结...")
                final_reply = chat_with_model(messages)
                if final_reply:
                    print(f"\n[Agent 最终回答]: {final_reply['content']}")
            
    except json.JSONDecodeError:
        print("\n[Agent] 模型没有调用工具，直接进行了回答。")

if __name__ == "__main__":
    run_agent()