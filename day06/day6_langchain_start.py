from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

# --- 【关键修复】强制绕过代理 ---
# 这几行代码告诉 Python：访问本地服务时，不要走公司的代理服务器
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
# 为了保险，把可能会影响的代理变量临时清空（只对当前脚本生效）
if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]

# --- 下面才是正常的 import ---
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ... (后面的代码保持不变) ...
# 记得保留 timeout=600.0 的设置
print("--- 正在初始化模型 ---")
llm = ChatOllama(
    model="qwen2.5:14b", 
    temperature=0.1,
    timeout=600.0 
)
# --- 步骤 1: 生成周报 ---
prompt_draft = ChatPromptTemplate.from_template(
    """你是一名员工。根据以下工作点，写一份简短的周报：
    工作内容：{input_data}
    """
)
# 构建第一条链
chain_draft = prompt_draft | llm | StrOutputParser()

# --- 步骤 2: 润色邮件 ---
prompt_polish = ChatPromptTemplate.from_template(
    """你是一名经理。请把下面的周报草稿，修改成一封发送给 CEO 的正式邮件。
    要求：语气专业、简洁、突出重点。
    
    周报草稿：
    {draft_content}
    """
)
# 构建第二条链
chain_polish = prompt_polish | llm | StrOutputParser()

# --- 组合运行 ---
if __name__ == "__main__":
    user_input = "1. 修复了登录 bug。 2. 优化了数据库查询速度。 3. 和产品经理吵了一架但最后和好了。"
    
    print(f"\n[原始输入]: {user_input}")
    
    print("\n>>> 正在生成草稿 (请耐心等待)...")
    try:
        # 运行第一步
        draft = chain_draft.invoke({"input_data": user_input})
        print(f"[草稿]:\n{draft}")
        
        print("\n>>> 正在润色成邮件 (请耐心等待)...")
        # 把第一步的结果 draft 传给第二步
        final_email = chain_polish.invoke({"draft_content": draft})
        print(f"[最终邮件]:\n{final_email}")
        
    except Exception as e:
        print(f"\n[错误]: {e}")
        print("建议：如果依然超时，请检查显存占用，或尝试换用 qwen2.5:7b 模型。")