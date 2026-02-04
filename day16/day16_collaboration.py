import os
import re  # 记得在文件最开头导入 re

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# --- 初始化模型 ---
llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

# --- 1. 底层工具 (修复了短路逻辑) ---
@tool
def calculator(expression: str) -> str:
    """数学计算工具。"""
    try:
        # 1. 打印一下原始输入，方便调试
        # print(f"DEBUG: 原始输入='{expression}'")
        
        # 2. 清洗数据：只保留数字、运算符(+-*/)、小数点和括号
        # 这一步会把 "expression=", "query=", 引号等全部删掉
        # 比如 'expression="5*50"' 会变成 '5*50'
        clean_expr = re.sub(r'[^0-9+\-*/().]', '', expression)
        
        # 3. 如果清洗后为空，说明输入完全不对
        if not clean_expr:
            return "计算错误: 未找到有效算式"
            
        # 4. 执行计算
        return str(eval(clean_expr))
    except Exception as e:
        return f"计算错误: {e}"

@tool
def check_policy(query: str) -> str:
    """查询行政制度。"""
    results = []
    if "报销" in query:
        results.append("制度：单笔报销上限为 200 元。")
    if "加班" in query:
        results.append("制度：加班费每小时 50 元。")
    
    if results:
        return " | ".join(results)
    return "未找到规定。"

# --- 2. 专家工厂 (修复了解析错误，禁止废话) ---
def make_expert_agent(name, tools, description):
    # 极简版 Prompt，强制 Agent 闭嘴干活
    template = f"""
    你是一名 {{name}}。{description}
    
    你的唯一任务是接收问题，调用工具，返回结果。
    
    【死命令】：
    1. 不要输出任何 "Thought" 或分析。
    2. 看到问题后，立刻输出 "Action"。
    3. 工具返回什么，你就把什么作为 Final Answer，禁止添加任何解释。

    You have access to the following tools:
    {{tools}}

    Use the following format:
    Question: the input question
    Action: the action to take, should be one of [{{tool_names}}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (repeat Action/Observation)
    Final Answer: the final answer

    Begin!
    Question: {{input}}
    {{agent_scratchpad}}
    """
    
    prompt = PromptTemplate.from_template(template).partial(name=name)
    agent = create_react_agent(llm, tools, prompt)
    
    # verbose=True 方便调试底层
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# 创建底层专家
math_expert = make_expert_agent("MathExpert", [calculator], "负责数字计算。")
admin_expert = make_expert_agent("AdminExpert", [check_policy], "负责查询制度。")

# --- 3. 封装为工具 ---
@tool
def ask_math_team(query: str) -> str:
    """【数学部】仅用于计算数字。输入：具体的数学算式或问题。"""
    return math_expert.invoke({"input": query})['output']

@tool
def ask_admin_team(query: str) -> str:
    """【行政部】仅用于查询客观规定。输入：'加班费多少'、'报销上限'等关键词。"""
    return admin_expert.invoke({"input": query})['output']

boss_tools = [ask_math_team, ask_admin_team]

# --- 4. Boss Agent (修复了推卸责任的 Bug) ---
boss_template = """
你是一名全能项目总监 (Boss)。
你手下有两个部门：数学部 (ask_math_team) 和 行政部 (ask_admin_team)。

用户的任务可能需要跨部门协作。

【核心决策逻辑 - 必须严格遵守】：
1. **信息获取**：使用 ask_admin_team 获取单价、上限等**客观数据**。
   - 注意：行政部只提供数据，**不负责判断**。不要问行政部“能不能报销”，只问“上限是多少”。
2. **数据计算**：使用 ask_math_team 计算总额。
3. **逻辑判断 (你自己做)**：
   - 拿到总额(A) 和 上限(B) 后，**由你自己 (Boss)** 进行比较。
   - 如果 A > B，结论是“不能全额报销，因为超过上限”。
   - 如果 A <= B，结论是“可以全额报销”。

You have access to the following tools:
{tools}

Use the following format:

Question: the input question
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

boss_prompt = PromptTemplate.from_template(boss_template)
boss_agent = create_react_agent(llm, boss_tools, boss_prompt)
boss_executor = AgentExecutor(
    agent=boss_agent, 
    tools=boss_tools, 
    verbose=True, # 开启上帝视角
    handle_parsing_errors=True
)

# --- 运行测试 ---
if __name__ == "__main__":
    print("\n=== 跨部门协作系统启动 (最终修正版) ===")
    task = "我加班了 5 个小时，请帮我算出总加班费，并告诉我这笔钱能不能全额报销？"
    
    # 【修改点】：用变量接收结果，并 print 出来
    result = boss_executor.invoke({"input": task})
    
    print("\n" + "="*30)
    print(f"💰 Boss 最终回复:\n{result['output']}")
    print("="*30)