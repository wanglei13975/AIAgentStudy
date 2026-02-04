"""
Day 3 - 练习2：多步推理任务
学习Agent如何链式使用工具

任务：让Agent完成需要多步的复杂任务
"先查询现在几点，然后计算距离中午12点还有多长时间"
"""

import requests
import json
from datetime import datetime


# ============================================================
# 步骤1：理解任务
# ============================================================

print("="*70)
print("📚 练习2：多步推理任务")
print("="*70)

print("""
任务："先查询现在几点，然后计算距离中午12点还有多长时间"

这个任务需要：
1️⃣ 调用 get_time 工具获取当前时间
2️⃣ 解析时间，提取小时
3️⃣ 调用 calculator 工具计算时间差
4️⃣ 组织答案返回给用户

这就是多步推理！
""")

input("按回车开始...")


# ============================================================
# 步骤2：定义工具
# ============================================================

print("\n" + "-"*70)
print("步骤2：准备工具")
print("-"*70)

def calculator(expression: str) -> str:
    """计算器"""
    try:
        result = eval(expression)
        return f"{result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

def get_time() -> str:
    """获取当前时间"""
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')

tools = [
    {
        "name": "calculator",
        "description": "执行数学计算。输入：数学表达式",
        "function": calculator
    },
    {
        "name": "get_time",
        "description": "获取当前时间，返回格式：YYYY-MM-DD HH:MM:SS",
        "function": get_time
    }
]

print("\n可用工具：")
for tool in tools:
    print(f"  - {tool['name']}: {tool['description']}")

input("\n✅ 工具准备完成！按回车继续...")


# ============================================================
# 步骤3：手动演示多步推理
# ============================================================

print("\n" + "-"*70)
print("步骤3：手动演示多步推理过程")
print("-"*70)

print("""
让我们手动执行这个任务，理解每一步：
""")

print("\n🔄 步骤1：获取当前时间")
print("-"*60)
current_time = get_time()
print(f"🔧 Action: get_time()")
print(f"👁️  Observation: {current_time}")

# 解析时间
hour = int(current_time.split()[1].split(':')[0])
minute = int(current_time.split()[1].split(':')[1])
print(f"\n💭 Thought: 当前是 {hour}点{minute}分")

input("\n按回车继续下一步...")

print("\n🔄 步骤2：计算距离12点的时间")
print("-"*60)

if hour < 12:
    # 还没到中午
    hours_left = 12 - hour
    minutes_left = 60 - minute if minute > 0 else 0
    
    print(f"💭 Thought: 现在是{hour}点，距离12点还有 {hours_left}小时")
    print(f"   需要计算：12 - {hour} = ?")
    
    expression = f"12 - {hour}"
    print(f"\n🔧 Action: calculator('{expression}')")
    result = calculator(expression)
    print(f"👁️  Observation: {result}")
    
    final_answer = f"现在是{hour}点{minute}分，距离中午12点还有约{result}小时"
    
elif hour == 12:
    final_answer = f"现在正好是中午12点！"
else:
    # 已经过了中午
    final_answer = f"现在是{hour}点{minute}分，已经过了中午12点"

print(f"\n✅ Final Answer: {final_answer}")

input("\n✅ 手动演示完成！按回车看Agent自动执行...")


# ============================================================
# 步骤4：用Agent自动执行
# ============================================================

print("\n" + "-"*70)
print("步骤4：创建能多步推理的Agent")
print("-"*70)

print("""
现在我们创建一个Agent，让它自己完成多步推理。

关键：Agent需要：
1. 保存中间结果
2. 基于结果决定下一步
3. 链式调用工具
""")

class MultiStepAgent:
    """支持多步推理的Agent"""
    
    def __init__(self, tools):
        self.tools = {t['name']: t for t in tools}
        self.memory = []  # 记忆：保存执行历史
    
    def _log(self, step: str, content: str):
        """记录步骤"""
        self.memory.append({"step": step, "content": content})
        print(f"{step}: {content}")
    
    def run_multi_step(self, task: str):
        """执行多步任务"""
        print(f"\n{'='*60}")
        print(f"📝 任务：{task}")
        print(f"{'='*60}\n")
        
        self.memory = []
        
        # 步骤1：获取当前时间
        self._log("💭 Thought", "首先需要获取当前时间")
        self._log("🔧 Action", "get_time()")
        
        current_time = self.tools['get_time']['function']()
        self._log("👁️  Observation", current_time)
        
        # 步骤2：解析时间
        hour = int(current_time.split()[1].split(':')[0])
        minute = int(current_time.split()[1].split(':')[1])
        
        self._log("💭 Thought", f"当前时间是 {hour}点{minute}分")
        
        # 步骤3：计算
        if hour < 12:
            self._log("💭 Thought", f"需要计算 12 - {hour}")
            self._log("🔧 Action", f"calculator('12 - {hour}')")
            
            result = self.tools['calculator']['function'](f"12 - {hour}")
            self._log("👁️  Observation", result)
            
            final_answer = f"现在是{hour}点{minute}分，距离中午12点还有约{result}小时"
        elif hour == 12:
            final_answer = f"现在正好是中午12点！"
        else:
            final_answer = f"现在是{hour}点{minute}分，已经过了中午12点"
        
        self._log("💭 Thought", "已获得所有信息，可以回答了")
        self._log("✅ Final Answer", final_answer)
        
        return final_answer
    
    def show_memory(self):
        """显示执行历史"""
        print("\n" + "="*60)
        print("📝 执行历史回顾")
        print("="*60)
        for i, item in enumerate(self.memory, 1):
            print(f"{i}. {item['step']}: {item['content']}")

# 创建Agent
agent = MultiStepAgent(tools)

print("\n开始执行：")
print("="*60)

# 执行任务
result = agent.run_multi_step("先查询现在几点，然后计算距离中午12点还有多长时间")

input("\n按回车查看执行历史...")

# 显示历史
agent.show_memory()

print("\n" + "="*70)
print("🎉 练习2完成！")
print("="*70)

print("""
✅ 你学会了：

1. 多步推理的结构
   - 步骤1 → 步骤2 → 步骤3 → 答案
   
2. 中间结果的使用
   - 第一步的输出是第二步的输入
   - 像人类一样思考

3. Agent的记忆
   - 保存执行历史
   - 可以回顾过程

4. 任务分解
   - 复杂任务 → 简单步骤
   - 逐步完成

💡 思考题：
如果任务是"查询北京天气，如果超过25度就提醒我带墨镜"
Agent需要几步？每步做什么？

提示：
1. 查询天气
2. 解析温度
3. 判断是否>25度
4. 给出建议
""")

input("\n按回车继续下一个练习...")
