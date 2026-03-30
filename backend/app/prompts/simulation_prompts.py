"""
AI模拟对话提示词模板
用于多候选人相亲模拟系统
"""
from typing import Dict, Any, List


SCENARIO_CONFIGS: Dict[str, Dict[str, Any]] = {
    "first_chat": {
        "label": "初识聊天",
        "summary": "围绕第一印象、共同兴趣和聊天舒适感推进关系。",
        "stage_goal": "先建立基本好感，再自然试探是否愿意继续接触。",
        "events": [
            {
                "key": "common_interest",
                "title": "共同兴趣深入",
                "cue": "双方发现了一个共同兴趣，需要把话题从表面喜好聊到具体经历和真实感受。",
                "goal": "建立真实共鸣，而不是浅层附和。"
            },
            {
                "key": "meeting_signal",
                "title": "是否愿意见面",
                "cue": "聊天已经顺了一段时间，双方会自然试探是否愿意线下见面或继续保持联系。",
                "goal": "给出清晰但不冒进的关系推进信号。"
            }
        ]
    },
    "weekend_plan": {
        "label": "周末约会计划",
        "summary": "围绕第一次线下安排，观察节奏、偏好和临场应对。",
        "stage_goal": "从轻松设想到偏好磨合，看双方能否一起把计划落地。",
        "events": [
            {
                "key": "preference_difference",
                "title": "安排偏好差异",
                "cue": "两人对周末安排的节奏或活动类型有点不同，需要沟通取舍。",
                "goal": "展现尊重、表达偏好，并尝试找到折中方案。"
            },
            {
                "key": "plan_change",
                "title": "临时变化应对",
                "cue": "原本的安排遇到小变化，比如天气、加班或临时改时间，需要调整计划。",
                "goal": "观察双方处理变化时的情绪和合作感。"
            }
        ]
    },
    "future_probe": {
        "label": "未来关系试探",
        "summary": "围绕工作、城市和关系节奏，测试长期相处潜力。",
        "stage_goal": "在不沉重的前提下聊到现实选择和关系期待。",
        "events": [
            {
                "key": "city_choice",
                "title": "城市与工作取舍",
                "cue": "双方会聊到未来工作发展、是否愿意换城市或怎样平衡现实机会。",
                "goal": "看价值观和生活规划是否兼容。"
            },
            {
                "key": "pace_expectation",
                "title": "关系节奏预期",
                "cue": "双方开始试探关系推进速度，比如多久见面、如何确认关系、各自对稳定关系的期待。",
                "goal": "给出成熟、真诚的关系态度。"
            }
        ]
    }
}


def format_user_profile(user_profile: Dict[str, Any]) -> str:
    """格式化用户资料"""
    return f"""性别: {user_profile.get('gender', '未知')}
年龄: {user_profile.get('age', 25)}岁
所在城市: {user_profile.get('city', '未知')}
学历: {user_profile.get('education', '未知')}
职业: {user_profile.get('occupation', '未知')}
兴趣爱好: {user_profile.get('interests', '未知')}
自我描述: {user_profile.get('self_description', '未填写')}
理想型: {user_profile.get('ideal_type', '未填写')}"""


def format_candidate_profile(candidate_profile: Dict[str, Any]) -> str:
    """格式化候选人资料"""
    return f"""姓名: {candidate_profile.get('name', '未知')}
年龄: {candidate_profile.get('age', 25)}岁
性别: {candidate_profile.get('gender', '未知')}
所在城市: {candidate_profile.get('city', '未知')}
职业: {candidate_profile.get('occupation', '未知')}
兴趣爱好: {candidate_profile.get('interests', '未知')}
性格: {candidate_profile.get('personality', '未知')}
背景故事: {candidate_profile.get('backstory', '热爱生活，期待遇到对的人')}
对话风格: {candidate_profile.get('chat_style', '自然亲切，真诚友善')}"""


def format_chat_history(chat_history: List[Dict[str, str]]) -> str:
    """格式化对话历史"""
    if not chat_history:
        return "（这是对话开始）"

    formatted = []
    for msg in chat_history:
        role = "用户" if msg.get('role') == 'user' else "候选人"
        formatted.append(f"{role}: {msg.get('content', '')}")
    return "\n".join(formatted)


