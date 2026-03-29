/**
 * 资料表单处理逻辑
 */

// 随机生成数据池（与后端 config.py 保持一致）
const RANDOM_DATA_POOLS = {
    occupations: [
        // 互联网/科技
        '软件工程师', '产品经理', 'UI设计师', '数据分析师', '运营专员',
        '游戏策划', '算法工程师', '测试工程师', '技术文档工程师',
        // 创意/设计
        '平面设计师', '插画师', '摄影师', '视频剪辑师', '广告创意',
        '室内设计师', '服装设计师', '品牌策划',
        // 教育/文化
        '小学教师', '中学教师', '大学教授', '教育咨询师', '图书馆员',
        '博物馆讲解员', '编辑', '记者', '翻译', '内容运营',
        // 医疗/健康
        '医生', '护士', '药剂师', '心理咨询师', '健身教练',
        '营养师', '物理治疗师', '兽医',
        // 金融/商业
        '银行职员', '证券分析师', '投资顾问', '会计', '审计',
        '市场营销', '销售经理', '人力资源', '行政助理',
        // 法律/公务
        '律师', '法官助理', '公务员', '警察', '消防员',
        // 服务行业
        '咖啡师', '调酒师', '花艺师', '烘焙师', '导游',
        '酒店管理', '活动策划',
        // 建筑/工程
        '建筑师', '土木工程师', '电气工程师', '景观设计师',
        // 其他
        '创业者', '自由职业者', '研究生', '科研人员', '飞行员'
    ],
    interests: [
        '阅读', '旅行', '音乐', '电影', '运动', '美食', '摄影', '绘画',
        '瑜伽', '健身', '篮球', '足球', '游泳', '爬山', '骑行', '烹饪',
        '编程', '写作', '游戏', '动漫', '追剧', '逛街', '品茶', '咖啡'
    ],
    cities: [
        '北京', '上海', '深圳', '广州', '杭州', '成都', '南京', '武汉',
        '西安', '重庆', '天津', '苏州', '长沙', '郑州', '青岛', '大连',
        '厦门', '济南', '沈阳', '宁波', '苏州', '东莞', '佛山', '合肥'
    ],
    educations: ['高中', '大专', '本科', '硕士', '博士'],
    selfDescriptions: [
        '性格开朗，喜欢结交新朋友，对生活充满热情。',
        '文静内敛但内心丰富，喜欢深度交流，追求有意义的关系。',
        '幽默风趣，善于活跃气氛，希望找到一个能一起笑的人。',
        '成熟稳重，做事踏实，相信真诚是相处的基础。',
        '温柔细腻，善于倾听，希望能成为一个温暖的陪伴者。',
        '独立自主，有自己的想法和追求，也尊重他人的选择。',
        '善良体贴，富有同情心，希望能用真心换来真情。',
        '活泼可爱，充满活力，每天都正能量满满。'
    ],
    idealTypes: [
        '希望对方善良真诚，能聊得来，有自己的兴趣爱好。',
        '寻找三观一致、性格互补的另一半，一起成长。',
        '希望对方成熟稳重，有责任感，能给我安全感。',
        '希望对方温柔体贴，懂得照顾人，能一起分享生活点滴。',
        '寻找有共同语言的人，无论是兴趣还是价值观都能产生共鸣。',
        '希望对方积极向上，有自己的人生目标，我们互相支持。',
        '简单真诚就好，希望能在平凡的日子里发现不平凡的快乐。',
        '希望对方有幽默感，能让生活充满欢声笑语。'
    ]
};

/**
 * 生成随机用户画像并填充表单
 */
