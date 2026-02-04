"""
Day 3 - 练习1：添加新工具
学习如何扩展Agent的能力

任务：添加一个天气查询工具
"""

import requests
import json


# ============================================================
# 步骤1：定义天气工具
# ============================================================

print("="*70)
print("📚 练习1：添加天气查询工具")
print("="*70)

print("""
我们要添加一个新工具：weather（天气查询）

工具的三要素：
1. name（名称）：工具叫什么
2. description（描述）：工具能做什么，何时使用
3. function（函数）：实际执行的代码

让我们开始！
""")

input("按回车看第一步...")

print("\n" + "-"*70)
print("步骤1：定义工具函数")
print("-"*70)

def weather(city: str) -> str:
    """
    查询城市天气（模拟版本）
    
    在真实项目中，这里会调用天气API
    现在我们用假数据模拟
    """
    # 模拟天气数据
    weather_data = {
        "北京": "北京今天晴朗，温度 15-25°C，空气质量良好",
        "上海": "上海今天多云，温度 18-26°C，有小雨",
        "广州": "广州今天晴朗，温度 22-30°C，炎热",
        "深圳": "深圳今天晴朗，温度 23-31°C，紫外线强",
        "成都": "成都今天阴天，温度 16-22°C，适合出行",
    }
    
    # 查找城市
    for key in weather_data:
        if key in city:
            return weather_data[key]
    
    # 默认返回
    return f"抱歉，暂无{city}的天气信息"

print("""
✅ 已定义函数：

def weather(city: str) -> str:
    \"\"\"查询城市天气\"\"\"
    # 模拟返回天气数据
    ...

让我们测试一下：
""")

# 测试工具
test_cities = ["北京", "上海", "杭州"]

for city in test_cities:
    result = weather(city)
    print(f"\n🌡️  {city}: {result}")

input("\n✅ 工具函数测试成功！按回车继续...")


# ============================================================
# 步骤2：将工具添加到工具列表
# ============================================================

print("\n" + "-"*70)
print("步骤2：创建工具描述")
print("-"*70)

print("""
现在我们要把函数包装成Agent能理解的格式。

重点是description（描述）：
- 要清楚说明工具的功能
- 要说明何时使用这个工具
- 要说明输入格式

这样LLM才知道什么时候该用这个工具！
""")

# 原有工具
def calculator(expression: str) -> str:
    """计算器"""
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

# 工具列表
tools = [
    {
        "name": "calculator",
        "description": "执行数学计算。输入：数学表达式（如：2+2, 10*5）",
        "function": calculator
    },
    {
        "name": "get_time",
        "description": "获取当前日期和时间",
        "function": get_time
    },
    {
        "name": "weather",  # 新工具！
        "description": "查询城市天气。输入：城市名称（如：北京、上海）。当用户询问天气、温度、气象等信息时使用。",
        "function": weather
    }
]

print("\n✅ 工具列表：")
for i, tool in enumerate(tools, 1):
    print(f"\n{i}. {tool['name']}")
    print(f"   描述：{tool['description']}")

input("\n✅ 工具添加完成！按回车继续...")


# ============================================================
# 步骤3：创建Agent并测试
# ============================================================

print("\n" + "-"*70)
print("步骤3：创建Agent并测试新工具")
print("-"*70)

print("""
现在我们创建一个简单的Agent来测试天气工具。

这个Agent会：
1. 接收用户任务
2. 判断是否需要查询天气
3. 调用天气工具
4. 返回结果
""")

class SimpleAgent:
    """简单的基于规则的Agent"""
    
    def __init__(self, tools):
        self.tools = {t['name']: t for t in tools}
    
    def run(self, task: str):
        """执行任务"""
        print(f"\n{'='*60}")
        print(f"📝 任务：{task}")
        print(f"{'='*60}")
        
        # 判断任务类型
        if any(word in task for word in ["天气", "温度", "气温", "下雨"]):
            print("💭 Thought: 用户想查询天气")
            
            # 提取城市名
            cities = ["北京", "上海", "广州", "深圳", "成都"]
            city = None
            for c in cities:
                if c in task:
                    city = c
                    break
            
            if city:
                print(f"🔧 Action: weather('{city}')")
                result = self.tools['weather']['function'](city)
                print(f"👁️  Observation: {result}")
                print(f"\n✅ Final Answer: {result}")
                return result
            else:
                return "请告诉我您想查询哪个城市的天气"
        
        elif "计算" in task or any(c in task for c in "+-*/"):
            print("💭 Thought: 这是计算任务")
            import re
            numbers = re.findall(r'[\d+\-*/()]+', task)
            if numbers:
                expr = numbers[0]
                print(f"🔧 Action: calculator('{expr}')")
                result = self.tools['calculator']['function'](expr)
                print(f"👁️  Observation: {result}")
                print(f"\n✅ Final Answer: {result}")
                return result
        
        elif "时间" in task or "几点" in task:
            print("💭 Thought: 用户想知道时间")
            print(f"🔧 Action: get_time()")
            result = self.tools['get_time']['function']()
            print(f"👁️  Observation: {result}")
            print(f"\n✅ Final Answer: {result}")
            return result
        
        return "抱歉，我不知道如何处理这个任务"

# 创建Agent
agent = SimpleAgent(tools)

print("\n开始测试：")
print("="*60)

# 测试任务
test_tasks = [
    "北京今天天气怎么样？",
    "上海会下雨吗？",
    "查询一下深圳的温度",
]

for task in test_tasks:
    agent.run(task)
    print()
    input("按回车继续下一个测试...")

print("\n" + "="*70)
print("🎉 练习1完成！")
print("="*70)

print("""
✅ 你学会了：

1. 如何定义新工具
   - 写一个Python函数
   - 返回字符串结果

2. 如何描述工具
   - 清楚说明功能
   - 说明何时使用
   - 说明输入格式

3. 如何添加到工具列表
   - name, description, function

4. Agent如何使用新工具
   - 理解任务
   - 选择合适的工具
   - 调用并返回结果

💡 思考题：
你能添加一个翻译工具吗？
- 输入：英文句子
- 输出：中文翻译

提示：可以用简单的字典模拟翻译
""")
