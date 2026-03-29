"""
模拟相关路由
处理多候选人AI模拟对话
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.models import (
    StartSimulationRequest,
    SimulationStatusResponse
)
from app.services.session_service import session_service
from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/api/simulation", tags=["模拟"])


@router.post("/start", response_model=dict)
async def start_simulation(
    request: StartSimulationRequest,
    background_tasks: BackgroundTasks
):
    """
    启动所有候选人的AI模拟

    Args:
        request: 包含会话ID的请求
        background_tasks: FastAPI后台任务

    Returns:
        启动响应
    """
    session = session_service.get_session(request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")

    # 添加后台任务运行模拟
    background_tasks.add_task(
        simulation_service.run_all_simulations,
        request.session_id
    )

    return {
        "success": True,
        "message": "模拟已启动，正在后台运行",
        "session_id": request.session_id
    }


@router.get("/stream")
async def stream_simulation_progress(session_id: str):
    """
    流式获取模拟进度（SSE）

    Args:
        session_id: 会话ID

    Returns:
        SSE流式响应
    """
    import json

    async def event_generator():
        try:
            async for event_type, data in simulation_service.stream_simulation_progress(session_id):
                if event_type == "round":
                    yield f"event: round\ndata: {data}\n\n"
                elif event_type == "complete":
                    yield f"event: complete\ndata: {data}\n\n"
                elif event_type == "error":
                    yield f"event: error\ndata: {data}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': f'获取模拟进度失败: {str(e)}'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/status", response_model=SimulationStatusResponse)
async def get_simulation_status(session_id: str):
    """
    获取模拟状态

    Args:
        session_id: 会话ID

    Returns:
        模拟状态响应
    """
    status = simulation_service.get_simulation_status(session_id)

    if not status:
        raise HTTPException(status_code=404, detail="会话不存在或状态不可用")

    return SimulationStatusResponse(
        success=True,
        status=status["status"],
        current_round=status["current_round"],
        max_rounds=status["max_rounds"],
        candidates_status=status["candidates_status"],
        message="查询成功"
    )


@router.post("/stop", response_model=dict)
async def stop_simulation(session_id: str):
    """
    停止模拟（标记为完成）

    Args:
        session_id: 会话ID

    Returns:
        响应
    """
    session = session_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")

    # 标记模拟完成
    from app.models import SimulationStatus
    session.status = SimulationStatus.COMPLETED

    return {
        "success": True,
        "message": "模拟已停止"
    }
