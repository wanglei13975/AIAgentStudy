import os
import re

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# --- 1. 定义工具 (Tools) ---
@tool
def calculator(expression: str) -> str:
    """
    强大的数学计算器。
    输入必须是纯数学表达式，例如 "100 * 2 + 50"。
    """
    try:
        # 移除可能干扰的字符，只留数字和运算符
        # 这是一个简单的安全过滤，防止 exec 执行恶意代码
        clean_expr = expression.replace(" ", "").replace("=", "")
        # 仅允许包含数字和运算符
        if not re.match(r'^[\d\+\-\*\/\(\)\.]+$', clean_expr):
             return "错误：输入包含非法字符，只允许数字和运算符。"
        
        return str(eval(clean_expr))
    except Exception as e:
        return f"计算错误: {e}"

tools = [calculator]

# --- 2. 初始化 Worker (执行者) ---
llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

# 标准 ReAct 模板 (不用改)
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

# 创建执行器
worker_executor = AgentExecutor(
    agent=worker_agent, 
    tools=tools, 
    verbose=False, 
    handle_parsing_errors=True
)

print(">> Step 1: 计算工具人 (Worker) 已就绪...")

# --- 3. 定义 Planner (数学课代表) ---
# --- 修改后的 Planner (故意诱导它偷懒) ---
planner_template = """
你是一名数学课代表。
现在的任务是：{objective}

{feedback}

请制定一个计算计划。
为了效率，**请尽量将计算合并为一个步骤完成**，不要过于繁琐。

【格式死命令】：每一行必须以 "1. ", "2. " (数字+点) 开头。

现在请写出你的计划：
"""

planner_prompt = PromptTemplate.from_template(planner_template)
planner_chain = planner_prompt | llm

# --- 4. 定义 Critic (苛刻的数学老师) ---
# 负责检查计划是否太偷懒
critic_template = """
用户问题：{objective}
当前计划：
{plan}

你是一名苛刻的数学老师。请检查上面的计划。
你的要求如下：
1. **必须分步**：如果计划只有一步（例如直接计算整个大公式），必须**打回**！要求必须拆解成至少 2 个步骤（先算括号里的，再算外面的）。
2. **格式正确**：必须以数字列表形式开头。

如果计划太偷懒（没拆解步骤），请输出具体修改意见。
如果计划完美（步骤拆解清晰），请只输出 "PLAN_OK"。
"""

critic_prompt = PromptTemplate.from_template(critic_template)
critic_chain = critic_prompt | llm

print(">> Step 2: 两个大脑 (Planner & Critic) 已就绪...")

# --- 5. 调度逻辑 (组装流水线) ---

def parse_plan(plan_text: str):
    """提取 '1. xxx' 形式的步骤"""
    steps = []
    for line in plan_text.split('\n'):
        line = line.strip()
        # 正则匹配数字开头，如 "1." 或 "1、"
        if re.match(r'^\d+[\.\、]', line):
            # 去掉序号，只留内容
            step_content = re.sub(r'^\d+[\.\、]\s*', '', line)
            steps.append(step_content)
    return steps

def solve_math_problem(problem: str):
    print(f"\n====== 收到数学题：{problem} ======")
    
    # === Phase 1: 规划与自省 (Plan & Critique) ===
    current_plan = ""
    feedback = "" 
    max_retries = 3
    
    print("\n[开始规划阶段]")
    
    for i in range(max_retries):
        print(f"\n>> 第 {i+1} 轮规划...")
        
        # A. Planner 写计划
        # 如果有 feedback，Planner 会看到“老师的批语”
        feedback_input = f"上一次的计划被老师打回了，意见是：{feedback}" if feedback else ""
        
        current_plan = planner_chain.invoke({
            "objective": problem,
            "feedback": feedback_input
        }).content
        
        print(f"--- 课代表的计划 (v{i+1}) ---\n{current_plan}\n----------------")
        
        # B. Critic 检查
        print(">> 老师正在检查...")
        review = critic_chain.invoke({
            "objective": problem,
            "plan": current_plan
        }).content
        
        print(f"--- 老师的评语 ---\n{review}\n----------------")
        
        # C. 判定
        if "PLAN_OK" in review:
            print("✅ 计划通过！")
            break
        else:
            print("❌ 计划被打回，准备重写。")
            feedback = review # 把评语存下来，下一轮传给 Planner
            
    else:
        print("⚠️ 警告：老师累了，强制执行最后一版计划。")

    # === Phase 2: 执行 (Execute) ===
    print("\n[开始执行阶段]")
    steps = parse_plan(current_plan)
    
    # 如果解析不到步骤，说明格式还是有问题
    if not steps:
        print("执行失败：无法解析计划步骤。")
        return

    context = "" # 记忆黑板
    
    for i, step in enumerate(steps):
        print(f"\n>> 执行步骤 {i+1}: {step}")
        
        # 告诉 Worker：当前算什么，以及之前的计算结果
        worker_input = f"""
        当前任务：{step}
        已知信息：{context}
        """
        
        try:
            result = worker_executor.invoke({"input": worker_input})
            output = result['output']
            print(f"   [计算结果]: {output}")
            context += f"步骤 {i+1} 结果: {output}\n"
        except Exception as e:
            print(f"   [出错]: {e}")

    print("\n====== 最终解题报告 ======")
    print(context)

# --- 启动测试 ---
if __name__ == "__main__":
    # 测试题：(123 + 456) * 789
    # 预期：
    # Planner 第一轮可能会想直接算 (123+456)*789
    # Critic 会打回，要求先算加法，再算乘法
    task = "(123 + 456) * 789 等于多少？"
    solve_math_problem(task)