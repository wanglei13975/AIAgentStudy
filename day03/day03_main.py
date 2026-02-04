"""
Day 3 - AI Agent核心：ReAct模式 + 工具调用
一个文件，顺序演示所有知识点，无需选择

学习目标：
1. 理解什么是Agent
2. 学习ReAct模式（Reasoning + Acting）
3. 实现工具调用
4. 构建第一个能使用工具的Agent

运行方式：
python day03_main.py

按回车继续每个演示，全程无需选择。
"""

import requests
import json
import time
from typing import List, Dict, Callable, Any


# ============================================================
# 第一部分：理解Agent是什么
# ============================================================

def part1_what_is_agent():
    """第一部分：理解Agent"""
    print("\n" + "="*70)
    print("📚 第一部分：什么是Agent？")
    print("="*70)
    
    print("""
Agent（智能体）是一个能够：
1. 感知环境（接收输入）
2. 自主决策（思考下一步做什么）
3. 采取行动（执行操作）
4. 达成目标（完成任务）

🤔 传统程序 vs Agent：

┌─────────────────────────────────────┐
│ 传统程序（固定流程）                 │
├─────────────────────────────────────┤
│ 输入 → 步骤1 → 步骤2 → 步骤3 → 输出 │
│ 流程固定，不能灵活调整               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Agent（智能决策）                    │
├─────────────────────────────────────┤
│ 输入 → 思考 → 选择工具 → 执行       │
│       ↑                     ↓       │
│       └──── 观察结果 ←──────┘       │
│ 循环直到完成任务                     │
└─────────────────────────────────────┘

💡 举例：

任务："告诉我北京今天的天气"

传统程序：
  - 必须提前编好"调用天气API"的代码
  - 改需求就要改代码

Agent：
  - 理解："我需要天气信息"
  - 决策："我应该使用天气查询工具"
  - 行动：调用工具
  - 返回：给出结果
    """)
    
    input("\n✅ 理解了吗？按回车继续下一部分...")


# ============================================================
# 第二部分：ReAct模式
# ============================================================

def part2_react_pattern():
    """第二部分：ReAct模式"""
    print("\n" + "="*70)
    print("📚 第二部分：ReAct模式（Reasoning + Acting）")
    print("="*70)
    
    print("""
ReAct = Reasoning（推理） + Acting（行动）

这是让AI成为Agent的核心模式！

🔄 ReAct循环：

1. Thought（思考）：分析当前情况，决定下一步
2. Action（行动）：选择并执行一个工具
3. Observation（观察）：看工具返回了什么
4. → 回到第1步，继续思考...
5. 直到任务完成

📝 实际例子：

用户问："2024年奥运会在哪举办？中国得了多少金牌？"

Thought 1: 我需要先查询2024年奥运会的举办地
Action 1: 使用搜索工具查询"2024年奥运会举办地"
Observation 1: 2024年奥运会在巴黎举办

Thought 2: 现在我知道了举办地，接下来查中国金牌数
Action 2: 使用搜索工具查询"2024巴黎奥运会中国金牌"
Observation 2: 中国获得40枚金牌

Thought 3: 我已经有了所有信息，可以回答了
Final Answer: 2024年奥运会在巴黎举办，中国获得了40枚金牌。

💡 关键点：
- Agent自己决定用什么工具
- Agent知道什么时候停止
- 像人类一样思考和行动
    """)
    
    input("\n✅ 理解ReAct了吗？按回车看具体实现...")


# ============================================================
# 第三部分：定义工具
# ============================================================

