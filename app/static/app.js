let soundEnabled = true;
let notifEnabled = false;
let chartDashboard = null;
let chartAnalytics = null;
let lastModeCode = null;
let allEvents = [];

function playAlertSound(type) {
  if (!soundEnabled) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
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
    }
  } catch (e) {
    console.error("Audio error:", e);
  }
}

function toggleNotificationPermission() {
  if (!("Notification" in window)) {
    alert("Ваш браузер не поддерживает Push-уведомления.");
    return;
  }

  if (Notification.permission === "granted") {
    notifEnabled = !notifEnabled;
    updateNotifButtons(notifEnabled);
    if (notifEnabled) {
      showNotification("ExeGate Pro", "Уведомления браузера включены");
    }
  } else if (Notification.permission !== "denied") {
    Notification.requestPermission().then(permission => {
      if (permission === "granted") {
        notifEnabled = true;
        updateNotifButtons(true);
        showNotification("ExeGate Pro", "Уведомления браузера включены");
      } else {
        notifEnabled = false;
        updateNotifButtons(false);
      }
    });
  } else {
    alert("Уведомления заблокированы в настройках браузера. Разрешите их возле адреса сайта.");
  }
}

function updateSoundButtons(enabled) {
  const btn1 = document.getElementById('soundToggle');
  const btn2 = document.getElementById('settingsSoundBtn');
  if (btn1) {
    setText('soundText', enabled ? 'Звук' : 'Выкл');
    btn1.classList.toggle('active', enabled);
  }
  if (btn2) {
    btn2.innerHTML = enabled 
      ? '<span class="status-dot-sm" style="background:#10b981;"></span> Включено' 
      : '<span class="status-dot-sm" style="background:#64748b;"></span> Выключено';
    btn2.classList.toggle('active', enabled);
  }
}