def get_scenario_config(scenario_mode: str) -> Dict[str, Any]:
    """获取场景配置，未知场景回退到初识聊天。"""
    scenario_key = getattr(scenario_mode, "value", scenario_mode)
    return SCENARIO_CONFIGS.get(str(scenario_key), SCENARIO_CONFIGS["first_chat"])


def get_scenario_label(scenario_mode: str) -> str:
    """获取场景中文名。"""
    return get_scenario_config(scenario_mode)["label"]


def build_event_schedule(
    scenario_mode: str,
    max_rounds: int
) -> Dict[int, Dict[str, Any]]:
    """根据场景和总轮次生成固定事件日程。"""
    config = get_scenario_config(scenario_mode)
    event_round_one = min(max_rounds - 2, max(3, round(max_rounds * 0.4)))
    event_round_two = min(max_rounds - 1, max(event_round_one + 2, round(max_rounds * 0.8)))

    if event_round_two <= event_round_one:
        event_round_two = min(max_rounds, event_round_one + 1)

    schedule = {}
    event_rounds = [event_round_one, event_round_two]

    for round_num, event in zip(event_rounds, config["events"]):
        schedule[round_num] = {
            "round": round_num,
            "title": event["title"],
            "cue": event["cue"],
            "goal": event["goal"]
        }

    return schedule


def get_dual_simulation_prompt(
    user_profile: Dict[str, Any],
    candidate_profile: Dict[str, Any],
    chat_history: List[Dict[str, str]],
    round_num: int,
    max_rounds: int,
    scenario_mode: str = "first_chat",
    event_card: Dict[str, Any] = None
) -> str:
    """
    生成双角色模拟对话提示词

    使用单次LLM调用同时模拟用户和候选人的对话
    """
    scenario = get_scenario_config(scenario_mode)
    event_section = "本轮没有额外事件卡，请自然推进关系。"
    if event_card:
        event_section = f"""本轮事件卡：{event_card.get('title', '事件推进')}
- 事件提示：{event_card.get('cue', '')}
- 事件目标：{event_card.get('goal', '')}
- 要求：本轮对话必须围绕这张事件卡自然展开，但不要写成任务说明口吻。"""

    return f"""你是一位专业的相亲对话模拟专家。你需要同时模拟对话的双方：真实用户和相亲候选人。

【用户画像】
{format_user_profile(user_profile)}

请根据用户的年龄、职业、兴趣爱好和自我描述，推断其说话风格和性格特点。

【候选人画像】
{format_candidate_profile(candidate_profile)}

候选人需要完全按照上述人设进行回应。

【当前玩法场景】
- 场景模式：{scenario['label']}
- 场景说明：{scenario['summary']}
- 本场景目标：{scenario['stage_goal']}

【对话上下文】
第 {round_num}/{max_rounds} 轮对话

之前的对话历史：
{format_chat_history(chat_history)}

【事件推进】
{event_section}

【对话阶段指南】
- 第1-3轮：破冰阶段——互相问候，建立初步印象，聊聊兴趣职业
- 第4-7轮：深入了解——分享经历、价值观、生活态度，开始有情感交流
- 第8-12轮：情感连接——谈论更深层次话题，试探对方想法，表达好感
- 第13轮以后：决定阶段——评估是否继续发展，可能提出见面或婉转拒绝

【任务】
请生成下一轮对话：
1. 用户会说什么？（基于用户画像和对话阶段，主动引导话题）
2. 候选人会怎么回应？（严格按候选人画像，展现真实个性）

【要求】
- **消息长度要有自然变化**——像真实聊天一样：
  * 简短回应："哈哈真的吗？""嗯嗯""对啊"（10-30字）
  * 中等表达：分享想法、回答问题（30-80字）
  * 详细阐述：讲故事、深入话题时可以长一点（80-150字）
  * 避免每轮消息长度都差不多，要自然波动
- 对话要自然流畅，像真实的相亲聊天场景
- 每轮都要推动对话进展，不要重复老话题
- 用户应主动提问、分享，候选人应真诚回应并适当反问
- 加入细节描述：具体的经历、感受、想法，让对话生动真实
- 保持人设一致性，但要让对话有发展变化
- 可以有追问、感叹、停顿语气，更贴近真实对话节奏
- 如果本轮有事件卡，必须体现在双方对话内容里，而不是忽略掉
- 当轮次进入后 25% 时，请自然体现双方是否愿意继续推进关系的信号
- **禁止括号描述**：不要使用括号内的动作或表情描述，如"（微笑）"、"（点头）"、"（害羞）"、"（思考片刻）"等

【对话技巧】
- 多用"我觉得""我之前""我特别喜欢"等表达个人感受
- 候选人可以适度展现幽默、温柔或独立等性格特质
- 遇到共同兴趣时，要深入展开讨论，不只是点到为止
- 中期可以聊一些稍微私人的话题（家庭观、未来规划、感情经历等）
- 情感逐渐升温：从礼貌→放松→信任→好感（或发现不合适）
- 用自然的对话节奏：有时快速回应，有时思考后再说

【输出格式】
严格按照以下JSON格式输出，不要添加任何额外文字：

```json
{{
    "user_message": "...",
    "candidate_reply": "..."
}}
```

请生成："""


