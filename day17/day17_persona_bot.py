import os
import streamlit as st
# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
# 【新增】引入 SystemMessage 用于设定人设
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# --- 页面配置 ---
st.set_page_config(page_title="百变 AI 演员", page_icon="🎭")
st.title("🎭 百变 AI 演员")

# --- 2. 定义 5 个精彩人设 ---
personas = {
    "🤖 Python 专家": """
        你是一名资深的 Python 架构师。
        你的回答必须包含代码示例，并且代码风格必须符合 PEP8 规范。
        你不喜欢讲废话，只关注技术细节。
    """,
    
    "🐱 傲娇猫娘": """
        你是一只可爱的猫娘，名字叫“奈奈”。
        你说话必须在句尾加上“喵~”。
        你的性格有点傲娇，虽然表面上嫌弃用户（比如叫用户“笨蛋”），但内心其实很关心用户。
        不要表现得太聪明，要软萌一点。
    """,
    
    "🎩 鲁迅风格": """
        你模仿鲁迅先生的笔风。
        多用“大约”、“确实”、“横眉冷对千夫指”等词汇。
        针砭时弊，语言犀利，带有一种旧时代的白话文沧桑感。
        如果用户问愚蠢的问题，你要用文字“刺”他一下。
    """,
    
    "🔮 算命大师": """
        你是一名精通周易、八卦的算命大师，道号“玄机子”。
        你说话要神神叨叨，半文半白。
        不管用户问什么，你都要扯到“运势”、“五行”、“命理”上去。
        最后一定要劝人向善。
    """,
    
    "🌈 夸夸群群主": """
        你是夸夸群的群主，这里没有负能量！
        不管用户说什么（哪怕是犯错了），你都要能找到角度疯狂夸赞他。
        语气要极度热情，多用感叹号！！！！
        目的是让用户建立自信。
    """
}

# --- 3. 初始化模型 ---
@st.cache_resource
def get_model():
    return ChatOllama(model="qwen2.5:14b", temperature=0.8) # 稍微调高温度，让性格更鲜明

llm = get_model()

# --- 4. 侧边栏：角色选择器 ---
with st.sidebar:
    st.header("🎭 导演控制台")
    # 让用户选择角色
    selected_role = st.selectbox("请选择 AI 的人设:", list(personas.keys()))
    
    # 显示当前人设的提示词（方便你调试看）
    with st.expander("查看当前人设指令"):
        st.write(personas[selected_role])
        
    st.divider()
    if st.button("🗑️ 清空对话"):
        st.session_state.chat_history = []
        st.rerun()

# --- 5. 状态管理 (核心逻辑) ---
# 这里的逻辑是：检测用户是否切换了角色。如果切了，就强制重置历史。

if "current_role" not in st.session_state:
    st.session_state.current_role = selected_role

# 如果当前选的角色 != 记录的角色，说明用户刚刚切换了下拉框
if st.session_state.current_role != selected_role:
    st.session_state.current_role = selected_role
    st.session_state.chat_history = [] # 清空历史，防止精神分裂
    st.rerun() # 强制刷新页面

# 初始化聊天记录（如果为空，则插入当前角色的 SystemMessage）
if "chat_history" not in st.session_state or len(st.session_state.chat_history) == 0:
    st.session_state.chat_history = [
        SystemMessage(content=personas[selected_role])
    ]

# --- 6. 渲染界面 ---
for msg in st.session_state.chat_history:
    # SystemMessage 不显示在界面上，那是给 AI 看的秘密
    if isinstance(msg, SystemMessage):
        continue
    
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    # 给不同的角色配不同的头像
    avatar = "👤" if role == "user" else "🤖"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg.content)

# --- 7. 处理输入 ---
user_input = st.chat_input("和它聊聊...")

if user_input:
    # 显示用户
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    # AI 回答
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        placeholder.markdown("▌ (酝酿情绪中...)")
        
        try:
            # 这里的 history 包含了第一条 SystemMessage，所以 AI 会知道自己是谁
            response = llm.invoke(st.session_state.chat_history)
            placeholder.markdown(response.content)
            st.session_state.chat_history.append(AIMessage(content=response.content))
        except Exception as e:
            placeholder.error(f"出戏了: {e}")