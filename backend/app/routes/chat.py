"""
对话相关路由
处理聊天消息发送和会话状态查询
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models import (
    ChatMessageRequest,
    StartChatRequest,
    EndChatRequest,
    ChatResponse,
    SessionResponse,
    SessionInfo
)
from app.services.session_service import session_service
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["对话"])


@router.post("/start", response_model=ChatResponse)
async def start_chat(request: StartChatRequest):
    """
    开始对话，获取机器人开场白

    Args:
        request: 包含会话ID的请求

    Returns:
        包含机器人开场白的响应
    """
    try:
        result = await chat_service.start_chat(request.session_id)

        if result is None:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        return ChatResponse(
            success=True,
            bot_reply=result.get("bot_reply"),
            current_round=result.get("current_round"),
            total_rounds=result.get("total_rounds"),
            is_finished=result.get("is_finished", False),
            message="获取开场白成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取开场白失败: {str(e)}")


@router.post("/end", response_model=ChatResponse)
async def end_chat(request: EndChatRequest):
    """
    提前结束对话并生成评价

    Args:
        request: 包含会话ID的请求

    Returns:
        包含对话结束状态的响应
    """
    try:
        result = chat_service.end_chat(request.session_id)

        if result is None:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        # 如果对话已结束，直接返回成功（用户的目标已经达成）
        if not result.get("success", True):
            message = result.get("message", "")
            if "对话已结束" in message or "会话不存在或已过期" in message:
                # 对话已经结束，这是正常情况，返回成功
                return ChatResponse(
                    success=True,
                    bot_reply=None,
                    current_round=result.get("current_round", 0),
                    total_rounds=result.get("total_rounds", 10),
                    is_finished=True,
                    message="对话已结束"
                )
            # 其他错误情况
            raise HTTPException(status_code=400, detail=message)

        return ChatResponse(
            success=True,
            bot_reply=None,
            current_round=result.get("current_round"),
            total_rounds=result.get("total_rounds"),
            is_finished=True,
            message="对话已结束"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结束对话失败: {str(e)}")


@router.post("", response_model=ChatResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    发送聊天消息，获取机器人回复

    Args:
        request: 包含会话ID和消息内容的请求

    Returns:
        包含机器人回复和对话状态的响应
    """
    try:
        result = await chat_service.send_message(
            request.session_id,
            request.message
        )

        if result is None:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        if not result.get("success", True):
            raise HTTPException(status_code=400, detail=result.get("message", "发送失败"))

        return ChatResponse(
            success=True,
            bot_reply=result.get("bot_reply"),
            current_round=result.get("current_round"),
            total_rounds=result.get("total_rounds"),
            is_finished=result.get("is_finished", False),
            history=result.get("history"),
            message="发送成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session_status(session_id: str):
    """
    查询会话状态

    Args:
        session_id: 会话ID

    Returns:
        会话状态信息
    """
    try:
        session = session_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        # 格式化对话历史
        history = None
        if session.chat_history:
            history = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in session.chat_history
            ]

        session_info = SessionInfo(
            session_id=session.session_id,
            status=session.status,
            current_round=session.current_round,
            total_rounds=session.total_rounds,
            bot_profile=session.bot_profile,
            history=history
        )

        return SessionResponse(
            success=True,
            session=session_info,
            message="查询成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询会话失败: {str(e)}")