def get_multi_candidate_generation_prompt(
    user_profile: Dict[str, Any],
    count: int = 10
) -> str:
    """生成多个候选人的提示词"""
    user_gender = user_profile.get('gender', 'male')
    target_gender = "女" if user_gender == 'male' else '男'
    user_age = user_profile.get('age', 25)
    user_interests = user_profile.get('interests', '').replace('、', '、').split('、')[:2]

    return f"""你是一位专业的相亲角色设计师。请为以下用户生成 {count} 个多样化的相亲候选人。

【用户资料】
{format_user_profile(user_profile)}

【候选人要求】
1. 性别：{target_gender}
2. 年龄范围：{user_age - 5} 到 {user_age + 5} 岁
3. 每个候选人必须与用户至少有1个共同兴趣
4. 确保多样性：
   - 职业分布：科技、创意、教育、金融、服务等不同领域
   - 性格分布：内向、外向、温和、活泼等不同类型
   - 年龄分布：覆盖整个年龄范围
   - 每个人有独特的故事和对话风格

【逻辑自洽性】
请运用你的常识判断，确保每个候选人的信息在逻辑上是自洽的：
- 年龄、职业、人生经历应该合理匹配
- 性格特点应该与职业和生活方式相符
- 背景故事应该能够解释这个人为什么成为现在的样子
- 避免出现明显的矛盾（比如年龄很小却是资深专家，或者学历与职业完全不匹配）
- 创造真实可信、立体生动的人物形象

【每个人设包含】
- name: 姓名（从常见中文名中选择）
- age: 年龄
- gender: 性别
- city: 所在城市（与用户同城或相近城市）
- occupation: 职业
- interests: 兴趣爱好（2-4个，用顿号分隔）
- personality: 性格特征（8-15字）
- backstory: 背景故事（30字以内，结合职业和兴趣，体现年龄和经历）
- chat_style: 对话风格（20字以内，符合性格特点）
- avatar: 头像emoji（女性用👩相关，男性用👨相关）

【输出格式】
严格按照以下JSON格式输出，不要添加任何额外文字：

```json
{{
    "candidates": [
        {{
            "name": "...",
            "age": ...,
            "gender": "...",
            "city": "...",
            "occupation": "...",
            "interests": "...",
            "personality": "...",
            "backstory": "...",
            "chat_style": "...",
            "avatar": "..."
        }}
    ]
}}
```

请生成："""


