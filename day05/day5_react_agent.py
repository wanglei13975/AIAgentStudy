import requests
import json
import time
import re
import random

# --- 配置区 ---
# 依然保持长超时，适应你的 14b 模型
TIMEOUT_SECONDS = 600 
MODEL_NAME = "qwen2.5:14b"
API_URL = "http://localhost:11434/api/chat"
MAX_STEPS = 5  # 防止模型陷入死循环，最多允许它思考 5 轮

# ==========================================
# 1. 工具定义 (昨天那一套)
# ==========================================
def get_weather(city: str):
    print(f"    [系统] 正在查询 {city} 天气...")
    return {"city": city, "temperature": "20°C", "condition": "晴天", "remark": "适合出去玩"}

def get_stock_price(symbol: str):
    print(f"    [系统] 正在查询 {symbol} 股价...")
    # 模拟波动
    price = 101.21 + random.uniform(-2, 2) 
    return {"symbol": symbol, "price": round(price, 2), "currency": "USD"}

def calculate_investment(principal: float, rate: float, years: int):
    print(f"    [系统] 正在计算: 本金{principal}, 利率{rate}, 年限{years}...")
    try:
        # 防止模型有时候传字符串表达式进来（如 "9*101"）
        if isinstance(principal, str):
            principal = eval(principal)
    except:
        pass
        
    total = principal * (1 + rate) ** years
    return {"total": round(total, 2)}

available_functions = {
    "get_stock_price": get_stock_price,
    "calculate_investment": calculate_investment,
    "get_weather": get_weather,
}

# ==========================================
# 2. ReAct Agent 类 (今天的核心)
# ==========================================

class ReActAgent:
    def __init__(self, model_name):
        self.model_name = model_name
        self.messages = [] # Agent 的短期记忆
        
        # System Prompt：这是 Agent 的“灵魂”，规定了它的思考方式
        self.system_prompt = """
        你是一个精通金融的 AI Agent。你需要通过【思考-工具-观察】的循环来解决复杂问题。

        【可用工具】
        1. get_stock_price(symbol): 查询股价
        2. calculate_investment(principal, rate, years): 计算复利
           - 注意：rate 必须是小数（如 0.05）。principal 必须是具体数字。
        3. get_weather(city): 查询天气
        【思维模式】
        对于用户的每个问题，请严格遵守以下格式：
        
        Thought: 思考还需要做什么（用自然语言）。
        Action: {"function_name": "工具名", "parameters": {参数}}
        
        （系统会执行你的 Action 并反馈 Observation）
        
        Thought: 根据 Observation 思考下一步...
        ...
        
        【最终回答】
        如果不需要再使用工具，或者已经得到了答案，请直接输出答案（不要包含 Action JSON）。
        """

    def _call_llm(self):
        """发送请求给 Ollama (Requests版，防超时)"""
        payload = {
            "model": self.model_name,
            "messages": self.messages,
            "stream": False,
            "options": {"temperature": 0.1, "stop": ["Observation:"]} # 小技巧：让模型在 Observation 前停下，等待我们填入结果
        }
        
        try:
            print(f"[*] Agent 正在思考... (请等待)")
            resp = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
            resp.raise_for_status()
            return resp.json()['message']['content']
        except Exception as e:
            print(f"[Error] LLM 调用失败: {e}")
            return None

    def run(self, user_query):
        print(f"\n====== 任务开始: {user_query} ======")
        
        # 1. 初始化记忆
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        step_count = 0
        
        # 2. 进入 ReAct 循环
        while step_count < MAX_STEPS:
            step_count += 1
            print(f"\n--- 第 {step_count} 轮思考 ---")
            
            # (1) LLM 思考
            response_text = self._call_llm()
            if not response_text: break
            
            print(f"[Agent 回复]: {response_text}")
            
            # 把模型的回复加入记忆，形成连贯上下文
            self.messages.append({"role": "assistant", "content": response_text})

            # (2) 解析：看看有没有 JSON Action
            # 使用昨天学会的正则技巧
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if match:
                # --- 发现需要调用工具 ---
                try:
                    json_str = match.group()
                    tool_call = json.loads(json_str)
                    
                    fn_name = tool_call.get("function_name")
                    fn_args = tool_call.get("parameters")
                    
                    if fn_name in available_functions:
                        print(f"[Action] 捕获到工具调用: {fn_name}")
                        
                        # (3) Act: 执行工具
                        func = available_functions[fn_name]
                        tool_result = func(**fn_args)
                        
                        # (4) Observe: 构造观察结果
                        observation = f"Observation: {json.dumps(tool_result, ensure_ascii=False)}"
                        print(f"[Observation] {observation}")
                        
                        # 把观察结果作为 User 消息（或者 Tool 消息）塞回给模型
                        # 在手动 ReAct 模式下，通常模拟成 User 说的话
                        self.messages.append({"role": "user", "content": observation})
                        
                    else:
                        print(f"[Error] 试图调用不存在的工具: {fn_name}")
                        # 也要反馈错误给模型，让它知道错了
                        self.messages.append({"role": "user", "content": f"System Error: Tool {fn_name} not found."})
                        
                except Exception as e:
                    print(f"[Error] 工具执行或解析异常: {e}")
            else:
                # --- 没有 JSON，说明模型给出了最终答案 ---
                print("\n✅ 任务完成！Agent 停止了循环。")
                break
        
        if step_count >= MAX_STEPS:
            print("\n[Warning] 达到最大步数，强制停止。")

# ==========================================
# 3. 运行
# ==========================================
if __name__ == "__main__":
    agent = ReActAgent("qwen2.5:14b")
    
    # 使用昨天那个导致程序中断的复杂问题
    # 观察它是否能自动走完：查股价 -> 算收益 -> 给结论
    # agent.run("我有 1000 美元。如果现在买入 AAPL，假设年化增长 10%，持有 5 年后总共有多少钱？")
    agent.run("明天北京天气怎么样？")