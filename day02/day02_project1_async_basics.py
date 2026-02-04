"""
Day 2 - 项目1: 异步编程基础
理解async/await的工作原理
"""

import asyncio
import aiohttp
import time
from typing import List


# ============================================================
# 第一部分：理解同步 vs 异步
# ============================================================

def sync_task(name: str, duration: int):
    """同步任务：会阻塞执行"""
    print(f"🔵 {name} 开始 (同步)")
    time.sleep(duration)  # 模拟耗时操作
    print(f"✅ {name} 完成 (耗时 {duration}秒)")
    return f"{name}的结果"


async def async_task(name: str, duration: int):
    """异步任务：不会阻塞执行"""
    print(f"🟢 {name} 开始 (异步)")
    await asyncio.sleep(duration)  # 异步等待
    print(f"✅ {name} 完成 (耗时 {duration}秒)")
    return f"{name}的结果"


def demo_sync():
    """演示同步执行"""
    print("\n" + "="*60)
    print("📊 同步执行演示")
    print("="*60)
    
    start = time.time()
    
    # 一个接一个执行
    sync_task("任务1", 2)
    sync_task("任务2", 2)
    sync_task("任务3", 2)
    
    total = time.time() - start
    print(f"\n⏱️  总耗时: {total:.2f}秒")
    print(f"💡 同步执行：2+2+2 = {total:.0f}秒\n")


async def demo_async():
    """演示异步执行"""
    print("\n" + "="*60)
    print("📊 异步执行演示")
    print("="*60)
    
    start = time.time()
    
    # 同时执行多个任务
    tasks = [
        async_task("任务1", 2),
        async_task("任务2", 2),
        async_task("任务3", 2)
    ]
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks)
    
    total = time.time() - start
    print(f"\n⏱️  总耗时: {total:.2f}秒")
    print(f"💡 异步执行：同时进行，只需 ~{total:.0f}秒")
    print(f"🚀 速度提升: {6/total:.1f}x\n")
    
    return results


# ============================================================
# 第二部分：异步HTTP请求
# ============================================================

async def async_ollama_chat(prompt: str, model: str = "qwen2.5:14b") -> dict:
    """异步调用Ollama API"""
    url = "http://localhost:11434/api/chat"
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "keep_alive": "5m"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=60)) as response:
                result = await response.json()
                return {
                    "prompt": prompt,
                    "response": result.get("message", {}).get("content", ""),
                    "success": True
                }
        except Exception as e:
            return {
                "prompt": prompt,
                "response": f"错误: {str(e)}",
                "success": False
            }


async def demo_async_requests():
    """演示异步HTTP请求"""
    print("\n" + "="*60)
    print("📊 异步HTTP请求演示")
    print("="*60)
    
    questions = [
        "1+1等于几？",
        "Python是什么？",
        "什么是机器学习？"
    ]
    
    print(f"\n📝 同时向AI提问 {len(questions)} 个问题:")
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q}")
    
    print("\n🚀 开始异步请求...")
    start = time.time()
    
    # 创建所有任务
    tasks = [async_ollama_chat(q) for q in questions]
    
    # 并发执行
    results = await asyncio.gather(*tasks)
    
    total = time.time() - start
    
    print("\n📋 结果:")
    print("-" * 60)
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        print(f"\n{status} 问题 {i}: {result['prompt']}")
        print(f"   回答: {result['response'][:100]}...")
    
    print("\n" + "-" * 60)
    print(f"⏱️  总耗时: {total:.2f}秒")
    print(f"💡 如果同步执行，可能需要 {len(questions) * 3:.0f}+ 秒")
    print(f"🚀 异步带来 ~{(len(questions) * 3) / total:.1f}x 速度提升！")


# ============================================================
# 第三部分：进度跟踪
# ============================================================

async def async_task_with_progress(task_id: int, duration: int) -> dict:
    """带进度显示的异步任务"""
    print(f"🟢 任务{task_id} 开始")
    
    start = time.time()
    await asyncio.sleep(duration)
    elapsed = time.time() - start
    
    print(f"✅ 任务{task_id} 完成 ({elapsed:.1f}秒)")
    
    return {
        "task_id": task_id,
        "duration": duration,
        "actual_time": elapsed
    }