function generateRandomProfile() {
    const form = document.getElementById('profileForm');

    // 随机选择性别
    const gender = Math.random() > 0.5 ? 'male' : 'female';

    // 随机生成年龄（22-35岁）
    const age = Math.floor(Math.random() * 14) + 22;
    const currentYear = new Date().getFullYear();
    const birthYear = currentYear - age;
    const birthMonth = Math.floor(Math.random() * 12) + 1;

    // 随机选择其他字段
    const education = RANDOM_DATA_POOLS.educations[Math.floor(Math.random() * RANDOM_DATA_POOLS.educations.length)];
    const occupation = RANDOM_DATA_POOLS.occupations[Math.floor(Math.random() * RANDOM_DATA_POOLS.occupations.length)];
    const city = RANDOM_DATA_POOLS.cities[Math.floor(Math.random() * RANDOM_DATA_POOLS.cities.length)];

    // 随机选择3-5个兴趣爱好
    const interestCount = Math.floor(Math.random() * 3) + 3;
    const shuffledInterests = [...RANDOM_DATA_POOLS.interests].sort(() => Math.random() - 0.5);
    const interests = shuffledInterests.slice(0, interestCount).join('、');

    const selfDescription = RANDOM_DATA_POOLS.selfDescriptions[Math.floor(Math.random() * RANDOM_DATA_POOLS.selfDescriptions.length)];
    const idealType = RANDOM_DATA_POOLS.idealTypes[Math.floor(Math.random() * RANDOM_DATA_POOLS.idealTypes.length)];

    // 填充表单
    form.querySelector('[name="gender"]').value = gender;
    form.querySelector('[name="birth_year"]').value = birthYear;
    form.querySelector('[name="birth_month"]').value = birthMonth;
    form.querySelector('[name="education"]').value = education;
    form.querySelector('[name="occupation"]').value = occupation;
    form.querySelector('[name="interests"]').value = interests;
    form.querySelector('[name="city"]').value = city;
    form.querySelector('[name="self_description"]').value = selfDescription;
    form.querySelector('[name="ideal_type"]').value = idealType;

    // 触发年龄计算
    form.querySelector('[name="birth_year"]').dispatchEvent(new Event('input'));

    // 显示成功提示
    showToast('已生成随机用户画像，您可以修改后提交', 'success');
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profileForm');
    const birthYearInput = document.getElementById('birth_year');
    const birthMonthInput = document.getElementById('birth_month');
    const calculatedAgeEl = document.getElementById('calculatedAge');

    // 配置滑块处理
    const candidateCountSlider = document.getElementById('candidateCount');
    const maxRoundsSlider = document.getElementById('maxRounds');
    const candidateCountValue = document.getElementById('candidateCountValue');
    const maxRoundsValue = document.getElementById('maxRoundsValue');
    const summaryCandidates = document.getElementById('summaryCandidates');
    const summaryRounds = document.getElementById('summaryRounds');
    const summaryTotalRounds = document.getElementById('summaryTotalRounds');
    const summaryBadge = document.getElementById('summaryBadge');

    function updateSimulationSummary() {
        const candidateCount = parseInt(candidateCountSlider?.value || '10');
        const maxRounds = parseInt(maxRoundsSlider?.value || '20');
        const totalRounds = candidateCount * maxRounds;

        if (candidateCountValue) {
            candidateCountValue.textContent = String(candidateCount);
        }

        if (maxRoundsValue) {
            maxRoundsValue.textContent = String(maxRounds);
        }

        if (summaryCandidates) {
            summaryCandidates.textContent = `${candidateCount} 人`;
        }

        if (summaryRounds) {
            summaryRounds.textContent = `${maxRounds} 轮`;
        }

        if (summaryTotalRounds) {
            summaryTotalRounds.textContent = `${totalRounds} 轮`;
        }

        if (summaryBadge) {
            if (candidateCount === 1) {
                summaryBadge.textContent = '单人精聊';
            } else if (candidateCount <= 5) {
                summaryBadge.textContent = '轻量对比';
            } else if (candidateCount <= 10) {
                summaryBadge.textContent = '标准模式';
            } else {
                summaryBadge.textContent = '深度筛选';
            }
        }
    }

    if (candidateCountSlider && candidateCountValue) {
        candidateCountSlider.addEventListener('input', function() {
            updateSimulationSummary();
        });
    }

    if (maxRoundsSlider && maxRoundsValue) {
        maxRoundsSlider.addEventListener('input', function() {
            updateSimulationSummary();
        });
    }

    updateSimulationSummary();

    /**
     * 根据出生年月计算年龄
     */
    function calculateAge() {
        const birthYear = parseInt(birthYearInput.value);
        const birthMonth = parseInt(birthMonthInput.value);

        if (birthYear && birthMonth) {
            const today = new Date();
            const currentYear = today.getFullYear();
            const currentMonth = today.getMonth() + 1;

            let age = currentYear - birthYear;

            // 如果还没到生日月份，年龄减1
            if (currentMonth < birthMonth) {
                age--;
            }

            // 验证年龄范围
            if (age >= 18 && age <= 80) {
                calculatedAgeEl.textContent = age;
                calculatedAgeEl.classList.remove('age-invalid');
            } else if (age < 18) {
                calculatedAgeEl.textContent = age + ' (未满18岁)';
                calculatedAgeEl.classList.add('age-invalid');
            } else {
                calculatedAgeEl.textContent = age + ' (超出范围)';
                calculatedAgeEl.classList.add('age-invalid');
            }
        } else {
            calculatedAgeEl.textContent = '--';
        }
    }

    // 监听出生年月变化，自动计算年龄
    birthYearInput.addEventListener('input', calculateAge);
    birthMonthInput.addEventListener('change', calculateAge);

    // 随机生成画像按钮
    const randomProfileBtn = document.getElementById('randomProfileBtn');
    if (randomProfileBtn) {
        randomProfileBtn.addEventListener('click', generateRandomProfile);
    }

    // 表单提交处理
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // 禁用提交按钮
        setSubmitButtonState(true);

        // 收集表单数据
        const formData = new FormData(form);

        // 自动计算年龄
        const birthYear = parseInt(formData.get('birth_year'));
        const birthMonth = parseInt(formData.get('birth_month'));
        const today = new Date();
        const currentYear = today.getFullYear();
        const currentMonth = today.getMonth() + 1;
        let age = currentYear - birthYear;
        if (currentMonth < birthMonth) {
            age--;
        }

        // 直接从DOM获取配置参数（因为滑块在form外面）
        const candidateCountSlider = document.getElementById('candidateCount');
        const maxRoundsSlider = document.getElementById('maxRounds');

        const profile = {
            age: age,
            gender: formData.get('gender'),
            birth_year: birthYear,
            birth_month: birthMonth,
            education: formData.get('education'),
            occupation: formData.get('occupation'),
            interests: formData.get('interests'),
            city: formData.get('city'),
            self_description: formData.get('self_description') || null,
            ideal_type: formData.get('ideal_type') || null,
            candidate_count: parseInt(candidateCountSlider?.value || '10'),
            max_rounds: parseInt(maxRoundsSlider?.value || '20')
        };

        // 验证数据
        const validation = validateProfile(profile);
        if (!validation.valid) {
            showToast(validation.message, 'error');
            setSubmitButtonState(false);
            return;
        }

        try {
            // 提交资料到多候选人API
            const response = await submitMultiCandidateProfile(profile);

            if (response.success && response.session_id) {
                // 保存会话数据
                saveSessionData(response.session_id, {
                    sessionId: response.session_id,
                    candidates: response.candidates,
                    candidateCount: response.candidate_count,
                    maxRounds: response.max_rounds,
                    userProfile: profile
                });

                showToast(`成功生成 ${response.candidate_count} 位候选人！`, 'success');

                // 延迟跳转到候选人页面
                setTimeout(() => {
                    window.location.href = `/candidates.html?session_id=${response.session_id}`;
                }, 500);
            } else {
                showToast(response.message || '提交失败，请重试', 'error');
                setSubmitButtonState(false);
            }
        } catch (error) {
            console.error('Submit error:', error);
            showToast('网络错误，请检查连接后重试', 'error');
            setSubmitButtonState(false);
        }
    });

    // 实时验证兴趣格式
    const interestsInput = document.getElementById('interests');
    interestsInput.addEventListener('blur', function() {
        const value = this.value.trim();
        if (value && !value.includes('、') && value.includes(',')) {
            this.value = value.replace(/,/g, '、');
            showToast('已自动将逗号转换为顿号', 'success');
        }
    });
});

