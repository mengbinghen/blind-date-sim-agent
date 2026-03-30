"""
会话管理服务
负责会话的创建、存储、查询和清理
"""
import uuid
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from app.models import (
    SessionData,
    SessionStatus,
    CandidateData,
    MultiCandidateSessionData,
    SimulationStatus,
    ScenarioMode
)
from app.config import Config


class SessionService:
    """会话管理服务类"""

    def __init__(self):
        """初始化会话服务"""
        self.sessions: Dict[str, Any] = {}
        self.config = Config()

    def create_session(
        self,
        user_profile: Dict[str, Any],
        bot_profile: Dict[str, Any]
    ) -> SessionData:
        """
        创建新会话

        Args:
            user_profile: 用户资料
            bot_profile: 机器人人设

        Returns:
            创建的会话数据对象
        """
        # 检查会话数量限制
        if len(self.sessions) >= self.config.MAX_CONCURRENT_SESSIONS:
            # 清理过期会话
            self._cleanup_expired_sessions()

        session_id = str(uuid.uuid4())
        session = SessionData(
            session_id=session_id,
            user_profile=user_profile,
            bot_profile=bot_profile
        )
        session.total_rounds = self.config.MAX_ROUNDS

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Any]:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话数据对象，不存在则返回None
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        if self.is_session_expired(session_id):
            self.delete_session(session_id)
            return None

        return session

    def update_session(self, session_id: str, **kwargs) -> bool:
        """
        更新会话信息

        Args:
            session_id: 会话ID
            **kwargs: 要更新的字段

        Returns:
            是否更新成功
        """
        session = self.get_session(session_id)
        if not session:
            return False

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        return True

    def add_chat_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        添加聊天消息到会话历史

        Args:
            session_id: 会话ID
            role: 消息角色 (user/assistant)
            content: 消息内容

        Returns:
            是否添加成功
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        return True

    def increment_round(self, session_id: str) -> Optional[int]:
        """
        增加对话轮次

        Args:
            session_id: 会话ID

        Returns:
            更新后的轮次数，失败返回None
        """
        session = self.get_session(session_id)
        if not session:
            return None

        session.current_round += 1
        return session.current_round

    def set_session_status(
        self,
        session_id: str,
        status: SessionStatus
    ) -> bool:
        """
        设置会话状态

        Args:
            session_id: 会话ID
            status: 会话状态

        Returns:
            是否设置成功
        """
        return self.update_session(session_id, status=status)

    def create_multi_candidate_session(
        self,
        user_profile: Dict[str, Any],
        candidates: list,
        max_rounds: int = 20,
        enhanced_mode: bool = True,
        scenario_mode: ScenarioMode = ScenarioMode.FIRST_CHAT
    ) -> MultiCandidateSessionData:
        """
        创建多候选人会话

        Args:
            user_profile: 用户资料
            candidates: 候选人列表（包含bot_profile和candidate_id的字典列表）
            max_rounds: 最大对话轮数

        Returns:
            创建的多候选人会话数据对象
        """
        import uuid

        # 检查会话数量限制
        if len(self.sessions) >= self.config.MAX_CONCURRENT_SESSIONS:
            self._cleanup_expired_sessions()

        session_id = str(uuid.uuid4())

        # 转换候选人数据为CandidateData对象
        candidate_data_list = []
        for candidate_dict in candidates:
            candidate_data = CandidateData(
                candidate_id=candidate_dict.get("candidate_id", str(uuid.uuid4())),
                bot_profile=candidate_dict
            )
            candidate_data_list.append(candidate_data)

        session = MultiCandidateSessionData(
            session_id=session_id,
            user_profile=user_profile,
            candidates=candidate_data_list,
            max_rounds=max_rounds,
            enhanced_mode=enhanced_mode,
            scenario_mode=scenario_mode
        )
        session.status = SimulationStatus.READY

        self.sessions[session_id] = session
        return session

    def is_session_expired(self, session_id: str) -> bool:
        """
        检查会话是否过期

        Args:
            session_id: 会话ID

        Returns:
            是否过期
        """
        session = self.sessions.get(session_id)
        if not session:
            return True

        expire_time = timedelta(minutes=self.config.SESSION_EXPIRE_MINUTES)
        return datetime.now() - session.created_at > expire_time

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否删除成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def _cleanup_expired_sessions(self) -> int:
        """
        清理过期会话

        Returns:
            清理的会话数量
        """
        expired_ids = [
            sid for sid in self.sessions
            if self.is_session_expired(sid)
        ]

        for sid in expired_ids:
            del self.sessions[sid]

        return len(expired_ids)

    def get_active_session_count(self) -> int:
        """
        获取活跃会话数量

        Returns:
            活跃会话数量
        """
        return len(self.sessions)


# 全局会话服务实例
session_service = SessionService()
