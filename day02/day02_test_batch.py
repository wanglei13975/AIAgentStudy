"""
Day 2 - 批量处理测试版
超简化版本，确保能正常工作
"""

import asyncio
import aiohttp
import time


async def simple_request(session, question, task_id):
    """单个简单请求"""
    url = "http://localhost:11434/api/chat"
    
    data = {
        "model": "qwen2.5:14b",
        "messages": [{"role": "user", "content": question}],
        "stream": True,
        "keep_alive": "10m",
        "options": {
            "num_ctx": 1024,  # 小上下文
            "num_predict": 100  # 短回答
        }
    }
    
    print(f"🟢 任务{task_id} 开始: {question}")
    start = time.time()
    
    try:
        async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=120)) as response:
            full_response = ""
            
            async for line in response.content:
                if line:
                    try:
                        import json
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        full_response += content
                    except:
                        continue
            
            elapsed = time.time() - start
            print(f"✅ 任务{task_id} 完成 ({elapsed:.1f}秒)")
            return {"id": task_id, "question": question, "answer": full_response, "success": True}
    
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ 任务{task_id} 失败 ({elapsed:.0f}秒): {str(e)[:50]}")
        return {"id": task_id, "question": question, "error": str(e), "success": False}


async def batch_process(questions, max_concurrent=2):
    """批量处理"""
    print(f"\n{'='*60}")
    print(f"🚀 批量处理 {len(questions)} 个问题")
    print(f"🔢 并发数: {max_concurrent}")
    print(f"{'='*60}\n")
    
    start = time.time()
    
    # 创建semaphore限制并发
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_request(session, q, i):
        async with semaphore:
            return await simple_request(session, q, i)
    
    # 执行所有请求
    async with aiohttp.ClientSession() as session:
        tasks = [limited_request(session, q, i) for i, q in enumerate(questions)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total = time.time() - start
    
    # 统计
    successes = [r for r in results if isinstance(r, dict) and r.get('success')]
    failures = [r for r in results if isinstance(r, dict) and not r.get('success')]
    
    print(f"\n{'='*60}")
    print(f"📊 处理完成")
    print(f"{'='*60}")
    print(f"✅ 成功: {len(successes)}/{len(questions)}")
    print(f"❌ 失败: {len(failures)}/{len(questions)}")
    print(f"⏱️  总耗时: {total:.2f}秒")
    
    if successes:
        avg = sum(1 for _ in successes) / total
        print(f"🚀 吞吐量: {avg:.2f} 任务/秒")
    
    print(f"{'='*60}\n")
    
    return results


async def test_single():
    """测试单个请求"""
    print("\n" + "="*60)
    print("🧪 测试1: 单个请求")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        result = await simple_request(session, "1+1等于几？", 0)
    
    if result['success']:
        print(f"\n✅ 测试成功！")
        print(f"回答: {result['answer'][:100]}")
    else:
        print(f"\n❌ 测试失败: {result.get('error')}")
    
    return result['success']


async def test_batch_simple():
    """测试批量处理（简单问题）"""
    print("\n" + "="*60)
    print("🧪 测试2: 批量处理（3个简单问题）")
    print("="*60)
    
    questions = [
        "1+1=?",
        "2+2=?",
        "3+3=?"
    ]
    
    results = await batch_process(questions, max_concurrent=2)
    
    # 显示结果
    print("结果预览:")
    for r in results[:3]:
        if isinstance(r, dict) and r.get('success'):
            print(f"\nQ: {r['question']}")
            print(f"A: {r['answer'][:80]}...")


async def test_batch_medium():
    """测试批量处理（稍复杂问题）"""
    print("\n" + "="*60)
    print("🧪 测试3: 批量处理（5个中等问题）")
    print("="*60)
    
    questions = [
        "什么是Python？（一句话）",
        "什么是API？（一句话）",
        "什么是变量？（一句话）",
        "什么是函数？（一句话）",
        "什么是循环？（一句话）"
    ]
    
    results = await batch_process(questions, max_concurrent=3)
    
    successes = [r for r in results if isinstance(r, dict) and r.get('success')]
    print(f"\n✅ 成功率: {len(successes)}/{len(questions)} ({len(successes)/len(questions)*100:.0f}%)")


async def main():
    print("="*60)
    print("🧪 批量处理 - 测试版")
    print("="*60)
    print("\n这个版本用于诊断问题，使用:")
    print("  - 流式输出")
    print("  - keep_alive")
    print("  - 小上下文")
    print("  - 短回答")
    print("  - 低并发")
    
    try:
        # 测试1：单个请求
        if not await test_single():
            print("\n⚠️  基本连接有问题，请检查Ollama是否运行")
            return
        
        input("\n按回车继续批量测试...")
        
        # 测试2：简单批量
        await test_batch_simple()
        
        input("\n按回车继续更多测试...")
        
        # 测试3：中等批量
        await test_batch_medium()
        
        print("\n" + "="*60)
        print("✅ 测试完成！")
        print("="*60)
        print("""
如果以上测试都成功:
  → 说明批量处理可以正常工作
  → 原来的超时可能是因为并发太高或问题太复杂

如果还是失败:
  → 检查Ollama是否正常运行
  → 尝试使用更小的模型 (qwen2.5:7b)
  → 检查系统资源（内存、CPU）

优化建议:
  - 并发数保持在2-3
  - 问题尽量简短
  - 使用 num_predict 限制输出长度
  - 首次运行会慢，模型加载后会快很多
        """)
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