function updateNotifButtons(enabled) {
  const btn1 = document.getElementById('notifToggle');
  const btn2 = document.getElementById('settingsNotifBtn');
  if (btn1) {
    setText('notifText', enabled ? 'Алерты' : 'Выкл');
    btn1.classList.toggle('active', enabled);
  }
  if (btn2) {
    btn2.innerHTML = enabled 
      ? '<span class="status-dot-sm" style="background:#10b981;"></span> Включено' 
      : '<span class="status-dot-sm" style="background:#64748b;"></span> Включить';
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
          label: 'Вход (В)',
          data: [],
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.15)',
          fill: true,
          tension: 0.3,
          borderWidth: 2.5,
          pointRadius: 1
        },
        {
          label: 'Выход (В)',
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

function renderEventsTable(events) {
  allEvents = events || [];

  // 1. Dashboard preview table (top 5 items)
  const tbody = document.getElementById('eventsTbody');
  if (tbody) {
    if (allEvents.length === 0) {
      tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--text-muted);padding:1.5rem;">История пуста</td></tr>';
    } else {
      const top5 = allEvents.slice(0, 5);
      tbody.innerHTML = top5.map(ev => {
        let tagClass = 'tag-green';
        const modeU = String(ev.mode || '').toUpperCase();
        if (modeU.includes('БАТАРЕ') || modeU.includes('BATTERY')) tagClass = 'tag-amber';
        else if (modeU.includes('AVR')) tagClass = 'tag-blue';
        return `<tr>
          <td>${ev.time_short || (ev.timestamp && String(ev.timestamp).split(' ')[1]) || ''}</td>
          <td><span class="tag ${tagClass}">${ev.mode}</span></td>
          <td style="font-weight:600">${ev.in_v} B</td>
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
    tabTbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:2rem;">События не найдены</td></tr>';
  } else {
    tabTbody.innerHTML = filtered.map(ev => {
      let tagClass = 'tag-green';
      const modeU = String(ev.mode || '').toUpperCase();
      if (modeU.includes('БАТАРЕ') || modeU.includes('BATTERY')) tagClass = 'tag-amber';
      else if (modeU.includes('AVR')) tagClass = 'tag-blue';
      return `<tr>
        <td class="mono">${ev.timestamp || ev.time_short || ''}</td>
        <td><span class="tag ${tagClass}">${ev.mode}</span></td>
        <td style="font-weight:600" class="mono">${ev.in_v} B</td>
        <td class="mono">${ev.out_v ? ev.out_v + ' B' : '—'}</td>
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

  if (countBadge) countBadge.textContent = `${filtered.length} из ${allEvents.length} событий`;

  if (filtered.length === 0) {
    modalTbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:2rem;">События не найдены</td></tr>';
  } else {
    modalTbody.innerHTML = filtered.map(ev => {
      let tagClass = 'tag-green';
      const modeU = String(ev.mode || '').toUpperCase();
      if (modeU.includes('БАТАРЕ') || modeU.includes('BATTERY')) tagClass = 'tag-amber';
      else if (modeU.includes('AVR')) tagClass = 'tag-blue';
      return `<tr>
        <td class="mono">${ev.timestamp || ev.time_short || ''}</td>
        <td><span class="tag ${tagClass}">${ev.mode}</span></td>
        <td style="font-weight:600" class="mono">${ev.in_v} B</td>
        <td class="mono">${ev.out_v ? ev.out_v + ' B' : '—'}</td>
        <td class="mono">${ev.load_pct !== undefined ? ev.load_pct + ' %' : '—'}</td>
        <td class="mono">${ev.batt_v ? ev.batt_v + ' V' : '—'}</td>
      </tr>`;
    }).join('');
  }
}

function updateUI(snapshot) {
  if (!snapshot || !snapshot.status) return;
  const status = snapshot.status;
  const history = snapshot.history;
  const events = snapshot.events;

  // Header & status banner
  setText('statusTitle', status.mode_title || 'Подключение...');
  setText('statusDesc', status.mode_desc || '');
  setText('statusTime', status.time_short || '--:--:--');
  setText('rawFrame', status.raw_frame || '—');

  const dot = document.getElementById('statusDot');
  if (dot) {
    const c = status.status_color || '#9ca3af';
    dot.style.backgroundColor = c;
    dot.style.boxShadow = `0 0 16px ${c}`;
  }

  // Live strip
  setText('liveRate', status.connected && status.freq ? `${status.freq.toFixed(1)} Гц` : '-- Гц');
  setText('liveSeq', `#${status.seq || 0}`);
  setText('liveStamp', status.time_short || '--:--:--');

  // Sidebar status badge
  const sbStatus = document.getElementById('sidebarStatusText');
  if (sbStatus) {
    sbStatus.textContent = status.connected ? 'ПОДКЛЮЧЕНО' : 'НЕТ СВЯЗИ';
  }

  // Sound / notification on mode change
  if (status.mode_code && status.mode_code !== lastModeCode) {
    if (lastModeCode !== null) {
      if (status.is_battery) {
        playAlertSound('battery');
        showNotification('⚡ Питание от батареи!', `Отключение сети. Вход: ${status.in_v}V`);
      } else if (status.is_avr) {
        playAlertSound('avr');
        showNotification('⚡ Сработка AVR', `${status.in_v}V → ${status.out_v}V`);
      } else if (status.mode_code === 'ONLINE') {
        playAlertSound('online');
        showNotification('🟢 Сеть восстановлена', `Вход: ${status.in_v}V`);
      }
    }
    lastModeCode = status.mode_code;
  }

  // Gauges / Cards values
  setText('valInV', status.in_v ? status.in_v.toFixed(1) : '--');
  setText('valOutV', status.out_v ? status.out_v.toFixed(1) : '--');
  setText('valBattPct', status.batt_pct !== undefined ? status.batt_pct : '--');
  setText('valLoadPct', status.load_pct !== undefined ? status.load_pct : '--');
  setText('valBattV', `Напряжение: ${status.batt_v ? status.batt_v.toFixed(1) : '--'} V`);
  setText('valLoadWatts', `~${status.load_watts || 0} Вт`);
  setText('valFreq', status.connected && status.freq ? `${status.freq.toFixed(1)} Гц` : '-- Гц');
  setText('statusInV', status.connected ? (status.in_v > 0 ? 'Сеть в норме' : 'Нет сети') : '—');
  setText('statusOutV', status.connected ? (status.is_battery ? 'Питание от АКБ' : 'Норма') : '—');

  const diff = status.out_v - status.in_v;
  setText('valAvrDiff', `AVR: ${diff >= 0 ? '+' : ''}${diff.toFixed(1)}V`);

  // Power flow diagram
  setText('flowModeLabel', status.mode_title || '—');
  setText('flowInV', status.connected ? `${status.in_v.toFixed(1)} В` : '-- В');
  setText('flowOutV', status.connected ? `${status.out_v.toFixed(1)} В` : '-- В');
  setText('flowLoad', status.connected ? `${status.load_pct} %` : '-- %');
  setText('flowWatts', status.connected ? `${status.load_watts} Вт` : '-- Вт');
  setText('flowBatt', status.connected ? `${status.batt_pct} %` : '-- %');
  setText('flowBattV', status.connected ? `${status.batt_v.toFixed(1)} V` : '-- V');
  setText('flowFreq', status.connected ? `${status.freq.toFixed(1)} Гц` : '-- Гц');
  setText('flowAvr', `AVR ${diff >= 0 ? '+' : ''}${diff.toFixed(1)} V`);
  updatePowerFlow(status);

  // Mini stats row
  setText('miniFreq', status.connected && status.freq !== undefined ? `${status.freq.toFixed(1)} Гц` : '-- Гц');
  setText('miniTemp', status.connected && status.temp !== undefined ? `${status.temp.toFixed(1)} °C` : '-- °C');
  setText('miniWatts', status.connected && status.load_watts !== undefined ? `${status.load_watts} Вт` : '-- Вт');
  setText('miniBattV', status.connected && status.batt_v !== undefined ? `${status.batt_v.toFixed(1)} V` : '-- V');
  setText('miniBits', status.connected && status.status_bits ? status.status_bits : '--------');

  // Freeze badge status
  if (status.telemetry_frozen) {
    setText('freezeBadge', 'ЗАМОРОЖЕНО');
    setText('freezeSec', ` (${status.freeze_sec.toFixed(1)}s)`);
  } else {
    setText('freezeBadge', status.connected ? 'LIVE DATA' : 'НЕТ СВЯЗИ');
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

  const inRatio = status.connected ? Math.max(0, Math.min(1, (status.in_v - 140) / 130)) : 0;
  const outRatio = status.connected ? Math.max(0, Math.min(1, (status.out_v - 140) / 130)) : 0;
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

  // Graceful Shutdown Banner Update
  if (snapshot.shutdown) {
    updateShutdownBanner(snapshot.shutdown);
    syncSettingsUI(snapshot.shutdown.settings);
  }
}

function updateShutdownBanner(shutdownData) {
  const banner = document.getElementById('shutdownBanner');
  const timer = document.getElementById('shutdownTimer');
  const reason = document.getElementById('shutdownReason');

  if (!banner || !timer || !reason) return;

  if (shutdownData.shutdown_active) {
    banner.style.display = 'flex';
    timer.textContent = `${shutdownData.seconds_left}с`;
    reason.textContent = `Причина: ${shutdownData.shutdown_reason || 'Критический разряд АКБ'}`;
  } else {
    banner.style.display = 'none';
  }
}

let lastSyncedSettings = {};
function syncSettingsUI(settings) {
  if (!settings) return;
  lastSyncedSettings = settings;

  const autoBtn = document.getElementById('settingsAutoShutdownBtn');
  const pctSel = document.getElementById('settingsShutdownPctSelect');
  const delaySel = document.getElementById('settingsShutdownDelaySelect');
  const toastBtn = document.getElementById('settingsToastBtn');

  if (autoBtn) {
    const isEn = !!settings.auto_shutdown_enabled;
    autoBtn.innerHTML = isEn 
      ? '<span class="status-dot-sm" style="background:#10b981;"></span> Включено' 
      : '<span class="status-dot-sm" style="background:#ef4444;"></span> Выключено';
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
      ? '<span class="status-dot-sm" style="background:#10b981;"></span> Включено' 
      : '<span class="status-dot-sm" style="background:#64748b;"></span> Выключено';
    toastBtn.classList.toggle('active', isToast);
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
    dashboard: 'Дашборд мониторинга',
    flow: 'Интерактивная схема питания',
    analytics: 'Аналитика и динамика напряжений',
    events: 'Журнал событий питания',
    settings: 'Настройки оповещений и системы'
  };

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tab = item.getAttribute('data-tab');
      if (!tab) return;

      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      tabViews.forEach(v => {
        v.classList.remove('active');
        if (v.id === `view-${tab}`) {
          v.classList.add('active');
        }
      });

      if (viewTitle && titles[tab]) {
        viewTitle.textContent = titles[tab];
      }

      // Trigger chart resize if navigating to analytics
      if (tab === 'analytics' && chartAnalytics) {
        setTimeout(() => chartAnalytics.resize(), 50);
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  initTabNavigation();
  connectWebSocket();

  // Sound toggles
  const soundBtn = document.getElementById('soundToggle');
  const settingsSoundBtn = document.getElementById('settingsSoundBtn');
  const toggleSound = () => {
    soundEnabled = !soundEnabled;
    updateSoundButtons(soundEnabled);
    if (soundEnabled) playAlertSound('avr');
  };

  if (soundBtn) soundBtn.addEventListener('click', toggleSound);
  if (settingsSoundBtn) settingsSoundBtn.addEventListener('click', toggleSound);

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
      if (confirm("Запустить тестовый отсчёт выключения ПК на 60 секунд?\nВы сможете сразу же отменить его кнопкой на экране.")) {
        try {
          await fetch('/api/trigger_shutdown', { method: 'POST' });
        } catch (err) {
          console.error("Error triggering test shutdown:", err);
        }
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

