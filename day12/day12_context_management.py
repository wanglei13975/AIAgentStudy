import os

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
# 【新组件】引入消息修剪工具
from langchain_core.messages import trim_messages, SystemMessage

# 2. 初始化模型
llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

# 3. 定义工具 (还是用这个简单的算工资)
@tool
def calculate_salary(dummy_arg: str = "") -> str:
    """计算工资的工具。"""
    return "你的月薪是 50,000 元 (税前)。"

tools = [calculate_salary]

# 4. 定义 Prompt
# 注意：这里没有变化，Prompt 依然以为自己拿到的是完整的 history
template = """Answer the following questions as best you can. You have access to the following tools:

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

Previous conversation history:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)
# --- 新增：自动摘要函数 ---

# 定义摘要的 Prompt
summary_template = """
你是一个对话总结助手。请根据“目前的摘要”和“新的对话片段”，生成一个新的、合并后的摘要。
摘要应简明扼要，保留关键信息（如用户名、爱好、关键事实），去除寒暄和废话。

【目前的摘要】：
{current_summary}

【新的对话片段】：
{new_lines}

请输出新的摘要内容：
"""
summary_prompt = PromptTemplate.from_template(summary_template)

# 创建一个专门用于总结的链
# 我们复用之前的 llm 实例
summary_chain = summary_prompt | llm

def update_summary(previous_summary: str, messages_to_prune: list) -> str:
    """
    参数:
      previous_summary: 之前的摘要字符串
      messages_to_prune: 即将被丢弃的消息对象列表
    返回:
      更新后的摘要字符串
    """
    # 1. 把消息对象列表转成可读的字符串 (例如 "Human: xxx\nAI: yyy")
    new_lines = ""
    for msg in messages_to_prune:
        role = "User" if msg.type == "human" else "AI"
        new_lines += f"{role}: {msg.content}\n"
    
    # 2. 调用 LLM 生成新摘要
    # 如果之前没有摘要，就填“无”
    current_val = previous_summary if previous_summary else "无"
    
    print(f"   [Summary] 正在把 {len(messages_to_prune)} 条旧消息压缩成摘要...")
    response = summary_chain.invoke({
        "current_summary": current_val, 
        "new_lines": new_lines
    })
    
    return response.content
# 5. 【核心修改】定义“带修剪功能”的历史记录获取器

def get_session_history(session_id: str):
    """
    这里返回的是完整的 SQL 历史记录对象。
    LangChain 会自动往这个对象里 .add_message()。
    """
    return SQLChatMessageHistory(
        session_id=session_id,
        connection="sqlite:///memory.db"
    )

# 6. 构建修剪器 (The Trimmer)
# 这是一个过滤器，它会拦截历史记录
trimmer = trim_messages(
    strategy="last",      # 策略：保留最后的
    token_counter=len,    # 简化版：按消息数量计算 (生产环境通常按 token 计算)
    max_tokens=5,         # 【关键设置】只保留最近的 5 条消息 (包含问和答)
    start_on="human",     # 确保切分后的第一句话是人类说的 (保持对话完整性)
    include_system=False, # 不计算系统提示词
    allow_partial=False,
)

# 7. 组装 Agent
# 在 v0.3 中，我们需要拦截传入 prompt 的 chat_history
# 由于 create_react_agent 封装较深，我们通过 RunnableWithMessageHistory 的特性来处理
# 但为了让你看清原理，我们这里采用一种更直观的“手动修剪”演示模式：
# (注：LangChain 标准做法是把 trimmer 塞进 chain 里，但 ReactAgent 结构比较固化)

agent_with_memory = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
# --- 运行交互 ---

print("=== 自动摘要 Agent (Rolling Summary) ===")
print("说明：当消息超过阈值，LLM 会自动把旧消息压缩成摘要。")

session_id = "user_auto_sum"
# 全局变量：用于存储当前的摘要文本
global_summary = "" 

while True:
    user_input = input("\n请提问 (输入 'exit' 退出): ")
    if user_input.lower() in ["exit", "quit", "q"]:
        break
    if not user_input.strip():
        continue

    # 1. 读历史
    history_obj = get_session_history(session_id)
    raw_messages = history_obj.messages
    
    # 2. 剪历史 + 自动摘要
    MAX_HISTORY = 4 # 阈值设为 4，方便快速触发
    
    # 这里的逻辑是：如果是“长对话”，我们需要构建 (摘要 + 最近 N 条)
    if len(raw_messages) > MAX_HISTORY:
        # A. 切分：哪些要留(keep)，哪些要扔(prune)
        # 我们保留最后 MAX_HISTORY 条作为短期记忆
        msgs_to_keep = raw_messages[-MAX_HISTORY:]
        
        # 剩下的就是我们要“扔掉但需要总结”的旧消息
        # 注意：这里有个小难点。
        # 如果我们每次都重新总结所有旧消息，会越来越慢。
        # 这里的策略是：我们只处理“溢出”的那部分。
        # 但为了简化 Day 12 的逻辑，我们假设每次把“已经存在数据库里、但不在短期窗口内”的所有消息都算作“旧消息”。
        # 实际更高效的做法是：只在刚溢出那一刻更新摘要。
        
        # --- 简化版逻辑：只要溢出，我们就假设之前的 global_summary 是基于 (total - keep) 的总结 ---
        # 但为了演示动态生成，我们需要一个触发点。
        # 让我们做一个简单的判断：
        # 只有当 raw_messages 增加时，我们才真正需要更新摘要吗？
        # 为了演示最直观的效果，我们采取【即时切分法】：
        
        msgs_to_prune = raw_messages[:-MAX_HISTORY] # 头部被切掉的部分
        
        # B. 【核心】如果没有摘要，或者旧消息变多了，我们需要更新摘要
        # (注意：为了不每轮都跑一次昂贵的总结，你应该把 global_summary 存数据库)
        # (但这里我们仅在内存演示，每次溢出都重新生成一次稍微有点慢，但能看到效果)
        
        # 为了避免重复总结 "Human: 我叫小王" 这一句，
        # 在真实系统中，summary 也是存在数据库里的。
        # 既然是练习，我们允许每次对话都重新生成一次摘要（虽然慢，但逻辑简单）。
        
        global_summary = update_summary(global_summary, msgs_to_prune)
        
        # C. 构造 SystemMessage
        summary_message = SystemMessage(content=f"【历史对话摘要】：{global_summary}")
        
        # D. 拼接
        trimmed_messages = [summary_message] + msgs_to_keep
        
        print(f"   [System] 已加载摘要: {global_summary[:30]}...") 
        
    else:
        # 还没满，不需要摘要
        trimmed_messages = raw_messages

    print(f">> Agent 思考中...")
    
    try:
        # 3. 传入 Agent
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": trimmed_messages 
        })
        
        print(f"回答: {response['output']}")
        
        # 4. 手动保存
        history_obj.add_user_message(user_input)
        history_obj.add_ai_message(response['output'])
        
    except Exception as e:
        print(f"发生错误: {e}")