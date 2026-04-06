"""
数据标准化工具
提供统一的数据格式转换函数
"""


def normalize_gender(gender_value: any) -> str:
    """
    标准化性别值为英文枚举值

    Args:
        gender_value: 性别值，可能是中文、英文或其他格式

    Returns:
        标准化的性别值: "male" 或 "female"

    Examples:
        >>> normalize_gender("男")
        'male'
        >>> normalize_gender("女")
        'female'
        >>> normalize_gender("male")
        'male'
        >>> normalize_gender("female")
        'female'
        >>> normalize_gender("其他")
        'female'  # 默认值
    """
    if not gender_value:
        return "female"  # 默认值

    # 如果已经是正确的英文值，直接返回
    if isinstance(gender_value, str):
        gender_lower = gender_value.lower().strip()
        if gender_lower in ("male", "female"):
            return gender_lower

        # 中文转英文
        if gender_lower in ("男", "male", "m", "man"):
            return "male"
        elif gender_lower in ("女", "female", "f", "woman"):
            return "female"

    # 无法识别时的默认值
    return "female"


def normalize_gender_in_profile(profile: dict) -> dict:
    """
    标准化资料中的性别字段

    Args:
        profile: 包含gender字段的资料字典

    Returns:
        标准化后的资料字典（不修改原字典）
    """
    if not profile or not isinstance(profile, dict):
        return profile

    # 创建副本避免修改原字典
    normalized = profile.copy()

    if "gender" in normalized:
        normalized["gender"] = normalize_gender(normalized["gender"])

    return normalized
