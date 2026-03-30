/**
 * API调用封装
 * 统一处理前后端API交互
 */

console.log('api.js loaded successfully');

const SCENARIO_META = {
    first_chat: {
        label: '初识聊天',
        description: '从第一印象聊到共同兴趣，再自然试探是否愿意继续接触。'
    },
    weekend_plan: {
        label: '周末约会计划',
        description: '围绕线下安排和偏好磨合，观察彼此的节奏感与配合度。'
    },
    future_probe: {
        label: '未来关系试探',
        description: '聊到城市、工作与关系节奏，测试长期相处潜力。'
    }
};

// 动态获取 API 基础 URL
// 如果页面从静态服务器访问（如 file:// 或其他端口），则使用默认地址
// 否则使用当前页面的协议和主机
function getApiBaseUrl() {
    // 检查是否在 localhost/127.0.0.1 环境
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // 如果当前端口是 8000，说明从后端直接访问，不需要设置基础 URL
        if (window.location.port === '8000') {
            return '';
        }
        // 否则返回完整的后端地址
        return 'http://localhost:8000';
    }
    // 生产环境或其他环境，使用相对路径（假设前后端同域）
    return '';
}

const API_BASE_URL = getApiBaseUrl();

function getScenarioMeta(mode) {
    return SCENARIO_META[mode] || SCENARIO_META.first_chat;
}

/**
 * 通用API调用函数
 * @param {string} endpoint - API端点
 * @param {Object} data - 请求数据
 * @param {string} method - HTTP方法
 * @returns {Promise<Object>} 响应数据
 */
async function apiCall(endpoint, data = null, method = 'POST') {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const url = API_BASE_URL + endpoint;
        console.log(`API Call: ${method} ${url}`, data);

        const response = await fetch(url, options);

        console.log(`API Response status: ${response.status} ${response.statusText}`);

        const result = await response.json();
        console.log(`API Response data:`, result);

        if (!response.ok) {
            throw new Error(result.detail || result.message || '请求失败');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        console.error('Request URL:', API_BASE_URL + endpoint);
        console.error('Request data:', data);
        throw error;
    }
}

/**
 * 提交用户资料
 * @param {Object} profile - 用户资料
 * @returns {Promise<Object>} 响应数据
 */
async function submitProfile(profile) {
    return apiCall('/api/profile', profile);
}

/**
 * 提交用户资料（多候选人模式）
 * @param {Object} profile - 用户资料
 * @returns {Promise<Object>} 响应数据
 */
async function submitMultiCandidateProfile(profile) {
    return apiCall('/api/profile/multi-candidate', profile);
}

/**
 * 发送聊天消息
 * @param {string} sessionId - 会话ID
 * @param {string} message - 消息内容
 * @returns {Promise<Object>} 响应数据
 */
async function sendMessage(sessionId, message) {
    return apiCall('/api/chat', { session_id: sessionId, message });
}

/**
 * 开始对话，获取开场白
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 响应数据
 */
async function startChat(sessionId) {
    return apiCall('/api/chat/start', { session_id: sessionId });
}

/**
 * 结束对话，生成评价
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 响应数据
 */
async function endChat(sessionId) {
    return apiCall('/api/chat/end', { session_id: sessionId });
}

/**
 * 获取会话状态
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 响应数据
 */
async function getSessionStatus(sessionId) {
    return apiCall(`/api/chat/session/${sessionId}`, null, 'GET');
}

/**
 * 获取评价结果
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 响应数据
 */
async function getEvaluation(sessionId) {
    return apiCall(`/api/evaluation?session_id=${sessionId}`, null, 'GET');
}

/**
 * 启动模拟
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 响应数据
 */
async function startSimulation(sessionId) {
    console.log('startSimulation called with sessionId:', sessionId);
    const result = await apiCall('/api/simulation/start', { session_id: sessionId });
    console.log('startSimulation result:', result);
    return result;
}

/**
 * 获取模拟状态
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 响应数据
 */
async function getSimulationStatus(sessionId) {
    return apiCall(`/api/simulation/status?session_id=${sessionId}`, null, 'GET');
}

/**
 * 获取推荐结果
 * @param {string} sessionId - 会话ID
 * @returns {Promise<Object>} 响应数据
 */
async function getRecommendation(sessionId) {
    return apiCall(`/api/evaluation/recommendation?session_id=${sessionId}`, null, 'GET');
}

/**
 * 显示Toast提示
 * @param {string} message - 提示消息
 * @param {string} type - 类型：success, error
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * 存储会话数据到localStorage
 * @param {string} sessionId - 会话ID
 * @param {Object} data - 会话数据
 */
function saveSessionData(sessionId, data) {
    try {
        localStorage.setItem(`session_${sessionId}`, JSON.stringify(data));
    } catch (e) {
        console.error('Failed to save session data:', e);
    }
}

/**
 * 从localStorage获取会话数据
 * @param {string} sessionId - 会话ID
 * @returns {Object|null} 会话数据
 */
function getSessionData(sessionId) {
    try {
        const data = localStorage.getItem(`session_${sessionId}`);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Failed to get session data:', e);
        return null;
    }
}

/**
 * 清除会话数据
 * @param {string} sessionId - 会话ID
 */
function clearSessionData(sessionId) {
    try {
        localStorage.removeItem(`session_${sessionId}`);
    } catch (e) {
        console.error('Failed to clear session data:', e);
    }
}

/**
 * 格式化时间
 * @param {Date} date - 日期对象
 * @returns {string} 格式化后的时间字符串
 */
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

// 暴露函数到全局作用域，确保可以跨文件调用
window.getApiBaseUrl = getApiBaseUrl;
window.getScenarioMeta = getScenarioMeta;
window.submitMultiCandidateProfile = submitMultiCandidateProfile;
window.startSimulation = startSimulation;
window.getSimulationStatus = getSimulationStatus;
window.getRecommendation = getRecommendation;

console.log('api.js functions exposed to window:', {
    submitMultiCandidateProfile: typeof window.submitMultiCandidateProfile,
    startSimulation: typeof window.startSimulation,
    getSimulationStatus: typeof window.getSimulationStatus,
    getRecommendation: typeof window.getRecommendation
});
