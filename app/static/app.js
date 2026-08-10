let soundEnabled = true;
let notifEnabled = true;
let chartDashboard = null;
let chartAnalytics = null;
let lastModeCode = null;
let allEvents = [];
let latestSnapshot = null;
let activeTab = 'dashboard';

let globalAudioCtx = null;

function getAudioContext() {
  if (!globalAudioCtx) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (AudioCtx) {
      globalAudioCtx = new AudioCtx();
    }
  }
  if (globalAudioCtx && globalAudioCtx.state === 'suspended') {
    globalAudioCtx.resume().catch(() => {});
  }
  return globalAudioCtx;
}

// Unlock Web Audio API on first user interaction anywhere on the page
document.addEventListener('pointerdown', () => {
  getAudioContext();
}, { once: true });

function playAlertSound(type) {
  if (!soundEnabled) return;
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    
    if (ctx.state === 'suspended') {
      ctx.resume().then(() => playAlertSoundImpl(ctx, type)).catch(() => {});
    } else {
      playAlertSoundImpl(ctx, type);
    }
  } catch (e) {
    console.error("Audio play error:", e);
  }
}

function playAlertSoundImpl(ctx, type) {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain);
  gain.connect(ctx.destination);

  if (type === 'battery') {
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    osc.start();
    osc.stop(ctx.currentTime + 0.3);
  } else if (type === 'avr') {
    osc.type = 'sine';
    osc.frequency.setValueAtTime(523.25, ctx.currentTime);
    gain.gain.setValueAtTime(0.1, ctx.currentTime);
    osc.start();
    osc.stop(ctx.currentTime + 0.15);
  } else if (type === 'online') {
    osc.type = 'sine';
    osc.frequency.setValueAtTime(659.25, ctx.currentTime);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    osc.start();
    osc.stop(ctx.currentTime + 0.2);
  } else if (type === 'test') {
    osc.type = 'sine';
    osc.frequency.setValueAtTime(523.25, ctx.currentTime);
    gain.gain.setValueAtTime(0.1, ctx.currentTime);
    osc.start();
    osc.stop(ctx.currentTime + 0.15);
  }
}

function initLanguage() {
  const savedLang = localStorage.getItem('ups_language') || 'en';
  applyLanguage(savedLang);

  const langBtn = document.getElementById('langToggle');
  if (langBtn) {
    langBtn.addEventListener('click', () => {
      const cur = getLanguage();
      const next = cur === 'en' ? 'ru' : 'en';
      applyLanguage(next);
      localStorage.setItem('ups_language', next);
      saveSettingPatch({ language: next });
    });
  }
}

function applyLanguage(lang) {
  setLanguage(lang);
  document.documentElement.lang = lang;

  // 1. Update text of elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (key) {
      el.textContent = t(key);
    }
  });

  // 2. Update placeholders with data-i18n-ph
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.getAttribute('data-i18n-ph');
    if (key) {
      el.placeholder = t(key);
    }
  });

  // 3. Document title
  document.title = t('app_title');

  // 4. Lang toggle button label
  setText('langText', lang === 'en' ? 'EN 🇬🇧' : 'RU 🇷🇺');

  // 5. Update header current view title
  const viewTitle = document.getElementById('currentViewTitle');
  if (viewTitle) {
    const titles = {
      dashboard: 'view_dashboard',
      flow: 'view_flow',
      analytics: 'view_analytics',
      events: 'view_events',
      settings: 'view_settings'
    };
    if (titles[activeTab]) {
      viewTitle.textContent = t(titles[activeTab]);
    }
  }

  // 6. Update chart dataset labels
  if (chartDashboard) {
    chartDashboard.data.datasets[0].label = `${t('chart_in_v')}`;
    chartDashboard.data.datasets[1].label = `${t('chart_out_v')}`;
    chartDashboard.update('none');
  }
  if (chartAnalytics) {
    chartAnalytics.data.datasets[0].label = `${t('chart_in_v')}`;
    chartAnalytics.data.datasets[1].label = `${t('chart_out_v')}`;
    chartAnalytics.update('none');
  }

  // 7. Update button states & latest telemetry UI
  updateSoundButtons(soundEnabled);
  updateNotifButtons(notifEnabled);
  if (latestSnapshot) {
    updateUI(latestSnapshot);
  } else {
    renderEventsTable(allEvents);
  }
}

function toggleNotificationPermission() {
  const isEnabled = !!lastSyncedSettings.toast_notif_enabled;
  const nextVal = !isEnabled;
  notifEnabled = nextVal;
  updateNotifButtons(nextVal);
  saveSettingPatch({ toast_notif_enabled: nextVal });

  if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
    try {
      Notification.requestPermission().catch(() => {});
    } catch (e) {}
  }
}

