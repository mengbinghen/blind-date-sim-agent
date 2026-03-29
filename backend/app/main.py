"""
FastAPI主应用
负责路由注册、CORS配置和静态文件服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.config import Config
from app.routes import profile, chat, evaluation, simulation

# 创建FastAPI应用
app = FastAPI(
    title="AI相亲模拟Agent",
    description="基于AI的相亲对话模拟系统，帮助用户练习与异性对话技巧",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(profile.router)
app.include_router(chat.router)
app.include_router(evaluation.router)
app.include_router(simulation.router)

# 静态文件服务
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
if frontend_dir.exists():
    # 挂载静态资源目录
    app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")

    # 主页路由
    @app.get("/")
    async def read_root():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "AI相亲模拟Agent API"}

    # 候选人页面路由
    @app.get("/candidates.html")
    async def read_candidates():
        candidates_file = frontend_dir / "candidates.html"
        if candidates_file.exists():
            return FileResponse(str(candidates_file))
        return {"message": "页面不存在"}

    # 模拟页面路由
    @app.get("/simulation.html")
    async def read_simulation():
        simulation_file = frontend_dir / "simulation.html"
        if simulation_file.exists():
            return FileResponse(str(simulation_file))
        return {"message": "页面不存在"}

    # 推荐页面路由
    @app.get("/recommendation.html")
    async def read_recommendation():
        recommendation_file = frontend_dir / "recommendation.html"
        if recommendation_file.exists():
            return FileResponse(str(recommendation_file))
        return {"message": "页面不存在"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "AI相亲模拟Agent"}


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("=" * 50)
    print("AI相亲模拟Agent 启动成功！")
    print("=" * 50)
    print(f"应用地址: http://localhost:8000")
    print(f"API文档: http://localhost:8000/docs")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    from app.services.agent_service import agent_service
    await agent_service.close()
    print("AI相亲模拟Agent 已关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
