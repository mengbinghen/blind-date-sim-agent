/**
 * 候选人页面逻辑
 */

document.addEventListener('DOMContentLoaded', function() {
    // 从URL获取session_id
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');

    if (!sessionId) {
        showToast('会话ID不存在，请重新填写资料', 'error');
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
        return;
    }

    // 加载候选人数据
    loadCandidates(sessionId);

    // 开始模拟按钮事件
    const startSimulationBtn = document.getElementById('startSimulationBtn');
    if (startSimulationBtn) {
        startSimulationBtn.addEventListener('click', async function() {
            await handleStartSimulation(sessionId);
        });
    }
});

/**
 * 加载候选人数据
 */
async function loadCandidates(sessionId) {
    const loadingState = document.getElementById('loadingState');
    const candidatesGrid = document.getElementById('candidatesGrid');
    const startSimulationBtn = document.getElementById('startSimulationBtn');

    try {
        loadingState.style.display = 'block';
        candidatesGrid.style.display = 'none';

        // 从localStorage获取会话数据
        const sessionData = getSessionData(sessionId);

        if (!sessionData || !sessionData.candidates) {
            throw new Error('无法获取候选人数据');
        }

        const candidates = sessionData.candidates;

        // 更新候选人数显示
        const candidateCountEl = document.getElementById('candidateCount');
        if (candidateCountEl) {
            candidateCountEl.textContent = candidates.length;
        }

        // 渲染候选人卡片
        renderCandidates(candidates);

        loadingState.style.display = 'none';
        candidatesGrid.style.display = 'grid';
        startSimulationBtn.disabled = false;

    } catch (error) {
        console.error('Load candidates error:', error);
        showToast('加载候选人失败: ' + error.message, 'error');
        loadingState.innerHTML = `
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h2>加载失败</h2>
                <p>${error.message}</p>
                <div class="error-actions">
                    <a href="/" class="btn btn-primary">返回重新开始</a>
                </div>
            </div>
        `;
    }
}

/**
 * 渲染候选人卡片
 */
function renderCandidates(candidates) {
    const candidatesGrid = document.getElementById('candidatesGrid');

    candidatesGrid.innerHTML = candidates.map((candidate, index) => `
        <div class="candidate-card" data-index="${index}">
            <div class="candidate-avatar">${candidate.avatar}</div>
            <div class="candidate-info">
                <h3>${candidate.name}, ${candidate.age}岁</h3>
                <p class="candidate-city">${candidate.city}</p>
                <p class="candidate-occupation">${candidate.occupation}</p>
                <p class="candidate-interests">${candidate.interests}</p>
                <p class="candidate-personality">${candidate.personality}</p>
            </div>
        </div>
    `).join('');
}

/**
 * 开始模拟（处理函数）
 */
async function handleStartSimulation(sessionId) {
    const startSimulationBtn = document.getElementById('startSimulationBtn');
    const btnText = startSimulationBtn.querySelector('.btn-text');
    const btnLoading = startSimulationBtn.querySelector('.btn-loading');

    try {
        startSimulationBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'inline';

        console.log('Starting simulation for session:', sessionId);

        // 调用 API 函数启动模拟
        const response = await window.startSimulation(sessionId);

        console.log('Start simulation response:', response);

        if (response && response.success) {
            showToast('模拟已启动，正在跳转...', 'success');

            // 延迟跳转到模拟页面
            setTimeout(() => {
                window.location.href = `/simulation.html?session_id=${sessionId}`;
            }, 1000);
        } else {
            showToast(response?.message || '启动模拟失败', 'error');
            btnText.style.display = 'inline';
            btnLoading.style.display = 'none';
            startSimulationBtn.disabled = false;
        }

    } catch (error) {
        console.error('Start simulation error:', error);
        showToast('启动模拟失败: ' + error.message, 'error');
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        startSimulationBtn.disabled = false;
    }
}
