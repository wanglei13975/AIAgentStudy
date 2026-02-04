import os
import time
from datetime import datetime

# --- 1. 网络配置 ---
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

# --- 2. 工具定义 (关键修复点) ---

@tool
def get_stock_price(symbol: str) -> str:
    """查询指定股票的当前价格。"""
    # 简单的模拟返回
    return f"{symbol} price is 100.0"

@tool
def calculator(expression: str) -> str:
    """通用数学计算器。"""
    try:
        # 移除可能多余的等号或空格
        clean_expression = expression.strip("=")
        return str(eval(clean_expression))
    except:
        return "Calculation Error"

# 【重要修复】增加一个 dummy 参数，专门用来接收模型传来的 "None"
@tool
def get_current_time(input_str: str = "") -> str:
    """
    获取当前系统时间。
    这个工具不需要参数，但如果模型传了参数，请忽略。
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [get_stock_price, calculator, get_current_time]

# --- 3. 初始化模型 ---
print("--- 初始化 Agent ---")
# 【修复】移除了 stop=["Observation:"]，防止和 create_react_agent 内部逻辑冲突
llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0.1,
    timeout=600.0, 
)

# --- 4. ReAct Prompt ---
template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

prompt = PromptTemplate.from_template(template)

# --- 5. 构建与运行 ---
agent = create_react_agent(llm, tools, prompt)

# handle_parsing_errors=True 会帮我们处理一些格式小错误
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True
)

if __name__ == "__main__":
    query = "现在几点了？我有 1000 美元，如果全仓买入 AAPL (股价翻倍后)，我有多少钱？"
    
    print(f"\n[用户]: {query}\n")
    try:
        # 使用 invoke 启动
        result = agent_executor.invoke({"input": query})
        print(f"\n[最终回复]: {result['output']}")
    except Exception as e:
        print(f"出错详情: {e}")