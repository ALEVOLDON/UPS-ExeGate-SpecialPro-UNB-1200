/**
 * Interactive 3D Voltage Graph (Three.js WebGL)
 * Renders Input (V) and Output (V) as parallel 3D neon ribbons with an AVR delta bridge.
 */
class VoltageChart3D {
  constructor(container) {
    this.container = container;
    this.labels = [];
    this.inData = [];
    this.outData = [];
    this.active = false;
    this.disposed = false;
    this.hoverIndex = -1;
    this.rafId = null;

    this.MIN_V = 140;
    this.MAX_V = 270;
    this.WIDTH = 10.4;
    this.HEIGHT = 4.6;
    this.Z_IN = 1.35;
    this.Z_OUT = -1.35;

    this.defaultCam = { theta: 0.30, phi: 1.18, radius: 11.4 };
    this.camState = { ...this.defaultCam };
    this.camTarget = { ...this.defaultCam };
    this.lookAt = new THREE.Vector3(0, 1.95, 0);

    this.isDragging = false;
    this.lastPointer = { x: 0, y: 0 };
    this.pointerNdc = new THREE.Vector2(-99, -99);
    this.isPointerInside = false;

    this._initDOM();
    this._initThree();
    this._bindEvents();
  }

  _tr(key, fallback) {
    return typeof t === 'function' ? t(key) : fallback;
  }

  _initDOM() {
    this.container.innerHTML = '';

    this.legendEl = document.createElement('div');
    this.legendEl.className = 'chart-3d-legend';
    this.legendEl.innerHTML = `
      <span class="chart-3d-legend-item">
        <span class="chart-3d-swatch in"></span>
        <span data-legend="in">${this._tr('chart_in_v', 'Input (V)')}</span>
      </span>
      <span class="chart-3d-legend-item">
        <span class="chart-3d-swatch out"></span>
        <span data-legend="out">${this._tr('chart_out_v', 'Output (V)')}</span>
      </span>
    `;
    this.container.appendChild(this.legendEl);

    this.labelsLayer = document.createElement('div');
    this.labelsLayer.className = 'chart-3d-labels';
    this.container.appendChild(this.labelsLayer);

    this.hintEl = document.createElement('div');
    this.hintEl.className = 'chart-3d-hint';
    this.hintEl.textContent = this._tr('chart_3d_hint', 'Drag to rotate · Scroll to zoom · Dbl-click to reset');
    this.container.appendChild(this.hintEl);

    this.tooltipEl = document.createElement('div');
    this.tooltipEl.className = 'chart-3d-tooltip';
    this.container.appendChild(this.tooltipEl);

    this.yLabelNodes = [];
    this.yTicks = [140, 160, 180, 200, 220, 240, 260];
    this.yTicks.forEach((v) => {
      const el = document.createElement('div');
      el.className = 'chart-3d-axis-label';
      el.textContent = `${v}V`;
      this.labelsLayer.appendChild(el);
      this.yLabelNodes.push({ value: v, el });
    });

    this.xLabelNodes = [];
    for (let i = 0; i < 6; i++) {
      const el = document.createElement('div');
      el.className = 'chart-3d-axis-label';
      this.labelsLayer.appendChild(el);
      this.xLabelNodes.push(el);
    }
  }

  _initThree() {
    const w = Math.max(this.container.clientWidth, 300);
    const h = Math.max(this.container.clientHeight, 200);

    this.scene = new THREE.Scene();

    this.camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 100);
    this._applyCamera();

    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.setSize(w, h);
    this.renderer.setClearColor(0x000000, 0);
    this.container.insertBefore(this.renderer.domElement, this.legendEl);

