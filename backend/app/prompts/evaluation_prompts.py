"""
评价生成提示词模板
用于根据对话历史生成用户表现评价
"""
from typing import List, Dict, Any


def get_evaluation_prompt(
    chat_history: List[Dict[str, str]],
    user_profile: Dict[str, Any],
    bot_profile: Dict[str, Any]
) -> str:
    """
    生成对话评价的提示词

    Args:
        chat_history: 对话历史记录
        user_profile: 用户资料
        bot_profile: 机器人资料

    Returns:
        评价生成提示词字符串
    """
    # 格式化对话历史
    formatted_history = ""
    for i, msg in enumerate(chat_history, 1):
        role = "用户" if msg.get("role") == "user" else bot_profile.get("name", "对方")
        content = msg.get("content", "")
        formatted_history += f"{i}. {role}: {content}\n"

    return f"""你是一位经验丰富的相亲顾问和情感沟通专家。请对以下相亲对话进行专业评价分析。

【用户信息】
- 性别：{user_profile.get('gender', 'male')}
- 年龄：{user_profile.get('age', 25)}岁
- 职业：{user_profile.get('occupation', '未知')}
- 兴趣爱好：{user_profile.get('interests', '未知')}

【对话对象信息】
- 姓名：{bot_profile.get('name', '小美')}
- 年龄：{bot_profile.get('age', 25)}岁
- 职业：{bot_profile.get('occupation', '未知')}
- 兴趣爱好：{bot_profile.get('interests', '未知')}

【完整对话记录】
{formatted_history}

【评价维度】
请从以下五个维度进行评价分析：

1. **开场表现**（15%权重）
   - 第一印象是否良好
   - 话题选择是否恰当
   - 是否展现了基本的礼貌和友好

2. **互动质量**（30%权重）
   - 话题连贯性和深度
   - 回应质量和相关性
   - 是否能展开有效交流

3. **情商表现**（25%权重）
   - 共情能力和情感感知
   - 对对方情绪的捕捉
   - 情感连接的建立

4. **对话技巧**（20%权重）
   - 倾听能力和提问技巧
   - 幽默感和氛围调节
   - 自我暴露的程度把控

5. **整体印象**（10%权重）
   - 真诚度和可信度
   - 礼貌和尊重程度
   - 综合吸引力感知

【输出要求】
请严格按照以下JSON格式输出评价结果，不要添加任何额外文字：

```json
{{
    "attraction_score": 评分（0-100整数）,
    "strengths": [
        "优点1（具体描述，20字以内）",
        "优点2（具体描述，20字以内）",
        "优点3（具体描述，20字以内）"
    ],
    "suggestions": [
        "改进建议1（具体可操作，25字以内）",
        "改进建议2（具体可操作，25字以内）",
        "改进建议3（具体可操作，25字以内）",
        "改进建议4（具体可操作，25字以内）"
    ],
    "summary": "总体评价（50字以内的总结性评语）"
}}
```

请生成这个评价："""
