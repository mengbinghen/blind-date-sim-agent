"""
模拟服务
负责编排多候选人的并行AI模拟对话
"""
import asyncio
import uuid
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from app.models import CandidateData, MultiCandidateSessionData, SimulationStatus
from app.services.agent_service import agent_service
from app.services.session_service import session_service
from app.prompts.simulation_prompts import get_opening_message_for_candidate
from app.config import Config


class SimulationService:
    """模拟服务类"""

    def __init__(self):
        """初始化模拟服务"""
        self.config = Config()
        self.active_simulations: Dict[str, bool] = {}  # session_id -> is_running

    async def run_all_simulations(
        self,
        session_id: str,
        batch_size: int = None
    ) -> None:
        """
        运行所有候选人的模拟对话

        Args:
            session_id: 会话ID
            batch_size: 批处理大小（并行候选人数）
        """
        if batch_size is None:
            batch_size = self.config.SIMULATION_BATCH_SIZE

        session = session_service.get_session(session_id)

        if not session or not isinstance(session, MultiCandidateSessionData):
            print(f"会话 {session_id} 不存在或不是多候选人会话")
            return

        if session_id in self.active_simulations:
            print(f"会话 {session_id} 的模拟已在运行中")
            return

        self.active_simulations[session_id] = True
        session.status = SimulationStatus.SIMULATING

        try:
            # 为每个候选人添加开场白
            for candidate in session.candidates:
                opening = get_opening_message_for_candidate(candidate.bot_profile)
                candidate.chat_history.append({
                    "role": "assistant",
                    "content": opening,
                    "timestamp": datetime.now().isoformat()
                })

            # 逐轮模拟对话
            for round_num in range(1, session.max_rounds + 1):
                session.current_simulation_round = round_num

                # 分批并行处理
                for i in range(0, len(session.candidates), batch_size):
                    batch = session.candidates[i:i + batch_size]

                    # 并行模拟这批候选人的本轮对话
                    await asyncio.gather(*[
                        self._simulate_single_round(
                            session.user_profile,
                            candidate,
                            round_num,
                            session.max_rounds
                        )
                        for candidate in batch
                    ])

            session.status = SimulationStatus.COMPLETED

        except Exception as e:
            print(f"模拟过程出错: {str(e)}")
            session.status = SimulationStatus.COMPLETED  # 即使出错也标记为完成

        finally:
            self.active_simulations.pop(session_id, None)

    async def _simulate_single_round(
        self,
        user_profile: Dict[str, Any],
        candidate: CandidateData,
        round_num: int,
        max_rounds: int
    ) -> None:
        """
        模拟单个候选人的一轮对话

        Args:
            user_profile: 用户资料
            candidate: 候选人数据
            round_num: 当前轮次
            max_rounds: 最大轮次
        """
        try:
            # 调用AI模拟本轮对话
            result = await agent_service.simulate_conversation_round(
                user_profile=user_profile,
                candidate_profile=candidate.bot_profile,
                chat_history=candidate.chat_history,
                round_num=round_num,
                max_rounds=max_rounds
            )

            if result:
                # 添加用户消息
                candidate.chat_history.append({
                    "role": "user",
                    "content": result["user_message"],
                    "timestamp": datetime.now().isoformat()
                })

                # 添加候选人回复
                candidate.chat_history.append({
                    "role": "assistant",
                    "content": result["candidate_reply"],
                    "timestamp": datetime.now().isoformat()
                })

                candidate.current_round = round_num

        except Exception as e:
            print(f"候选人 {candidate.candidate_id} 第 {round_num} 轮模拟失败: {str(e)}")

    async def stream_simulation_progress(
        self,
        session_id: str
    ) -> AsyncGenerator[tuple, None]:
        """
        流式输出模拟进度

        Args:
            session_id: 会话ID

        Yields:
            元组 (event_type, data):
                - ('round', {'candidate_id': str, 'round': int, 'messages': list})
                - ('complete', {'session_id': str})
                - ('error', str)
        """
        import json

        session = session_service.get_session(session_id)

        if not session or not isinstance(session, MultiCandidateSessionData):
            yield ('error', json.dumps({'message': '会话不存在或不是多候选人会话'}, ensure_ascii=False))
            return

        try:
            # 追踪每个候选人已发送的轮次
            sent_rounds = {c.candidate_id: 0 for c in session.candidates}

            async def yield_pending_rounds() -> AsyncGenerator[tuple, None]:
                for candidate in session.candidates:
                    # 如果这个候选人有新的对话轮次
                    if candidate.current_round > sent_rounds[candidate.candidate_id]:
                        # 发送新轮次的消息
                        yield ('round', json.dumps({
                            'candidate_id': candidate.candidate_id,
                            'round': candidate.current_round,
                            'messages': candidate.chat_history[-2:] if len(candidate.chat_history) >= 2 else candidate.chat_history
                        }, ensure_ascii=False))

                        sent_rounds[candidate.candidate_id] = candidate.current_round

            # 轮询检查进度
            while True:
                async for event in yield_pending_rounds():
                    yield event

                # 检查是否全部完成
                if session.status == SimulationStatus.COMPLETED:
                    break

                await asyncio.sleep(0.5)  # 每0.5秒检查一次

            # 发送完成事件
            yield ('complete', json.dumps({
                'session_id': session_id,
                'all_candidates': [
                    {
                        'candidate_id': c.candidate_id,
                        'name': c.bot_profile.get('name', '未知'),
                        'rounds': c.current_round,
                        'messages_count': len(c.chat_history),
                        'last_messages': c.chat_history[-2:] if len(c.chat_history) >= 2 else c.chat_history
                    }
                    for c in session.candidates
                ]
            }, ensure_ascii=False))

        except Exception as e:
            yield ('error', json.dumps({'message': f'流式输出失败: {str(e)}'}, ensure_ascii=False))

    def get_simulation_status(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取模拟状态

        Args:
            session_id: 会话ID

        Returns:
            状态信息字典
        """
        session = session_service.get_session(session_id)

        if not session or not isinstance(session, MultiCandidateSessionData):
            return None

        return {
            'status': session.status,
            'current_round': session.current_simulation_round,
            'max_rounds': session.max_rounds,
            'candidates_status': [
                {
                    'candidate_id': c.candidate_id,
                    'name': c.bot_profile.get('name', '未知'),
                    'current_round': c.current_round,
                    'messages_count': len(c.chat_history)
                }
                for c in session.candidates
            ]
        }


# 全局模拟服务实例
simulation_service = SimulationService()