function updateSoundButtons(enabled) {
  const btn1 = document.getElementById('soundToggle');
  const btn2 = document.getElementById('settingsSoundBtn');
  const txt = enabled ? t('sound_toggle') : t('sound_off');
  if (btn1) {
    setText('soundText', txt);
    btn1.classList.toggle('active', enabled);
  }
  if (btn2) {
    btn2.innerHTML = enabled 
      ? `<span class="status-dot-sm" style="background:#10b981;"></span> ${t('btn_enabled')}` 
      : `<span class="status-dot-sm" style="background:#64748b;"></span> ${t('btn_disabled')}`;
    btn2.classList.toggle('active', enabled);
  }
}

function updateNotifButtons(enabled) {
  notifEnabled = !!enabled;
  const btn1 = document.getElementById('notifToggle');
  const btn2 = document.getElementById('settingsToastBtn');
  const txt = enabled ? t('notif_toggle') : t('notif_off');
  if (btn1) {
    setText('notifText', txt);
    btn1.classList.toggle('active', enabled);
  }
  if (btn2) {
    btn2.innerHTML = enabled 
      ? `<span class="status-dot-sm" style="background:#10b981;"></span> ${t('btn_enabled')}` 
      : `<span class="status-dot-sm" style="background:#64748b;"></span> ${t('btn_disabled')}`;
    btn2.classList.toggle('active', enabled);
  }
}

function showNotification(title, body) {
  if (notifEnabled && "Notification" in window && Notification.permission === "granted") {
    try { new Notification(title, { body }); } catch (e) { console.error(e); }
  }
}

function createChartConfig() {
  return {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: t('chart_in_v'),
          data: [],
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.15)',
          fill: true,
          tension: 0.3,
          borderWidth: 2.5,
          pointRadius: 1
        },
        {
          label: t('chart_out_v'),
          data: [],
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          fill: true,
          tension: 0.3,
          borderWidth: 2.5,
          pointRadius: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', font: { size: 10 }, maxTicksLimit: 8 }
        },
        y: {
          min: 140,
          max: 270,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#94a3b8', font: { size: 11 } }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#e2e8f0', font: { size: 12, family: 'Inter' } }
        }
      }
    }
  };
}

