// Migrate logic from legacy app.js; page-aware init
(function initTryPage() {
  function qs(sel, root = document) { return root.querySelector(sel); }
  function nowTime() {
    const d = new Date();
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  function validateForm(form) {
    const urlEl = qs('#companyUrl', form);
    const drugEl = qs('#drugName', form);
    let ok = true;
    if (!urlEl.checkValidity()) {
      qs('[data-for="companyUrl"]', form).textContent = 'Please enter a valid URL.';
      urlEl.classList.add('invalid');
      ok = false;
    } else {
      qs('[data-for="companyUrl"]', form).textContent = '';
      urlEl.classList.remove('invalid');
    }
    if (!drugEl.value.trim()) {
      qs('[data-for="drugName"]', form).textContent = 'Drug / product name is required.';
      drugEl.classList.add('invalid');
      ok = false;
    } else {
      qs('[data-for="drugName"]', form).textContent = '';
      drugEl.classList.remove('invalid');
    }
    return ok;
  }

  function openPanel() {
    const panel = qs('#activityPanel');
    const backdrop = qs('#panelBackdrop');
    if (!panel) return;
    panel.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');
    if (backdrop) backdrop.hidden = false;
  }
  function closePanel() {
    const panel = qs('#activityPanel');
    const backdrop = qs('#panelBackdrop');
    if (!panel) return;
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
    if (backdrop) backdrop.hidden = true;
  }
  function appendLog(text, level = 'ok') {
    const logs = qs('#activityLogs');
    if (!logs) return;
    const li = document.createElement('li');
    const dot = document.createElement('span');
    dot.className = `dot ${level}`;
    const content = document.createElement('div');
    const p = document.createElement('p');
    p.textContent = text;
    const t = document.createElement('span');
    t.className = 'time';
    t.textContent = nowTime();
    content.appendChild(p);
    content.appendChild(t);
    li.appendChild(dot);
    li.appendChild(content);
    logs.appendChild(li);
    logs.scrollTop = logs.scrollHeight;
  }
  function setSubtitle(text) { const el = qs('#panel-subtitle'); if (el) el.textContent = text; }
  function setProgress(percent) { const bar = qs('#progressBar'); if (bar) bar.style.width = `${percent}%`; }

  function showBriefModal(markdownContent) {
    const modal = qs('#briefModal');
    const backdrop = qs('#briefBackdrop');
    const content = qs('#briefContent');
    if (!modal || !content) return;

    // Convert markdown to HTML or display as formatted text
    // For now, we'll use a pre-formatted display with basic markdown rendering
    content.innerHTML = `<pre class="markdown-content">${escapeHtml(markdownContent)}</pre>`;

    modal.hidden = false;
    if (backdrop) backdrop.hidden = false;

    // Store markdown for download
    modal.dataset.markdown = markdownContent;
  }

  function closeBriefModal() {
    const modal = qs('#briefModal');
    const backdrop = qs('#briefBackdrop');
    if (modal) modal.hidden = true;
    if (backdrop) backdrop.hidden = true;
  }

  function downloadMarkdown() {
    const modal = qs('#briefModal');
    if (!modal || !modal.dataset.markdown) return;

    const blob = new Blob([modal.dataset.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `marketing-brief-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
  async function startRun(formData) {
    appendLog('Sending RFP to server…', 'ok');
    setSubtitle('Submitting');
    setProgress(5);
    try {
      const res = await fetch('/api/rfp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          companyUrl: formData.companyUrl,
          drugName: formData.drugName,
          trialsPapers: formData.trialsPapers,
          doctorTypes: formData.doctorTypes,
        })
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      setSubtitle('Agents running');
      setProgress(25);
      const data = await res.json();
      appendLog('Pipeline completed.', 'ok');
      setProgress(90);
      if (data.deploy_path) {
        appendLog(`Deployed artifact at: ${data.deploy_path}`, 'ok');
      }
      setProgress(100);
      setSubtitle('Complete');

      // Extract and display the marketing brief
      if (data.result && data.result.scope_report) {
        appendLog('Marketing brief ready. Opening preview…', 'ok');
        showBriefModal(data.result.scope_report);
      } else {
        appendLog('Warning: No marketing brief found in response', 'warn');
      }

      const doneBtn = qs('#panelDone'); if (doneBtn) doneBtn.hidden = false;
    } catch (err) {
      console.error(err);
      appendLog(`Error: ${err.message || err}`, 'err');
      setSubtitle('Error');
      setProgress(100);
      const doneBtn = qs('#panelDone'); if (doneBtn) doneBtn.hidden = false;
    }
  }

  function startSimulation(formData) {
    const steps = [
      { text: `Crawling ${formData.companyUrl} for product and pipeline pages…`, delay: 900 },
      { text: 'Resolving internal links and product detail pages…', delay: 900 },
      { text: 'Scraping content and extracting medical claims…', delay: 1000 },
      { text: 'Checking content against FDA/OPDP guidance…', delay: 1000 },
      { text: `Drafting outreach tailored to ${formData.drugName} and audience…`, delay: 1000 },
      { text: 'Packaging proposal with compliance notes and email drafts…', delay: 900 }
    ];
    let idx = 0; const total = steps.length;
    appendLog('Agents initialized. Starting workflow…', 'ok');
    setSubtitle('Agents running');
    function next() {
      if (idx >= total) { setProgress(100); appendLog('Proposal ready (demo). No data was sent to a server.', 'ok'); setSubtitle('Complete'); const doneBtn = qs('#panelDone'); if (doneBtn) doneBtn.hidden = false; return; }
      const step = steps[idx]; const pct = Math.round(((idx) / total) * 100); setProgress(Math.min(95, pct)); appendLog(step.text, 'ok'); idx += 1; setTimeout(next, step.delay);
    }
    setTimeout(next, 350);
  }

  function onTryPage() {
    const form = qs('#proposal-form');
    if (!form) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!validateForm(form)) { form.reportValidity(); return; }
      const formData = {
        companyUrl: form.querySelector('#companyUrl').value.trim(),
        drugName: form.querySelector('#drugName').value.trim(),
        trialsPapers: form.querySelector('#trialsPapers').value.trim(),
        doctorTypes: form.querySelector('#doctorTypes').value.trim()
      };
      openPanel();
      // Prefer server mode if API available, else fallback to simulation
      const apiBase = '';
      fetch(apiBase + '/api/health', { method: 'GET' })
        .then(() => startRun(formData))
        .catch(() => startSimulation(formData));
    });
    const closeBtn = qs('#panelClose'); const doneBtn = qs('#panelDone'); const backdrop = qs('#panelBackdrop');
    if (closeBtn) closeBtn.addEventListener('click', closePanel);
    if (doneBtn) doneBtn.addEventListener('click', closePanel);
    if (backdrop) backdrop.addEventListener('click', closePanel);

    // Brief modal event listeners
    const briefModalClose = qs('#briefModalClose');
    const closeBriefBtn = qs('#closeBrief');
    const downloadBriefBtn = qs('#downloadBrief');
    const briefBackdrop = qs('#briefBackdrop');

    if (briefModalClose) briefModalClose.addEventListener('click', closeBriefModal);
    if (closeBriefBtn) closeBriefBtn.addEventListener('click', closeBriefModal);
    if (downloadBriefBtn) downloadBriefBtn.addEventListener('click', downloadMarkdown);
    if (briefBackdrop) briefBackdrop.addEventListener('click', closeBriefModal);
  }

  document.addEventListener('DOMContentLoaded', onTryPage);
})();


