/**
 * 模拟页面逻辑
 */

// 全局状态变量（在模块顶部声明，确保所有函数都能访问）
let currentCandidateIndex = 0;
let candidates = [];
let candidateConversations = {};  // { candidate_id: { messages: [], currentRound: 0 } }
let simulationComplete = false;
let pollingInterval = null;  // 轮询定时器
let maxRounds = 20;  // 最大对话轮数，从会话数据中获取

function getCandidateKey(candidate) {
    return candidate?.candidate_id || candidate?.name || '';
}

document.addEventListener('DOMContentLoaded', function() {
    // 从URL获取session_id
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');

    if (!sessionId) {
        showToast('会话ID不存在', 'error');
        setTimeout(() => window.location.href = '/', 2000);
        return;
    }

    // 初始化
    initSimulation(sessionId);

    // 查看推荐按钮
    const viewRecommendationBtn = document.getElementById('viewRecommendationBtn');
    if (viewRecommendationBtn) {
        viewRecommendationBtn.addEventListener('click', function() {
            window.location.href = `/recommendation.html?session_id=${sessionId}`;
        });
    }
});

/**
 * 初始化模拟
 */
async function initSimulation(sessionId) {
    try {
        // 从localStorage获取会话数据
        const sessionData = getSessionData(sessionId);

        if (!sessionData || !sessionData.candidates) {
            throw new Error('无法获取会话数据');
        }

        candidates = sessionData.candidates;
        maxRounds = sessionData.maxRounds || 20;  // 从会话数据获取最大轮数

        console.log('Session maxRounds:', maxRounds);

        // 初始化对话状态
        candidates.forEach(c => {
            candidateConversations[getCandidateKey(c)] = {
                messages: [],
                currentRound: 0
            };
        });

        // 渲染候选人列表
        renderCandidateList(candidates);

        // 默认显示第一个候选人
        showCandidate(0);

        // 连接SSE流获取模拟进度
        connectSimulationStream(sessionId);

        // 启动轮询备用方案（每2秒检查一次）
        startPolling(sessionId);

    } catch (error) {
        console.error('Init simulation error:', error);
        showToast('初始化失败: ' + error.message, 'error');
    }
}

/**
 * 渲染候选人列表
 */
function renderCandidateList(candidates) {
    const candidateList = document.getElementById('candidateList');

    candidateList.innerHTML = candidates.map((candidate, index) => `
        <div class="candidate-tab" data-index="${index}" data-name="${candidate.name}" data-candidate-id="${candidate.candidate_id || ''}">
            <span class="tab-avatar">${candidate.avatar}</span>
            <span class="tab-name">${candidate.name}</span>
            <span class="tab-progress">0/${maxRounds}</span>
        </div>
    `).join('');

    // 添加点击事件
    candidateList.querySelectorAll('.candidate-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const index = parseInt(this.dataset.index);
            showCandidate(index);
        });
    });
}

/**
 * 显示指定候选人
 */
function showCandidate(index) {
    currentCandidateIndex = index;

    const tabs = document.querySelectorAll('.candidate-tab');
    tabs.forEach(t => t.classList.remove('active'));

    const activeTab = tabs[index];
    if (activeTab) {
        activeTab.classList.add('active');
    }

    const candidate = candidates[index];
    const conversation = candidateConversations[getCandidateKey(candidate)];

    // 更新头部信息
    document.getElementById('currentCandidateAvatar').textContent = candidate.avatar;
    document.getElementById('currentCandidateName').textContent = candidate.name;
    document.getElementById('currentCandidateDetails').textContent = `${candidate.age}岁 · ${candidate.city} · ${candidate.occupation}`;

    // 更新轮次显示
    document.getElementById('roundIndicator').textContent = `第 ${conversation.currentRound}/${maxRounds} 轮`;

    // 渲染对话消息
    renderMessages(conversation.messages);
}

/**
 * 渲染对话消息
 */