function initCharts() {
  const canvas1 = document.getElementById('voltageChart');
  const canvas2 = document.getElementById('voltageChartAnalytics');
  if (typeof Chart === 'undefined') return;

  if (canvas1) {
    chartDashboard = new Chart(canvas1.getContext('2d'), createChartConfig());
  }
  if (canvas2) {
    chartAnalytics = new Chart(canvas2.getContext('2d'), createChartConfig());
  }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function formatModeText(modeStr) {
  if (!modeStr) return '—';
  const u = String(modeStr).toUpperCase();
  if (u.includes('BATTERY') || u.includes('БАТАРЕ')) {
    return t('mode_battery');
  }
  if (u.includes('BOOST') || u.includes('ПОДЪЕМ')) {
    return t('mode_avr_boost');
  }
  if (u.includes('TRIM') || u.includes('ПОНИЖЕНИЕ')) {
    return t('mode_avr_trim');
  }
  if (u.includes('AVR') || u.includes('СТАБИЛИЗАЦИЯ')) {
    return t('mode_avr');
  }
  if (u.includes('ONLINE') || u.includes('СЕТЬ') || u.includes('НОРМ')) {
    return t('mode_online');
  }
  if (u.includes('DISCONNECT') || u.includes('СВЯЗ')) {
    return t('mode_disconnected');
  }
  return modeStr;
}

function renderEventsTable(events) {
  allEvents = events || [];

  // 1. Dashboard preview table (top 5 items)
  const tbody = document.getElementById('eventsTbody');
  if (tbody) {
    if (allEvents.length === 0) {
      tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;color:var(--text-muted);padding:1.5rem;">${t('tbl_empty')}</td></tr>`;
    } else {
      const top5 = allEvents.slice(0, 5);
      tbody.innerHTML = top5.map(ev => {
        let tagClass = 'tag-green';
        const modeU = String(ev.mode || '').toUpperCase();
        if (modeU.includes('БАТАРЕ') || modeU.includes('BATTERY')) tagClass = 'tag-amber';
        else if (modeU.includes('AVR')) tagClass = 'tag-blue';
        const modeLabel = formatModeText(ev.mode);
        return `<tr>
          <td>${ev.time_short || (ev.timestamp && String(ev.timestamp).split(' ')[1]) || ''}</td>
          <td><span class="tag ${tagClass}">${modeLabel}</span></td>
          <td style="font-weight:600">${ev.in_v} V</td>
        </tr>`;
      }).join('');
    }
  }

  // 2. Tab Events table
  renderTabEvents();

  // 3. Modal Events table
  renderModalEvents();
}

function renderTabEvents() {
  const tabTbody = document.getElementById('tabEventsTbody');
  const searchInput = document.getElementById('tabEventsSearch');
  const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

  if (!tabTbody) return;

  const filtered = allEvents.filter(ev => {
    if (!query) return true;
    const ts = String(ev.timestamp || '').toLowerCase();
    const mode = String(ev.mode || '').toLowerCase();
    return ts.includes(query) || mode.includes(query);
  });

  if (filtered.length === 0) {
    tabTbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:2rem;">${t('tbl_not_found')}</td></tr>`;
  } else {
    tabTbody.innerHTML = filtered.map(ev => {
      let tagClass = 'tag-green';
      const modeU = String(ev.mode || '').toUpperCase();
      if (modeU.includes('БАТАРЕ') || modeU.includes('BATTERY')) tagClass = 'tag-amber';
      else if (modeU.includes('AVR')) tagClass = 'tag-blue';
      const modeLabel = formatModeText(ev.mode);
      return `<tr>
        <td class="mono">${ev.timestamp || ev.time_short || ''}</td>
        <td><span class="tag ${tagClass}">${modeLabel}</span></td>
        <td style="font-weight:600" class="mono">${ev.in_v} V</td>
        <td class="mono">${ev.out_v ? ev.out_v + ' V' : '—'}</td>
        <td class="mono">${ev.load_pct !== undefined ? ev.load_pct + ' %' : '—'}</td>
        <td class="mono">${ev.batt_v ? ev.batt_v + ' V' : '—'}</td>
      </tr>`;
    }).join('');
  }
}

function renderModalEvents() {
  const modalTbody = document.getElementById('modalEventsTbody');
  const countBadge = document.getElementById('modalEventsCount');
  const searchInput = document.getElementById('modalEventsSearch');
  const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

  if (!modalTbody) return;

  const filtered = allEvents.filter(ev => {
    if (!query) return true;
    const ts = String(ev.timestamp || '').toLowerCase();
    const mode = String(ev.mode || '').toLowerCase();
    return ts.includes(query) || mode.includes(query);
  });

  if (countBadge) {
    countBadge.textContent = t('events_count_fmt', { filtered: filtered.length, total: allEvents.length });
  }

  if (filtered.length === 0) {
    modalTbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:2rem;">${t('tbl_not_found')}</td></tr>`;
  } else {
    modalTbody.innerHTML = filtered.map(ev => {
      let tagClass = 'tag-green';
      const modeU = String(ev.mode || '').toUpperCase();
      if (modeU.includes('БАТАРЕ') || modeU.includes('BATTERY')) tagClass = 'tag-amber';
      else if (modeU.includes('AVR')) tagClass = 'tag-blue';
      const modeLabel = formatModeText(ev.mode);
      return `<tr>
        <td class="mono">${ev.timestamp || ev.time_short || ''}</td>
        <td><span class="tag ${tagClass}">${modeLabel}</span></td>
        <td style="font-weight:600" class="mono">${ev.in_v} V</td>
        <td class="mono">${ev.out_v ? ev.out_v + ' V' : '—'}</td>
        <td class="mono">${ev.load_pct !== undefined ? ev.load_pct + ' %' : '—'}</td>
        <td class="mono">${ev.batt_v ? ev.batt_v + ' V' : '—'}</td>
      </tr>`;
    }).join('');
  }
}

const animGaugeStates = {};

function animateGaugeNumber(id, targetVal, decimals = 1, showDashIfDisconnected = false, isConnected = true, prefix = '', suffix = '') {
  const el = document.getElementById(id);
  if (!el) return;

  if (!animGaugeStates[id]) {
    animGaugeStates[id] = { current: null, animId: null, target: null };
  }
  const state = animGaugeStates[id];

  const isValidNumber = targetVal !== null && targetVal !== undefined && !isNaN(targetVal);
  const numTarget = (isConnected && isValidNumber) ? parseFloat(targetVal) : 0.0;

  const targetText = (!isConnected && showDashIfDisconnected && numTarget === 0)
    ? (prefix + '--' + suffix)
    : (prefix + numTarget.toFixed(decimals) + suffix);

  // If sub-precision change (e.g., tiny energy accumulation), update cleanly without re-animating
  const stepThreshold = Math.pow(10, -decimals) * 0.5;
  if (state.target !== null && Math.abs(state.target - numTarget) < stepThreshold) {
    state.target = numTarget;
    state.current = numTarget;
    if (el.textContent !== targetText) {
      el.textContent = targetText;
    }
    return;
  }

  // Determine starting value for animation
  let startVal = state.current;
  if (startVal === null || startVal === undefined || isNaN(startVal)) {
    const rawText = el.textContent ? el.textContent.replace(/[^0-9.-]/g, '') : '';
    const parsedVal = parseFloat(rawText);
    startVal = isNaN(parsedVal) ? 0.0 : parsedVal;
  }

  state.target = numTarget;
  if (state.animId) {
    cancelAnimationFrame(state.animId);
    state.animId = null;
  }

  const startTime = performance.now();
  const duration = 600;

  function step(now) {
    const elapsed = now - startTime;
    const progress = Math.min(1, elapsed / duration);
    const ease = 1 - Math.pow(1 - progress, 3);
    const curVal = startVal + (numTarget - startVal) * ease;

    state.current = curVal;
    el.textContent = prefix + curVal.toFixed(decimals) + suffix;

    if (progress < 1) {
      state.animId = requestAnimationFrame(step);
    } else {
      state.current = numTarget;
      state.animId = null;
      el.textContent = targetText;
    }
  }

  state.animId = requestAnimationFrame(step);
}

function updateUI(snapshot) {
  if (!snapshot || !snapshot.status) return;
  latestSnapshot = snapshot;
  const status = snapshot.status;
  const history = snapshot.history;
  const events = snapshot.events;

  const curLang = getLanguage();

  // Mode Title & Description lookup
  let modeTitleText = curLang === 'en' ? status.mode_title : (status.mode_title_ru || status.mode_title);
  let modeDescText = curLang === 'en' ? status.mode_desc : (status.mode_desc_ru || status.mode_desc);

  if (status.mode_code) {
    const keyTitle = 'mode_' + status.mode_code.toLowerCase();
    const keyDesc = 'mode_' + status.mode_code.toLowerCase() + '_desc';
    const trTitle = t(keyTitle);
    if (trTitle && trTitle !== keyTitle) modeTitleText = trTitle;
    const trDesc = t(keyDesc, { in_v: status.in_v, out_v: status.out_v });
    if (trDesc && trDesc !== keyDesc) modeDescText = trDesc;
  }

  // Header & status banner
  setText('statusTitle', modeTitleText || t('status_connecting'));
  setText('statusDesc', modeDescText || '');
  setText('statusTime', status.time_short || '--:--:--');
  setText('rawFrame', status.raw_frame || '—');

  const dot = document.getElementById('statusDot');
  if (dot) {
    const c = status.status_color || '#9ca3af';
    dot.style.backgroundColor = c;
    dot.style.boxShadow = `0 0 16px ${c}`;
  }

  // Live strip
  setText('liveRate', status.connected && status.freq ? `${status.freq.toFixed(1)} ${t('unit_hz')}` : `-- ${t('unit_hz')}`);
  setText('liveSeq', `#${status.seq || 0}`);
  setText('liveStamp', status.time_short || '--:--:--');

  // Sidebar status badge
  const sbStatus = document.getElementById('sidebarStatusText');
  if (sbStatus) {
    sbStatus.textContent = status.connected ? t('sidebar_connected') : t('sidebar_disconnected');
  }

  // Sound / notification on mode change
  if (status.mode_code && status.mode_code !== lastModeCode) {
    if (lastModeCode !== null) {
      if (status.is_battery) {
        playAlertSound('battery');
        showNotification(
          `⚡ ${t('status_batt_mode')}!`,
          `${curLang === 'ru' ? 'Отключение сети. Вход: ' : 'Mains power lost. Input: '}${status.in_v}V`
        );
      } else if (status.is_avr) {
        playAlertSound('avr');
        showNotification('⚡ AVR', `${status.in_v}V → ${status.out_v}V`);
      } else if (status.mode_code === 'ONLINE') {
        playAlertSound('online');
        showNotification(
          `🟢 ${t('status_grid_ok')}`,
          `${curLang === 'ru' ? 'Входное напряжение: ' : 'Input voltage: '}${status.in_v}V`
        );
      }
    }
    lastModeCode = status.mode_code;
  }

  // Gauges / Cards values with smooth number interpolation
  animateGaugeNumber('valInV', status.in_v, 1, true, status.connected);
  animateGaugeNumber('valOutV', status.out_v, 1, true, status.connected);
  animateGaugeNumber('valBattPct', status.batt_pct, 0, true, status.connected);
  animateGaugeNumber('valLoadPct', status.load_pct, 0, true, status.connected);
  animateGaugeNumber('valBattV', status.batt_v, 1, true, status.connected, `${t('mini_batt_v')}: `, ' V');
  animateGaugeNumber('valLoadWatts', status.load_watts, 0, false, status.connected, '~', ` ${t('unit_w')}`);
  animateGaugeNumber('valFreq', status.freq, 1, true, status.connected, '', ` ${t('unit_hz')}`);
  
  setText('statusInV', status.connected ? (status.in_v > 0 ? t('status_grid_ok') : t('status_grid_no')) : '—');
  setText('statusOutV', status.connected ? (status.is_battery ? t('status_batt_mode') : t('status_normal')) : '—');

  const diff = (status.connected && status.out_v !== undefined && status.in_v !== undefined) ? (status.out_v - status.in_v) : 0;
  const avrSign = diff > 0 ? '+' : '';
  animateGaugeNumber('valAvrDiff', diff, 1, true, status.connected, `AVR: ${avrSign}`, 'V');

  // Power flow diagram
  setText('flowModeLabel', modeTitleText || '—');
  animateGaugeNumber('flowInV', status.in_v, 1, true, status.connected, '', ` ${t('unit_v')}`);
  animateGaugeNumber('flowOutV', status.out_v, 1, true, status.connected, '', ` ${t('unit_v')}`);
  animateGaugeNumber('flowLoad', status.load_pct, 0, true, status.connected, '', ' %');
  animateGaugeNumber('flowWatts', status.load_watts, 0, true, status.connected, '', ` ${t('unit_w')}`);
  animateGaugeNumber('flowBatt', status.batt_pct, 0, true, status.connected, '', ' %');
  animateGaugeNumber('flowBattV', status.batt_v, 1, true, status.connected, '', ' V');
  animateGaugeNumber('flowFreq', status.freq, 1, true, status.connected, '', ` ${t('unit_hz')}`);
  animateGaugeNumber('flowAvr', diff, 1, true, status.connected, `AVR ${avrSign}`, ' V');
  updatePowerFlow(status);
  updateOutletsUI(status);

  // Mini stats row
  animateGaugeNumber('miniFreq', status.freq, 1, true, status.connected, '', ` ${t('unit_hz')}`);
  animateGaugeNumber('miniTemp', status.temp, 1, true, status.connected, '', ' °C');
  animateGaugeNumber('miniWatts', status.load_watts, 0, true, status.connected, '', ` ${t('unit_w')}`);
  animateGaugeNumber('miniBattV', status.batt_v, 1, true, status.connected, '', ' V');
  setText('miniBits', status.connected && status.status_bits ? status.status_bits : '--------');

  // Freeze badge status
  if (status.telemetry_frozen) {
    setText('freezeBadge', t('frozen'));
    setText('freezeSec', ` (${status.freeze_sec.toFixed(1)}s)`);
  } else {
    setText('freezeBadge', status.connected ? t('live_data') : t('no_connection'));
    setText('freezeSec', '');
  }

  // Update SVG Arc Gauges (Segmented Slices)
  const GAUGE_C = 351.86;
  const setArc = (id, ratio) => {
    const mask = document.getElementById(id + 'Mask');
    const arc = document.getElementById(id);
    const r = Math.max(0, Math.min(1, ratio || 0));
    if (mask) {
      mask.style.strokeDashoffset = GAUGE_C * (1 - r);
    } else if (arc) {
      arc.style.strokeDashoffset = GAUGE_C * (1 - r);
    }
  };

  const inRatio = (status.connected && status.in_v > 0) ? Math.max(0, Math.min(1, (status.in_v - 140) / 130)) : 0;
  const outRatio = (status.connected && status.out_v > 0) ? Math.max(0, Math.min(1, (status.out_v - 140) / 130)) : 0;
  setArc('arcIn', inRatio);
  setArc('arcOut', outRatio);
  setArc('arcBatt', status.connected ? status.batt_pct / 100 : 0);
  setArc('arcLoad', status.connected ? status.load_pct / 100 : 0);

  // Charts update
  if (history && history.length) {
    const labels = history.map(h => h.time);
    const inData = history.map(h => h.in_v);
    const outData = history.map(h => h.out_v);

    if (chartDashboard) {
      chartDashboard.data.labels = labels;
      chartDashboard.data.datasets[0].data = inData;
      chartDashboard.data.datasets[1].data = outData;
      chartDashboard.update('none');
    }
    if (chartAnalytics) {
      chartAnalytics.data.labels = labels;
      chartAnalytics.data.datasets[0].data = inData;
      chartAnalytics.data.datasets[1].data = outData;
      chartAnalytics.update('none');
    }
  }

  // Events Tables
  if (events) {
    renderEventsTable(events);
  }

  // Energy & Cost Section
  if (snapshot.energy) {
    updateEnergyUI(snapshot.energy);
  }

  // Graceful Shutdown Banner Update
  if (snapshot.shutdown) {
    updateShutdownBanner(snapshot.shutdown);
    syncSettingsUI(snapshot.shutdown.settings);
  }
}

function updateEnergyUI(energy) {
  if (!energy) return;
  const rubSymbol = t('currency_rub');

  animateGaugeNumber('energyTotalWatts', energy.total_watts || 0, 0, false, true);
  animateGaugeNumber('energyLoadWatts', energy.load_watts || 0, 0, false, true, '', ' W');
  animateGaugeNumber('energySelfWatts', energy.self_watts || 0, 0, false, true, '', ' W');

  animateGaugeNumber('costHour', energy.cost_per_hour || 0, 2, false, true, '', ` ${rubSymbol}`);
  animateGaugeNumber('costDay', energy.cost_per_day || 0, 2, false, true, '', ` ${rubSymbol}`);
  animateGaugeNumber('costMonth', energy.cost_per_month || 0, 1, false, true, '', ` ${rubSymbol}`);

  animateGaugeNumber('sessionKwh', energy.accumulated_kwh || 0, 3, false, true);
  animateGaugeNumber('sessionCost', energy.accumulated_cost || 0, 2, false, true, '', ` ${rubSymbol}`);
}

function updateShutdownBanner(shutdownData) {
  const banner = document.getElementById('shutdownBanner');
  const timer = document.getElementById('shutdownTimer');
  const reason = document.getElementById('shutdownReason');

  if (!banner || !timer || !reason) return;

  if (shutdownData.shutdown_active) {
    banner.style.display = 'flex';
    timer.textContent = `${shutdownData.seconds_left}s`;
    reason.textContent = `${t('shutdown_alert_reason')}: ${shutdownData.shutdown_reason || ''}`;
  } else {
    banner.style.display = 'none';
  }
}

let lastSyncedSettings = {};
function syncSettingsUI(settings) {
  if (!settings) return;
  lastSyncedSettings = settings;

  // Sync language if backend has a saved setting
  if (settings.language && settings.language !== getLanguage()) {
    applyLanguage(settings.language);
    localStorage.setItem('ups_language', settings.language);
  }

  const autoBtn = document.getElementById('settingsAutoShutdownBtn');
  const pctSel = document.getElementById('settingsShutdownPctSelect');
  const delaySel = document.getElementById('settingsShutdownDelaySelect');
  const toastBtn = document.getElementById('settingsToastBtn');

  if (autoBtn) {
    const isEn = !!settings.auto_shutdown_enabled;
    autoBtn.innerHTML = isEn 
      ? `<span class="status-dot-sm" style="background:#10b981;"></span> ${t('btn_enabled')}` 
      : `<span class="status-dot-sm" style="background:#ef4444;"></span> ${t('btn_disabled')}`;
    autoBtn.classList.toggle('active', isEn);
  }
  if (pctSel && pctSel.value != settings.shutdown_battery_pct) {
    pctSel.value = settings.shutdown_battery_pct || 15;
  }
  if (delaySel && delaySel.value != settings.shutdown_delay_sec) {
    delaySel.value = settings.shutdown_delay_sec || 60;
  }
  if (toastBtn) {
    const isToast = !!settings.toast_notif_enabled;
    toastBtn.innerHTML = isToast 
      ? `<span class="status-dot-sm" style="background:#10b981;"></span> ${t('btn_enabled')}` 
      : `<span class="status-dot-sm" style="background:#64748b;"></span> ${t('btn_disabled')}`;
    toastBtn.classList.toggle('active', isToast);
  }

  if (settings.sound_enabled !== undefined && settings.sound_enabled !== soundEnabled) {
    soundEnabled = !!settings.sound_enabled;
    updateSoundButtons(soundEnabled);
  }

  const tariffInput = document.getElementById('settingsTariffInput');
  if (tariffInput && document.activeElement !== tariffInput && settings.electricity_tariff !== undefined) {
    tariffInput.value = settings.electricity_tariff;
  }

  const selfWattsInput = document.getElementById('settingsSelfWattsInput');
  if (selfWattsInput && document.activeElement !== selfWattsInput && settings.self_consumption_watts !== undefined) {
    selfWattsInput.value = settings.self_consumption_watts;
  }
}

function updatePowerFlow(status) {
  const mains = document.getElementById('nodeMains');
  const linkMains = document.getElementById('linkMainsUps');
  const ups = document.getElementById('nodeUps');
  const linkBatt = document.getElementById('linkBattUps');
  const batt = document.getElementById('nodeBatt');
  const linkLoad = document.getElementById('linkUpsLoad');
  const load = document.getElementById('nodeLoad');

  if (!mains || !ups || !batt || !load) return;

  const isConnected = !!status.connected;
  const isBattery = !!status.is_battery;
  const isAvr = !!status.is_avr;
  const hasMainsPower = isConnected && !isBattery && status.in_v > 50;

  mains.className = 'flow-node';
  ups.className = 'flow-node flow-node-ups';
  batt.className = 'flow-node flow-node-batt';
  load.className = 'flow-node';

  if (linkMains) linkMains.className = 'flow-link';
  if (linkBatt) linkBatt.className = 'flow-batt-branch';
  if (linkLoad) linkLoad.className = 'flow-link';

  if (!isConnected) {
    mains.classList.add('dim');
    ups.classList.add('dim');
    batt.classList.add('dim');
    load.classList.add('dim');
    return;
  }

  if (hasMainsPower) {
    mains.classList.add('active-green');
    if (linkMains) linkMains.classList.add('active-green', 'active');
  } else {
    mains.classList.add('dim');
  }

  if (isBattery) {
    ups.classList.add('active-amber');
  } else if (isAvr) {
    ups.classList.add('active');
  } else {
    ups.classList.add('active-green');
  }

  if (isBattery) {
    batt.classList.add('active-amber');
    if (linkBatt) linkBatt.classList.add('active');
  } else {
    batt.classList.add('active-green');
  }

  if (status.out_v > 50) {
    load.classList.add('active-green');
    if (linkLoad) linkLoad.classList.add('active-green', 'active');
  } else {
    load.classList.add('dim');
  }
}

function initOutletsManager() {
  const defaults = [
    t('socket_default_1'),
    t('socket_default_2'),
    t('socket_default_3'),
    t('socket_default_4')
  ];

  for (let i = 1; i <= 4; i++) {
    const input = document.getElementById(`socketLabel${i}`);
    if (!input) continue;

    const saved = localStorage.getItem(`ups_socket_name_${i}`);
    if (saved) input.value = saved;
    else input.value = defaults[i - 1];

    input.addEventListener('change', () => {
      const val = input.value.trim() || defaults[i - 1];
      input.value = val;
      localStorage.setItem(`ups_socket_name_${i}`, val);
    });
  }
}

function updateOutletsUI(status) {
  if (!status) return;
  const isPowered = !!(status.connected && status.out_v > 50);
  const outVText = status.connected && status.out_v ? `${status.out_v.toFixed(0)} ${t('unit_v')}` : `-- ${t('unit_v')}`;

  for (let i = 1; i <= 4; i++) {
    const card = document.querySelector(`.socket-card[data-socket-id="${i}"]`);
    const vLabel = document.getElementById(`socketV${i}`);
    if (!card || !vLabel) continue;

    const dot = card.querySelector('.socket-status-dot');
    if (isPowered) {
      card.classList.add('active');
      if (dot) dot.classList.remove('off');
      vLabel.textContent = `${outVText} · ${t('socket_active')}`;
    } else {
      card.classList.remove('active');
      if (dot) dot.classList.add('off');
      vLabel.textContent = `0 ${t('unit_v')} · ${t('socket_disabled')}`;
    }
  }
}

function connectWebSocket() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const liveStrip = document.getElementById('liveStrip');
  let socket;
  try {
    socket = new WebSocket(`${protocol}//${location.host}/ws`);
  } catch (e) {
    if (liveStrip) liveStrip.className = 'live-pill offline';
    setTimeout(connectWebSocket, 3000);
    return;
  }
  socket.onopen = () => {
    if (liveStrip) liveStrip.className = 'live-pill';
  };
  socket.onmessage = (event) => {
    try {
      if (liveStrip) liveStrip.className = 'live-pill';
      updateUI(JSON.parse(event.data));
    } catch (e) { console.error(e); }
  };
  socket.onclose = () => {
    if (liveStrip) liveStrip.className = 'live-pill offline';
    setTimeout(connectWebSocket, 2000);
  };
  socket.onerror = () => {
    if (liveStrip) liveStrip.className = 'live-pill offline';
    try { socket.close(); } catch (e) {}
  };
}

