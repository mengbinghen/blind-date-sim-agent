"""
AI Agent服务
负责与大模型交互，生成机器人人设、对话回复和评价
"""
import json
import re
import httpx
from typing import Dict, Any, Optional, List
from app.config import Config
from app.utils.normalization import normalize_gender, normalize_gender_in_profile
from app.prompts.persona_prompts import (
    get_persona_generation_prompt,
    get_chat_system_prompt,
    get_opening_message
)
from app.prompts.evaluation_prompts import get_evaluation_prompt
from app.prompts.simulation_prompts import (
    get_dual_simulation_prompt,
    get_multi_candidate_generation_prompt,
    get_comparative_recommendation_prompt,
    get_opening_message_for_candidate,
    format_chat_history,
    build_event_schedule
)


class AgentService:
    """AI Agent服务类"""

    VALID_ENDING_LABELS = {
        "互有好感",
        "建议继续接触",
        "适合慢慢了解",
        "更适合做朋友"
    }

    def __init__(self):
        """初始化Agent服务"""
        self.config = Config()
        self.client = None
        self._client_pool = {}  # 客户端池，按timeout值索引

    def _get_client(self, timeout: int = None) -> httpx.AsyncClient:
        """
        获取HTTP客户端（支持连接池复用）

        Args:
            timeout: 超时时间（秒），为None时使用默认值

        Returns:
            httpx异步客户端
        """
        # 使用默认超时时间
        if timeout is None:
            timeout = self.config.DEEPSEEK_TIMEOUT

        # 从池中获取或创建客户端
        if timeout not in self._client_pool:
            self._client_pool[timeout] = httpx.AsyncClient(
                base_url=self.config.DEEPSEEK_BASE_URL,
                timeout=timeout,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )

        return self._client_pool[timeout]

    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        model: str = None,
        timeout: int = None,
        max_tokens: int = None,
        scene: str = "default"
    ) -> str:
        """
        调用大模型API

        Args:
            messages: 消息列表，格式为 [{"role": "system/user", "content": "..."}]
            temperature: 温度参数，控制随机性
            model: 指定使用的模型，默认使用 DEEPSEEK_MODEL
            timeout: 超时时间（秒），为None时使用默认值
            max_tokens: 最大token数，显式指定时优先使用
            scene: 场景类型，用于自动选择合适的max_tokens

        Returns:
            模型返回的文本内容

        Raises:
            Exception: API调用失败时抛出异常
        """
        client = self._get_client(timeout)

        headers = {
            "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        # 使用指定模型或默认模型
        model_name = model or self.config.DEEPSEEK_MODEL

        # 确定max_tokens：显式指定 > 场景配置 > 默认值
        if max_tokens is None:
            max_tokens = self.config.MAX_TOKENS_MAP.get(scene, 2000)

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = await client.post(
                "/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            raise Exception(f"DeepSeek API调用失败: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise Exception("DeepSeek API调用超时")
        except Exception as e:
            raise Exception(f"DeepSeek API调用异常: {str(e)}")

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取JSON内容

        Args:
            text: 可能包含JSON的文本

        Returns:
            解析后的JSON字典，失败返回None
        """
        # 尝试直接解析
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # 尝试提取JSON代码块
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        match = re.search(json_pattern, text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 尝试提取花括号内容
        brace_pattern = r'\{[\s\S]*\}'
        match = re.search(brace_pattern, text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    async def generate_bot_persona(
        self,
        user_profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        根据用户资料生成机器人人设

        Args:
            user_profile: 用户资料字典

        Returns:
            机器人人设字典，失败返回None
        """
        import random

        # 从配置池中随机选择基础信息，保证多样性
        user_gender = user_profile.get("gender", "male")
        bot_gender = "female" if user_gender == "male" else "male"
        user_age = user_profile.get("age", 25)

        # 随机选择名字
        if bot_gender == "female":
            name = random.choice(self.config.FEMALE_NAMES)
        else:
            name = random.choice(self.config.MALE_NAMES)

        # 随机选择职业（从预定义池中）
        occupation = random.choice(self.config.OCCUPATIONS)

        # 随机选择性格
        personality = random.choice(self.config.PERSONALITIES)

        # 随机选择2-3个兴趣爱好
        selected_interests = random.sample(self.config.INTERESTS, k=random.randint(2, 3))

        # 获取用户兴趣，确保至少有一个共同兴趣
        user_interests = user_profile.get("interests", "").split("、")
        if user_interests and user_interests[0]:
            # 将用户的第一个兴趣加入，去重
            if user_interests[0] not in selected_interests:
                selected_interests.insert(0, user_interests[0])

        interests_str = "、".join(selected_interests[:4])  # 最多4个

        # 使用AI生成个性化的背景故事和对话风格
        ai_prompt = f"""你是一位专业的相亲角色设计师。请根据以下基础信息，生成一个吸引人的角色补充信息。

【基础信息】
- 姓名：{name}
- 性别：{bot_gender}
- 年龄：{user_age + random.randint(-2, 3)}岁
- 职业：{occupation}
- 兴趣爱好：{interests_str}
- 性格特征：{personality}

【用户信息】
- 职业：{user_profile.get('occupation', '未知')}
- 兴趣爱好：{user_profile.get('interests', '未知')}
- 自我描述：{user_profile.get('self_description', '未填写')}

【生成要求】
请生成以下内容，让角色更生动有趣：
1. **背景故事**（30字以内）：结合职业和兴趣，创造有趣的个人背景
2. **对话风格**（20字以内）：符合性格特点的自然交流风格
3. **回复示例**（15字以内）：一个符合人设的开场白示例

【输出格式】
严格按照以下JSON格式输出，不要添加任何额外文字：

```json
{{
    "backstory": "背景故事",
    "chat_style": "对话风格",
    "opening_example": "开场白示例"
}}
```

请生成："""

        messages = [
            {"role": "system", "content": "你是一位专业的相亲角色设计师，擅长创建真实、有吸引力的角色人设。请严格按照要求的JSON格式输出。"},
            {"role": "user", "content": ai_prompt}
        ]

        try:
            response = await self._call_llm(messages, temperature=0.9, scene="persona_generation")
            ai_generated = self._extract_json(response)

            # 构建完整人设
            bot_age = user_age + random.randint(-2, 3)
            bot_age = max(22, min(35, bot_age))  # 限制在22-35岁

            persona = {
                "name": name,
                "age": bot_age,
                "gender": bot_gender,
                "occupation": occupation,
                "interests": interests_str,
                "personality": personality,
                "avatar": "👩" if bot_gender == "female" else "👨"
            }

            # 如果AI生成成功，使用AI生成的内容
            if ai_generated:
                persona["backstory"] = ai_generated.get("backstory", "热爱生活，期待遇到对的人")
                persona["chat_style"] = ai_generated.get("chat_style", "自然亲切，真诚友善")
            else:
                # AI生成失败，使用默认值
                persona["backstory"] = "热爱生活，期待遇到对的人"
                persona["chat_style"] = "自然亲切，真诚友善"

            return persona

        except Exception as e:
            print(f"生成人设失败: {str(e)}")
            return self._get_default_persona(user_profile)

    def _get_default_persona(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取默认机器人人设（当AI生成失败时使用）

        Args:
            user_profile: 用户资料

        Returns:
            默认人设字典（性别已标准化为英文）
        """
        import random

        # 确保用户性别也是标准化的
        user_gender = normalize_gender(user_profile.get("gender", "male"))
        bot_gender = "female" if user_gender == "male" else "male"
        user_age = user_profile.get("age", 25)
        user_interests = user_profile.get("interests", "").split("、")

        # 随机选择名字
        if bot_gender == "female":
            name = random.choice(self.config.FEMALE_NAMES)
        else:
            name = random.choice(self.config.MALE_NAMES)

        # 随机选择职业、性格和兴趣
        random_interest = random.choice(self.config.INTERESTS)

        # 构建兴趣字符串
        if user_interests and user_interests[0]:
            interests = f"{user_interests[0]}、{random_interest}"
        else:
            interests = random_interest

        # 构建人设（性别已经是英文）
        return {
            "name": name,
            "age": max(22, min(35, user_age + random.randint(-2, 3))),
            "gender": bot_gender,
            "occupation": random.choice(self.config.OCCUPATIONS),
            "interests": interests,
            "personality": random.choice(self.config.PERSONALITIES),
            "city": user_profile.get("city", "北京"),
            "backstory": "热爱生活，期待遇到对的人",
            "chat_style": "自然亲切，真诚友善",
            "avatar": "👩" if bot_gender == "female" else "👨"
        }

    async def generate_chat_response(
        self,
        user_message: str,
        bot_profile: Dict[str, Any],
        user_profile: Dict[str, Any],
        chat_history: List[Dict[str, str]]
    ) -> str:
        """
        生成机器人回复

        Args:
            user_message: 用户消息
            bot_profile: 机器人人设
            user_profile: 用户资料
            chat_history: 对话历史

        Returns:
            机器人回复内容
        """
        # 构建系统提示词
        system_prompt = get_chat_system_prompt(bot_profile, user_profile)

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 添加对话历史（最近5轮）
        recent_history = chat_history[-10:] if chat_history else []
        for msg in recent_history:
            role = "assistant" if msg.get("role") == "assistant" else "user"
            messages.append({
                "role": role,
                "content": msg.get("content", "")
            })

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            response = await self._call_llm(messages, temperature=0.8, scene="chat_response")
            # 清理可能的JSON代码块标记
            response = re.sub(r'```\w*\n?', '', response).strip()
            return response

        except Exception as e:
            print(f"生成回复失败: {str(e)}")
            # 返回默认回复
            return "抱歉，我刚才有点走神了，能再说一遍吗？ 😊"

    def get_opening_message(self, bot_profile: Dict[str, Any]) -> str:
        """
        获取机器人开场白

        Args:
            bot_profile: 机器人人设

        Returns:
            开场白消息
        """
        return get_opening_message(bot_profile)

    async def generate_evaluation(
        self,
        chat_history: List[Dict[str, str]],
        user_profile: Dict[str, Any],
        bot_profile: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        生成对话评价（使用推理模型）

        Args:
            chat_history: 对话历史
            user_profile: 用户资料
            bot_profile: 机器人人设

        Returns:
            评价结果字典，失败返回None
        """
        prompt = get_evaluation_prompt(chat_history, user_profile, bot_profile)

        messages = [
            {"role": "system", "content": "你是一位经验丰富的相亲顾问和情感沟通专家。请严格按照要求的JSON格式输出评价结果。"},
            {"role": "user", "content": prompt}
        ]

        try:
            # 使用推理模型生成评价，使用更长的超时时间
            response = await self._call_llm(
                messages,
                temperature=0.7,
                model=self.config.DEEPSEEK_REASONER_MODEL,
                timeout=self.config.EVALUATION_TIMEOUT,
                scene="evaluation"
            )
            evaluation = self._extract_json(response)

            if evaluation:
                # 确保分数在有效范围内
                score = evaluation.get("attraction_score", 70)
                evaluation["attraction_score"] = max(0, min(100, int(score)))
                return evaluation
            else:
                return self._get_default_evaluation()

        except Exception as e:
            print(f"生成评价失败: {str(e)}")
            return self._get_default_evaluation()

    async def generate_evaluation_stream(
        self,
        chat_history: List[Dict[str, str]],
        user_profile: Dict[str, Any],
        bot_profile: Dict[str, Any]
    ):
        """
        流式生成对话评价（使用推理模型）

        Args:
            chat_history: 对话历史
            user_profile: 用户资料
            bot_profile: 机器人人设

        Yields:
            元组 (type, data): type为 'progress', 'content', 'complete', 'error'
                - progress: 进度更新，data为进度消息
                - content: 内容块，data为文本片段
                - complete: 完成，data为完整评价字典
                - error: 错误，data为错误消息
        """
        from typing import AsyncGenerator, Tuple

        prompt = get_evaluation_prompt(chat_history, user_profile, bot_profile)

        messages = [
            {"role": "system", "content": "你是一位经验丰富的相亲顾问和情感沟通专家。请严格按照要求的JSON格式输出评价结果。"},
            {"role": "user", "content": prompt}
        ]

        client = self._get_client(timeout=self.config.EVALUATION_TIMEOUT)

        headers = {
            "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        # 使用场景配置的max_tokens
        max_tokens = self.config.MAX_TOKENS_MAP.get("evaluation", 2500)

        payload = {
            "model": self.config.DEEPSEEK_REASONER_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": max_tokens,
            "stream": True  # 启用流式输出
        }

        try:
            # 发送进度更新
            yield ("progress", "正在连接AI分析服务...")

            response = await client.post(
                "/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.config.EVALUATION_TIMEOUT
            )
            response.raise_for_status()

            yield ("progress", "AI正在分析对话内容...")

            # 读取流式响应
            full_content = ""
            async for line in response.aiter_lines():
                if not line.strip():
                    continue

                # SSE格式: data: {...}
                if line.startswith("data: "):
                    data_str = line[6:]  # 移除 "data: " 前缀

                    # 检查是否为结束标记
                    if data_str.strip() == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")

                        if content:
                            full_content += content
                            yield ("content", content)

                    except json.JSONDecodeError:
                        continue

            yield ("progress", "正在解析评价结果...")

            # 解析完整的JSON响应
            evaluation = self._extract_json(full_content)

            if evaluation:
                # 确保分数在有效范围内
                score = evaluation.get("attraction_score", 70)
                evaluation["attraction_score"] = max(0, min(100, int(score)))
                yield ("complete", evaluation)
            else:
                # JSON解析失败，使用默认评价
                yield ("complete", self._get_default_evaluation())

        except Exception as e:
            print(f"流式生成评价失败: {str(e)}")
            yield ("error", f"生成评价失败: {str(e)}")

    def _get_default_evaluation(self) -> Dict[str, Any]:
        """
        获取默认评价（当AI生成失败时使用）

        Returns:
            默认评价字典
        """
        return {
            "attraction_score": 65,
            "strengths": [
                "完成了完整对话流程",
                "展现了基本的交流意愿",
                "保持了基本的礼貌"
            ],
            "suggestions": [
                "可以更主动地了解对方的兴趣爱好",
                "尝试用提问来延续话题",
                "适当分享自己的经历和感受",
                "注意倾听并给予回应"
            ],
            "summary": "你完成了对话，但还有提升空间。继续练习，相信会越来越好的！"
        }

    async def generate_multiple_candidates(
        self,
        user_profile: Dict[str, Any],
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        生成多个候选人

        Args:
            user_profile: 用户资料
            count: 候选人数量

        Returns:
            候选人列表
        """
        import uuid
        import random

        try:
            # 使用AI批量生成候选人
            prompt = get_multi_candidate_generation_prompt(user_profile, count)

            messages = [
                {"role": "system", "content": "你是一位专业的相亲角色设计师，擅长创建真实、有吸引力的角色人设。请严格按照要求的JSON格式输出。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_llm(messages, temperature=0.9, scene="multi_candidate")
            result = self._extract_json(response)

            candidates = []

            if result and "candidates" in result:
                print(f"AI成功生成 {len(result['candidates'])} 个候选人")
                # AI生成的候选人
                for i, persona in enumerate(result["candidates"]):
                    print(f"候选人 {i+1} 字段: {list(persona.keys())}")
                    # 使用统一函数标准化性别
                    persona = normalize_gender_in_profile(persona)

                    candidates.append({
                        **persona,
                        "candidate_id": str(uuid.uuid4())
                    })
            else:
                # AI生成失败，使用随机生成
                print(f"AI返回结果无效: {result}")
                raise Exception("AI生成候选人失败，使用备用方案")

            # 确保返回指定数量的候选人
            while len(candidates) < count:
                fallback_persona = self._get_default_persona(user_profile)
                fallback_persona["candidate_id"] = str(uuid.uuid4())
                candidates.append(fallback_persona)

            return candidates[:count]

        except Exception as e:
            print(f"批量生成候选人失败: {str(e)}，使用随机生成")
            # 回退到随机生成
            candidates = []
            for _ in range(count):
                persona = self._get_default_persona(user_profile)
                persona["candidate_id"] = str(uuid.uuid4())
                candidates.append(persona)
            return candidates

    async def simulate_conversation_round(
        self,
        user_profile: Dict[str, Any],
        candidate_profile: Dict[str, Any],
        chat_history: List[Dict[str, str]],
        round_num: int,
        max_rounds: int,
        scenario_mode: str = "first_chat",
        event_card: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        模拟一轮对话（AI同时模拟用户和候选人）

        Args:
            user_profile: 用户资料
            candidate_profile: 候选人资料
            chat_history: 对话历史
            round_num: 当前轮次
            max_rounds: 最大轮次

        Returns:
            包含user_message和candidate_reply的字典，失败返回None
        """
        try:
            prompt = get_dual_simulation_prompt(
                user_profile,
                candidate_profile,
                chat_history,
                round_num,
                max_rounds,
                scenario_mode=scenario_mode,
                event_card=event_card
            )

            messages = [
                {"role": "system", "content": "你是一位专业的相亲对话模拟专家。请严格按照要求的JSON格式输出。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_llm(
                messages,
                temperature=self.config.SIMULATION_TEMPERATURE,
                scene="simulation_round"
            )

            result = self._extract_json(response)

            if result and "user_message" in result and "candidate_reply" in result:
                return {
                    "user_message": result["user_message"],
                    "candidate_reply": result["candidate_reply"]
                }
            else:
                # JSON解析失败，尝试备用方案
                return self._get_fallback_conversation_round(round_num)

        except Exception as e:
            print(f"模拟对话轮次失败: {str(e)}")
            return self._get_fallback_conversation_round(round_num)

    def _get_fallback_conversation_round(self, round_num: int) -> Dict[str, Any]:
        """获取备用对话轮次（当AI模拟失败时）"""
        fallback_rounds = [
            {
                "user_message": "你好呀！很高兴认识你，我对你还挺好奇的呢~",
                "candidate_reply": "哈哈，我也是！感觉应该能聊得来。你的资料写得挺真诚的，让我很想多了解你一点。"
            },
            {
                "user_message": "谢谢夸奖！我平时喜欢旅行和摄影，周末经常出去拍照放松。你呢，周末一般怎么过？",
                "candidate_reply": "哇，摄影师啊，那一定去过很多地方吧！我周末喜欢瑜伽和看书，偶尔也会出去走走。下次可以分享你的照片给我看看呀~"
            },
            {
                "user_message": "当然可以！我拍过不少风景照，还有城市街拍。你平时喜欢看什么类型的书？",
                "candidate_reply": "我比较喜欢看小说和一些心理学相关的书。小说可以让我放松，心理学书能帮我更好地理解人。你呢，除了摄影还有什么特别的爱好吗？"
            }
        ]

        index = min(round_num - 1, len(fallback_rounds) - 1)
        return fallback_rounds[index]

    def get_event_schedule(
        self,
        scenario_mode: str,
        max_rounds: int
    ) -> Dict[int, Dict[str, Any]]:
        """生成固定事件日程。"""
        return build_event_schedule(scenario_mode, max_rounds)

    def _normalize_ending_label(self, label: Optional[str]) -> str:
        """规范化关系结局标签。"""
        if label in self.VALID_ENDING_LABELS:
            return label
        return "适合慢慢了解"

    def _normalize_recommendation_result(
        self,
        result: Dict[str, Any],
        candidates: List[Any]
    ) -> Dict[str, Any]:
        """校正推荐结果中的候选人身份，避免模型输出与真实候选人错位。"""
        if not candidates:
            return result

        candidate_by_id = {candidate.candidate_id: candidate for candidate in candidates}
        candidate_by_name = {}
        for candidate in candidates:
            name = candidate.bot_profile.get("name", "")
            if name:
                candidate_by_name.setdefault(name, []).append(candidate)

        def resolve_candidate(candidate_id: Optional[str], name: Optional[str]):
            if candidate_id and candidate_id in candidate_by_id:
                return candidate_by_id[candidate_id]
            if name and name in candidate_by_name and len(candidate_by_name[name]) == 1:
                return candidate_by_name[name][0]
            return None

        normalized_rankings = []
        seen_candidate_ids = set()

        for ranking in result.get("all_candidates_ranking", []):
            candidate = resolve_candidate(
                ranking.get("candidate_id"),
                ranking.get("name")
            )
            if not candidate or candidate.candidate_id in seen_candidate_ids:
                continue

            normalized_rankings.append({
                **ranking,
                "candidate_id": candidate.candidate_id,
                "name": candidate.bot_profile.get("name", "未知"),
                "score": max(0, min(100, int(ranking.get("score", 70)))),
                "brief": ranking.get("brief", "待补充评价"),
                "ending_label": self._normalize_ending_label(ranking.get("ending_label"))
            })
            seen_candidate_ids.add(candidate.candidate_id)

        for candidate in candidates:
            if candidate.candidate_id in seen_candidate_ids:
                continue

            normalized_rankings.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.bot_profile.get("name", "未知"),
                "score": 60,
                "brief": "待补充评价",
                "ending_label": "适合慢慢了解"
            })

        best_candidate = resolve_candidate(
            result.get("best_match_candidate_id"),
            result.get("best_match_name")
        )
        if best_candidate is None and normalized_rankings:
            best_candidate = candidate_by_id[normalized_rankings[0]["candidate_id"]]
        if best_candidate is None:
            best_candidate = max(candidates, key=lambda candidate: len(candidate.chat_history))

        result["best_match_candidate_id"] = best_candidate.candidate_id
        result["best_match_name"] = best_candidate.bot_profile.get("name", "未知")
        result["ending_label"] = self._normalize_ending_label(result.get("ending_label"))
        result["ending_reason"] = result.get("ending_reason", "双方关系有继续了解的空间。")

        best_candidate_id = result["best_match_candidate_id"]
        normalized_rankings.sort(
            key=lambda ranking: ranking["candidate_id"] != best_candidate_id
        )
        result["all_candidates_ranking"] = normalized_rankings

        return result

    async def generate_comparative_recommendation(
        self,
        user_profile: Dict[str, Any],
        candidates: List[Any],
        scenario_mode: str = "first_chat"
    ) -> Optional[Dict[str, Any]]:
        """
        生成比较推荐（分析所有候选人对话，推荐最佳匹配）

        Args:
            user_profile: 用户资料
            candidates: 候选人列表（CandidateData对象）

        Returns:
            推荐结果字典，失败返回None
        """
        try:
            prompt = get_comparative_recommendation_prompt(
                user_profile,
                candidates,
                scenario_mode=scenario_mode
            )

            messages = [
                {"role": "system", "content": "你是一位经验丰富的婚恋顾问和情感分析专家。请严格按照要求的JSON格式输出推荐结果。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_llm(
                messages,
                temperature=0.7,
                model=self.config.DEEPSEEK_REASONER_MODEL,
                timeout=self.config.EVALUATION_TIMEOUT,
                scene="comparative_recommendation"
            )

            result = self._extract_json(response)

            if result:
                # 确保分数在有效范围内
                if "compatibility_score" in result:
                    score = result["compatibility_score"]
                    result["compatibility_score"] = max(0, min(100, int(score)))
                return self._normalize_recommendation_result(result, candidates)
            else:
                return self._get_default_recommendation(candidates)

        except Exception as e:
            print(f"生成比较推荐失败: {str(e)}")
            return self._get_default_recommendation(candidates)

    def _get_default_recommendation(self, candidates: List[Any]) -> Dict[str, Any]:
        """获取默认推荐（当AI分析失败时）"""
        if not candidates:
            return {}

        # 选择对话轮次最多的作为最佳匹配
        best_candidate = max(candidates, key=lambda c: len(c.chat_history))

        rankings = []
        for i, c in enumerate(candidates):
            score = 70 - i * 3  # 简单的分数递减
            rankings.append({
                "candidate_id": c.candidate_id,
                "name": c.bot_profile.get("name", "未知"),
                "score": max(50, score),
                "brief": f"对话{len(c.chat_history)}轮，{'较流畅' if len(c.chat_history) > 5 else '一般'}",
                "ending_label": "适合慢慢了解" if i > 0 else "建议继续接触"
            })

        return {
            "best_match_candidate_id": best_candidate.candidate_id,
            "best_match_name": best_candidate.bot_profile.get("name", "未知"),
            "compatibility_score": 75,
            "ending_label": "建议继续接触",
            "ending_reason": "双方整体交流顺畅，值得继续了解。",
            "reasoning": [
                "双方对话较为顺畅",
                "有一定共同话题",
                "沟通风格较为匹配"
            ],
            "conversation_highlights": [],
            "potential_growth_areas": [
                "可以更深入地了解彼此的兴趣爱好",
                "尝试探索更多共同话题"
            ],
            "all_candidates_ranking": rankings
        }

    async def close(self):
        """关闭所有HTTP客户端"""
        # 关闭默认客户端（向后兼容）
        if self.client:
            await self.client.aclose()
            self.client = None

        # 关闭池中的所有客户端
        for timeout, client in self._client_pool.items():
            await client.aclose()
        self._client_pool.clear()


# 全局Agent服务实例
agent_service = AgentService()
