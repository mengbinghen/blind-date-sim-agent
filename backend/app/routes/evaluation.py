"""
评价相关路由
处理对话评价生成和查询
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import json
import asyncio
from app.models import EvaluationResponse, EvaluationResult, RecommendationResponse, RecommendationResult, MultiCandidateSessionData
from app.services.session_service import session_service
from app.services.evaluation_service import evaluation_service
from app.services.agent_service import agent_service

router = APIRouter(prefix="/api/evaluation", tags=["评价"])


# 默认评价
DEFAULT_EVALUATION = {
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


class GenerateEvaluationRequest(BaseModel):
    """开始生成评价请求模型"""
    session_id: str = Field(..., description="会话ID")


class GenerateEvaluationResponse(BaseModel):
    """开始生成评价响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")


@router.post("/generate", response_model=GenerateEvaluationResponse)
async def start_evaluation_generation(
    request: GenerateEvaluationRequest,
    background_tasks: BackgroundTasks
):
    """
    开始生成评价（后台任务，不阻塞）

    Args:
        request: 包含会话ID的请求
        background_tasks: FastAPI后台任务

    Returns:
        立即返回成功响应，评价在后台生成
    """
    try:
        session = session_service.get_session(request.session_id)

        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        # 如果已有评价，不需要重新生成
        if session.evaluation:
            return GenerateEvaluationResponse(
                success=True,
                message="评价已存在"
            )

        # 添加后台任务生成评价
        background_tasks.add_task(
            evaluation_service.generate_evaluation,
            request.session_id
        )

        return GenerateEvaluationResponse(
            success=True,
            message="评价生成已开始"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动评价生成失败: {str(e)}")


@router.get("", response_model=EvaluationResponse)
async def get_evaluation(session_id: str):
    """
    获取对话评价结果

    Args:
        session_id: 会话ID

    Returns:
        评价结果
    """
    try:
        session = session_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        # 如果已有评价，直接返回
        if session.evaluation:
            return EvaluationResponse(
                success=True,
                evaluation=session.evaluation,
                message="获取评价成功"
            )

        # 生成新评价
        evaluation_data = await evaluation_service.generate_evaluation(session_id)

        if evaluation_data is None:
            raise HTTPException(status_code=500, detail="生成评价失败")

        return EvaluationResponse(
            success=True,
            evaluation=EvaluationResult(**evaluation_data),
            message="获取评价成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评价失败: {str(e)}")


@router.get("/stream")
async def stream_evaluation_generation(session_id: str):
    """
    流式生成评价（SSE），实时返回生成过程中的中间结果和AI生成的内容

    Args:
        session_id: 会话ID

    Returns:
        SSE流式响应
    """
    async def event_generator():
        try:
            session = session_service.get_session(session_id)
            if not session:
                yield f"event: error\ndata: {json.dumps({'message': '会话不存在或已过期'}, ensure_ascii=False)}\n\n"
                return

            # 每次都重新生成评测（基于最新的对话历史）
            chat_history = session.chat_history
            user_profile = session.user_profile
            bot_profile = session.bot_profile

            async for event_type, data in agent_service.generate_evaluation_stream(
                chat_history, user_profile, bot_profile
            ):
                if event_type == "progress":
                    # 进度更新
                    yield f"event: progress\ndata: {json.dumps({'message': data}, ensure_ascii=False)}\n\n"
                elif event_type == "content":
                    # 内容块
                    yield f"event: content\ndata: {json.dumps({'text': data}, ensure_ascii=False)}\n\n"
                elif event_type == "complete":
                    # 完成
                    yield f"event: complete\ndata: {json.dumps({'evaluation': data}, ensure_ascii=False)}\n\n"
                    # 更新session中的evaluation
                    session.evaluation = EvaluationResult(**data)
                elif event_type == "error":
                    # 错误
                    yield f"event: error\ndata: {json.dumps({'message': data}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': f'生成评价失败: {str(e)}'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/recommendation", response_model=RecommendationResponse)
async def get_recommendation(session_id: str):
    """
    获取多候选人比较推荐结果

    Args:
        session_id: 会话ID

    Returns:
        推荐结果
    """
    try:
        session = session_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="会话不存在或已过期")

        # 检查是否为多候选人会话
        if not isinstance(session, MultiCandidateSessionData):
            raise HTTPException(status_code=400, detail="此会话不是多候选人模式")

        # 如果已有推荐结果，直接返回
        if session.final_recommendation:
            return RecommendationResponse(
                success=True,
                recommendation=RecommendationResult(**session.final_recommendation),
                message="获取推荐成功"
            )

        # 生成新的推荐结果
        recommendation_data = await agent_service.generate_comparative_recommendation(
            user_profile=session.user_profile,
            candidates=session.candidates,
            scenario_mode=session.scenario_mode
        )

        if not recommendation_data:
            raise HTTPException(status_code=500, detail="生成推荐失败")

        # 保存推荐结果到会话
        session.final_recommendation = recommendation_data
        session.best_match_candidate_id = recommendation_data.get("best_match_candidate_id")

        return RecommendationResponse(
            success=True,
            recommendation=RecommendationResult(**recommendation_data),
            message="获取推荐成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")