function initTabNavigation() {
  const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
  const tabViews = document.querySelectorAll('.tab-view');
  const viewTitle = document.getElementById('currentViewTitle');

  const titles = {
    dashboard: 'view_dashboard',
    flow: 'view_flow',
    analytics: 'view_analytics',
    events: 'view_events',
    settings: 'view_settings'
  };

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tab = item.getAttribute('data-tab');
      if (!tab) return;
      activeTab = tab;

      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      tabViews.forEach(v => {
        v.classList.remove('active');
        if (v.id === `view-${tab}`) {
          v.classList.add('active');
        }
      });

      if (viewTitle && titles[tab]) {
        viewTitle.textContent = t(titles[tab]);
      }

      // Trigger chart resize if navigating to analytics
      if (tab === 'analytics' && chartAnalytics) {
        setTimeout(() => chartAnalytics.resize(), 50);
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initLanguage();
  initCharts();
  initTabNavigation();
  initOutletsManager();
  connectWebSocket();

  // Sound toggles
  const soundBtn = document.getElementById('soundToggle');
  const settingsSoundBtn = document.getElementById('settingsSoundBtn');
  const toggleSound = () => {
    soundEnabled = !soundEnabled;
    updateSoundButtons(soundEnabled);
    if (soundEnabled) {
      playAlertSound('test');
    }
    saveSettingPatch({ sound_enabled: soundEnabled });
  };

  if (soundBtn) soundBtn.addEventListener('click', toggleSound);
  if (settingsSoundBtn) settingsSoundBtn.addEventListener('click', toggleSound);

  const testSoundBtn = document.getElementById('testSoundBtn');
  if (testSoundBtn) {
    testSoundBtn.addEventListener('click', () => {
      playAlertSound('test');
    });
  }

  // Notification toggles
  const notifBtn = document.getElementById('notifToggle');
  const settingsNotifBtn = document.getElementById('settingsNotifBtn');
  if (notifBtn) notifBtn.addEventListener('click', toggleNotificationPermission);
  if (settingsNotifBtn) settingsNotifBtn.addEventListener('click', toggleNotificationPermission);

  // Check initial notification permission
  if ("Notification" in window && Notification.permission === "granted") {
    notifEnabled = true;
    updateNotifButtons(true);
  }

  // Modal event listeners
  const openModalBtn = document.getElementById('openEventsModalBtn');
  const closeModalBtn = document.getElementById('closeEventsModalBtn');
  const eventsModal = document.getElementById('eventsModal');
  const modalSearchInput = document.getElementById('modalEventsSearch');
  const tabSearchInput = document.getElementById('tabEventsSearch');

  const openModal = () => {
    if (eventsModal) {
      eventsModal.classList.add('active');
      renderModalEvents();
      if (modalSearchInput) modalSearchInput.focus();
    }
  };

  const closeModal = () => {
    if (eventsModal) eventsModal.classList.remove('active');
  };

  if (openModalBtn) openModalBtn.addEventListener('click', openModal);
  if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);

  if (eventsModal) {
    eventsModal.addEventListener('click', (e) => {
      if (e.target === eventsModal) closeModal();
    });
  }

  if (modalSearchInput) {
    modalSearchInput.addEventListener('input', () => {
      renderModalEvents();
    });
  }

  if (tabSearchInput) {
    tabSearchInput.addEventListener('input', () => {
      renderTabEvents();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && eventsModal && eventsModal.classList.contains('active')) {
      closeModal();
    }
  });

  // Emergency Cancel Shutdown Button
  const cancelBtn = document.getElementById('cancelShutdownBtn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/cancel_shutdown', { method: 'POST' });
        const data = await res.json();
        console.log('Shutdown canceled:', data);
      } catch (err) {
        console.error('Error canceling shutdown:', err);
      }
    });
  }

  // Auto Shutdown Settings Handlers
  const autoShutdownBtn = document.getElementById('settingsAutoShutdownBtn');
  if (autoShutdownBtn) {
    autoShutdownBtn.addEventListener('click', () => {
      const nextVal = !lastSyncedSettings.auto_shutdown_enabled;
      saveSettingPatch({ auto_shutdown_enabled: nextVal });
    });
  }

  const pctSelect = document.getElementById('settingsShutdownPctSelect');
  if (pctSelect) {
    pctSelect.addEventListener('change', () => {
      saveSettingPatch({ shutdown_battery_pct: parseInt(pctSelect.value, 10) });
    });
  }

  const delaySelect = document.getElementById('settingsShutdownDelaySelect');
  if (delaySelect) {
    delaySelect.addEventListener('change', () => {
      saveSettingPatch({ shutdown_delay_sec: parseInt(delaySelect.value, 10) });
    });
  }

  const toastBtn = document.getElementById('settingsToastBtn');
  if (toastBtn) {
    toastBtn.addEventListener('click', () => {
      const nextVal = !lastSyncedSettings.toast_notif_enabled;
      saveSettingPatch({ toast_notif_enabled: nextVal });
    });
  }

  const testBtn = document.getElementById('testShutdownBtn');
  if (testBtn) {
    testBtn.addEventListener('click', async () => {
      const confirmMsg = getLanguage() === 'ru'
        ? "Запустить тестовый отсчёт выключения ПК на 60 секунд?\nВы сможете сразу же отменить его кнопкой на экране."
        : "Start 60-second PC shutdown test?\nYou can cancel it immediately using the button on screen.";
      if (confirm(confirmMsg)) {
        try {
          await fetch('/api/trigger_shutdown', { method: 'POST' });
        } catch (err) {
          console.error("Error triggering test shutdown:", err);
        }
      }
    });
  }

  // Energy & Cost handlers
  const btnResetEnergy = document.getElementById('btnResetEnergy');
  if (btnResetEnergy) {
    btnResetEnergy.addEventListener('click', async () => {
      const confirmMsg = getLanguage() === 'ru'
        ? "Сбросить накопительный счетчик израсходованной энергии кВт⋅ч?"
        : "Reset accumulated kWh energy counter?";
      if (confirm(confirmMsg)) {
        try {
          await fetch('/api/reset_energy', { method: 'POST' });
        } catch (err) {
          console.error("Error resetting energy counter:", err);
        }
      }
    });
  }

  const tariffInput = document.getElementById('settingsTariffInput');
  if (tariffInput) {
    tariffInput.addEventListener('change', () => {
      const val = parseFloat(tariffInput.value);
      if (!isNaN(val) && val >= 0) {
        saveSettingPatch({ electricity_tariff: val });
      }
    });
  }

  const selfWattsInput = document.getElementById('settingsSelfWattsInput');
  if (selfWattsInput) {
    selfWattsInput.addEventListener('change', () => {
      const val = parseFloat(selfWattsInput.value);
      if (!isNaN(val) && val >= 0) {
        saveSettingPatch({ self_consumption_watts: val });
      }
    });
  }
});

async function saveSettingPatch(patchObj) {
  try {
    const newSettings = Object.assign({}, lastSyncedSettings, patchObj);
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newSettings)
    });
    const data = await res.json();
    if (data.settings) syncSettingsUI(data.settings);
  } catch (e) {
    console.error("Error saving settings:", e);
  }
}
