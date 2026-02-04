import os
import re

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# 2. 定义工具 (给 Worker 用的)
@tool
def search_data(query: str) -> str:
    """只有当需要查询事实、数据、历史信息时使用。"""
    # 模拟搜索结果
    if "人口" in query:
        return "数据中心：2024年统计显示，该城市人口为 800 万。"
    if "GDP" in query:
        return "数据中心：2023年 GDP 为 1.5 万亿。"
    return "数据中心：未找到具体数据，但趋势是增长的。"

@tool
def calculate_calc(expression: str) -> str:
    """计算数学表达式，如 '100 * 2'。"""
    try:
        # 注意：eval 有安全风险，仅限本地学习使用
        return str(eval(expression))
    except:
        return "计算错误"

tools = [search_data, calculate_calc]

# 3. 初始化模型
llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

# 4. 构建 Worker (ReAct Agent)
# 这就是我们 Day 7 写的那个东西
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

# 这个 Executor 就是我们的“工程师”，给它一个具体指令，它就能搞定
worker_executor = AgentExecutor(agent=worker_agent, tools=tools, verbose=False, handle_parsing_errors=True)

print(">> Worker (工程师) 已就绪...")

# 5. 构建 Planner Chain
planner_template = """
你是一个高级项目经理。
用户的目标是：{objective}

请将这个目标拆解为 3-5 个具体的、可执行的步骤。
每个步骤必须是简短的单行指令。
不需要解释，只需要列出步骤。

格式要求（严格遵守）：
1. 第一步干什么
2. 第二步干什么
3. ...
"""

planner_prompt = PromptTemplate.from_template(planner_template)
planner_chain = planner_prompt | llm

print(">> Planner (项目经理) 已就绪...")

def parse_plan(plan_text: str):
    """简单的解析器，提取出 '1. xxx' 这样的行"""
    steps = []
    for line in plan_text.split('\n'):
        # 匹配 "1. ", "2. " 开头的行
        line = line.strip()
        if re.match(r'^\d+\.', line):
            # 去掉前面的数字和点，只留任务描述
            step_content = re.sub(r'^\d+\.\s*', '', line)
            steps.append(step_content)
    return steps

def run_plan_and_execute(objective: str):
    print(f"\n====== 收到复杂任务：{objective} ======")
    
    # 1. 制定计划
    print("Step 1: 正在制定计划 (Planner 思考中)...")
    plan_text = planner_chain.invoke({"objective": objective}).content
    print(f"--- 计划清单 ---\n{plan_text}\n----------------")
    
    steps = parse_plan(plan_text)
    if not steps:
        print("解析计划失败，模型可能没按格式输出。")
        return

    # 2. 执行计划
    final_context = "" # 用来累积上下文，把上一步的结果告诉下一步
    
    for i, step in enumerate(steps):
        print(f"\n>> 正在执行第 {i+1} 步: {step}")
        
        # 构造 Worker 的输入
        # 关键技巧：把之前的执行结果拼接到 Prompt 里，
        # 这样 Worker 才能知道前面发生了什么（比如第一步查到了数字，第二步才能算）
        worker_input = f"""
        当前任务：{step}
        
        已知信息（之前步骤的成果）：
        {final_context}
        """
        
        try:
            result = worker_executor.invoke({"input": worker_input})
            output = result['output']
            print(f"   [执行结果]: {output}")
            
            # 累积上下文
            final_context += f"步骤 {i+1} 结果: {output}\n"
            
        except Exception as e:
            print(f"   [执行出错]: {e}")

    print("\n====== 任务完成！ ======")
    print("最终汇总报告：")
    print(final_context)

# --- 启动 ---
if __name__ == "__main__":
    # 测试一个复杂任务
    # 这个任务如果直接扔给 ReAct，它可能不知道先查哪个，容易乱
    task = "请调查 A 市的人口和 B 市的 GDP，然后计算：如果 A 市每人贡献 10 元，总额是 B 市 GDP 的百分之多少？"
    
    run_plan_and_execute(task)