def part3_define_tools():
    """第三部分：定义工具"""
    print("\n" + "="*70)
    print("📚 第三部分：定义工具（Tools）")
    print("="*70)
    
    print("""
工具就是Agent可以调用的函数。

每个工具需要三个要素：
1. name（名称）：工具叫什么
2. description（描述）：工具能做什么
3. function（函数）：实际执行的代码

让我们定义几个简单的工具：
    """)
    
    # 定义工具
    def calculator(expression: str) -> str:
        """计算器工具"""
        try:
            result = eval(expression)
            return f"计算结果：{result}"
        except:
            return "计算错误"
    
    def get_time() -> str:
        """获取当前时间"""
        from datetime import datetime
        now = datetime.now()
        return f"现在是：{now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def search(query: str) -> str:
        """模拟搜索（简化版）"""
        # 实际项目中这里会调用真实的搜索API
        fake_results = {
            "python": "Python是一种高级编程语言，由Guido van Rossum创建于1991年。",
            "天气": "今天北京晴朗，温度15-25度。",
            "新闻": "今日头条：科技进步推动AI发展。"
        }
        for key in fake_results:
            if key in query.lower():
                return fake_results[key]
        return f"搜索'{query}'：未找到相关结果"
    
    # 工具列表
    tools = [
        {
            "name": "calculator",
            "description": "执行数学计算，输入数学表达式，返回结果。例如：2+2, 10*5",
            "function": calculator
        },
        {
            "name": "get_time",
            "description": "获取当前时间",
            "function": get_time
        },
        {
            "name": "search",
            "description": "搜索信息，输入查询内容，返回搜索结果",
            "function": search
        }
    ]
    
    print("\n✅ 已定义3个工具：")
    for tool in tools:
        print(f"\n🔧 {tool['name']}")
        print(f"   描述：{tool['description']}")
    
    print("\n\n让我们测试这些工具：")
    print("-" * 70)
    
    # 测试工具
    print("\n1️⃣ 测试计算器：")
    print(f"   输入：100 * 3 + 50")
    print(f"   输出：{calculator('100 * 3 + 50')}")
    
    print("\n2️⃣ 测试时间：")
    print(f"   输出：{get_time()}")
    
    print("\n3️⃣ 测试搜索：")
    print(f"   输入：python")
    print(f"   输出：{search('python')}")
    
    input("\n✅ 工具都能正常工作！按回车继续...")
    
    return tools


# ============================================================
# 第四部分：简单的Agent（不使用LLM）
# ============================================================

def part4_simple_agent(tools):
    """第四部分：简单Agent"""
    print("\n" + "="*70)
    print("📚 第四部分：构建简单Agent（规则驱动）")
    print("="*70)
    
    print("""
先做一个简单版本：基于规则的Agent
（不用LLM，用if-else决策）

这帮助我们理解Agent的基本结构。
    """)
    
    class SimpleAgent:
        """简单的基于规则的Agent"""
        
        def __init__(self, tools):
            self.tools = {t['name']: t for t in tools}
        
        def run(self, task: str):
            """执行任务"""
            print(f"\n📝 任务：{task}")
            print("-" * 70)
            
            # 简单规则匹配
            if "计算" in task or "+" in task or "*" in task or any(c.isdigit() for c in task):
                print("💭 Thought: 这是个计算任务，使用计算器")
                
                # 提取表达式
                import re
                numbers = re.findall(r'[\d+\-*/()]+', task)
                if numbers:
                    expression = numbers[0]
                    print(f"🔧 Action: calculator('{expression}')")
                    result = self.tools['calculator']['function'](expression)
                    print(f"👁️  Observation: {result}")
                    return result
            
            elif "时间" in task or "几点" in task:
                print("💭 Thought: 用户想知道时间")
                print(f"🔧 Action: get_time()")
                result = self.tools['get_time']['function']()
                print(f"👁️  Observation: {result}")
                return result
            
            elif "搜索" in task or "查询" in task:
                print("💭 Thought: 需要搜索信息")
                query = task.replace("搜索", "").replace("查询", "").strip()
                print(f"🔧 Action: search('{query}')")
                result = self.tools['search']['function'](query)
                print(f"👁️  Observation: {result}")
                return result
            
            else:
                return "❌ 抱歉，我不知道如何处理这个任务"
    
    # 创建Agent
    agent = SimpleAgent(tools)
    
    # 测试任务
    test_tasks = [
        "帮我计算 50 + 30",
        "现在几点了？",
        "搜索一下Python"
    ]
    
    print("\n开始测试Agent：")
    print("="*70)
    
    for task in test_tasks:
        result = agent.run(task)
        print(f"✅ 最终答案：{result}\n")
        time.sleep(1)
    
    print("""
💡 观察到了什么？

这个Agent能工作，但是：
❌ 完全依赖规则（if-else）
❌ 无法处理复杂任务
❌ 不够智能和灵活

解决方案：用LLM做决策！
    """)
    
    input("\n按回车看LLM驱动的Agent...")


# ============================================================
# 第五部分：LLM驱动的Agent
# ============================================================

