import os

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate

# --- 团队 A：数学组工具 ---
@tool
def calculator(expression: str) -> str:
    """数学计算工具。输入如 '1+1'。"""
    try:
        return str(eval(expression))
    except:
        return "计算错误"

# --- 团队 B：行政组工具 ---
@tool
def check_policy(query: str) -> str:
    """查询公司行政制度。"""
    # 模拟 RAG 检索
    if "报销" in query:
        return "制度：餐费报销上限 100 元，需发票。"
    if "上班" in query or "打卡" in query:
        return "制度：早 9 晚 6，打卡在钉钉。"
    return "未找到相关行政规定。"

# ---团队C: IT支持团队工具 ---
@tool
def reset_password(username: str) -> str:
    """重置密码。"""
    return "用户 {username} 密码已重置为 123456"

print("1. 两组专业工具箱已准备就绪...")

# --- 初始化模型 ---
llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

# --- 工厂函数：生产专家 Agent ---
def make_specialist_agent(name, tools, system_prompt_text):
    """
    创建一个专门的 ReAct Agent
    """
    print(f">> 正在聘请专家：{name}...")
    
    # 定义专用的 Prompt
    template = f"""
    你是一名 {{name}}。
    {system_prompt_text}
    
    You have access to the following tools:
    {{tools}}

    Use the following format:
    Question: the input question
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{{tool_names}}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (repeat Thought/Action/Observation)
    Thought: I now know the final answer
    Final Answer: the final answer

    Begin!
    Question: {{input}}
    Thought:{{agent_scratchpad}}
    """
    
    prompt = PromptTemplate.from_template(template).partial(name=name)
    agent = create_react_agent(llm, tools, prompt)
    
    # 返回执行器
    return AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=False, # 专家干活时保持安静，只输出结果
        handle_parsing_errors=True
    )

# --- 创建两名专家 ---

# 1. 数学专家 (MathPro)
math_agent = make_specialist_agent(
    name="MathPro", 
    tools=[calculator], 
    system_prompt_text="你只负责处理数字计算问题。如果用户问非数学问题，请拒绝回答。"
)

# 2. 行政专员 (AdminHr)
admin_agent = make_specialist_agent(
    name="AdminHr", 
    tools=[check_policy], 
    system_prompt_text="你只负责回答公司考勤、报销等行政问题。不要回答数学问题。"
)
# 3. IT支持团队 (ITSupport)
it_agent = make_specialist_agent(
    name="ITSupport", 
    tools=[reset_password], 
    system_prompt_text="你只负责重置密码问题。不要回答其他问题。"
)

print("2. 专家团队已入职...")

# --- 构建经理 (Supervisor/Router) ---

# 定义分类的 Prompt
router_template = """
你是一个用户请求分发中心。
请根据用户的输入，判断应该交给哪个部门处理。

可选部门：
1. MATH: 处理加减乘除、统计等数字问题。
2. ADMIN: 处理报销、打卡、放假等公司制度问题。
3. IT: 处理密码重置、网络故障问题。
4. NONE: 用户在闲聊，或者问题不属于以上任何部门。

用户输入：{input}

【格式要求】：
请仅输出部门名称，不要输出任何其他文字。
只能输出其中一个：MATH, ADMIN, NONE
"""

router_prompt = PromptTemplate.from_template(router_template)
router_chain = router_prompt | llm

def run_company_system():
    print("\n=== 虚拟办公室已启动 (输入 'exit' 退出) ===")
    print("你可以问：'100乘以5是多少' (测试数学组)")
    print("也可以问：'报销需要发票吗' (测试行政组)")
    
    while True:
        user_input = input("\n客户提问: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break
        if not user_input.strip():
            continue

        print(f">> 经理正在分拣工单...")
        
        # 1. 路由分类
        try:
            route_result = router_chain.invoke({"input": user_input}).content.strip()
            # 清理一下可能的多余标点
            route_result = route_result.replace(".", "").upper()
            
            print(f"   [分发结果]: 任务被派往 -> {route_result}")
            
            # 2. 路由分发
            if "MATH" in route_result:
                print(">> MathPro 正在计算...")
                response = math_agent.invoke({"input": user_input})
                print(f"专家回答: {response['output']}")
                
            elif "ADMIN" in route_result:
                print(">> AdminHr 正在查询...")
                response = admin_agent.invoke({"input": user_input})
                print(f"专家回答: {response['output']}")
                
            elif "IT" in route_result:
                print(">> ITSupport 正在重置密码...")
                response = it_agent.invoke({"input": user_input})
                print(f"专家回答: {response['output']}")
            else:
                print("经理回答: 抱歉，这个问题不属于数学组、行政组也不属于IT组，我无法处理。")
                
        except Exception as e:
            print(f"系统错误: {e}")

if __name__ == "__main__":
    run_company_system()