"""
数据模型定义
使用Pydantic定义请求/响应的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"


class SessionStatus(str, Enum):
    """会话状态枚举"""
    PROFILE = "profile"      # 资料填写阶段
    CHATTING = "chatting"    # 对话进行中
    FINISHED = "finished"    # 对话已结束


class SimulationStatus(str, Enum):
    """模拟状态枚举"""
    GENERATING_CANDIDATES = "generating_candidates"  # 生成候选人中
    READY = "ready"                    # 候选人生成完成，准备开始模拟
    SIMULATING = "simulating"          # AI模拟进行中
    COMPLETED = "completed"            # 所有模拟完成
    RECOMMENDING = "recommending"      # 生成推荐中


class ScenarioMode(str, Enum):
    """玩法场景模式"""
    FIRST_CHAT = "first_chat"
    WEEKEND_PLAN = "weekend_plan"
    FUTURE_PROBE = "future_probe"


# ==================== 请求模型 ====================

class UserProfileSubmit(BaseModel):
    """用户资料提交模型"""
    age: int = Field(..., ge=18, le=80, description="年龄")
    gender: Gender = Field(..., description="性别")
    birth_year: int = Field(..., ge=1940, le=2010, description="出生年份")
    birth_month: int = Field(..., ge=1, le=12, description="出生月份")
    education: str = Field(..., min_length=1, description="学历")
    occupation: str = Field(..., min_length=1, description="职业")
    interests: str = Field(..., min_length=1, description="兴趣爱好")
    self_description: Optional[str] = Field(None, max_length=500, description="自我描述")
    ideal_type: Optional[str] = Field(None, max_length=500, description="理想型描述")


class ChatMessageRequest(BaseModel):
    """聊天消息请求模型"""
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., min_length=1, max_length=500, description="用户消息内容")


class StartChatRequest(BaseModel):
    """开始对话请求模型（获取开场白）"""
    session_id: str = Field(..., description="会话ID")


class EndChatRequest(BaseModel):
    """结束对话请求模型（提前结束并评估）"""
    session_id: str = Field(..., description="会话ID")


# ==================== 响应模型 ====================

class BotProfile(BaseModel):
    """机器人资料模型"""
    candidate_id: Optional[str] = Field(None, description="候选人ID")
    name: str = Field(..., description="机器人名字")
    age: int = Field(..., description="机器人年龄")
    gender: Gender = Field(..., description="机器人性别")
    occupation: str = Field(..., description="机器人职业")
    interests: str = Field(..., description="机器人兴趣爱好")
    personality: str = Field(..., description="机器人性格特征")
    city: Optional[str] = Field(None, description="所在城市")
    avatar: str = Field(..., description="机器人头像emoji")


class ProfileSubmitResponse(BaseModel):
    """资料提交响应模型"""
    success: bool = Field(..., description="是否成功")
    session_id: Optional[str] = Field(None, description="会话ID")
    bot_profile: Optional[BotProfile] = Field(None, description="机器人资料")
    message: str = Field(..., description="响应消息")


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user/assistant")
    content: str = Field(..., description="消息内容")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool = Field(..., description="是否成功")
    bot_reply: Optional[str] = Field(None, description="机器人回复")
    current_round: Optional[int] = Field(None, description="当前轮次")
    total_rounds: Optional[int] = Field(None, description="总轮次")
    is_finished: bool = Field(False, description="对话是否结束")
    history: Optional[List[ChatMessage]] = Field(None, description="对话历史")
    message: Optional[str] = Field(None, description="响应消息")


class EvaluationResult(BaseModel):
    """评价结果模型"""
    attraction_score: int = Field(..., ge=0, le=100, description="吸引力度评分")
    strengths: List[str] = Field(..., description="优点列表")
    suggestions: List[str] = Field(..., description="改进建议列表")
    summary: str = Field(..., description="总体评价")


class EvaluationResponse(BaseModel):
    """评价响应模型"""
    success: bool = Field(..., description="是否成功")
    evaluation: Optional[EvaluationResult] = Field(None, description="评价结果")
    message: Optional[str] = Field(None, description="响应消息")


class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str = Field(..., description="会话ID")
    status: SessionStatus = Field(..., description="会话状态")
    current_round: int = Field(..., description="当前轮次")
    total_rounds: int = Field(..., description="总轮次")
    bot_profile: Optional[BotProfile] = Field(None, description="机器人资料")
    history: Optional[List[ChatMessage]] = Field(None, description="对话历史")


class SessionResponse(BaseModel):
    """会话查询响应模型"""
    success: bool = Field(..., description="是否成功")
    session: Optional[SessionInfo] = Field(None, description="会话信息")
    message: Optional[str] = Field(None, description="响应消息")


# ==================== 多候选人模式模型 ====================

class MultiCandidateProfileSubmit(BaseModel):
    """多候选人模式资料提交模型"""
    age: int = Field(..., ge=18, le=80, description="年龄")
    gender: Gender = Field(..., description="性别")
    birth_year: int = Field(..., ge=1940, le=2010, description="出生年份")
    birth_month: int = Field(..., ge=1, le=12, description="出生月份")
    education: str = Field(..., min_length=1, description="学历")
    occupation: str = Field(..., min_length=1, description="职业")
    interests: str = Field(..., min_length=1, description="兴趣爱好")
    city: str = Field(..., min_length=1, description="所在城市")
    self_description: Optional[str] = Field(None, max_length=500, description="自我描述")
    ideal_type: Optional[str] = Field(None, max_length=500, description="理想型描述")
    candidate_count: int = Field(10, ge=1, le=20, description="候选人数")
    max_rounds: int = Field(20, ge=10, le=50, description="最大对话轮数")
    enhanced_mode: bool = Field(True, description="是否开启玩法增强")
    scenario_mode: ScenarioMode = Field(ScenarioMode.FIRST_CHAT, description="场景模式")


class MultiCandidateProfileResponse(BaseModel):
    """多候选人资料提交响应模型"""
    success: bool = Field(..., description="是否成功")
    session_id: Optional[str] = Field(None, description="会话ID")
    candidates: List[BotProfile] = Field(..., description="候选人列表")
    candidate_count: int = Field(..., description="候选人数")
    max_rounds: int = Field(..., description="最大对话轮数")
    enhanced_mode: bool = Field(..., description="是否开启玩法增强")
    scenario_mode: ScenarioMode = Field(..., description="场景模式")
    message: str = Field(..., description="响应消息")


class StartSimulationRequest(BaseModel):
    """开始模拟请求模型"""
    session_id: str = Field(..., description="会话ID")


class SimulationStatusResponse(BaseModel):
    """模拟状态响应模型"""
    success: bool = Field(..., description="是否成功")
    status: SimulationStatus = Field(..., description="模拟状态")
    current_round: int = Field(..., description="当前模拟轮次")
    max_rounds: int = Field(..., description="总轮次")
    candidates_status: List[Dict[str, Any]] = Field(..., description="各候选人状态")
    message: Optional[str] = Field(None, description="响应消息")


class ConversationHighlight(BaseModel):
    """对话高光时刻模型"""
    round: int = Field(..., description="轮次")
    exchange: str = Field(..., description="对话内容")
    why: str = Field(..., description="为什么重要")


class CandidateRanking(BaseModel):
    """候选人排名模型"""
    candidate_id: str = Field(..., description="候选人ID")
    name: str = Field(..., description="姓名")
    score: int = Field(..., ge=0, le=100, description="匹配分数")
    brief: str = Field(..., description="简要评价")
    ending_label: str = Field(..., description="关系结局标签")


class RecommendationResult(BaseModel):
    """推荐结果模型"""
    best_match_candidate_id: str = Field(..., description="最佳匹配候选人ID")
    best_match_name: str = Field(..., description="最佳匹配姓名")
    compatibility_score: int = Field(..., ge=0, le=100, description="兼容性分数")
    ending_label: str = Field(..., description="最佳匹配关系结局")
    ending_reason: str = Field(..., description="最佳匹配结局理由")
    reasoning: List[str] = Field(..., description="推荐理由")
    conversation_highlights: List[ConversationHighlight] = Field(..., description="对话高光时刻")
    potential_growth_areas: List[str] = Field(..., description="潜在成长空间")
    all_candidates_ranking: List[CandidateRanking] = Field(..., description="所有候选人排名")


class RecommendationResponse(BaseModel):
    """推荐响应模型"""
    success: bool = Field(..., description="是否成功")
    recommendation: Optional[RecommendationResult] = Field(None, description="推荐结果")
    message: Optional[str] = Field(None, description="响应消息")


# ==================== 内部数据模型 ====================

class CandidateData:
    """单个候选人数据类"""
    def __init__(self, candidate_id: str, bot_profile: Dict[str, Any]):
        self.candidate_id = candidate_id
        self.bot_profile = bot_profile
        self.chat_history: List[Dict[str, str]] = []
        self.current_round = 0
        self.simulation_score: Optional[float] = None
        self.simulation_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "candidate_id": self.candidate_id,
            "bot_profile": self.bot_profile,
            "chat_history": self.chat_history,
            "current_round": self.current_round,
            "simulation_score": self.simulation_score,
            "simulation_notes": self.simulation_notes
        }


class SessionData:
    """会话数据类（存储在内存中）"""
    def __init__(
        self,
        session_id: str,
        user_profile: Dict[str, Any],
        bot_profile: Dict[str, Any]
    ):
        self.session_id = session_id
        self.user_profile = user_profile
        self.bot_profile = bot_profile
        self.chat_history: List[Dict[str, str]] = []
        self.current_round = 0
        self.total_rounds = 10
        self.status = SessionStatus.CHATTING
        self.created_at = datetime.now()
        self.evaluation: Optional[EvaluationResult] = None
        self._expire_cache = None  # 过期状态缓存
        self._expire_cache_time = None  # 缓存时间

    def is_expired(self, expire_minutes: int) -> bool:
        """
        检查会话是否过期（带缓存）

        Args:
            expire_minutes: 过期分钟数

        Returns:
            是否过期
        """
        now = datetime.now()

        # 如果缓存存在且未过期（1分钟内），直接使用缓存
        if (self._expire_cache is not None and
            self._expire_cache_time is not None and
            (now - self._expire_cache_time).total_seconds() < 60):
            return self._expire_cache

        # 重新计算并缓存
        expire_time = timedelta(minutes=expire_minutes)
        is_expired = now - self.created_at > expire_time

        self._expire_cache = is_expired
        self._expire_cache_time = now

        return is_expired

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_profile": self.user_profile,
            "bot_profile": self.bot_profile,
            "chat_history": self.chat_history,
            "current_round": self.current_round,
            "total_rounds": self.total_rounds,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "evaluation": self.evaluation
        }


class MultiCandidateSessionData:
    """多候选人会话数据类"""
    def __init__(
        self,
        session_id: str,
        user_profile: Dict[str, Any],
        candidates: List[CandidateData],
        max_rounds: int = 20,
        enhanced_mode: bool = True,
        scenario_mode: ScenarioMode = ScenarioMode.FIRST_CHAT
    ):
        self.session_id = session_id
        self.user_profile = user_profile
        self.candidates = candidates  # List[CandidateData]
        self.max_rounds = max_rounds
        self.enhanced_mode = enhanced_mode
        self.scenario_mode = scenario_mode
        self.event_schedule: Dict[int, Dict[str, Any]] = {}
        self.current_simulation_round = 0
        self.status = SimulationStatus.GENERATING_CANDIDATES
        self.created_at = datetime.now()
        self.final_recommendation: Optional[Dict[str, Any]] = None
        self.best_match_candidate_id: Optional[str] = None
        self._expire_cache = None  # 过期状态缓存
        self._expire_cache_time = None  # 缓存时间

    def is_expired(self, expire_minutes: int) -> bool:
        """
        检查会话是否过期（带缓存）

        Args:
            expire_minutes: 过期分钟数

        Returns:
            是否过期
        """
        now = datetime.now()

        # 如果缓存存在且未过期（1分钟内），直接使用缓存
        if (self._expire_cache is not None and
            self._expire_cache_time is not None and
            (now - self._expire_cache_time).total_seconds() < 60):
            return self._expire_cache

        # 重新计算并缓存
        expire_time = timedelta(minutes=expire_minutes)
        is_expired = now - self.created_at > expire_time

        self._expire_cache = is_expired
        self._expire_cache_time = now

        return is_expired

    def get_candidate(self, candidate_id: str) -> Optional[CandidateData]:
        """根据ID获取候选人"""
        for candidate in self.candidates:
            if candidate.candidate_id == candidate_id:
                return candidate
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "user_profile": self.user_profile,
            "candidates": [c.to_dict() for c in self.candidates],
            "max_rounds": self.max_rounds,
            "enhanced_mode": self.enhanced_mode,
            "scenario_mode": self.scenario_mode,
            "event_schedule": self.event_schedule,
            "current_simulation_round": self.current_simulation_round,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "final_recommendation": self.final_recommendation,
            "best_match_candidate_id": self.best_match_candidate_id
        }