def part5_llm_agent(tools):
    """第五部分：LLM驱动的Agent"""
    print("\n" + "="*70)
    print("📚 第五部分：LLM驱动的真正Agent")
    print("="*70)
    
    print("""
现在用LLM来做决策！

Agent的工作流程：
1. 把任务和可用工具告诉LLM
2. LLM思考并选择使用哪个工具
3. 执行工具，获得结果
4. 把结果反馈给LLM
5. LLM决定：继续？还是给出最终答案？
    """)
    
    class LLMAgent:
        """LLM驱动的Agent"""
        
        def __init__(self, tools, model="qwen2.5:14b"):
            self.tools = {t['name']: t for t in tools}
            self.model = model
            self.url = "http://localhost:11434/api/chat"
        
        def _build_system_prompt(self):
            """构建系统提示词"""
            tools_desc = "\n".join([
                f"- {t['name']}: {t['description']}"
                for t in self.tools.values()
            ])
            
            return f"""你是一个有用的AI助手，可以使用工具完成任务。

可用工具：
{tools_desc}

你必须按照以下格式思考和行动：

Thought: [分析任务，决定下一步]
Action: [工具名称]
Action Input: [工具的输入参数]

或者，当你有了最终答案：

Final Answer: [给用户的最终答案]

重要规则：
1. 每次只能使用一个工具
2. 必须等待观察结果再继续
3. 回答要基于实际观察到的结果
4. 格式必须严格遵守"""
        
        def _call_llm(self, messages):
            """调用LLM"""
            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "keep_alive": "10m",
                "options": {
                    "temperature": 0.1,  # 低温度，让输出更确定
                    "num_ctx": 2048
                }
            }
            
            try:
                response = requests.post(self.url, json=data, timeout=60)
                result = response.json()
                return result.get("message", {}).get("content", "")
            except Exception as e:
                return f"LLM调用错误: {str(e)}"
        
        def _parse_response(self, response: str):
            """解析LLM的响应"""
            # 查找 Final Answer
            if "Final Answer:" in response:
                answer = response.split("Final Answer:")[-1].strip()
                return {"type": "answer", "content": answer}
            
            # 查找 Action
            if "Action:" in response and "Action Input:" in response:
                lines = response.split("\n")
                action = None
                action_input = None
                
                for line in lines:
                    if "Action:" in line:
                        action = line.split("Action:")[-1].strip()
                    if "Action Input:" in line:
                        action_input = line.split("Action Input:")[-1].strip()
                
                if action and action_input:
                    return {
                        "type": "action",
                        "action": action,
                        "input": action_input
                    }
            
            # 无法解析
            return {"type": "error", "content": response}
        
        def _execute_tool(self, tool_name: str, tool_input: str):
            """执行工具"""
            if tool_name not in self.tools:
                return f"错误：工具 {tool_name} 不存在"
            
            tool = self.tools[tool_name]
            try:
                result = tool['function'](tool_input)
                return result
            except Exception as e:
                return f"工具执行错误: {str(e)}"
        
        def run(self, task: str, max_steps: int = 5):
            """执行任务"""
            print(f"\n📝 任务：{task}")
            print("="*70)
            
            messages = [
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": task}
            ]
            
            for step in range(max_steps):
                print(f"\n🔄 步骤 {step + 1}")
                print("-" * 70)
                
                # 调用LLM
                print("💭 LLM思考中...")
                response = self._call_llm(messages)
                print(f"\n回复：\n{response}")
                
                # 解析响应
                parsed = self._parse_response(response)
                
                if parsed["type"] == "answer":
                    # 得到最终答案
                    print(f"\n✅ 最终答案：{parsed['content']}")
                    return parsed['content']
                
                elif parsed["type"] == "action":
                    # 执行工具
                    action = parsed['action']
                    action_input = parsed['input']
                    
                    print(f"\n🔧 执行工具：{action}")
                    print(f"   输入：{action_input}")
                    
                    observation = self._execute_tool(action, action_input)
                    print(f"👁️  观察：{observation}")
                    
                    # 添加到对话历史
                    messages.append({"role": "assistant", "content": response})
                    messages.append({"role": "user", "content": f"Observation: {observation}"})
                
                else:
                    print(f"\n❌ 无法解析LLM响应")
                    return "执行失败"
            
            print(f"\n⚠️  达到最大步骤数({max_steps})，任务未完成")
            return "任务超时"
    
    # 创建Agent
    print("\n正在创建LLM Agent...")
    agent = LLMAgent(tools)
    
    # 测试任务
    print("\n" + "="*70)
    print("开始测试LLM Agent")
    print("="*70)
    
    test_task = "帮我计算 123 + 456 的结果"
    
    try:
        result = agent.run(test_task)
        print("\n" + "="*70)
        print(f"✅ 任务完成！最终结果：{result}")
        print("="*70)
    except Exception as e:
        print(f"\n❌ 出错了：{e}")
        print("💡 确保Ollama正在运行")
    
    print("""
💡 LLM Agent vs 简单Agent：

简单Agent：
  - 固定规则
  - 无法适应新任务
  
LLM Agent：
  ✅ 自己理解任务
  ✅ 自己选择工具
  ✅ 能处理复杂任务
  ✅ 可以链式推理
    """)
    
    input("\n按回车看更复杂的例子...")


