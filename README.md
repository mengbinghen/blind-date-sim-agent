# AI 相亲模拟 Agent

<p align="center">
  <strong>让 AI 先替你聊一轮，再决定谁值得继续认识。</strong>
</p>

<p align="center">
  一个把候选人生成、批量聊天模拟、匹配推荐串成完整闭环的 AI Web Demo。
</p>

<p align="center">
  多角色对话编排 · SSE 流式体验 · 场景模式 · 事件卡 · 结局卡
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white">
  <img alt="Frontend" src="https://img.shields.io/badge/Frontend-HTML%2FCSS%2FVanilla%20JS-FF6B81?style=flat-square">
  <img alt="LLM" src="https://img.shields.io/badge/LLM-DeepSeek-6C63FF?style=flat-square">
  <img alt="Streaming" src="https://img.shields.io/badge/Streaming-SSE-4F46E5?style=flat-square">
</p>

## 这是什么

AI 相亲模拟 Agent 是一个完整的 AI Web Demo：输入一份用户资料，系统会批量生成候选人，自动完成多轮对话模拟，并在最后给出最佳匹配、关系结局和对话总结。

它的重点不只是“聊天”，而是把候选人生成、关系推进、过程展示和结果判断串成一条完整体验链路。

## 为什么有意思

- 一次生成多位候选人，而不是只和单个角色对话
- 批量推进多轮模拟，更接近真实的筛选过程
- 通过 SSE 实时展示模拟进度，过程本身就有观看价值
- 支持不同场景模式，同一批候选人可以跑出不同结果
- 事件卡会在关键轮次推动对话，不会一直停留在浅层寒暄
- 最终结果除了分数和排序，还会给出更直观的关系结局

## 最新玩法

### `场景模式`

你可以直接决定这一轮关系推进发生在什么语境里：

- `初识聊天`
- `周末约会计划`
- `未来关系试探`

同一组候选人，在不同场景下往往会呈现出不同的聊天走向和匹配结果。

### `事件卡`

系统会在关键轮次插入事件，让对话自然发生变化，比如：

- 共同兴趣深入
- 安排偏好差异
- 临时变化应对
- 是否愿意见面
- 城市与工作取舍
- 关系节奏预期

这些事件不会生硬打断对话，而是把聊天从“聊得下去”推进到“值不值得继续了解”。

### `结局卡`

推荐页除了排序，还会给每位候选人一个关系结局：

- `互有好感`
- `建议继续接触`
- `适合慢慢了解`
- `更适合做朋友`

这让结果不再只是抽象评分，而更像一次完整的关系判断。

## 体验流程

1. 填写个人资料，设置候选人数、对话轮数和场景模式。
2. AI 生成一批候选人，形成这一轮的候选池。
3. 系统并行推进所有候选人的多轮聊天。
4. 模拟页实时展示轮次、内容和当前事件卡。
5. 最终输出最佳匹配、推荐理由、对话高光和关系结局。

## 页面预览

### 首页

资料录入、模拟规模和场景模式都集中在一个页面，便于快速进入整条体验流程。

![首页预览](docs/images/home.jpg)

### 候选人页

先浏览这一轮生成出的候选人，再进入批量模拟流程。

![候选人页](docs/images/candidates.jpg)

### 模拟页

这是整个项目最能体现过程感的页面。左侧看每位候选人的进度，右侧查看当前对话内容。

![模拟页](docs/images/simulation.jpg)

## 技术栈

- 后端：Python、FastAPI、httpx、Pydantic
- 前端：HTML、CSS、Vanilla JavaScript
- 模型：
  - `deepseek-chat` 负责候选人生成与对话模拟
  - `deepseek-reasoner` 负责推荐分析与结果总结
- 通信：SSE（Server-Sent Events）

## 快速开始

### 1. 安装依赖

```bash
cd ai-blind-date
python -m venv venv
source venv/bin/activate  # Linux / macOS
# venv\Scripts\activate   # Windows
pip install -r backend/requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

填写你的 DeepSeek API Key：

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 启动服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或者直接在项目根目录运行：

```bash
./start.sh
```

### 4. 打开应用

- 首页：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## License

MIT License
