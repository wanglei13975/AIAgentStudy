import os
import streamlit as st
# 1. 环境配置 (防止代理报错)
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

# --- 页面配置 ---
st.set_page_config(page_title="Day 17 - 我的 AI 助手", page_icon="🤖")
st.title("🤖 简易 AI 聊天助手")

# --- 1. 初始化模型 ---
# 使用 @st.cache_resource 装饰器
# 作用：只有第一次运行时加载模型，后面刷新页面时直接用缓存，不用重新连接 Ollama
@st.cache_resource
def get_model():
    return ChatOllama(model="qwen2.5:14b", temperature=0.7)

llm = get_model()

# --- 2. 初始化聊天记录 (Session State) ---
# 这就是 Streamlit 的“短期记忆”。
# 如果不这么写，每次你发一条消息，之前的聊天记录就消失了。
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 3. 渲染历史消息 ---
# 每次脚本重新运行时，先要把存起来的历史记录画在屏幕上
for msg in st.session_state.chat_history:
    # 区分是谁说的
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- 4. 处理用户输入 ---
# st.chat_input() 会在页面底部创建一个输入框
user_input = st.chat_input("说点什么吧...")

if user_input:
    # A. 显示用户的话
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # B. 存入历史 (User)
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    # C. 调用模型 (AI 思考中...)
    with st.chat_message("assistant"):
        # 创建一个空容器，用来显示“加载中”或流式输出
        message_placeholder = st.empty()
        message_placeholder.markdown("▌ 思考中...")
        
        try:
            # 调用 LLM (这里把整个历史传给它，带有简单的上下文能力)
            response = llm.invoke(st.session_state.chat_history)
            ai_content = response.content
            
            # 显示最终结果
            message_placeholder.markdown(ai_content)
            
            # D. 存入历史 (AI)
            st.session_state.chat_history.append(AIMessage(content=ai_content))
            
        except Exception as e:
            message_placeholder.error(f"发生错误: {e}")

# --- 侧边栏 (可选) ---
with st.sidebar:
    st.write("🔧 **控制面板**")
    if st.button("🗑️ 清空对话"):
        st.session_state.chat_history = []
        st.rerun() # 强制立刻刷新页面