"""
系统配置文件
包含API密钥、对话轮次、评价标准等参数化配置
"""
import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "backend" / ".env")


class Config:
    """系统配置类"""

    # ==================== DeepSeek API 配置 ====================
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL = "deepseek-chat"
    DEEPSEEK_REASONER_MODEL = "deepseek-reasoner"  # 推理模型，用于评价生成
    DEEPSEEK_TIMEOUT = 30  # API调用超时时间（秒）
    EVALUATION_TIMEOUT = 120  # 评价生成超时时间（秒），推理模型需要更长时间

    # ==================== 场景化token配置 ====================
    MAX_TOKENS_MAP = {
        "default": 2000,                      # 默认场景
        "persona_generation": 1500,           # 人设生成
        "chat_response": 1000,                # 聊天回复
        "evaluation": 2500,                   # 对话评价
        "multi_candidate": 3000,              # 批量候选人生成
        "comparative_recommendation": 3500,   # 比较推荐
        "simulation_round": 1500              # 模拟对话轮次
    }

    # ==================== 对话配置 ====================
    MAX_ROUNDS = int(os.getenv("MAX_ROUNDS", "20"))  # 最大对话轮次（多候选人模式默认20）
    MAX_MESSAGE_LENGTH = 500  # 单条消息最大长度
    CONVERSATION_TIMEOUT = 1800  # 对话超时时间（秒），30分钟

    # ==================== 多候选人模拟配置 ====================
    CANDIDATE_COUNT = int(os.getenv("CANDIDATE_COUNT", "10"))  # 默认候选人数
    SIMULATION_BATCH_SIZE = int(os.getenv("SIMULATION_BATCH_SIZE", "3"))  # 并行模拟批大小
    SIMULATION_TEMPERATURE = 0.9  # 模拟对话的temperature参数（越高越有创意）

    # ==================== 评价配置 ====================
    # 评价维度权重
    EVALUATION_DIMENSIONS: Dict[str, float] = {
        "opening": 0.15,      # 开场表现
        "interaction": 0.30,  # 互动质量
        "emotional": 0.25,    # 情商表现
        "technique": 0.20,    # 对话技巧
        "overall": 0.10       # 整体印象
    }

    # ==================== 会话配置 ====================
    SESSION_EXPIRE_MINUTES = 60  # 会话过期时间（分钟）
    MAX_CONCURRENT_SESSIONS = 100  # 最大并发会话数

    # ==================== CORS配置 ====================
    CORS_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]

    # ==================== 人设生成配置 ====================
    # 机器人年龄范围（相对于用户年龄的偏移）
    BOT_AGE_MIN_OFFSET = -5
    BOT_AGE_MAX_OFFSET = 5

    # 机器人名字池
    FEMALE_NAMES = [
        "小美", "小雅", "小雪", "小琳", "小婷", "小慧", "小芳", "小娟",
        "小薇", "小静", "小娜", "小颖", "小萱", "小雯", "小怡", "小月",
        "晓雨", "思琪", "梦洁", "雅琴", "诗涵", "欣妍", "雨婷", "佳琪"
    ]

    MALE_NAMES = [
        "小杰", "小明", "小强", "小刚", "小伟", "小涛", "小军", "小亮",
        "小峰", "小鹏", "小辉", "小宇", "小健", "小飞", "小龙", "小波",
        "浩然", "俊杰", "博文", "天宇", "志强", "家豪", "建国", "明轩"
    ]

    # 职业池（更多样化的职业选择）
    OCCUPATIONS = [
        # 互联网/科技
        "软件工程师", "产品经理", "UI设计师", "数据分析师", "运营专员",
        "游戏策划", "算法工程师", "测试工程师", "技术文档工程师",
        # 创意/设计
        "平面设计师", "插画师", "摄影师", "视频剪辑师", "广告创意",
        "室内设计师", "服装设计师", "品牌策划",
        # 教育/文化
        "小学教师", "中学教师", "大学教授", "教育咨询师", "图书馆员",
        "博物馆讲解员", "编辑", "记者", "翻译", "内容运营",
        # 医疗/健康
        "医生", "护士", "药剂师", "心理咨询师", "健身教练",
        "营养师", "物理治疗师", "兽医",
        # 金融/商业
        "银行职员", "证券分析师", "投资顾问", "会计", "审计",
        "市场营销", "销售经理", "人力资源", "行政助理",
        # 法律/公务
        "律师", "法官助理", "公务员", "警察", "消防员",
        # 服务行业
        "咖啡师", "调酒师", "花艺师", "烘焙师", "导游",
        "酒店管理", "活动策划",
        # 建筑/工程
        "建筑师", "土木工程师", "电气工程师", "景观设计师",
        # 其他
        "创业者", "自由职业者", "研究生", "科研人员", "飞行员"
    ]

    # 兴趣爱好池
    INTERESTS = [
        "阅读", "旅行", "音乐", "电影", "运动", "美食", "摄影", "绘画",
        "瑜伽", "健身", "篮球", "足球", "游泳", "爬山", "骑行", "烹饪",
        "编程", "写作", "游戏", "动漫", "追剧", "逛街", "品茶", "咖啡"
    ]

    # 性格特征池
    PERSONALITIES = [
        "温柔细腻，善于倾听",
        "开朗大方，热情友善",
        "文静内向，心思缜密",
        "活泼可爱，充满活力",
        "成熟稳重，做事踏实",
        "幽默风趣，乐于助人",
        "独立自主，有主见",
        "善良体贴，富有同情心"
    ]

    # ==================== 前端资源路径 ====================
    STATIC_DIR = "frontend"
