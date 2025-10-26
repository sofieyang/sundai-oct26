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
      startSimulation(formData);
    });
    const closeBtn = qs('#panelClose'); const doneBtn = qs('#panelDone'); const backdrop = qs('#panelBackdrop');
    if (closeBtn) closeBtn.addEventListener('click', closePanel);
    if (doneBtn) doneBtn.addEventListener('click', closePanel);
    if (backdrop) backdrop.addEventListener('click', closePanel);
  }

  document.addEventListener('DOMContentLoaded', onTryPage);
})();