    // Subtle lighting for 3D tubes and nodes
    const ambient = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambient);
    const dirLight = new THREE.DirectionalLight(0xe2e8f0, 0.6);
    dirLight.position.set(5, 10, 7);
    this.scene.add(dirLight);

    this._buildGrid();

    this.dataGroup = new THREE.Group();
    this.scene.add(this.dataGroup);

    // Hover indicator group
    this.hoverGroup = new THREE.Group();
    this.hoverGroup.visible = false;
    const markerGeo = new THREE.SphereGeometry(0.11, 16, 16);
    this.hoverInSphere = new THREE.Mesh(markerGeo, new THREE.MeshBasicMaterial({ color: 0x60a5fa }));
    this.hoverOutSphere = new THREE.Mesh(markerGeo, new THREE.MeshBasicMaterial({ color: 0x34d399 }));
    const beamGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, this.Z_OUT),
      new THREE.Vector3(0, 0, this.Z_IN)
    ]);
    this.hoverBeam = new THREE.Line(
      beamGeo,
      new THREE.LineBasicMaterial({ color: 0xf8fafc, transparent: true, opacity: 0.45 })
    );
    this.hoverGroup.add(this.hoverInSphere, this.hoverOutSphere, this.hoverBeam);
    this.scene.add(this.hoverGroup);
  }

  _vToY(v) {
    const clamped = Math.max(this.MIN_V, Math.min(this.MAX_V, Number(v) || this.MIN_V));
    return ((clamped - this.MIN_V) / (this.MAX_V - this.MIN_V)) * this.HEIGHT;
  }

  _idxToX(idx, total) {
    if (total <= 1) return 0;
    return -this.WIDTH / 2 + (idx / (total - 1)) * this.WIDTH;
  }

  _buildGrid() {
    const gridGroup = new THREE.Group();
    const halfW = this.WIDTH / 2;
    const zFront = 2.2;
    const zBack = -2.2;

    // Floor grid
    const floorPts = [];
    for (let i = 0; i <= 10; i++) {
      const x = -halfW + (i / 10) * this.WIDTH;
      floorPts.push(x, 0, zBack, x, 0, zFront);
    }
    for (let j = 0; j <= 4; j++) {
      const z = zBack + (j / 4) * (zFront - zBack);
      floorPts.push(-halfW, 0, z, halfW, 0, z);
    }
    const floorGeo = new THREE.BufferGeometry();
    floorGeo.setAttribute('position', new THREE.Float32BufferAttribute(floorPts, 3));
    gridGroup.add(new THREE.LineSegments(
      floorGeo,
      new THREE.LineBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.35 })
    ));

    // Back wall voltage lines
    const wallPts = [];
    this.yTicks.forEach((v) => {
      const y = this._vToY(v);
      wallPts.push(-halfW, y, zBack, halfW, y, zBack);
    });
    for (let i = 0; i <= 5; i++) {
      const x = -halfW + (i / 5) * this.WIDTH;
      wallPts.push(x, 0, zBack, x, this.HEIGHT, zBack);
    }
    const wallGeo = new THREE.BufferGeometry();
    wallGeo.setAttribute('position', new THREE.Float32BufferAttribute(wallPts, 3));
    gridGroup.add(new THREE.LineSegments(
      wallGeo,
      new THREE.LineBasicMaterial({ color: 0x475569, transparent: true, opacity: 0.25 })
    ));

    // Subtle 220V reference line on floor/back
    const refY = this._vToY(220);
    const refGeo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-halfW, refY, zBack),
      new THREE.Vector3(halfW, refY, zBack)
    ]);
    gridGroup.add(new THREE.Line(
      refGeo,
      new THREE.LineBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.3 })
    ));

    this.scene.add(gridGroup);
  }

  _clearDataGroup() {
    while (this.dataGroup.children.length > 0) {
      const child = this.dataGroup.children[0];
      this.dataGroup.remove(child);
      if (child.geometry) child.geometry.dispose();
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach((m) => m.dispose());
        } else {
          child.material.dispose();
        }
      }
    }
  }

  _buildSeries(values, zPos, topColorHex, bottomColorHex, tubeColorHex) {
    const n = values.length;
    if (n < 2) return;

    const points = [];
    const positions = [];
    const colors = [];
    const indices = [];

    const topCol = new THREE.Color(topColorHex);
    const botCol = new THREE.Color(bottomColorHex);

    for (let i = 0; i < n; i++) {
      const x = this._idxToX(i, n);
      const y = this._vToY(values[i]);
      points.push(new THREE.Vector3(x, y, zPos));

      // Top vertex
      positions.push(x, y, zPos);
      colors.push(topCol.r, topCol.g, topCol.b, 0.42);

      // Bottom vertex
      positions.push(x, 0.01, zPos);
      colors.push(botCol.r, botCol.g, botCol.b, 0.06);

      if (i < n - 1) {
        const a = i * 2;
        const b = i * 2 + 1;
        const c = (i + 1) * 2;
        const d = (i + 1) * 2 + 1;
        indices.push(a, b, c, b, d, c);
      }
    }

    // Translucent 3D ribbon wall
    const wallGeo = new THREE.BufferGeometry();
    wallGeo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    wallGeo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 4));
    wallGeo.setIndex(indices);
    wallGeo.computeVertexNormals();

    const wallMat = new THREE.MeshBasicMaterial({
      vertexColors: true,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide
    });
    this.dataGroup.add(new THREE.Mesh(wallGeo, wallMat));

    // 3D glowing tube along the top curve
    const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal', 0.2);
    const tubularSegments = Math.min(Math.max(n * 2, 24), 220);
    const tubeGeo = new THREE.TubeGeometry(curve, tubularSegments, 0.042, 8, false);
    const tubeMat = new THREE.MeshStandardMaterial({
      color: tubeColorHex,
      emissive: tubeColorHex,
      emissiveIntensity: 0.45,
      roughness: 0.25,
      metalness: 0.1
    });
    this.dataGroup.add(new THREE.Mesh(tubeGeo, tubeMat));

    // Point nodes (InstancedMesh for high performance)
    const nodeGeo = new THREE.SphereGeometry(0.055, 8, 8);
    const nodeMat = new THREE.MeshBasicMaterial({ color: tubeColorHex });
    const inst = new THREE.InstancedMesh(nodeGeo, nodeMat, n);
    const dummy = new THREE.Object3D();
    for (let i = 0; i < n; i++) {
      dummy.position.copy(points[i]);
      dummy.updateMatrix();
      inst.setMatrixAt(i, dummy.matrix);
    }
    inst.instanceMatrix.needsUpdate = true;
    this.dataGroup.add(inst);
  }

  _buildDeltaBridge(inValues, outValues) {
    const n = Math.min(inValues.length, outValues.length);
    if (n < 2) return;

    const positions = [];
    const colors = [];
    const indices = [];

    const colNormal = new THREE.Color(0x38bdf8);
    const colAvr = new THREE.Color(0xf59e0b);

    for (let i = 0; i < n; i++) {
      const x = this._idxToX(i, n);
      const yIn = this._vToY(inValues[i]);
      const yOut = this._vToY(outValues[i]);
      const diff = Math.abs((Number(outValues[i]) || 0) - (Number(inValues[i]) || 0));
      const avrFactor = Math.min(1, Math.max(0, (diff - 4) / 18));
      const col = colNormal.clone().lerp(colAvr, avrFactor);
      const alpha = 0.08 + avrFactor * 0.16;

      positions.push(x, yIn, this.Z_IN);
      colors.push(col.r, col.g, col.b, alpha);

      positions.push(x, yOut, this.Z_OUT);
      colors.push(col.r, col.g, col.b, alpha);

      if (i < n - 1) {
        const a = i * 2;
        const b = i * 2 + 1;
        const c = (i + 1) * 2;
        const d = (i + 1) * 2 + 1;
        indices.push(a, b, c, b, d, c);
      }
    }

    const bridgeGeo = new THREE.BufferGeometry();
    bridgeGeo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    bridgeGeo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 4));
    bridgeGeo.setIndex(indices);

    const bridgeMat = new THREE.MeshBasicMaterial({
      vertexColors: true,
      transparent: true,
      depthWrite: false,
      side: THREE.DoubleSide
    });
    this.dataGroup.add(new THREE.Mesh(bridgeGeo, bridgeMat));
  }

  updateData(labels, inData, outData) {
    this.labels = labels || [];
    this.inData = inData || [];
    this.outData = outData || [];

    this._clearDataGroup();

    if (this.inData.length >= 2 && this.outData.length >= 2) {
      this._buildDeltaBridge(this.inData, this.outData);
      this._buildSeries(this.outData, this.Z_OUT, 0x10b981, 0x064e3b, 0x34d399);
      this._buildSeries(this.inData, this.Z_IN, 0x3b82f6, 0x1e3a8a, 0x60a5fa);
    }

    if (this.active) {
      this._updateAxisLabels();
      this._updateHover();
    }
  }

  updateLanguage() {
    const inSpan = this.legendEl.querySelector('[data-legend="in"]');
    const outSpan = this.legendEl.querySelector('[data-legend="out"]');
    if (inSpan) inSpan.textContent = this._tr('chart_in_v', 'Input (V)');
    if (outSpan) outSpan.textContent = this._tr('chart_out_v', 'Output (V)');
    if (this.hintEl) {
      this.hintEl.textContent = this._tr('chart_3d_hint', 'Drag to rotate · Scroll to zoom · Dbl-click to reset');
    }
  }

  setActive(isActive) {
    this.active = Boolean(isActive);
    if (this.active) {
      this.resize();
      this._startLoop();
    } else {
      this._stopLoop();
      this._hideHover();
    }
  }

  resetView() {
    this.camTarget = { ...this.defaultCam };
  }

  resize() {
    if (!this.renderer || !this.camera) return;
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    if (w <= 0 || h <= 0) return;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
    this._updateAxisLabels();
  }

  _applyCamera() {
    const { theta, phi, radius } = this.camState;
    const sinPhi = Math.sin(phi);
    this.camera.position.set(
      this.lookAt.x + radius * sinPhi * Math.sin(theta),
      this.lookAt.y + radius * Math.cos(phi),
      this.lookAt.z + radius * sinPhi * Math.cos(theta)
    );
    this.camera.lookAt(this.lookAt);
  }

  _updateAxisLabels() {
    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    if (w <= 0 || h <= 0) return;

    const project = (x, y, z) => {
      const v = new THREE.Vector3(x, y, z).project(this.camera);
      if (v.z > 1) return null;
      return {
        x: (v.x * 0.5 + 0.5) * w,
        y: (-v.y * 0.5 + 0.5) * h
      };
    };

    const leftX = -this.WIDTH / 2 - 0.35;
    this.yLabelNodes.forEach(({ value, el }) => {
      const pos = project(leftX, this._vToY(value), -2.2);
      if (!pos || pos.x < -20 || pos.x > w + 20 || pos.y < 10 || pos.y > h - 10) {
        el.style.display = 'none';
      } else {
        el.style.display = 'block';
        el.style.left = `${pos.x}px`;
        el.style.top = `${pos.y}px`;
      }
    });

    const n = this.labels.length;
    const count = this.xLabelNodes.length;
    this.xLabelNodes.forEach((el, idx) => {
      if (n < 2) {
        el.style.display = 'none';
        return;
      }
      const dataIdx = Math.round((idx / (count - 1)) * (n - 1));
      const label = this.labels[dataIdx];
      if (!label) {
        el.style.display = 'none';
        return;
      }
      const x = this._idxToX(dataIdx, n);
      const pos = project(x, -0.18, 2.38);
      if (!pos || pos.x < 10 || pos.x > w - 10 || pos.y < 10 || pos.y > h - 5) {
        el.style.display = 'none';
      } else {
        el.style.display = 'block';
        el.textContent = label;
        el.style.left = `${pos.x}px`;
        el.style.top = `${pos.y}px`;
      }
    });
  }

  _updateHover() {
    if (!this.isPointerInside || this.isDragging || this.inData.length < 2) {
      this._hideHover();
      return;
    }

    const w = this.container.clientWidth;
    const h = this.container.clientHeight;
    if (w <= 0 || h <= 0) return;

    const n = this.inData.length;
    let bestIdx = -1;
    let bestDist = Infinity;

    for (let i = 0; i < n; i++) {
      const x = this._idxToX(i, n);
      const yMid = (this._vToY(this.inData[i]) + this._vToY(this.outData[i])) * 0.5;
      const proj = new THREE.Vector3(x, yMid, 0).project(this.camera);
      const dx = proj.x - this.pointerNdc.x;
      const dy = proj.y - this.pointerNdc.y;
      const d = dx * dx + dy * dy;
      if (d < bestDist) {
        bestDist = d;
        bestIdx = i;
      }
    }

    if (bestIdx === -1 || bestDist > 0.06) {
      this._hideHover();
      return;
    }

    this.hoverIndex = bestIdx;
    const x = this._idxToX(bestIdx, n);
    const inV = this.inData[bestIdx];
    const outV = this.outData[bestIdx];
    const yIn = this._vToY(inV);
    const yOut = this._vToY(outV);

    this.hoverInSphere.position.set(x, yIn, this.Z_IN);
    this.hoverOutSphere.position.set(x, yOut, this.Z_OUT);
    const beamPos = this.hoverBeam.geometry.attributes.position;
    beamPos.setXYZ(0, x, yOut, this.Z_OUT);
    beamPos.setXYZ(1, x, yIn, this.Z_IN);
    beamPos.needsUpdate = true;
    this.hoverGroup.visible = true;

    const diff = (Number(outV) - Number(inV)).toFixed(1);
    const diffSign = Number(diff) > 0 ? `+${diff}` : diff;
    const timeLabel = this.labels[bestIdx] || '';

    this.tooltipEl.innerHTML = `
      <div class="chart-3d-tooltip-time">${timeLabel}</div>
      <div class="chart-3d-tooltip-row">
        <span><span class="chart-3d-dot" style="background:#3b82f6"></span>${this._tr('chart_in_v', 'Input (V)')}</span>
        <strong>${Number(inV).toFixed(1)} V</strong>
      </div>
      <div class="chart-3d-tooltip-row">
        <span><span class="chart-3d-dot" style="background:#10b981"></span>${this._tr('chart_out_v', 'Output (V)')}</span>
        <strong>${Number(outV).toFixed(1)} V</strong>
      </div>
      <div class="chart-3d-tooltip-row" style="margin-top:2px;border-top:1px solid rgba(255,255,255,0.08);padding-top:2px;">
        <span style="color:#94a3b8">${this._tr('chart_3d_avr_diff', 'AVR Delta')}</span>
        <strong style="color:#fbbf24">${diffSign} V</strong>
      </div>
    `;

    const px = ((this.pointerNdc.x * 0.5 + 0.5) * w);
    const py = ((-this.pointerNdc.y * 0.5 + 0.5) * h);
    const tipX = Math.min(Math.max(12, px + 14), w - 165);
    const tipY = Math.min(Math.max(12, py - 24), h - 95);
    this.tooltipEl.style.left = `${tipX}px`;
    this.tooltipEl.style.top = `${tipY}px`;
    this.tooltipEl.classList.add('visible');
  }

  _hideHover() {
    this.hoverIndex = -1;
    if (this.hoverGroup) this.hoverGroup.visible = false;
    if (this.tooltipEl) this.tooltipEl.classList.remove('visible');
  }

  _bindEvents() {
    this._onPointerDown = (e) => {
      this.isDragging = true;
      this.lastPointer = { x: e.clientX, y: e.clientY };
      this._hideHover();
    };

    this._onPointerMove = (e) => {
      const rect = this.container.getBoundingClientRect();
      this.isPointerInside = true;
      this.pointerNdc.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointerNdc.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      if (this.isDragging) {
        const dx = e.clientX - this.lastPointer.x;
        const dy = e.clientY - this.lastPointer.y;
        this.lastPointer = { x: e.clientX, y: e.clientY };

        this.camTarget.theta -= dx * 0.008;
        this.camTarget.phi = Math.max(0.35, Math.min(1.48, this.camTarget.phi - dy * 0.007));
      } else if (this.active) {
        this._updateHover();
      }
    };

    this._onPointerUp = () => {
      this.isDragging = false;
    };

    this._onPointerLeave = () => {
      this.isDragging = false;
      this.isPointerInside = false;
      this._hideHover();
    };

    this._onWheel = (e) => {
      e.preventDefault();
      this.camTarget.radius = Math.max(6.2, Math.min(18.5, this.camTarget.radius + e.deltaY * 0.008));
    };

    this._onDblClick = () => {
      this.resetView();
    };

    this.container.addEventListener('pointerdown', this._onPointerDown);
    window.addEventListener('pointermove', this._onPointerMove);
    window.addEventListener('pointerup', this._onPointerUp);
    this.container.addEventListener('pointerleave', this._onPointerLeave);
    this.container.addEventListener('wheel', this._onWheel, { passive: false });
    this.container.addEventListener('dblclick', this._onDblClick);

    if (typeof ResizeObserver !== 'undefined') {
      this.resizeObserver = new ResizeObserver(() => {
        if (this.active) this.resize();
      });
      this.resizeObserver.observe(this.container);
    }
  }

  _startLoop() {
    if (this.rafId !== null || this.disposed) return;
    const tick = () => {
      if (!this.active || this.disposed) {
        this.rafId = null;
        return;
      }
      const ease = 0.14;
      const moved =
        Math.abs(this.camState.theta - this.camTarget.theta) > 0.0005 ||
        Math.abs(this.camState.phi - this.camTarget.phi) > 0.0005 ||
        Math.abs(this.camState.radius - this.camTarget.radius) > 0.0005;

      this.camState.theta += (this.camTarget.theta - this.camState.theta) * ease;
      this.camState.phi += (this.camTarget.phi - this.camState.phi) * ease;
      this.camState.radius += (this.camTarget.radius - this.camState.radius) * ease;

      this._applyCamera();
      if (moved) {
        this._updateAxisLabels();
      }
      this.renderer.render(this.scene, this.camera);
      this.rafId = requestAnimationFrame(tick);
    };
    this.rafId = requestAnimationFrame(tick);
  }

  _stopLoop() {
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }
}

window.VoltageChart3D = VoltageChart3D;
