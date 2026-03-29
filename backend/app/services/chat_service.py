"""
对话服务
负责对话历史维护、轮次控制和对话状态管理
"""
from typing import Dict, Any, List, Optional
from app.services.session_service import session_service
from app.services.agent_service import agent_service
from app.models import SessionStatus, ChatMessage
from app.config import Config


class ChatService:
    """对话服务类"""

    def __init__(self):
        """初始化对话服务"""
        self.config = Config()

    async def start_chat(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        开始对话，生成机器人开场白

        Args:
            session_id: 会话ID

        Returns:
            包含开场白的响应字典，失败返回None
        """
        session = session_service.get_session(session_id)
        if not session:
            return None

        # 检查是否已有消息历史
        if session.chat_history:
            # 已有历史消息，返回第一条消息
            first_message = session.chat_history[0]
            return {
                "bot_reply": first_message.get("content"),
                "current_round": session.current_round,
                "total_rounds": session.total_rounds,
                "is_finished": session.status == SessionStatus.FINISHED
            }

        # 没有历史消息，生成开场白
        bot_profile = session.bot_profile
        opening_message = agent_service.get_opening_message(bot_profile)

        # 添加机器人开场白到历史
        session_service.add_chat_message(
            session_id,
            "assistant",
            opening_message
        )

        return {
            "bot_reply": opening_message,
            "current_round": 0,
            "total_rounds": session.total_rounds,
            "is_finished": False
        }

    def end_chat(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        提前结束对话

        Args:
            session_id: 会话ID

        Returns:
            包含结束状态的响应字典，失败返回None
        """
        session = session_service.get_session(session_id)
        if not session:
            return {
                "success": False,
                "message": "会话不存在或已过期"
            }

        # 检查会话状态
        if session.status == SessionStatus.FINISHED:
            return {
                "success": False,
                "message": "对话已结束"
            }

        # 标记会话为结束
        session_service.set_session_status(session_id, SessionStatus.FINISHED)

        return {
            "success": True,
            "current_round": session.current_round,
            "total_rounds": session.total_rounds
        }

    async def send_message(
        self,
        session_id: str,
        user_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        发送用户消息并获取机器人回复

        Args:
            session_id: 会话ID
            user_message: 用户消息内容

        Returns:
            包含回复信息的响应字典，失败返回None
        """
        session = session_service.get_session(session_id)
        if not session:
            return {
                "success": False,
                "message": "会话不存在或已过期"
            }

        # 检查会话状态
        if session.status == SessionStatus.FINISHED:
            return {
                "success": False,
                "message": "对话已结束"
            }

        # 检查消息长度
        if len(user_message) > self.config.MAX_MESSAGE_LENGTH:
            return {
                "success": False,
                "message": f"消息长度不能超过{self.config.MAX_MESSAGE_LENGTH}字"
            }

        # 添加用户消息到历史
        session_service.add_chat_message(session_id, "user", user_message)

        # 增加轮次
        current_round = session_service.increment_round(session_id)
        if current_round is None:
            return {
                "success": False,
                "message": "会话更新失败"
            }

        # 检查是否达到最大轮次
        if current_round >= session.total_rounds:
            # 标记会话为结束，但不返回结束消息
            session_service.set_session_status(session_id, SessionStatus.FINISHED)
            return {
                "bot_reply": None,  # 不显示结束消息
                "current_round": current_round,
                "total_rounds": session.total_rounds,
                "is_finished": True,
                "history": self._format_history(session.chat_history)
            }

        # 生成机器人回复
        bot_reply = await agent_service.generate_chat_response(
            user_message,
            session.bot_profile,
            session.user_profile,
            session.chat_history
        )

        # 添加机器人回复到历史
        session_service.add_chat_message(session_id, "assistant", bot_reply)

        return {
            "bot_reply": bot_reply,
            "current_round": current_round,
            "total_rounds": session.total_rounds,
            "is_finished": False,
            "history": self._format_history(session.chat_history)
        }

    def _format_history(self, chat_history: List[Dict[str, Any]]) -> List[ChatMessage]:
        """
        格式化对话历史

        Args:
            chat_history: 原始对话历史

        Returns:
            格式化后的消息列表
        """
        return [
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in chat_history
        ]

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息字典，不存在返回None
        """
        session = session_service.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "status": session.status,
            "current_round": session.current_round,
            "total_rounds": session.total_rounds,
            "bot_profile": session.bot_profile
        }


# 全局对话服务实例
chat_service = ChatService()
