import os
import re

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# --- 复用 Day 13 的旅行工具 ---
@tool
def check_flight_price(destination: str) -> str:
    """查询去往某地的单程机票。参数 destination 是目的地。"""
    # 这里的关键是：模拟真实 API，如果没给出发地，我们假设它不知道
    # 既然是模拟，我们简化逻辑，假设 API 只需要目的地
    # 但为了演示 Critic，我们稍后会在 Critic 里挑刺“没问出发地”
    if "上海" in destination:
        return "机票价格是 800 元。"
    if "北京" in destination:
        return "机票价格是 600 元。"
    return "未查询到航班。"

@tool
def check_hotel_price(destination: str) -> str:
    """查询某地酒店价格。"""
    if "上海" in destination:
        return "上海酒店 500 元/晚。"
    if "北京" in destination:
        return "北京酒店 400 元/晚。"
    return "未查询到酒店。"

@tool
def calculate_cost(expression: str) -> str:
    """数学计算。"""
    try:
        clean_expr = expression.replace("元", "").replace(" ", "")
        return str(eval(clean_expr))
    except:
        return "计算错误"

tools = [check_flight_price, check_hotel_price, calculate_cost]

# --- 初始化模型与 Worker ---
llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

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
worker_agent = create_react_agent(llm, tools, worker_prompt)
# 注意：verbose=False
worker_executor = AgentExecutor(agent=worker_agent, tools=tools, verbose=False, handle_parsing_errors=True)

print("1. 工具人 (Worker) 已就绪...")

# --- 2. 定义 Planner (规划者) ---
# --- 修改后的 Planner Prompt ---
planner_template = """
你是一位旅行顾问。用户的目标是：{objective}

{feedback}

请制定（或修改）一个逻辑严密的 3-5 步执行计划。

【关键约束】：
1. **格式必须严格**：每一行必须以 "1. ", "2. " (数字+点) 开头。不要用"第一步"。
2. **拒绝交互**：不要向用户提问！不要说“请告诉我”。
3. **自动补全**：如果用户没提供天数，**默认假设玩 3 天**。如果没提供具体日期，**默认查询当前价格**。
4. **指令化**：步骤必须是 Agent 可以执行的动作（如“查询...”、“计算...”）。

格式示例：
1. 查询上海的酒店价格
2. 假设行程为 3 天，计算住宿总费用
"""

planner_prompt = PromptTemplate.from_template(planner_template)
planner_chain = planner_prompt | llm

# --- 3. 定义 Critic (质检员) ---
# --- 修改后的 Critic Prompt ---
critic_template = """
用户目标：{objective}
当前计划：
{plan}

请审查计划。如果发现以下任何问题，请拒绝并通过：
1. **格式错误**：步骤不是以数字加点（如 "1."）开头。
2. **反问用户**：计划中包含“请提供”、“请告诉”等需要用户回答的步骤。（Agent 无法与用户对话，必须自己假设）。
3. **缺少参数**：没有具体的城市名或假设的天数。

如果计划完美且可直接执行，输出 "PLAN_OK"。
否则，指出具体问题。
"""

critic_prompt = PromptTemplate.from_template(critic_template)
critic_chain = critic_prompt | llm

print("2. 规划部 (Planner & Critic) 已就绪...")

# --- 4. 调度逻辑 (带自省机制) ---

def parse_plan(plan_text: str):
    """(复用) 提取步骤"""
    steps = []
    for line in plan_text.split('\n'):
        line = line.strip()
        if re.match(r'^\d+\.', line):
            step_content = re.sub(r'^\d+\.\s*', '', line)
            steps.append(step_content)
    return steps

def run_self_correcting_agent(objective: str):
    print(f"\n====== 收到需求：{objective} ======")
    
    # === 阶段一：规划与自省 (Plan & Critique) ===
    
    current_plan = ""
    feedback = "" # 初始没有反馈
    max_retries = 3 # 最多改 3 次，防止死循环
    
    print("\n[开始规划阶段]")
    
    for i in range(max_retries):
        print(f"\n>> 第 {i+1} 轮规划思考中...")
        
        # 1. 生成计划 (如果 feedback 有内容，Planner 会参考)
        feedback_prompt = f"上一轮计划的反馈意见：{feedback}\n请根据反馈修正计划。" if feedback else ""
        current_plan = planner_chain.invoke({
            "objective": objective,
            "feedback": feedback_prompt
        }).content
        
        print(f"--- 草拟计划 (v{i+1}) ---\n{current_plan}\n----------------")
        
        # 2. 质检 (Critic)
        print(">> Critic 正在审核...")
        review = critic_chain.invoke({
            "objective": objective,
            "plan": current_plan
        }).content
        
        print(f"--- 审核结果 ---\n{review}\n----------------")
        
        # 3. 判断是否通过
        if "PLAN_OK" in review:
            print("✅ 计划审核通过！")
            break
        else:
            print("❌ 计划被打回，准备修改。")
            feedback = review # 把审核意见作为下一轮的 feedback
            
    else:
        # 如果循环结束了还没 break，说明超过了最大重试次数
        print("⚠️ 警告：计划未能完全通过审核，将强制执行最后一版。")

    # === 阶段二：执行 (Execute) ===
    print("\n[开始执行阶段]")
    steps = parse_plan(current_plan)
    context = ""
    
    for i, step in enumerate(steps):
        print(f"\n>> 执行步骤 {i+1}: {step}")
        worker_input = f"当前任务：{step}\n已知信息：\n{context}"
        try:
            result = worker_executor.invoke({"input": worker_input})
            output = result['output']
            print(f"   [结果]: {output}")
            context += f"步骤 {i+1} output: {output}\n"
        except Exception as e:
            print(f"   [出错]: {e}")

    print("\n====== 最终报告 ======")
    print(context)

if __name__ == "__main__":
    # 测试案例：故意给一个模糊的需求
    # 我们故意不说去几天，看看 Critic 会不会跳出来
    task = "我想去上海玩，帮我算算酒店要花多少钱？"
    
    run_self_correcting_agent(task)