/**
 * 推荐页面逻辑
 */

function getCandidateByIdOrName(candidates, candidateId, candidateName) {
    if (!candidates || candidates.length === 0) {
        return null;
    }

    return (
        candidates.find(candidate => candidate.candidate_id === candidateId) ||
        candidates.find(candidate => candidate.name === candidateName) ||
        null
    );
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

    // 加载推荐结果
    loadRecommendation(sessionId);

    // 查看所有对话按钮
    const viewAllConversationsBtn = document.getElementById('viewAllConversationsBtn');
    if (viewAllConversationsBtn) {
        viewAllConversationsBtn.addEventListener('click', function() {
            window.location.href = `/simulation.html?session_id=${sessionId}`;
        });
    }
});

/**
 * 加载推荐结果
 */
async function loadRecommendation(sessionId) {
    const loadingState = document.getElementById('loadingState');
    const recommendationContent = document.getElementById('recommendationContent');

    try {
        // 首先尝试从localStorage获取会话数据
        const sessionData = getSessionData(sessionId);

        // 调用API获取推荐结果
        const response = await getRecommendation(sessionId);

        if (response.success && response.recommendation) {
            const rec = response.recommendation;

            // 隐藏加载状态
            loadingState.style.display = 'none';
            recommendationContent.style.display = 'block';

            // 渲染推荐结果
            renderBestMatch(rec, sessionData?.candidates);
            renderHighlights(rec.conversation_highlights);
            renderGrowthAreas(rec.potential_growth_areas);
            renderRankings(rec.all_candidates_ranking, sessionData?.candidates, rec.best_match_candidate_id);
        } else {
            throw new Error(response.message || '获取推荐失败');
        }

    } catch (error) {
        console.error('Load recommendation error:', error);
        showToast('加载推荐失败: ' + error.message, 'error');
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
 * 渲染最佳匹配
 */
function renderBestMatch(rec, candidates) {
    if (!rec) return;

    // 找到最佳匹配的候选人
    const bestCandidate = getCandidateByIdOrName(
        candidates,
        rec.best_match_candidate_id,
        rec.best_match_name
    );

    document.getElementById('bestMatchAvatar').textContent = bestCandidate?.avatar || '👩';
    document.getElementById('bestMatchName').textContent = bestCandidate?.name || rec.best_match_name;
    document.getElementById('bestMatchDetails').textContent = bestCandidate ? `${bestCandidate.age}岁 · ${bestCandidate.occupation}` : '';
    document.getElementById('bestMatchInterests').textContent = bestCandidate?.interests || '';

    // 渲染分数
    const scoreEl = document.getElementById('compatibilityScore');
    scoreEl.textContent = rec.compatibility_score;

    // 根据分数设置颜色等级
    scoreEl.className = 'score-circle';
    if (rec.compatibility_score >= 90) {
        scoreEl.classList.add('excellent');
    } else if (rec.compatibility_score >= 80) {
        scoreEl.classList.add('good');
    } else if (rec.compatibility_score >= 70) {
        scoreEl.classList.add('average');
    } else {
        scoreEl.classList.add('poor');
    }

    // 渲染推荐理由
    const reasoningList = document.getElementById('reasoningList');
    reasoningList.innerHTML = rec.reasoning.map(reason => `<li>${reason}</li>`).join('');
}

/**
 * 渲染对话高光时刻
 */
function renderHighlights(highlights) {
    const highlightsEl = document.getElementById('conversationHighlights');

    if (!highlights || highlights.length === 0) {
        highlightsEl.innerHTML = '<p class="empty-state">暂无高光时刻</p>';
        return;
    }

    highlightsEl.innerHTML = highlights.map(h => `
        <div class="highlight-item">
            <div class="highlight-round">第 ${h.round} 轮</div>
            <div class="highlight-exchange">${h.exchange}</div>
            <div class="highlight-why">💡 ${h.why}</div>
        </div>
    `).join('');
}

/**
 * 渲染成长空间
 */
function renderGrowthAreas(growthAreas) {
    const growthEl = document.getElementById('growthAreas');

    if (!growthAreas || growthAreas.length === 0) {
        growthEl.innerHTML = '<p class="empty-state">继续深入了解彼此吧！</p>';
        return;
    }

    growthEl.innerHTML = growthAreas.map(area => `<li>${area}</li>`).join('');
}

/**
 * 渲染所有候选人排名
 */
function renderRankings(rankings, candidates, bestMatchCandidateId) {
    const rankingsEl = document.getElementById('allRankings');

    if (!rankings || rankings.length === 0) {
        rankingsEl.innerHTML = '<p class="empty-state">暂无排名数据</p>';
        return;
    }

    rankingsEl.innerHTML = `
        <table class="ranking-table">
            <thead>
                <tr>
                    <th>排名</th>
                    <th>候选人</th>
                    <th>匹配分数</th>
                    <th>简评</th>
                </tr>
            </thead>
                <tbody>
                ${rankings.map((r, index) => {
                    const candidate = getCandidateByIdOrName(candidates, r.candidate_id, r.name);
                    const rankIcon = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}`;
                    const isBestMatch = r.candidate_id === bestMatchCandidateId;
                    return `
                        <tr class="${isBestMatch ? 'best-match-row' : ''}">
                            <td class="rank-cell">${rankIcon}</td>
                            <td class="candidate-cell">
                                <span class="avatar">${candidate?.avatar || '👤'}</span>
                                <span class="name">${r.name}</span>
                            </td>
                            <td class="score-cell">
                                <span class="score-badge ${getScoreClass(r.score)}">${r.score}</span>
                            </td>
                            <td class="brief-cell">${r.brief}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

/**
 * 获取分数对应的CSS类
 */
function getScoreClass(score) {
    if (score >= 90) return 'excellent';
    if (score >= 80) return 'good';
    if (score >= 70) return 'average';
    return 'poor';
}
