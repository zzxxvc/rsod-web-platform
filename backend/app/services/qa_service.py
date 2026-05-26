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
    通过阿里云百炼 API 获取回答
    """
    api_key = os.getenv("BAILIAN_API_KEY")
    if not api_key:
        return "错误：未配置 BAILIAN_API_KEY 环境变量"
    
    try:
        # 在线程池中运行同步的 OpenAI 调用
        loop = asyncio.get_event_loop()
        
        def call_bailian():
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.bailian.aliyun.com/v1"
            )
            
            response = client.chat.completions.create(
                model="qwen-max",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的皮肤病变诊断助手。请根据用户的描述，提供有用的诊断建议、可能的病变类型和复诊建议。"
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        return await loop.run_in_executor(None, call_bailian)
    
    except Exception as e:
        return f"抱歉，调用 AI 服务出错: {str(e)}"


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
