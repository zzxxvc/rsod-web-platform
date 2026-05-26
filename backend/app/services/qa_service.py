"""
QA 服务模块 - 处理AI问答逻辑
"""
import os
import asyncio
from typing import Optional

# 尝试导入 OpenAI，如果不存在则使用模拟实现
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


async def get_qa_answer(question: str) -> str:
    """
    获取问题的AI回答
    
    Args:
        question: 用户提出的问题
    
    Returns:
        AI生成的回答
    """
    if OPENAI_AVAILABLE:
        return await _get_bailian_answer(question)
    else:
        return _get_mock_answer(question)


async def _get_bailian_answer(question: str) -> str:
    """
    通过阿里云百炼 dashscope SDK 获取回答
    ✅ 使用已验证成功的配置：qwen-turbo + Generation.call + prompt
    """
    import dashscope
    import os
    
    api_key = os.getenv("BAILIAN_API_KEY")
    if not api_key:
        return "错误：未配置 BAILIAN_API_KEY 环境变量"
    
    # 🔑 关键：主线程绑定 Key（dashscope 使用全局变量）
    dashscope.api_key = api_key
    
    try:
        loop = asyncio.get_event_loop()
        
        def call_dashscope():
            # 🔥 子线程内也绑定一次，确保 100% 可靠（子线程不继承主线程全局变量）
            dashscope.api_key = os.getenv("BAILIAN_API_KEY")
            
            # ✅ 使用已验证成功的配置
            return dashscope.Generation.call(
                model="qwen-turbo",  # ✅ 已验证能通的模型
                prompt=question,     # ✅ Generation 接口用 prompt 参数
                timeout=60           # 延长超时，防止网络波动
            )
        
        # 在线程池执行同步调用，避免阻塞 FastAPI 事件循环
        response = await loop.run_in_executor(None, call_dashscope)
        
        # ✅ Generation 接口返回结构：response.output.text
        if response.status_code == 200:
            return response.output.text
        else:
            # 返回阿里云业务错误码，方便排查
            return f"AI 服务报错: {response.code} - {response.message}"
            
    except Exception as e:
        # 🔥 打印完整堆栈到终端，方便后续调试
        import traceback
        print(f"\n❌ [ERROR] dashscope 调用失败 - 完整堆栈:")
        traceback.print_exc()
        print(f"❌ [ERROR] 简要: {type(e).__name__}: {e}\n")
        
        return f"调用大模型异常: {str(e)}"


def _get_mock_answer(question: str) -> str:
    """
    模拟 AI 回答（当 OpenAI 不可用时）
    """
    keywords_answers = {
        "痤疮": "痤疮是毛囊皮脂腺单位的慢性炎症性疾病。建议保持面部清洁，避免挤压，必要时就医进行专业治疗。",
        "湿疹": "湿疹是一种常见的皮肤炎症反应。建议避免刺激性物质，保持皮肤湿润，严重时应就医治疗。",
        "真菌": "皮肤真菌感染需要专业诊断。建议保持患处干燥，避免自行用药，应前往医院进行真菌检查。",
        "癣": "皮肤癣是真菌感染，具有传染性。建议保持清洁卫生，穿透气衣物，必要时使用抗真菌药物。",
        "晒伤": "晒伤是紫外线过度照射引起的皮肤损伤。建议冷敷患处，补水保湿，预防方面应涂防晒霜。",
    }
    
    for keyword, answer in keywords_answers.items():
        if keyword in question:
            return answer
    
    return "感谢您的提问。根据您描述的症状，建议：\n1. 拍摄清晰的患处照片供医生参考\n2. 记录症状出现的时间和演变过程\n3. 尽快咨询皮肤科医生进行专业诊断\n\n如果症状加重或伴有瘙痒、疼痛，应立即就医。"