def get_comparative_recommendation_prompt(
    user_profile: Dict[str, Any],
    candidates: List[Any],
    scenario_mode: str = "first_chat",
    max_highlights: int = 3
) -> str:
    """
    生成比较评价和推荐提示词

    分析所有候选人的对话，推荐最佳匹配
    """
    # 构建候选人对话摘要
    conversations_summary = []

    for i, candidate in enumerate(candidates):
        bot_profile = candidate.bot_profile
        chat_history = candidate.chat_history

        # 统计对话质量指标
        total_rounds = len([m for m in chat_history if m.get('role') == 'user'])
        user_msg_count = len([m for m in chat_history if m.get('role') == 'user'])

        # 提取对话片段（前3轮、中间2轮、最后2轮）
        key_exchanges = []
        for j, msg in enumerate(chat_history):
            if j < 6 or (len(chat_history) - 4 <= j < len(chat_history)):
                role = "用户" if msg.get('role') == 'user' else "候选人"
                key_exchanges.append(f"  {role}: {msg.get('content', '')}")

        conversation_text = "\n".join(key_exchanges[-10:])  # 最后10条消息

        conversations_summary.append(f"""
【候选人 {i+1}】: {bot_profile.get('name', '未知')}
- 资料: {bot_profile.get('age', 25)}岁，{bot_profile.get('occupation', '未知')}
- 性格: {bot_profile.get('personality', '未知')}
- 对话轮次: {total_rounds}
- 关键对话片段:
{conversation_text}
""")

    all_conversations = "\n".join(conversations_summary)

    scenario = get_scenario_config(scenario_mode)

    return f"""你是一位经验丰富的婚恋顾问和情感分析专家。请分析用户与 {len(candidates)} 位候选人的相亲对话，找出最匹配的人选。

【用户资料】
{format_user_profile(user_profile)}

【玩法场景】
- 场景模式：{scenario['label']}
- 场景说明：{scenario['summary']}

【所有对话记录】
{all_conversations}

【分析维度】
1. **对话流畅度**: 双方是否聊得来，是否有话题共鸣
2. **价值观契合**: 生活方式、人生观是否一致
3. **情感连接**: 是否有情感共鸣，能否建立信任
4. **沟通方式**: 说话风格是否搭配
5. **成长潜力**: 关系是否有发展空间

【任务】
请从 {len(candidates)} 位候选人中选出最匹配的1位，并说明理由。

【结局标签可选值】
- 互有好感
- 建议继续接触
- 适合慢慢了解
- 更适合做朋友

【输出格式】
严格按照以下JSON格式输出：

```json
{{
    "best_match_candidate_id": "{candidates[0].candidate_id if candidates else ''}",
    "best_match_name": "候选人姓名",
    "compatibility_score": 85,
    "ending_label": "建议继续接触",
    "ending_reason": "一句话说明为什么适合继续推进关系",
    "reasoning": [
        "对话流畅自然，双方都有回应",
        "价值观高度契合，都重视XX",
        "情感连接明显，在XX话题上产生共鸣"
    ],
    "conversation_highlights": [
        {{"round": 5, "exchange": "用户:XXX | 候选人:YYY", "why": "为什么这个对话很重要"}},
        {{"round": 12, "exchange": "用户:AAA | 候选人:BBB", "why": "展现了价值观一致性"}}
    ],
    "potential_growth_areas": [
        "可以更多探索XX话题",
        "在XX方面可能需要更多沟通"
    ],
    "all_candidates_ranking": [
        {{"candidate_id": "...", "name": "...", "score": 85, "brief": "简短评价（15字内）", "ending_label": "互有好感"}},
        {{"candidate_id": "...", "name": "...", "score": 78, "brief": "简短评价", "ending_label": "适合慢慢了解"}}
    ]
}}
```

【评分标准】
- 90-100分: 非常匹配，强烈推荐
- 80-89分: 匹配度很高，推荐交往
- 70-79分: 有一定匹配度，可以尝试
- 60-69分: 匹配度一般，需要更多了解
- 60分以下: 匹配度较低，不建议继续

请分析并给出推荐："""


def get_opening_message_for_candidate(candidate_profile: Dict[str, Any]) -> str:
    """为候选人生成开场白"""
    name = candidate_profile.get('name', '我')
    interests = candidate_profile.get('interests', '旅行')
    occupation = candidate_profile.get('occupation', '未知')
    personality = candidate_profile.get('personality', '')

    # 根据性格和兴趣生成更个性化的开场白
    interest_list = interests.split('、') if interests else []
    main_interest = interest_list[0] if interest_list else '聊天'

    templates = [
        f"你好呀！我是{name}。看到你的资料，感觉我们挺投缘的~我平时喜欢{main_interest}，你呢？",
        f"嗨！我是{name}。很高兴认识你！我是个{occupation}，平时工作挺忙的，但周末喜欢{main_interest}放松一下。你周末一般都做什么呀？",
        f"你好~ 我是{name}。说实话，我对相亲有点紧张，哈哈。不过看到你，感觉应该能聊得来。你呢？平时喜欢做什么？",
        f"嗨，我是{name}。朋友都说我是{personality}的人，不知道你是不是也这么觉得？😄 我最近对{main_interest}特别感兴趣，你呢？",
        f"你好！我是{name}。我是个比较简单的人，喜欢{main_interest}，过着朝九晚五的生活。你呢？有没有什么特别想做的事情？"
    ]

    import random
    return random.choice(templates)