/**
 * 验证用户资料
 * @param {Object} profile - 用户资料
 * @returns {Object} 验证结果
 */
function validateProfile(profile) {
    // 年龄验证
    if (!profile.age || profile.age < 18 || profile.age > 80) {
        return { valid: false, message: '请输入有效的年龄（18-80岁）' };
    }

    // 性别验证
    if (!profile.gender || !['male', 'female'].includes(profile.gender)) {
        return { valid: false, message: '请选择性别' };
    }

    // 出生年份验证
    const currentYear = new Date().getFullYear();
    if (!profile.birth_year || profile.birth_year < currentYear - 80 || profile.birth_year > currentYear - 18) {
        return { valid: false, message: '请输入有效的出生年份' };
    }

    // 学历验证
    if (!profile.education) {
        return { valid: false, message: '请选择学历' };
    }

    // 职业验证
    if (!profile.occupation || profile.occupation.trim().length < 2) {
        return { valid: false, message: '请输入有效的职业' };
    }

    // 兴趣验证
    if (!profile.interests || profile.interests.trim().length < 2) {
        return { valid: false, message: '请输入至少一个兴趣爱好' };
    }

    // 城市验证
    if (!profile.city || profile.city.trim().length < 2) {
        return { valid: false, message: '请输入所在城市' };
    }

    // 自我描述长度验证
    if (profile.self_description && profile.self_description.length > 500) {
        return { valid: false, message: '自我描述不能超过500字' };
    }

    // 理想型长度验证
    if (profile.ideal_type && profile.ideal_type.length > 500) {
        return { valid: false, message: '理想型描述不能超过500字' };
    }

    return { valid: true };
}

/**
 * 设置提交按钮状态
 * @param {boolean} loading - 是否加载中
 */
function setSubmitButtonState(loading) {
    const btn = document.getElementById('submitBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    btn.disabled = loading;
    if (loading) {
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';
    } else {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}
