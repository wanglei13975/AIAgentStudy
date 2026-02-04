"""
真正的Agent：LLM自动判断和选择工具

对比：
- 规则驱动Agent：手动写if-else（简单但笨）
- LLM驱动Agent：AI自己判断（智能但稍复杂）

这个文件展示真正的Agent是如何工作的。
"""

import requests
import json
import re


# ============================================================
# 第一部分：对比两种Agent
# ============================================================

def part1_comparison():
    """对比规则驱动 vs LLM驱动"""
    print("="*70)
    print("📚 规则驱动 vs LLM驱动 Agent")
    print("="*70)
    
    print("""
你发现的问题非常对！

🔴 规则驱动Agent（教学版）：
┌─────────────────────────────────────┐
│ if "天气" in task:                  │
│     use_weather()                   │
│ elif "计算" in task:                │
│     use_calculator()                │
│ else:                               │
│     return "不知道怎么做"            │
└─────────────────────────────────────┘

问题：
❌ 必须手动写规则
❌ 无法处理新问题
❌ 不够智能

🟢 LLM驱动Agent（真实版）：
┌─────────────────────────────────────┐
│ 把任务和工具列表告诉LLM              │
│ ↓                                   │
│ LLM自己分析任务                      │
│ ↓                                   │
│ LLM自己选择工具                      │
│ ↓                                   │
│ 执行工具，返回结果                   │
└─────────────────────────────────────┘

优势：
✅ 自动判断
✅ 能处理各种问题
✅ 真正智能
    """)
    
    input("\n按回车看真正的Agent实现...")


# ============================================================
# 第二部分：定义工具
# ============================================================

def calculator(expr: str) -> str:
    """计算器工具"""
    try:
        result = eval(expr)
        return f"计算结果：{result}"
    except:
        return "计算错误"


def weather(city: str) -> str:
    """天气查询工具"""
    weather_data = {
        "北京": "北京今天晴朗，15-25°C",
        "上海": "上海今天多云，18-26°C",
        "广州": "广州今天晴朗，22-30°C",
    }
    for key in weather_data:
        if key in city:
            return weather_data[key]
    return f"暂无{city}的天气信息"


def get_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


# 工具列表
TOOLS = [
    {
        "name": "calculator",
        "description": "数学计算工具。当需要精确计算时使用。输入：数学表达式（如：100+50）",
        "function": calculator
    },
    {
        "name": "weather",
        "description": "天气查询工具。查询城市天气时使用。输入：城市名称（如：北京）",
        "function": weather
    },
    {
        "name": "get_time",
        "description": "时间查询工具。获取当前时间时使用。无需输入参数。",
        "function": get_time
    }
]


# ============================================================
# 第三部分：真正的LLM Agent
# ============================================================

class RealLLMAgent:
    """真正的LLM驱动Agent - 自动判断和选择工具"""
    
    def __init__(self, tools, model="qwen2.5:14b"):
        self.tools = {t['name']: t for t in tools}
        self.model = model
        self.url = "http://localhost:11434/api/chat"
    
    def _build_system_prompt(self):
        """构建系统提示词"""
        tools_desc = "\n".join([
            f"{i+1}. {t['name']}: {t['description']}"
            for i, t in enumerate(self.tools.values())
        ])
        
        return f"""你是一个智能助手，可以使用工具完成任务。

【可用工具】
{tools_desc}

【工作流程】
1. 分析用户任务
2. 决定是否需要使用工具
3. 如果需要，选择最合适的工具
4. 调用工具获取结果
5. 基于结果回答用户

【输出格式】
当需要使用工具时，必须严格按此格式：

Thought: [你的分析思考]
Action: [工具名称]
Action Input: [工具输入]

当已有答案时：

Final Answer: [给用户的最终回答]

【重要规则】
- 仔细分析任务，选择正确的工具
- 每次只使用一个工具
- 必须等待观察结果再继续
- 不要编造信息
- 格式必须正确

【示例】
用户："帮我计算100+200"

Thought: 用户需要数学计算，应该使用calculator工具
Action: calculator
Action Input: 100+200

[系统会执行工具并返回结果]

Thought: 已获得计算结果
Final Answer: 100 + 200 = 300
"""
    
    def _call_llm(self, messages):
        """调用LLM"""
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "temperature": 0.1,  # 低温度，输出更确定
                "num_ctx": 2048
            }
        }
        
        try:
            response = requests.post(self.url, json=data, timeout=60)
            result = response.json()
            return result.get("message", {}).get("content", "")
        except Exception as e:
            return f"LLM错误: {str(e)}"
    
    def _parse_response(self, response: str):
        """解析LLM的回复"""
        print(f"\nLLM回复：\n{response}\n")
        
        # 检查是否是最终答案
        if "Final Answer:" in response:
            answer = response.split("Final Answer:")[-1].strip()
            return {"type": "answer", "content": answer}
        
        # 检查是否要使用工具
        if "Action:" in response and "Action Input:" in response:
            # 提取工具名
            action_match = re.search(r'Action:\s*(\w+)', response)
            # 提取输入
            input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', response)
            
            if action_match and input_match:
                action = action_match.group(1).strip()
                action_input = input_match.group(1).strip()
                
                return {
                    "type": "action",
                    "action": action,
                    "input": action_input
                }
        
        # 无法解析
        return {"type": "unknown", "content": response}
    
    def _execute_tool(self, tool_name: str, tool_input: str):
        """执行工具"""
        if tool_name not in self.tools:
            return f"错误：工具'{tool_name}'不存在"
        
        tool = self.tools[tool_name]
        try:
            # 特殊处理get_time（不需要参数）
            if tool_name == "get_time":
                result = tool['function']()
            else:
                result = tool['function'](tool_input)
            return result
        except Exception as e:
            return f"工具执行错误: {str(e)}"
    
    def run(self, task: str, max_steps: int = 5, verbose: bool = True):
        """
        执行任务
        
        参数:
            task: 用户任务
            max_steps: 最大推理步骤
            verbose: 是否显示详细过程
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"📝 用户任务：{task}")
            print(f"{'='*70}")
        
        # 初始化对话
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": task}
        ]
        
        for step in range(max_steps):
            if verbose:
                print(f"\n{'─'*70}")
                print(f"🔄 推理步骤 {step + 1}")
                print(f"{'─'*70}")
            
            # 调用LLM
            if verbose:
                print("💭 LLM正在思考...")
            
            response = self._call_llm(messages)
            
            # 解析回复
            parsed = self._parse_response(response)
            
            if parsed["type"] == "answer":
                # 得到最终答案
                if verbose:
                    print(f"\n✅ 最终答案：{parsed['content']}")
                return parsed['content']
            
            elif parsed["type"] == "action":
                # 需要使用工具
                action = parsed['action']
                action_input = parsed['input']
                
                if verbose:
                    print(f"\n🔧 选择工具：{action}")
                    print(f"📥 输入参数：{action_input}")
                
                # 执行工具
                observation = self._execute_tool(action, action_input)
                
                if verbose:
                    print(f"👁️  执行结果：{observation}")
                
                # 添加到对话历史
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user", 
                    "content": f"Observation: {observation}"
                })
            
            else:
                if verbose:
                    print("\n❌ 无法解析LLM回复，尝试引导...")
                # 尝试引导LLM
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": "请按照正确格式输出：Thought, Action, Action Input 或 Final Answer"
                })
        
        return "任务未完成（超过最大步骤）"


# ============================================================
# 第四部分：实际测试
# ============================================================

def part2_real_demo():
    """真实演示"""
    print("\n" + "="*70)
    print("🚀 真正的LLM Agent演示")
    print("="*70)
    
    print("""