# ============================================================
# 第六部分：复杂任务演示
# ============================================================

def part6_complex_task(tools):
    """第六部分：复杂任务"""
    print("\n" + "="*70)
    print("📚 第六部分：Agent处理复杂任务")
    print("="*70)
    
    print("""
复杂任务需要多步推理和多次工具调用。

示例任务：
"告诉我现在的时间，然后帮我计算从现在到晚上8点还有多少小时"

这需要：
1. 调用get_time工具获取当前时间
2. 解析时间
3. 调用calculator计算时间差
4. 组织答案
    """)
    
    print("\n💡 这就是Agent的强大之处：")
    print("   - 能够分解复杂任务")
    print("   - 链式使用多个工具")
    print("   - 整合信息给出答案")
    
    input("\n✅ 理解了吗？按回车看总结...")


# ============================================================
# 第七部分：总结
# ============================================================

def part7_summary():
    """第七部分：总结"""
    print("\n" + "="*70)
    print("📚 Day 3 总结")
    print("="*70)
    
    print("""
今天学到的核心概念：

1️⃣ Agent是什么
   - 能感知、决策、行动的智能体
   - 不同于固定流程的程序

2️⃣ ReAct模式
   - Thought（思考）→ Action（行动）→ Observation（观察）
   - 循环直到完成任务

3️⃣ 工具（Tools）
   - Agent可以调用的函数
   - 需要：名称、描述、实现

4️⃣ Agent的两种实现
   - 规则驱动：简单但不灵活
   - LLM驱动：智能且能适应

5️⃣ Agent的工作流程
   ┌──────────────┐
   │  收到任务    │
   └──────┬───────┘
          ↓
   ┌──────────────┐
   │ LLM思考决策  │←──┐
   └──────┬───────┘   │
          ↓            │
   ┌──────────────┐   │
   │  执行工具    │   │
   └──────┬───────┘   │
          ↓            │
   ┌──────────────┐   │
   │  获得结果    │───┘
   └──────┬───────┘
          ↓
   ┌──────────────┐
   │  返回答案    │
   └──────────────┘

💡 关键要点：
✅ Agent能自己决策，不需要写固定流程
✅ 工具让Agent能够与外部世界交互
✅ LLM是Agent的"大脑"
✅ ReAct模式让Agent能够推理和行动

🚀 接下来的学习：
- Day 4: 更多工具类型（搜索、文件、API等）
- Day 5: 记忆系统（让Agent记住历史）
- Day 6: 多Agent协作

📝 今日练习：
1. 添加一个新工具（比如：天气查询、翻译等）
2. 让Agent处理更复杂的任务
3. 优化Agent的提示词

恭喜完成Day 3！🎉
    """)


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数"""
    print("="*70)
    print("🎓 Day 3: ReAct模式 + 工具调用")
    print("="*70)
    print("""
今天的学习非常重要！

我们会学习：
- Agent的核心概念
- ReAct推理模式
- 如何让AI使用工具
- 构建真正能干活的Agent

全程自动演示，按回车继续每一部分。

准备好了吗？
    """)
    
    input("按回车开始学习...")
    
    try:
        # 第一部分：理解Agent
        part1_what_is_agent()
        
        # 第二部分：ReAct模式
        part2_react_pattern()
        
        # 第三部分：定义工具
        tools = part3_define_tools()
        
        # 第四部分：简单Agent
        part4_simple_agent(tools)
        
        # 第五部分：LLM Agent
        part5_llm_agent(tools)
        
        # 第六部分：复杂任务
        part6_complex_task(tools)
        
        # 第七部分：总结
        part7_summary()
        
        print("\n✅ Day 3 学习完成！")
        print("\n保存这个文件，随时可以重新学习。")
        print("明天我们会学习更多工具和记忆系统！")
        
    except KeyboardInterrupt:
        print("\n\n👋 学习已暂停，随时可以继续！")
    except Exception as e:
        print(f"\n❌ 出错了：{e}")
        print("\n💡 如果是连接错误，请确保Ollama正在运行")


if __name__ == "__main__":
    main()
