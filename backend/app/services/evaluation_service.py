"""
评价服务
负责生成和获取对话评价结果
"""
from typing import Dict, Any, Optional
from app.services.session_service import session_service
from app.services.agent_service import agent_service
from app.models import SessionStatus, EvaluationResult


class EvaluationService:
    """评价服务类"""

    async def generate_evaluation(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        生成对话评价

        Args:
            session_id: 会话ID

        Returns:
            评价结果字典，失败返回None
        """
        session = session_service.get_session(session_id)
        if not session:
            return None

        # 检查是否已有评价
        if session.evaluation:
            return self._format_evaluation(session.evaluation)

        # 生成新评价
        evaluation_data = await agent_service.generate_evaluation(
            session.chat_history,
            session.user_profile,
            session.bot_profile
        )

        if evaluation_data:
            # 构建评价结果对象
            evaluation = EvaluationResult(
                attraction_score=evaluation_data.get("attraction_score", 70),
                strengths=evaluation_data.get("strengths", []),
                suggestions=evaluation_data.get("suggestions", []),
                summary=evaluation_data.get("summary", "")
            )

            # 保存评价到会话
            session.evaluation = evaluation

            return self._format_evaluation(evaluation)

        return None

    def get_evaluation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取已生成的评价结果

        Args:
            session_id: 会话ID

        Returns:
            评价结果字典，不存在返回None
        """
        session = session_service.get_session(session_id)
        if not session:
            return None

        # 如果没有评价，尝试生成
        if not session.evaluation and session.status == SessionStatus.FINISHED:
            # 这里需要异步调用，但get_evaluation是同步方法
            # 实际使用时应该调用generate_evaluation
            return None

        if session.evaluation:
            return self._format_evaluation(session.evaluation)

        return None

    def _format_evaluation(self, evaluation: EvaluationResult) -> Dict[str, Any]:
        """
        格式化评价结果

        Args:
            evaluation: 评价结果对象

        Returns:
            格式化后的评价字典
        """
        return {
            "attraction_score": evaluation.attraction_score,
            "strengths": evaluation.strengths,
            "suggestions": evaluation.suggestions,
            "summary": evaluation.summary
        }


# 全局评价服务实例
evaluation_service = EvaluationService()
