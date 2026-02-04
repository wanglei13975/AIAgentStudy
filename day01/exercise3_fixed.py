"""
练习3：温度对比实验（修复超时版本）
增加超时时间，添加进度提示
"""

import requests
import json
import time
import sys


def test_with_temperature(question: str, temperature: float, model: str = "qwen2.5:14b"):
    """测试指定温度，增加超时时间和进度提示"""
    url = "http://localhost:11434/api/chat"
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": question}],
        "stream": True,  # 改为流式，避免超时
        "keep_alive": "10m",
        "options": {
            "temperature": temperature,
            "num_ctx": 2048,
        }
    }
    
    print(f"\n{'='*70}")
    print(f"🌡️  Temperature: {temperature}")
    print(f"{'='*70}")
    print("🤔 AI正在思考（首次会较慢，请耐心等待）...")
    
    start = time.time()
    
    try:
        # 使用流式输出，避免超时
        response = requests.post(url, json=data, stream=True, timeout=300)  # 增加到5分钟
        response.raise_for_status()
        
        full_response = ""
        print(f"\n🤖 回复内容:")
        print("-" * 70)
        
        # 流式接收，实时显示
        first_chunk = True
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    content = chunk.get("message", {}).get("content", "")
                    
                    if first_chunk and content:
                        chunk_time = time.time() - start
                        print(f"⚡ 首个响应: {chunk_time:.2f}秒")
                        print()
                        first_chunk = False
                    
                    full_response += content
                    print(content, end="", flush=True)
                except json.JSONDecodeError:
                    continue
        
        print()
        print("-" * 70)
        
        elapsed = time.time() - start
        print(f"⏱️  总耗时: {elapsed:.2f}秒")
        print(f"📏 长度: {len(full_response)} 字符")
        
        return full_response
    
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"❌ 超时错误（已等待 {elapsed:.0f} 秒）")
        print("💡 建议:")
        print("   1. 检查Ollama是否正在运行: ollama list")
        print("   2. 尝试使用更小的模型: qwen2.5:7b")
        print("   3. 检查系统资源是否充足")
        return None
    
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误：无法连接到Ollama")
        print("💡 请确保Ollama正在运行: ollama serve")
        return None
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def check_ollama_status():
    """检查Ollama状态"""
    print("🔍 检查Ollama状态...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama正在运行")
            print(f"📦 可用模型: {len(models)} 个")
            
            for model in models:
                name = model.get('name', 'unknown')
                size = model.get('size', 0) / (1024**3)  # 转换为GB
                print(f"   - {name} ({size:.1f} GB)")
            return True
    except:
        print("❌ 无法连接到Ollama")
        print("💡 请先启动Ollama: ollama serve")
        return False
    
    return False


def main():
    print("="*70)
    print("🔬 温度对比实验 - 修复超时版")
    print("="*70)
    
    # 先检查Ollama状态
    if not check_ollama_status():
        print("\n⚠️  请先启动Ollama，然后重新运行此脚本")
        return
    
    print("\n" + "="*70)
    
    question = "用Python写一个快速排序"
    
    print(f"\n📝 实验问题: {question}")
    print("\n⚠️  注意事项:")
    print("   - 首次运行会加载模型到内存，可能需要1-3分钟")
    print("   - 使用流式输出，可以实时看到生成过程")
    print("   - 如果模型太大导致超时，建议使用 qwen2.5:7b")
    print("\n我们将测试三个温度值:")
    print("  🧊 0.1 - 低温(确定性强)")
    print("  🌡️  0.5 - 中温(平衡)")
    print("  🔥 0.9 - 高温(随机性强)")
    
    # 询问是否继续
    choice = input("\n准备好了吗？按回车开始，或输入 'q' 退出: ")
    if choice.lower() == 'q':
        print("👋 已退出")
        return
    
    results = []
    
    # 测试1: 低温
    print("\n" + "🧊"*35)
    print("测试1: 低温模式 (Temperature=0.1)")
    print("🧊"*35)
    result1 = test_with_temperature(question, 0.1)
    if result1:
        results.append(('0.1', result1))
    
    if result1 is None:
        retry = input("\n是否继续下一个测试？(y/n): ")
        if retry.lower() != 'y':
            print("👋 实验结束")
            return
    else:
        input("\n✅ 第一次测试完成！按回车继续下一次测试...")
    
    # 测试2: 中温
    print("\n" + "🌡️ "*35)
    print("测试2: 中温模式 (Temperature=0.5)")
    print("🌡️ "*35)
    result2 = test_with_temperature(question, 0.5)
    if result2:
        results.append(('0.5', result2))
    
    if result2 is None:
        retry = input("\n是否继续最后一个测试？(y/n): ")
        if retry.lower() != 'y':
            print("👋 实验结束")
            if results:
                save_results(question, results)
            return
    else:
        input("\n✅ 第二次测试完成！按回车继续最后一次测试...")
    
    # 测试3: 高温
    print("\n" + "🔥"*35)
    print("测试3: 高温模式 (Temperature=0.9)")
    print("🔥"*35)
    result3 = test_with_temperature(question, 0.9)
    if result3:
        results.append(('0.9', result3))
    
    # 总结
    print("\n\n" + "="*70)
    print("📊 实验总结")
    print("="*70)
    
    if len(results) >= 2:
        print(f"\n✅ 成功完成 {len(results)} 次测试")
        print(f"\n📏 回复长度对比:")
        for temp, result in results:
            print(f"   Temperature {temp}: {len(result)} 字符")
        
        print(f"\n🔍 观察要点:")
        print("""
请对比回复，注意以下几点:

1. 代码结构是否相同？
2. 注释详细程度的差异
3. 是否包含额外的说明或示例
4. 代码风格的不同

💡 思考:
- 哪个温度的结果你最满意？
- 如果用于生产环境，你会选择哪个？
        """)
        
        # 保存结果
        save_results(question, results)
    else:
        print("\n⚠️  测试未完成")
        print("💡 如果持续超时，建议:")
        print("   1. 使用更小的模型: qwen2.5:7b")
        print("   2. 增加系统可用内存")
        print("   3. 使用 GPU 加速（如果可用）")


def save_results(question, results):
    """保存结果"""
    save = input("\n是否保存实验结果到文件？(y/n): ")
    if save.lower() == 'y':
        filename = f"temperature_comparison_{int(time.time())}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("温度对比实验结果\n")
            f.write("="*70 + "\n\n")
            f.write(f"问题: {question}\n\n")
            
            for temp, result in results:
                f.write(f"\nTemperature {temp}:\n")
                f.write("-"*70 + "\n")
                f.write(result)
                f.write("\n\n")
        
        print(f"✅ 已保存到: {filename}")


if __name__ == "__main__":
    main()
