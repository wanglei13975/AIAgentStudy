import os
import re

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# --- 定义新工具 (Travel Tools) ---

@tool
def check_flight_price(destination: str) -> str:
    """
    查询去往某地的单程机票价格。
    参数 destination 是目的地名称（如：上海、北京）。
    """
    # 模拟数据
    if "上海" in destination:
        return "去往上海的机票价格是 800 元。"
    if "北京" in destination:
        return "去往北京的机票价格是 600 元。"
    return "未查询到该目的地的航班信息。"

@tool
def check_hotel_price(destination: str) -> str:
    """
    查询某地的酒店每晚价格。
    参数 destination 是目的地名称。
    """
    # 模拟数据
    if "上海" in destination:
        return "上海的酒店每晚价格是 500 元。"
    if "北京" in destination:
        return "北京的酒店每晚价格是 400 元。"
    return "未查询到该目的地的酒店信息。"

@tool
def calculate_cost(expression: str) -> str:
    """
    数学计算工具。用于计算总价。
    例如输入 '800 + 500 * 3'。
    """
    try:
        # 简单的 eval，仅供本地学习
        # 移除可能导致错误的字符
        clean_expr = expression.replace("元", "").replace(" ", "")
        return str(eval(clean_expr))
    except:
        return "计算出错，请检查格式。"

# 打包工具
tools = [check_flight_price, check_hotel_price, calculate_cost]

print("1. 旅行工具箱已准备就绪...")

# --- 初始化模型与 Worker ---

llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

# ReAct Prompt (标准模板，不需要改)
worker_template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

worker_prompt = PromptTemplate.from_template(worker_template)

# 创建 Worker
worker_agent = create_react_agent(llm, tools, worker_prompt)
worker_executor = AgentExecutor(
    agent=worker_agent, 
    tools=tools, 
    verbose=False, 
    handle_parsing_errors=True
)

print("2. 执行者 (Worker) 已就绪...")

# --- 构建 Planner (大脑) ---

# 修改 Planner Prompt，强制要求具体化
planner_template = """
你是一位资深旅行顾问。
用户的目标是：{objective}

请根据用户的需求，将其拆解为逻辑严密的 3-5 个执行步骤。

【关键要求】：
1. **步骤必须具体**：不要说“查询目的地”，必须直接说出地名（例如：“查询去上海的机票”）。
2. **包含参数**：如果涉及计算，必须在步骤中包含具体数字（例如：“计算 3 晚的住宿费”）。
3. **忽略缺失信息**：如果用户没说出发地，就默认只查询“去往该地”的单程机票。

格式要求（严格遵守，每行一个步骤）：
1. 第一步干什么
2. 第二步干什么
...
"""

planner_prompt = PromptTemplate.from_template(planner_template)
planner_chain = planner_prompt | llm

print("3. 规划师 (Planner) 已就绪...")

# --- 调度逻辑 (Orchestrator) ---

def parse_plan(plan_text: str):
    """提取步骤的解析器"""
    steps = []
    for line in plan_text.split('\n'):
        line = line.strip()
        # 匹配 "1. ", "2. " 等开头的行
        if re.match(r'^\d+\.', line):
            step_content = re.sub(r'^\d+\.\s*', '', line)
            steps.append(step_content)
    return steps

def run_travel_plan(objective: str):
    print(f"\n====== 收到客户需求：{objective} ======")
    
    # 1. 规划阶段
    print("Step 1: 顾问正在规划行程...")
    plan_text = planner_chain.invoke({"objective": objective}).content
    print(f"--- 建议方案 ---\n{plan_text}\n----------------")
    
    steps = parse_plan(plan_text)
    if not steps:
        print("解析计划失败。")
        return

    # 2. 执行阶段
    context = "" # 记忆黑板
    
    for i, step in enumerate(steps):
        print(f"\n>> 执行步骤 {i+1}: {step}")
        
        # 构造 Worker 的 Prompt，把之前的查价结果告诉它
        worker_input = f"""
        当前任务：{step}
        
        已知信息（上下文）：
        {context}
        """
        
        try:
            result = worker_executor.invoke({"input": worker_input})
            output = result['output']
            print(f"   [结果]: {output}")
            
            # 记录结果，供下一步使用
            context += f"步骤 {i+1} output: {output}\n"
            
        except Exception as e:
            print(f"   [出错]: {e}")

    print("\n====== 最终预算报告 ======")
    print(context)

# --- 启动测试 ---
if __name__ == "__main__":
    # 测试案例：去上海玩 3 天
    # 预期逻辑：机票800 + 酒店500*3 = 2300
    task = "我想去上海玩 3 天，请帮我计算机票和酒店的总预算。"
    
    run_travel_plan(task)