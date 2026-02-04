import requests
import json
import time
import re

# --- 基础配置 (保持不变) ---
TIMEOUT_SECONDS = 600
MODEL_NAME = "qwen2.5:14b"
API_URL = "http://localhost:11434/api/chat"
MAX_STEPS = 6  # 因为步骤较多，稍微给多一点步数

# --- 1. 定义新工具 ---

# 模拟的商品数据库
PRODUCT_DB = {
    "iphone15": 5999,
    "macbook": 12999,
    "ps5": 3500,
    "switch": 2000,
    "airpods": 1000
}

def check_price(product_name: str):
    """查询商品价格工具"""
    # 模拟模糊匹配，把用户输入的 "iPhone 15" 转成 "iphone15"
    key = product_name.lower().replace(" ", "")
    
    print(f"    [系统] 正在数据库中检索: {product_name}...")
    
    if key in PRODUCT_DB:
        price = PRODUCT_DB[key]
        return {"product": product_name, "price": price, "currency": "CNY"}
    else:
        return {"error": f"未找到商品 {product_name}，我们在售的只有: {list(PRODUCT_DB.keys())}"}

def calculator(expression: str):
    """通用计算器工具"""
    print(f"    [系统] 正在计算: {expression}...")
    try:
        # 注意：eval 在生产环境中很危险，但作为学习练习非常方便
        # 它能计算 "20000 - 5999 - 12999" 这样的字符串
        result = eval(expression) 
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": "计算公式错误", "details": str(e)}

# 注册工具
available_functions = {
    "check_price": check_price,
    "calculator": calculator,
}

# --- 2. 核心 Agent 类 ---

class ShoppingAgent:
    def __init__(self, model_name):
        self.model_name = model_name
        self.messages = []
        
        # 【修改点】System Prompt
        self.system_prompt = """
        你是一个精明的购物助手。你需要通过【思考-工具-观察】的循环来回答用户的预算问题。

        【可用工具】
        1. check_price(product_name): 查询商品价格。
           - 例如: check_price("iPhone15")
        2. calculator(expression): 通用计算器。
           - 支持加减乘除，例如: calculator("20000 - 5999 - 12999")
           - 当你需要进行数学计算时，必须使用此工具，不要自己心算。

        【思维模式】 (严格遵守 ReAct 格式)
        Thought: 思考还需要做什么。
        Action: {"function_name": "工具名", "parameters": {参数}}
        Observation: (这里会显示工具结果)
        ...
        Final Answer: (当得到最终结果时，用自然语言回答)
        """

    # ... 下面的 _call_llm 和 run 方法可以直接复制昨天 day5_react_agent.py 的代码 ...
    # ... 为了方便，我把 run 方法的核心部分贴在下面，你确保它在类里面即可 ...

    def _call_llm(self):
        payload = {
            "model": self.model_name,
            "messages": self.messages,
            "stream": False,
            "options": {"temperature": 0.1, "stop": ["Observation:"]}
        }
        try:
            print(f"[*] Agent 正在思考...")
            resp = requests.post(API_URL, json=payload, timeout=TIMEOUT_SECONDS)
            resp.raise_for_status()
            return resp.json()['message']['content']
        except Exception as e:
            print(f"[Error] {e}")
            return None

    def run(self, user_query):
        print(f"\n====== 🛒 购物任务: {user_query} ======")
        self.messages = [{"role": "system", "content": self.system_prompt},
                         {"role": "user", "content": user_query}]
        
        step_count = 0
        while step_count < MAX_STEPS:
            step_count += 1
            print(f"\n--- Step {step_count} ---")
            
            response = self._call_llm()
            if not response: break
            
            print(f"[Agent]: {response}")
            self.messages.append({"role": "assistant", "content": response})
            
            # 正则提取 JSON
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                try:
                    tool_call = json.loads(match.group())
                    fn_name = tool_call.get("function_name")
                    fn_args = tool_call.get("parameters")
                    
                    if fn_name in available_functions:
                        print(f"[Action] 执行工具: {fn_name}")
                        func = available_functions[fn_name]
                        result = func(**fn_args)
                        
                        observation = f"Observation: {json.dumps(result, ensure_ascii=False)}"
                        print(f"[Observation] {observation}")
                        self.messages.append({"role": "user", "content": observation})
                    else:
                        self.messages.append({"role": "user", "content": "Error: Tool not found"})
                except:
                    pass
            else:
                print("\n✅ 任务完成")
                break
if __name__ == "__main__":
    agent = ShoppingAgent("qwen2.5:14b")
    
    # 这是一个典型的 3 步任务：
    # 1. 查 iPhone 价格
    # 2. 查 MacBook 价格
    # 3. 用计算器算余额
    agent.run("我有 20000 元预算。我想买一台 iPhone15 和一台 MacBook。请帮我查查价格，算算买完这两个之后，我还剩多少钱？")