async def demo_with_progress():
    """演示带进度的异步执行"""
    print("\n" + "="*60)
    print("📊 带进度跟踪的异步执行")
    print("="*60)
    
    print("\n🚀 启动5个任务，随机耗时...")
    
    import random
    tasks = [
        async_task_with_progress(i, random.randint(1, 3))
        for i in range(1, 6)
    ]
    
    start = time.time()
    results = await asyncio.gather(*tasks)
    total = time.time() - start
    
    print(f"\n📊 统计:")
    print(f"   任务数: {len(results)}")
    print(f"   总耗时: {total:.2f}秒")
    print(f"   平均耗时: {sum(r['actual_time'] for r in results) / len(results):.2f}秒")


# ============================================================
# 第四部分：错误处理
# ============================================================

async def async_task_with_error(task_id: int, will_fail: bool = False):
    """可能失败的异步任务"""
    print(f"🟢 任务{task_id} 开始")
    
    await asyncio.sleep(1)
    
    if will_fail:
        print(f"❌ 任务{task_id} 失败")
        raise Exception(f"任务{task_id}遇到错误")
    
    print(f"✅ 任务{task_id} 成功")
    return f"任务{task_id}的结果"


async def demo_error_handling():
    """演示异步错误处理"""
    print("\n" + "="*60)
    print("📊 异步错误处理演示")
    print("="*60)
    
    print("\n🚀 启动5个任务，其中2个会失败...")
    
    tasks = [
        async_task_with_error(1, False),
        async_task_with_error(2, True),   # 会失败
        async_task_with_error(3, False),
        async_task_with_error(4, True),   # 会失败
        async_task_with_error(5, False),
    ]
    
    # 方法1：return_exceptions=True，收集所有结果（包括异常）
    print("\n方法1: 收集所有结果（包括错误）")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    
    print(f"\n📊 结果:")
    print(f"   ✅ 成功: {len(successes)}")
    print(f"   ❌ 失败: {len(failures)}")
    
    # 方法2：单独处理每个任务
    print("\n方法2: 单独处理每个任务")
    
    async def safe_task(task_id, will_fail):
        try:
            return await async_task_with_error(task_id, will_fail)
        except Exception as e:
            return f"错误: {str(e)}"
    
    tasks2 = [
        safe_task(i, i % 2 == 0)  # 偶数任务失败
        for i in range(6, 11)
    ]
    
    results2 = await asyncio.gather(*tasks2)
    print(f"\n所有任务都有结果（成功或错误消息）:")
    for i, result in enumerate(results2, 6):
        status = "✅" if not result.startswith("错误") else "❌"
        print(f"   {status} 任务{i}: {result}")


# ============================================================
# 主程序
# ============================================================

async def main():
    """主函数"""
    print("="*60)
    print("🎓 Day 2 - 项目1: 异步编程基础")
    print("="*60)
    
    # 演示1：同步 vs 异步
    demo_sync()
    await demo_async()
    
    # 演示2：异步HTTP请求
    try:
        await demo_async_requests()
    except Exception as e:
        print(f"\n⚠️  HTTP请求演示跳过（Ollama未运行）: {e}")
    
    # 演示3：进度跟踪
    await demo_with_progress()
    
    # 演示4：错误处理
    await demo_error_handling()
    
    # 总结
    print("\n" + "="*60)
    print("📚 关键知识点总结")
    print("="*60)
    print("""
1. async/await 基础:
   - async def: 定义异步函数
   - await: 等待异步操作完成
   - asyncio.gather(): 并发执行多个任务

2. 异步的优势:
   - 同时执行多个IO操作
   - 大幅提升性能（特别是网络请求）
   - 不阻塞程序执行

3. 错误处理:
   - return_exceptions=True: 收集异常而不抛出
   - try/except: 单独处理每个任务
   - 优雅降级：部分失败不影响整体

4. 实际应用:
   - 批量API调用
   - 并发数据处理
   - 提升用户体验

💡 记住：异步不会让单个任务更快，但能让多个任务同时进行！
    """)


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
