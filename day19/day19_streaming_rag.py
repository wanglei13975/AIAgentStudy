import os
# --- 核心修复：强制绕过公司代理 (保留昨天的修复) ---
os.environ["NO_PROXY"] = "localhost,127.0.0.1,0.0.0.0"
if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]

import tempfile
import streamlit as st
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

st.set_page_config(page_title="Day 19 - 流式 PDF 助手", page_icon="🌊")
st.title("🌊 丝滑的 PDF 问答助手")

# --- 侧边栏 ---
with st.sidebar:
    st.header("📄 文档上传")
    uploaded_file = st.file_uploader("上传 PDF", type=["pdf"])

# --- 核心逻辑 (带缓存) ---
@st.cache_resource
def process_uploaded_file(uploaded_file):
    if not uploaded_file: return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    loader = PyPDFLoader(tmp_file_path)
    docs = loader.load()
    os.remove(tmp_file_path)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # 强制指定 base_url 防止代理干扰
    embeddings = OllamaEmbeddings(model="qwen2.5:14b", base_url="http://127.0.0.1:11434")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    return vectorstore.as_retriever()

# --- 聊天记录 ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 主逻辑 ---
if uploaded_file:
    with st.spinner("🌊 正在处理文档 (Embedding)..."):
        retriever = process_uploaded_file(uploaded_file)
    st.success("准备就绪！")

    # 定义 Chain
    llm = ChatOllama(model="qwen2.5:14b", temperature=0)
    
    template = """基于已知信息回答问题：
    {context}
    问题：{question}
    """
    prompt = PromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 渲染历史
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # --- 【重点修改】流式输出逻辑 ---
    user_input = st.chat_input("问点什么...")

    if user_input:
        # 1. 显示用户输入
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # 2. 显示 AI 回答 (带光标特效)
        with st.chat_message("assistant"):
            # A. 获取生成器 (Generator)
            # chain.stream() 不会等待结果，而是返回一个“水龙头”
            stream_generator = rag_chain.stream(user_input)
            
            # B. 使用 Streamlit 的魔法命令 write_stream
            # 它会自动从水龙头接水，并一个个字打印在屏幕上
            response_text = st.write_stream(stream_generator)
            
            # C. 这里的 response_text 是流结束后的完整字符串，存入历史
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})

else:
    st.info("👋 请先上传 PDF 文件。")