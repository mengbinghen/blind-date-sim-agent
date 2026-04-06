"""
用户资料相关路由
处理用户资料提交和会话创建
"""
from fastapi import APIRouter, HTTPException
from app.models import (
    UserProfileSubmit,
    ProfileSubmitResponse,
    BotProfile,
    MultiCandidateProfileSubmit,
    MultiCandidateProfileResponse
)
from app.services.session_service import session_service
from app.services.agent_service import agent_service

router = APIRouter(prefix="/api/profile", tags=["用户资料"])


@router.post("", response_model=ProfileSubmitResponse)
async def submit_profile(profile: UserProfileSubmit):
    """
    提交用户资料，创建会话并生成机器人人设

    Args:
        profile: 用户资料

    Returns:
        包含会话ID和机器人资料的响应
    """
    try:
        # 转换为字典
        user_profile = profile.dict()

        # 生成机器人人设
        bot_persona = await agent_service.generate_bot_persona(user_profile)

        if not bot_persona:
            raise HTTPException(status_code=500, detail="生成机器人人设失败")

        # 创建会话
        session = session_service.create_session(user_profile, bot_persona)

        # 构建机器人资料响应
        bot_profile = BotProfile(
            name=bot_persona.get("name", "小美"),
            age=bot_persona.get("age", 25),
            gender=bot_persona.get("gender", "female"),
            occupation=bot_persona.get("occupation", "未知"),
            interests=bot_persona.get("interests", ""),
            personality=bot_persona.get("personality", ""),
            avatar=bot_persona.get("avatar", "👩")
        )

        return ProfileSubmitResponse(
            success=True,
            session_id=session.session_id,
            bot_profile=bot_profile,
            message="资料提交成功，即将开始对话"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"资料提交失败: {str(e)}")


@router.post("/multi-candidate", response_model=MultiCandidateProfileResponse)
async def submit_profile_multi_candidate(profile: MultiCandidateProfileSubmit):
    """
    提交用户资料（多候选人模式），生成多个候选人并创建会话

    Args:
        profile: 用户资料（包含候选人数和对话轮数配置）

    Returns:
        包含会话ID和候选人列表的响应
    """
    try:
        # 转换为字典
        user_profile = profile.dict()

        print(f"收到用户资料: {user_profile}")

        # 生成多个候选人
        candidates = await agent_service.generate_multiple_candidates(
            user_profile,
            count=profile.candidate_count
        )

        print(f"AI生成候选人数量: {len(candidates) if candidates else 0}")

        if not candidates or len(candidates) < profile.candidate_count:
            # 如果生成数量不足，使用默认填充
            while len(candidates) < profile.candidate_count:
                default_persona = agent_service._get_default_persona(user_profile)
                import uuid
                default_persona["candidate_id"] = str(uuid.uuid4())
                candidates.append(default_persona)

        # 创建多候选人会话
        session = session_service.create_multi_candidate_session(
            user_profile=user_profile,
            candidates=candidates,
            max_rounds=profile.max_rounds,
            enhanced_mode=profile.enhanced_mode,
            scenario_mode=profile.scenario_mode
        )

        # 构建候选人资料响应列表
        bot_profiles = []
        for candidate in candidates:
            # 性别已在agent_service中标准化，这里添加防御性检查
            gender_value = candidate.get("gender", "female")
            from app.utils.normalization import normalize_gender
            gender_value = normalize_gender(gender_value)

            # 获取城市，优先使用候选人自己的城市，否则使用用户所在城市
            city = candidate.get("city") or user_profile.get("city") or "未知"

            try:
                bot_profiles.append(BotProfile(
                    candidate_id=candidate.get("candidate_id"),
                    name=candidate.get("name", "小美"),
                    age=candidate.get("age", 25),
                    gender=gender_value,
                    occupation=candidate.get("occupation", "未知"),
                    interests=candidate.get("interests", ""),
                    personality=candidate.get("personality", ""),
                    city=city,
                    avatar=candidate.get("avatar", "👩")
                ))
            except Exception as e:
                print(f"Error creating BotProfile for candidate: {candidate}")
                print(f"Error: {str(e)}")
                # 跳过这个候选人，继续处理下一个
                continue

        return MultiCandidateProfileResponse(
            success=True,
            session_id=session.session_id,
            candidates=bot_profiles,
            candidate_count=len(bot_profiles),
            max_rounds=profile.max_rounds,
            enhanced_mode=profile.enhanced_mode,
            scenario_mode=profile.scenario_mode,
            message=f"已生成{len(bot_profiles)}位候选人，即将开始AI模拟对话"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"资料提交失败: {str(e)}")
