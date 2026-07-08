// CP-AH WebUI frontend logic
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const goalInput = document.getElementById('goalInput');
const askBtn = document.getElementById('askBtn');
const resultArea = document.getElementById('resultArea');

let sessionId = null;
let uploadedFile = null;

// Upload: click + drag-drop
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = 'var(--accent)';
});
uploadArea.addEventListener('dragleave', () => {
  uploadArea.style.borderColor = 'var(--border)';
});
uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = 'var(--border)';
  if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

function handleFile(file) {
  uploadedFile = file;
  fileInfo.textContent = `✓ ${file.name} (${file.size} bytes)`;
  askBtn.disabled = false;
}

// Ask: upload + run
askBtn.addEventListener('click', async () => {
  if (!uploadedFile) return;
  askBtn.disabled = true;
  askBtn.textContent = '思考中...';
  resultArea.innerHTML = '<p class="placeholder">Agent 正在分析...</p>';

  try {
    // Step 1: upload
    const formData = new FormData();
    formData.append('file', uploadedFile);
    const uploadResp = await fetch('/api/upload', { method: 'POST', body: formData });
    const uploadData = await uploadResp.json();
    sessionId = uploadData.session_id;

    // Step 2: ask
    const goal = goalInput.value || 'explain this code';
    const askResp = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, goal: goal }),
    });
    const data = await askResp.json();

    displayResult(data);
  } catch (err) {
    resultArea.innerHTML = `<p class="placeholder" style="color:var(--danger)">错误: ${err.message}</p>`;
  } finally {
    askBtn.disabled = false;
    askBtn.textContent = '提交';
  }
});

function displayResult(data) {
  let html = '';

  // Mock warning
  if (data.is_mock) {
    html += `<div class="result-step" style="border-left-color: var(--warning)">
      <div class="role" style="color: var(--warning)">⚠ Mock 模式</div>
      <div class="content">未配置 API key，使用 MockLLM。Agent 会读文件 + 跑编译反馈，但不会用 LLM 分析代码。运行 <code>cpa-harness setup</code> 配置 key 后可获得真 LLM 分析。</div>
    </div>`;
  }

  // History steps
  if (data.history && data.history.length > 0) {
    for (const step of data.history) {
      const role = step.role || 'unknown';
      let content = '';
      let blocked = false;
      if (step.text) content = step.text;
      if (step.observation) {
        content = step.observation;
        if (content.includes('BLOCKED')) blocked = true;
      }
      const roleLabel = role === 'assistant' ? '🤖 Agent' : '📋 工具结果';
      html += `<div class="result-step${blocked ? ' result-blocked' : ''}">
        <div class="role">${roleLabel}</div>
        <div class="content">${escapeHtml(content)}</div>
      </div>`;
    }
  }

  // Summary
  html += `<div class="result-summary">
    <div class="answer">${escapeHtml(data.answer || '(no answer)')}</div>
    <div class="meta">Steps: ${data.steps} · Exit: ${data.exit_reason}</div>
  </div>`;

  resultArea.innerHTML = html;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// HITL WebSocket (placeholder for future integration)
function connectHITL(sessionId) {
  const ws = new WebSocket(`ws://${location.host}/ws/hitl`);
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === 'approval_request') {
      document.getElementById('hitlReason').textContent = msg.reason;
      document.getElementById('diffView').textContent = msg.diff || '';
      document.getElementById('hitlModal').hidden = false;
    }
  };
  return ws;
}

// HITL buttons
document.getElementById('approveBtn').addEventListener('click', () => {
  // ws.send(JSON.stringify({type: 'approve'}))
  document.getElementById('hitlModal').hidden = true;
});
document.getElementById('rejectBtn').addEventListener('click', () => {
  document.getElementById('hitlModal').hidden = true;
});
document.getElementById('editBtn').addEventListener('click', () => {
  // TODO: open edit mode
});