现在让LLM自己判断和选择工具！

观察：
1. LLM如何分析任务
2. LLM如何选择工具
3. 完全自动，无需if-else
    """)
    
    # 创建Agent
    agent = RealLLMAgent(TOOLS)
    
    # 测试任务
    test_tasks = [
        "帮我计算 123 + 456",
        "北京今天天气怎么样？",
        "现在几点了？",
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n\n{'='*70}")
        print(f"测试 {i}/{len(test_tasks)}")
        print(f"{'='*70}")
        
        try:
            result = agent.run(task)
            print(f"\n{'='*70}")
            print(f"✅ 任务完成！")
            print(f"{'='*70}")
        except Exception as e:
            print(f"\n❌ 出错：{e}")
        
        if i < len(test_tasks):
            input("\n按回车继续下一个测试...")


def part3_key_points():
    """关键点总结"""
    print("\n" + "="*70)
    print("📚 真正Agent的关键点")
    print("="*70)
    
    print("""
✅ 真正的Agent工作原理：

1️⃣ 系统提示词告诉LLM：
   - 你有哪些工具
   - 每个工具能做什么
   - 什么时候用什么工具
   - 输出什么格式

2️⃣ LLM分析任务：
   "帮我计算100+200"
   → LLM思考："这需要数学计算"
   → LLM决定："使用calculator工具"
   → LLM输出："Action: calculator"

3️⃣ Agent执行工具：
   - 解析LLM的输出
   - 调用对应的工具
   - 获得结果

4️⃣ 反馈给LLM：
   - 把工具结果告诉LLM
   - LLM继续思考
   - 直到任务完成

💡 与规则驱动的区别：

规则驱动：
  if "计算" in task:      # ← 手动判断
      use_calculator()

LLM驱动：
  llm.decide(task, tools) # ← AI自动判断

🎯 为什么这样更好？

1. 自动适应：
   - "100加200等于多少" ✅ 能理解
   - "帮我算一下100和200的和" ✅ 能理解
   - 不需要写规则

2. 智能推理：
   - 能理解复杂任务
   - 能多步推理
   - 像人一样思考

3. 可扩展：
   - 添加新工具，只需更新工具列表
   - 不需要改代码逻辑

⚠️ 注意：
- 需要好的系统提示词（告诉LLM怎么做）
- 需要清晰的工具描述（让LLM知道用途）
- 需要解析LLM的输出（提取Action和Input）
    """)


def main():
    """主函数"""
    print("="*70)
    print("🎓 真正的Agent：LLM自动判断")
    print("="*70)
    
    print("""
你的观察非常正确！

之前的代码用if-else判断，那是为了教学。
真正的Agent应该让LLM自己判断和选择工具。

让我带你看真正的实现！
    """)
    
    input("按回车开始...")
    
    try:
        # 第一部分：对比
        part1_comparison()
        
        # 第二部分：真实演示
        print("\n" + "="*70)
        print("现在运行真正的Agent（需要Ollama）")
        print("="*70)
        
        choice = input("\nOllama正在运行吗？(y/n): ").strip().lower()
        
        if choice == 'y':
            part2_real_demo()
        else:
            print("\n💡 请先启动Ollama，然后重新运行这个脚本")
        
        # 第三部分：总结
        part3_key_points()
        
        print("\n" + "="*70)
        print("🎉 学习完成！")
        print("="*70)
        
        print("""
现在你理解了：
✅ 规则驱动 vs LLM驱动的区别
✅ 真正的Agent如何工作
✅ 为什么LLM驱动更智能

下一步：
- 优化系统提示词
- 添加更多工具
- 处理更复杂的任务
        """)
    
    except KeyboardInterrupt:
        print("\n\n👋 已退出")
    except Exception as e:
        print(f"\n❌ 错误：{e}")


if __name__ == "__main__":
    main()
