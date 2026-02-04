"""
练习3：温度对比实验（手动版）
逐步测试，方便观察每次的差异
"""

import requests
import json
import time


def test_with_temperature(question: str, temperature: float, model: str = "qwen2.5:14b"):
    """测试指定温度"""
    url = "http://localhost:11434/api/chat"
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": question}],
        "stream": False,
        "keep_alive": "5m",
        "options": {
            "temperature": temperature,
            "num_ctx": 2048,
        }
    }
    
    print(f"\n{'='*70}")
    print(f"🌡️  Temperature: {temperature}")
    print(f"{'='*70}")
    print("🤔 AI正在思考...")
    
    start = time.time()
    
    try:
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start
        
        answer = result.get("message", {}).get("content", "")
        
        print(f"\n🤖 回复内容:")
        print("-" * 70)
        print(answer)
        print("-" * 70)
        print(f"⏱️  耗时: {elapsed:.2f}秒")
        print(f"📏 长度: {len(answer)} 字符")
        
        return answer
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def main():
    print("="*70)
    print("🔬 温度对比实验 - 手动版")
    print("="*70)
    
    question = "用Python写一个快速排序"
    
    print(f"\n📝 实验问题: {question}")
    print("\n我们将测试三个温度值:")
    print("  🧊 0.1 - 低温(确定性强)")
    print("  🌡️  0.5 - 中温(平衡)")
    print("  🔥 0.9 - 高温(随机性强)")
    
    input("\n按回车键开始第一次测试 (Temperature=0.1)...")
    
    # 测试1: 低温
    print("\n" + "🧊"*35)
    print("测试1: 低温模式")
    print("🧊"*35)
    result1 = test_with_temperature(question, 0.1)
    
    input("\n\n按回车键继续第二次测试 (Temperature=0.5)...")
    
    # 测试2: 中温
    print("\n" + "🌡️ "*35)
    print("测试2: 中温模式")
    print("🌡️ "*35)
    result2 = test_with_temperature(question, 0.5)
    
    input("\n\n按回车键继续第三次测试 (Temperature=0.9)...")
    
    # 测试3: 高温
    print("\n" + "🔥"*35)
    print("测试3: 高温模式")
    print("🔥"*35)
    result3 = test_with_temperature(question, 0.9)
    
    # 总结
    print("\n\n" + "="*70)
    print("📊 实验总结")
    print("="*70)
    
    if result1 and result2 and result3:
        print(f"\n📏 回复长度对比:")
        print(f"   Temperature 0.1: {len(result1)} 字符")
        print(f"   Temperature 0.5: {len(result2)} 字符")
        print(f"   Temperature 0.9: {len(result3)} 字符")
        
        print(f"\n🔍 观察要点:")
        print("""
请对比三次回复，注意以下几点:

1. 代码结构:
   - 三次的实现思路是否相同？
   - 是否都选择了递归/迭代方案？

2. 注释和说明:
   - 哪个温度的注释更详细？
   - 解释性文字有什么差异？

3. 代码风格:
   - 变量命名有何不同？
   - 代码的简洁程度？

4. 额外内容:
   - 是否包含测试代码？
   - 是否有使用示例？

💡 思考题:
- 如果是代码生成任务，你会选择哪个温度？为什么？
- 如果是创意写作任务，你会选择哪个温度？为什么？
        """)
        
        # 保存结果
        save = input("\n是否保存实验结果到文件？(y/n): ")
        if save.lower() == 'y':
            filename = f"temperature_comparison_{int(time.time())}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("温度对比实验结果\n")
                f.write("="*70 + "\n\n")
                
                f.write(f"问题: {question}\n\n")
                
                f.write("Temperature 0.1:\n")
                f.write("-"*70 + "\n")
                f.write(result1)
                f.write("\n\n")
                
                f.write("Temperature 0.5:\n")
                f.write("-"*70 + "\n")
                f.write(result2)
                f.write("\n\n")
                
                f.write("Temperature 0.9:\n")
                f.write("-"*70 + "\n")
                f.write(result3)
                f.write("\n")
            
            print(f"✅ 已保存到: {filename}")


if __name__ == "__main__":
    main()