function renderMessages(messages) {
    const messagesContainer = document.getElementById('conversationMessages');

    if (!messages || messages.length === 0) {
        messagesContainer.innerHTML = `
            <div class="empty-state">
                <p>等待AI模拟开始...</p>
            </div>
        `;
        return;
    }

    messagesContainer.innerHTML = messages.map(msg => {
        const isUser = msg.role === 'user';
        return `
            <div class="message ${isUser ? 'user' : 'assistant'}">
                <div class="message-bubble">
                    ${msg.content}
                </div>
            </div>
        `;
    }).join('');

    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * 连接SSE流获取模拟进度
 */
function connectSimulationStream(sessionId) {
    const streamUrl = `${getApiBaseUrl()}/api/simulation/stream?session_id=${sessionId}`;
    console.log('Connecting to SSE stream:', streamUrl);

    const eventSource = new EventSource(streamUrl);

    // 监听连接打开
    eventSource.onopen = function() {
        console.log('SSE connection opened');
    };

    eventSource.addEventListener('round', function(e) {
        console.log('SSE round event:', e.data);
        const data = JSON.parse(e.data);
        handleRoundUpdate(data);
    });

    eventSource.addEventListener('complete', function(e) {
        console.log('SSE complete event:', e.data);
        const data = JSON.parse(e.data);
        handleSimulationComplete(data);
    });

    eventSource.addEventListener('error', function(e) {
        console.error('SSE error:', e);
        console.log('EventSource readyState:', eventSource.readyState);
        eventSource.close();
    });

    // 保存EventSource引用以便后续关闭
    window.simulationEventSource = eventSource;
}

/**
 * 处理轮次更新
 */
function handleRoundUpdate(data) {
    console.log('handleRoundUpdate called with:', data);
    const { candidate_id, round, messages } = data;

    // 通过 candidate_id 找到对应的候选人
    let candidateIndex = -1;
    let candidate = null;

    for (let i = 0; i < candidates.length; i++) {
        if (candidates[i].candidate_id === candidate_id) {
            candidateIndex = i;
            candidate = candidates[i];
            break;
        }
    }

    // 如果找不到，记录日志并跳过
    if (candidateIndex === -1) {
        console.log('Candidate not found for candidate_id:', candidate_id);
        console.log('Available candidates:', candidates.map(c => ({ name: c.name, candidate_id: c.candidate_id })));
        return;
    }

    const conversation = candidateConversations[getCandidateKey(candidate)];

    // 添加新消息 - 后端消息有 role 和 content 字段
    messages.forEach(msg => {
        conversation.messages.push({
            role: msg.role,
            content: msg.content
        });
    });

    conversation.currentRound = round;

    console.log(`Updated ${candidate.name}: round ${round}, messages ${conversation.messages.length}`);

    // 更新进度显示
    const tab = document.querySelector(`.candidate-tab[data-index="${candidateIndex}"]`);
    if (tab) {
        tab.querySelector('.tab-progress').textContent = `${round}/${maxRounds}`;
    }

    // 更新总体进度
    updateOverallProgress();

    // 如果当前显示的是这个候选人，刷新消息显示
    const activeTab = document.querySelector('.candidate-tab.active');
    if (activeTab && parseInt(activeTab.dataset.index) === candidateIndex) {
        showCandidate(candidateIndex);
    }
}

/**
 * 处理模拟完成
 */
function handleSimulationComplete(data) {
    if (data?.all_candidates) {
        data.all_candidates.forEach(candidateData => {
            const candidate = candidates.find(c => c.candidate_id === candidateData.candidate_id);
            if (!candidate) {
                return;
            }

            const conversation = candidateConversations[getCandidateKey(candidate)];
            if (conversation && candidateData.rounds > conversation.currentRound) {
                handleRoundUpdate({
                    candidate_id: candidateData.candidate_id,
                    round: candidateData.rounds,
                    messages: candidateData.last_messages || []
                });
            }
        });
    }

    simulationComplete = true;

    // 停止轮询
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }

    // 关闭SSE连接
    if (window.simulationEventSource) {
        window.simulationEventSource.close();
    }

    // 隐藏加载状态
    const statusEl = document.getElementById('simulationStatus');
    if (statusEl) {
        statusEl.style.display = 'none';
    }

    // 启用查看推荐按钮
    const viewRecommendationBtn = document.getElementById('viewRecommendationBtn');
    if (viewRecommendationBtn) {
        viewRecommendationBtn.disabled = false;
    }

    showToast('模拟已完成，可以查看推荐结果', 'success');
}

/**
 * 更新总体进度
 */
function updateOverallProgress() {
    const totalRounds = candidates.reduce((sum, c) => {
        const conv = candidateConversations[getCandidateKey(c)];
        return sum + conv.currentRound;
    }, 0);

    const maxTotal = candidates.length * maxRounds;

    const progressText = document.getElementById('overallProgressText');
    if (progressText) {
        progressText.textContent = `${totalRounds}/${maxTotal} 轮`;
    }
}

/**
 * 启动轮询备用方案
 */
function startPolling(sessionId) {
    // 每2秒轮询一次状态
    pollingInterval = setInterval(async () => {
        try {
            const status = await getSimulationStatus(sessionId);
            console.log('Polling status:', status);

            if (status && status.candidates_status) {
                // 更新每个候选人的进度
                status.candidates_status.forEach(c => {
                    const candidate = candidates.find(cand => cand.candidate_id === c.candidate_id);
                    if (candidate) {
                        const conv = candidateConversations[getCandidateKey(candidate)];
                        if (conv && c.current_round > conv.currentRound) {
                            // 轮次有更新，刷新显示
                            conv.currentRound = c.current_round;
                            const tab = document.querySelector(`.candidate-tab[data-candidate-id="${candidate.candidate_id}"]`);
                            if (tab) {
                                tab.querySelector('.tab-progress').textContent =
                                    `${c.current_round}/${maxRounds}`;
                            }

                            // 如果当前显示的是这个候选人，刷新显示
                            const activeTab = document.querySelector('.candidate-tab.active');
                            if (activeTab && activeTab.dataset.candidateId === candidate.candidate_id) {
                                showCandidate(candidates.indexOf(candidate));
                            }
                        }
                    }
                });

                updateOverallProgress();

                // 检查是否完成
                if (status.status === 'completed' && !simulationComplete) {
                    handleSimulationComplete({ all_candidates: status.candidates_status });
                }
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 2000);
}
