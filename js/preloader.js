/* Intro animation. The bird from the Kiwi's logo walks in, lowers its head and
   flicks a kiwi fruit at the screen with its beak. The fruit splats into a kiwi
   slice, the wordmark appears, and the page is revealed through a hole that
   grows from the centre. Canvas only, no assets. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var nav = window.performance && performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
  var fromOwnPage = document.referrer.indexOf(location.origin + '/') === 0 && !(nav && nav.type === 'reload');
  if (reduceMotion || fromOwnPage || !window.Path2D) return;

  // ---------- setup ----------
  var canvas = document.createElement('canvas');
  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:9999;display:block;cursor:pointer;touch-action:none;';
  document.body.appendChild(canvas);
  var ctx = canvas.getContext('2d');
  var W = 0, H = 0, dpr = 1;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
  }
  resize();
  window.addEventListener('resize', resize);

  // ---------- palette (from the logo) ----------
  var C = {
    bg: '#EEDFCD',
    ink: '#615E34',
    shadow: 'rgba(97,94,52,0.16)',
    fruit: '#7D5D35',
    fruitLight: '#9C7C4C',
    fruitDark: '#5A4122',
    flesh: '#8BBE3F',
    fleshLight: '#A8D462',
    fleshDark: '#6E9E2A',
    core: '#F4F0CE',
    coreEdge: '#DFE6A6',
    seed: '#2E2A17'
  };

  // ---------- helpers ----------
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function prog(t, a, b) { return clamp((t - a) / (b - a), 0, 1); }
  var ease = {
    inQuad: function (t) { return t * t; },
    outQuad: function (t) { return 1 - (1 - t) * (1 - t); },
    inCubic: function (t) { return t * t * t; },
    outCubic: function (t) { return 1 - Math.pow(1 - t, 3); },
    inOutCubic: function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; },
    inOutSine: function (t) { return -(Math.cos(Math.PI * t) - 1) / 2; },
    outSine: function (t) { return Math.sin(t * Math.PI / 2); },
    outBack: function (t) { var c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); }
  };
  var seed = 11;
  function rand() { // deterministic, so it looks the same every time
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  }
  function rr(a, b) { return a + rand() * (b - a); }
  function rotAbout(p, c, a) {
    var s = Math.sin(a), co = Math.cos(a), x = p.x - c.x, y = p.y - c.y;
    return { x: c.x + x * co - y * s, y: c.y + x * s + y * co };
  }

  // ---------- the bird and wordmark from the logo (traced; 1 unit = 10 logo px) ----------
  // Bird origin: between the feet, on the ground. Head and legs are separate so they can move.
  var LOGO = {
    body: new Path2D('M8.20 -39.27L7.42 -39.00L7.30 -39.00L7.08 -38.90L6.92 -38.90L6.62 -38.80L6.47 -38.80L6.10 -38.70L5.85 -38.70L5.83 -38.67L5.75 -38.70L5.62 -38.65L5.25 -38.67L5.22 -38.62L5.30 -38.55L5.45 -38.52L5.67 -38.42L5.80 -38.42L6.08 -38.33L6.58 -38.30L6.65 -38.25L6.65 -38.17L6.55 -38.10L6.45 -38.10L6.33 -38.02L6.15 -38.00L5.92 -37.90L5.80 -37.90L5.53 -37.80L5.35 -37.80L4.95 -37.70L4.65 -37.70L4.25 -37.62L2.45 -37.60L2.42 -37.58L2.45 -37.52L3.08 -37.23L3.15 -37.23L3.38 -37.12L3.48 -37.12L3.62 -37.05L3.90 -37.02L4.15 -36.95L4.62 -36.92L4.67 -36.88L4.62 -36.80L4.25 -36.77L4.05 -36.70L3.75 -36.70L3.58 -36.65L3.08 -36.62L3.05 -36.60L2.25 -36.60L2.23 -36.58L1.65 -36.60L1.45 -36.55L0.25 -36.50L0.23 -36.48L0.15 -36.50L-0.07 -36.45L-0.03 -36.35L0.20 -36.33L0.28 -36.27L0.50 -36.23L0.68 -36.12L1.00 -36.02L1.15 -35.92L1.23 -35.92L1.35 -35.83L1.57 -35.73L1.65 -35.65L1.60 -35.60L0.62 -35.65L0.42 -35.70L0.15 -35.67L0.12 -35.70L-0.68 -35.70L-0.70 -35.73L-3.17 -35.70L-3.23 -35.65L-3.12 -35.58L-2.75 -35.42L-2.45 -35.23L-2.40 -35.23L-2.20 -35.08L-2.02 -34.85L-2.10 -34.83L-2.17 -34.88L-2.80 -34.92L-2.90 -34.98L-3.15 -34.95L-3.27 -35.00L-3.35 -34.98L-4.47 -34.98L-4.55 -35.00L-4.70 -34.95L-5.17 -34.95L-5.20 -34.92L-5.95 -34.90L-5.97 -34.88L-6.05 -34.90L-6.60 -34.80L-7.05 -34.77L-7.25 -34.70L-7.28 -34.65L-7.25 -34.62L-6.92 -34.62L-6.58 -34.52L-6.40 -34.52L-6.15 -34.42L-6.03 -34.42L-5.95 -34.38L-5.67 -34.33L-5.30 -34.15L-5.15 -34.12L-5.08 -34.05L-5.15 -34.00L-5.58 -34.00L-5.60 -34.02L-6.65 -34.00L-7.33 -33.90L-7.75 -33.88L-7.95 -33.80L-8.15 -33.80L-8.35 -33.73L-8.60 -33.70L-8.78 -33.62L-8.97 -33.60L-9.22 -33.50L-9.32 -33.50L-9.47 -33.42L-10.00 -33.27L-10.12 -33.20L-10.20 -33.20L-10.38 -33.10L-10.45 -33.10L-10.85 -32.92L-10.90 -32.88L-10.88 -32.83L-10.70 -32.83L-10.57 -32.88L-10.12 -32.88L-10.10 -32.85L-10.00 -32.90L-9.72 -32.90L-9.62 -32.85L-9.60 -32.88L-8.85 -32.85L-8.70 -32.83L-8.65 -32.75L-8.70 -32.70L-8.85 -32.70L-9.18 -32.60L-9.32 -32.60L-9.57 -32.50L-9.70 -32.50L-9.93 -32.40L-10.05 -32.40L-11.25 -31.98L-11.35 -31.90L-11.43 -31.90L-11.57 -31.80L-11.65 -31.80L-11.85 -31.70L-11.93 -31.62L-12.07 -31.57L-13.03 -30.98L-13.12 -30.88L-13.07 -30.77L-12.68 -30.93L-12.47 -30.95L-12.35 -31.02L-12.07 -31.05L-11.93 -31.12L-11.68 -31.12L-11.55 -31.18L-11.12 -31.23L-10.93 -31.23L-10.88 -31.18L-10.93 -31.10L-11.10 -31.07L-11.20 -31.00L-11.28 -31.00L-11.38 -30.93L-11.50 -30.90L-12.35 -30.48L-12.57 -30.32L-12.68 -30.30L-13.28 -29.90L-13.32 -29.90L-14.03 -29.40L-14.78 -28.77L-15.18 -28.38L-15.78 -27.65L-16.30 -26.85L-16.32 -26.73L-16.23 -26.73L-16.12 -26.82L-16.07 -26.82L-15.97 -26.93L-15.78 -27.02L-15.68 -27.12L-15.22 -27.40L-14.68 -27.65L-14.57 -27.62L-14.57 -27.55L-15.47 -26.68L-15.53 -26.57L-16.07 -25.98L-16.48 -25.48L-17.20 -24.35L-17.50 -23.75L-17.52 -23.60L-17.60 -23.48L-17.60 -23.38L-17.70 -23.18L-17.70 -22.77L-17.65 -22.75L-17.43 -23.07L-16.85 -23.65L-16.38 -23.95L-16.32 -23.93L-16.32 -23.85L-16.40 -23.77L-16.40 -23.73L-16.77 -23.10L-16.90 -22.80L-16.98 -22.73L-17.10 -22.48L-17.10 -22.40L-17.30 -22.05L-17.30 -21.98L-17.40 -21.82L-17.43 -21.68L-17.60 -21.32L-17.60 -21.23L-17.68 -21.10L-17.70 -20.95L-17.80 -20.73L-17.80 -20.57L-17.88 -20.45L-17.90 -20.18L-17.98 -20.02L-18.00 -19.65L-18.05 -19.48L-18.00 -18.93L-17.93 -18.98L-17.93 -19.05L-17.80 -19.30L-17.43 -19.85L-17.07 -20.20L-17.02 -20.18L-17.02 -20.10L-17.07 -20.05L-17.10 -19.90L-17.20 -19.73L-17.20 -19.65L-17.40 -19.12L-17.40 -18.98L-17.48 -18.85L-17.50 -18.60L-17.57 -18.45L-17.62 -18.05L-17.70 -17.85L-17.70 -17.55L-17.75 -17.32L-17.75 -17.10L-17.80 -16.95L-17.77 -16.88L-17.80 -16.57L-17.73 -16.25L-17.65 -16.18L-17.62 -16.38L-17.43 -16.77L-17.40 -16.90L-17.32 -16.98L-17.30 -17.07L-16.93 -17.65L-16.65 -17.95L-16.60 -17.90L-16.60 -17.80L-16.70 -17.62L-16.70 -17.52L-16.77 -17.38L-16.80 -17.18L-16.90 -16.88L-16.90 -16.70L-17.00 -16.35L-17.02 -15.93L-17.07 -15.82L-17.05 -15.70L-17.10 -15.55L-17.07 -15.47L-17.10 -14.88L-17.00 -14.40L-17.00 -14.22L-16.90 -14.00L-16.90 -13.90L-16.85 -13.85L-16.77 -13.93L-16.73 -14.30L-16.68 -14.38L-16.62 -14.65L-16.45 -15.00L-16.43 -15.12L-16.23 -15.45L-16.05 -15.60L-16.00 -15.53L-16.02 -15.50L-16.02 -14.12L-15.97 -13.65L-16.00 -13.57L-15.90 -13.20L-15.90 -13.00L-15.80 -12.75L-15.80 -12.60L-15.60 -12.15L-15.47 -12.00L-15.43 -12.05L-15.43 -12.60L-15.32 -13.18L-15.32 -13.47L-15.25 -13.75L-15.15 -13.85L-15.10 -13.75L-15.10 -13.47L-15.03 -13.28L-15.00 -12.97L-14.93 -12.80L-14.90 -12.55L-14.82 -12.35L-14.78 -12.05L-14.70 -11.90L-14.68 -11.70L-14.62 -11.62L-14.47 -11.12L-14.40 -11.00L-14.40 -10.93L-14.00 -10.15L-13.88 -9.97L-13.80 -9.97L-13.85 -11.38L-13.82 -11.45L-13.75 -11.47L-13.70 -11.43L-13.68 -11.28L-13.60 -11.18L-13.60 -11.10L-13.50 -10.90L-13.43 -10.82L-13.38 -10.68L-13.10 -10.25L-13.10 -10.20L-12.57 -9.45L-12.10 -8.95L-11.82 -8.70L-11.70 -8.62L-11.65 -8.65L-11.72 -8.75L-11.88 -9.25L-11.82 -9.43L-11.72 -9.45L-11.20 -9.05L-10.82 -8.82L-10.70 -8.70L-10.70 -8.60L-10.75 -8.55L-10.80 -8.32L-10.88 -8.22L-10.93 -8.00L-10.97 -7.95L-11.00 -7.80L-11.10 -7.65L-11.12 -7.53L-8.43 -7.53L-8.35 -7.62L-8.18 -7.62L-7.97 -7.53L-7.83 -7.53L-7.67 -7.45L-7.45 -7.42L-7.15 -7.33L-6.95 -7.33L-6.75 -7.25L-6.33 -7.22L-5.97 -7.17L-5.85 -7.12L-5.67 -7.15L-5.17 -7.10L-3.92 -7.10L-3.90 -7.12L-3.40 -7.12L-3.38 -7.15L-3.27 -7.12L-2.45 -7.25L-2.38 -7.22L-2.00 -7.33L-1.77 -7.33L-1.55 -7.40L-1.15 -7.45L-0.95 -7.53L-0.80 -7.53L-0.53 -7.62L-0.30 -7.65L-0.28 -7.62L-0.30 -7.50L-0.50 -7.28L-0.68 -7.12L-0.90 -7.00L-0.95 -6.92L-0.72 -6.92L-0.40 -7.03L-0.12 -7.05L-0.05 -7.10L0.15 -7.12L0.28 -7.20L0.82 -7.38L1.18 -7.22L1.30 -7.12L4.58 -7.12L3.88 -8.07L3.75 -8.30L3.75 -8.38L3.92 -8.53L4.33 -8.75L5.45 -9.55L5.62 -9.72L5.70 -9.68L5.70 -9.62L5.62 -9.53L5.60 -9.38L5.47 -9.12L4.83 -8.28L4.90 -8.25L5.15 -8.32L5.35 -8.43L5.42 -8.50L5.53 -8.53L5.62 -8.62L5.85 -8.75L6.35 -9.15L7.35 -10.15L7.40 -10.25L7.88 -10.80L7.90 -10.88L8.28 -11.35L8.68 -12.00L8.75 -12.05L8.82 -11.95L8.80 -11.78L8.72 -11.62L8.70 -11.43L8.60 -11.22L8.60 -11.15L8.40 -10.75L8.28 -10.35L8.35 -10.35L8.68 -10.65L9.25 -11.25L9.55 -11.62L9.88 -12.10L10.35 -12.93L10.38 -13.05L10.68 -13.65L10.68 -13.75L10.78 -13.90L10.78 -14.00L10.85 -14.12L10.88 -14.28L10.97 -14.50L10.97 -14.60L11.03 -14.68L11.07 -14.95L11.18 -15.20L11.20 -15.45L11.25 -15.53L11.28 -15.85L11.32 -15.93L11.40 -15.85L11.50 -15.28L11.50 -14.60L11.43 -14.00L11.50 -13.97L11.57 -14.05L11.78 -14.50L11.80 -14.65L11.85 -14.70L11.88 -14.85L12.05 -15.30L12.07 -15.55L12.15 -15.70L12.18 -16.02L12.28 -16.48L12.30 -17.10L12.35 -17.20L12.32 -17.23L12.32 -17.73L12.38 -18.07L12.45 -18.10L12.50 -18.05L12.53 -17.88L12.60 -17.73L12.60 -17.57L12.68 -17.38L12.75 -16.82L12.80 -16.82L12.88 -16.95L12.88 -17.18L12.95 -17.38L12.97 -17.90L13.03 -18.20L13.03 -19.38L12.97 -19.70L12.95 -20.25L12.88 -20.45L12.88 -20.65L12.80 -20.88L12.78 -21.15L12.68 -21.40L12.68 -21.52L12.57 -21.77L12.57 -21.88L12.50 -22.02L12.53 -22.10L12.57 -22.10L12.70 -21.98L12.80 -21.77L12.90 -21.68L13.00 -21.48L13.28 -21.10L13.32 -20.98L13.38 -20.95L13.45 -20.98L13.40 -21.12L13.38 -21.55L13.28 -21.85L13.25 -22.07L13.07 -22.52L13.07 -22.62L12.97 -22.77L12.95 -22.93L12.90 -22.98L12.88 -23.10L12.78 -23.25L12.78 -23.32L12.20 -24.35L12.25 -24.40L13.15 -23.70L13.20 -23.62L13.28 -23.62L13.15 -24.35L13.07 -24.52L13.05 -24.85L12.97 -25.02L12.97 -25.23L12.88 -25.48L12.85 -25.75L12.78 -25.88L12.78 -26.00L12.65 -26.40L12.45 -26.82L12.45 -26.88L12.53 -26.93L12.97 -26.55L13.30 -26.23L13.35 -26.23L13.35 -26.30L13.28 -26.45L13.28 -26.75L13.25 -26.77L13.28 -27.00L13.10 -27.02Z'),
    head: new Path2D('M8.10 -39.23L12.97 -27.02L13.28 -27.02L13.30 -27.40L13.35 -27.48L13.38 -27.75L13.47 -28.02L13.47 -28.15L13.57 -28.30L13.57 -28.40L13.68 -28.55L13.68 -28.62L14.07 -29.27L14.45 -29.75L14.95 -30.25L15.40 -30.60L15.75 -30.82L16.15 -31.02L16.30 -31.05L16.35 -31.10L16.50 -31.12L16.73 -31.23L16.98 -31.25L17.20 -31.32L17.82 -31.35L17.85 -31.32L18.18 -31.32L18.55 -31.23L18.77 -31.23L18.95 -31.15L19.32 -31.10L19.48 -31.02L19.62 -31.02L19.75 -30.95L19.93 -30.93L20.07 -30.85L20.52 -30.73L20.88 -30.55L21.02 -30.52L21.18 -30.43L21.25 -30.43L22.25 -29.93L22.32 -29.85L22.43 -29.82L22.88 -29.52L22.93 -29.52L23.52 -29.12L24.32 -28.52L25.05 -27.93L26.20 -26.82L26.32 -26.65L26.50 -26.50L27.18 -25.75L27.23 -25.65L27.57 -25.27L28.00 -24.70L28.48 -24.15L28.93 -23.82L29.05 -23.82L29.10 -23.88L29.07 -24.05L28.77 -24.65L27.95 -25.95L27.18 -26.95L25.68 -28.70L23.65 -30.68L22.15 -31.98L22.07 -32.00L20.45 -33.38L20.38 -33.40L19.15 -34.48L18.68 -34.98L18.48 -35.25L18.38 -35.48L18.38 -35.55L18.27 -35.77L18.27 -35.90L18.18 -36.08L18.18 -36.20L18.07 -36.38L18.05 -36.52L17.65 -37.30L17.45 -37.60L17.07 -38.02L16.35 -38.67L15.72 -39.10L15.62 -39.12L15.40 -39.27L15.07 -39.40L14.93 -39.50L14.78 -39.52L14.65 -39.60L14.55 -39.60L14.38 -39.70L14.25 -39.70L14.05 -39.80L13.93 -39.80L13.62 -39.90L13.32 -39.92L13.22 -39.98L12.45 -40.05L11.50 -40.05L11.47 -40.08L11.38 -40.02L10.55 -39.98L10.35 -39.90L10.15 -39.90L9.88 -39.80L9.72 -39.80L9.53 -39.70L9.30 -39.67L9.18 -39.60L9.05 -39.60L8.90 -39.50L8.78 -39.50L8.62 -39.40L8.53 -39.40L8.35 -39.30L8.25 -39.30ZM13.38 -35.95L13.80 -36.42L14.15 -36.62L14.28 -36.62L14.60 -36.73L14.75 -36.73L14.82 -36.67L14.95 -36.67L15.22 -36.60L15.55 -36.40L15.68 -36.27L16.00 -35.80L16.00 -35.73L16.10 -35.55L16.10 -35.38L16.15 -35.20L16.15 -34.83L16.07 -34.55L15.85 -34.30L15.68 -34.30L15.57 -34.40L15.47 -34.65L15.47 -35.05L15.38 -35.25L15.38 -35.35L15.15 -35.60L14.97 -35.70L14.78 -35.75L14.53 -35.75L14.45 -35.70L14.32 -35.70L14.25 -35.62L14.12 -35.58L14.00 -35.45L13.90 -35.27L13.82 -35.00L13.82 -34.65L13.75 -34.48L13.60 -34.38L13.40 -34.40L13.18 -34.67L13.15 -34.85L13.18 -35.48L13.25 -35.58L13.28 -35.75L13.38 -35.88Z'),
    backLeg: new Path2D('M-14.30 -3.52L-14.32 -3.23L-14.28 -2.98L-13.90 -2.52L-13.62 -2.35L-12.85 -2.02L-12.68 -2.00L-12.53 -1.93L-12.40 -1.93L-12.18 -1.82L-12.00 -1.82L-11.85 -1.73L-11.62 -1.73L-11.43 -1.62L-11.28 -1.62L-10.70 -1.43L-10.57 -1.43L-10.45 -1.35L-10.28 -1.32L-10.12 -1.25L-9.68 -1.12L-9.50 -1.02L-9.38 -1.02L-9.03 -0.85L-8.88 -0.82L-8.15 -0.50L-8.07 -0.42L-7.80 -0.30L-7.72 -0.23L-6.55 0.47L-6.47 0.55L-5.83 0.88L-5.72 0.88L-5.45 0.97L-5.20 0.95L-5.08 0.88L-5.00 0.75L-5.03 0.28L-5.25 -0.15L-5.42 -0.38L-5.90 -0.85L-6.20 -1.07L-6.47 -1.20L-6.53 -1.25L-6.50 -1.35L-6.22 -1.32L-6.00 -1.23L-5.88 -1.23L-5.75 -1.15L-5.60 -1.12L-5.42 -1.02L-5.35 -1.02L-5.25 -0.95L-5.12 -0.93L-4.28 -0.50L-3.65 -0.15L-3.33 -0.03L-3.00 0.05L-2.85 0.00L-2.73 -0.17L-2.70 -0.33L-2.73 -0.82L-2.83 -1.05L-3.15 -1.48L-3.23 -1.50L-3.60 -1.80L-4.15 -2.10L-4.22 -2.10L-4.38 -2.20L-4.53 -2.23L-4.58 -2.27L-4.90 -2.40L-4.97 -2.40L-5.45 -2.58L-5.65 -2.60L-5.75 -2.67L-5.62 -2.75L-5.03 -2.73L-4.65 -2.62L-4.42 -2.62L-4.20 -2.55L-3.90 -2.52L-3.65 -2.45L-3.38 -2.45L-3.35 -2.42L-2.95 -2.45L-2.77 -2.52L-2.65 -2.65L-2.62 -2.85L-2.75 -3.10L-3.20 -3.50L-3.80 -3.80L-3.90 -3.80L-4.05 -3.88L-4.30 -3.90L-4.42 -3.95L-5.50 -3.95L-6.17 -3.88L-6.35 -3.90L-6.47 -3.85L-6.70 -3.85L-6.95 -3.80L-7.35 -3.80L-7.65 -3.75L-8.38 -3.75L-8.53 -3.80L-8.70 -3.80L-8.78 -3.85L-9.00 -3.90L-9.28 -4.08L-9.47 -4.30L-9.55 -4.47L-9.55 -4.65L-9.43 -5.20L-9.22 -5.70L-9.20 -5.85L-9.15 -5.90L-9.10 -6.12L-8.95 -6.40L-8.93 -6.55L-8.82 -6.70L-8.80 -6.83L-8.50 -7.42L-8.43 -7.50L-11.15 -7.50L-11.50 -6.67L-11.93 -5.83L-12.00 -5.75L-12.03 -5.65L-12.22 -5.33L-12.65 -4.90L-12.85 -4.80L-12.93 -4.72L-13.45 -4.47L-13.85 -4.20L-14.10 -3.92Z'),
    frontLeg: new Path2D('M1.35 -7.10L1.77 -6.75L2.60 -5.85L3.30 -4.95L3.60 -4.42L3.75 -3.92L3.75 -3.65L3.70 -3.40L3.50 -3.00L3.50 -2.92L3.40 -2.70L3.38 -2.02L3.40 -1.90L3.52 -1.65L3.62 -1.55L3.85 -1.43L3.98 -1.43L4.17 -1.35L4.20 -1.38L4.58 -1.38L4.72 -1.43L5.00 -1.45L5.15 -1.52L5.28 -1.52L5.45 -1.62L5.55 -1.62L5.67 -1.70L5.85 -1.73L6.05 -1.82L6.22 -1.82L6.38 -1.88L6.85 -1.88L7.05 -1.82L7.22 -1.82L7.38 -1.75L7.60 -1.70L7.72 -1.62L7.80 -1.62L7.95 -1.52L8.03 -1.52L8.28 -1.40L8.50 -1.25L8.65 -1.20L8.72 -1.12L9.00 -1.00L9.07 -0.93L9.18 -0.90L9.25 -0.82L9.35 -0.80L9.43 -0.72L9.53 -0.70L10.20 -0.33L10.43 -0.23L10.53 -0.23L10.70 -0.12L10.85 -0.10L11.25 -0.12L11.40 -0.25L11.45 -0.35L11.47 -0.78L11.28 -1.30L10.85 -1.88L10.65 -2.08L9.55 -2.80L9.40 -2.98L9.45 -3.02L9.90 -3.02L9.93 -3.05L10.12 -3.02L10.25 -3.08L10.70 -3.08L10.85 -3.02L10.93 -3.05L11.40 -3.02L11.95 -2.92L12.20 -2.92L12.43 -2.85L12.72 -2.83L13.05 -2.73L13.22 -2.73L13.57 -2.62L14.12 -2.58L14.25 -2.52L14.50 -2.55L14.62 -2.62L14.75 -2.77L14.78 -2.88L14.75 -3.12L14.55 -3.48L14.15 -3.88L13.60 -4.20L13.53 -4.20L13.40 -4.28L13.25 -4.30L13.03 -4.40L12.88 -4.40L12.65 -4.50L12.50 -4.50L12.43 -4.55L12.15 -4.60L12.10 -4.70L12.18 -4.75L12.32 -4.75L12.40 -4.80L12.72 -4.83L12.95 -4.90L13.32 -4.92L13.47 -4.97L15.15 -5.03L15.35 -5.12L15.45 -5.25L15.45 -5.42L15.38 -5.55L15.10 -5.83L14.85 -6.00L14.32 -6.20L14.18 -6.20L13.82 -6.30L13.78 -6.28L13.72 -6.30L12.75 -6.30L12.40 -6.20L12.22 -6.20L11.65 -6.00L11.55 -6.00L10.72 -5.70L10.60 -5.70L10.38 -5.60L10.20 -5.60L9.88 -5.50L9.10 -5.45L9.07 -5.42L8.72 -5.42L8.70 -5.40L8.05 -5.40L8.03 -5.38L6.60 -5.40L6.25 -5.50L6.05 -5.60L5.67 -5.88L5.15 -6.40L4.58 -7.10Z'),
    word: new Path2D('M11.15 -2.05L10.95 -1.82L10.88 -1.57L10.88 6.53L10.90 6.67L11.00 6.85L11.18 7.00L11.35 7.08L11.68 7.12L15.07 7.12L15.50 7.03L15.75 6.80L15.82 6.58L15.82 -1.62L15.78 -1.80L15.55 -2.05L15.32 -2.15L15.12 -2.17L11.57 -2.17L11.38 -2.15L11.22 -2.05ZM-21.02 -2.12L-21.30 -1.95L-21.40 -1.80L-21.48 -1.52L-21.48 6.45L-21.40 6.78L-21.27 6.92L-21.12 7.03L-20.70 7.12L-17.30 7.12L-17.07 7.10L-16.93 7.03L-16.85 7.03L-16.65 6.88L-16.52 6.65L-16.50 6.47L-16.50 -1.52L-16.52 -1.70L-16.62 -1.90L-16.75 -2.02L-17.02 -2.15L-17.23 -2.17L-20.75 -2.17ZM11.00 -6.80L10.90 -6.62L10.88 -6.47L10.88 -3.67L10.90 -3.52L11.00 -3.35L11.18 -3.20L11.35 -3.12L11.68 -3.08L15.03 -3.08L15.28 -3.10L15.35 -3.15L15.50 -3.17L15.75 -3.40L15.82 -3.62L15.82 -6.53L15.78 -6.70L15.57 -6.92L15.28 -7.05L11.45 -7.05L11.12 -6.92ZM-21.38 -6.75L-21.48 -6.45L-21.48 -3.70L-21.40 -3.42L-21.27 -3.27L-21.12 -3.17L-20.70 -3.08L-17.30 -3.08L-17.07 -3.10L-16.85 -3.17L-16.65 -3.33L-16.52 -3.55L-16.50 -3.73L-16.50 -6.42L-16.52 -6.60L-16.62 -6.80L-16.77 -6.92L-17.07 -7.05L-20.90 -7.05L-21.20 -6.92ZM-37.83 -6.80L-37.90 -6.70L-37.95 -6.45L-37.95 6.53L-37.90 6.62L-37.90 6.75L-37.73 6.95L-37.62 7.03L-37.23 7.12L-33.50 7.12L-33.27 7.10L-33.08 7.03L-32.85 6.85L-32.73 6.55L-32.73 1.57L-32.62 1.48L-32.52 1.48L-32.30 1.73L-30.88 3.80L-30.70 4.00L-30.18 4.80L-30.00 5.00L-29.48 5.80L-29.30 6.00L-29.23 6.15L-28.93 6.55L-28.82 6.75L-28.57 6.97L-28.25 7.10L-28.05 7.12L-23.68 7.12L-23.38 7.08L-23.25 7.03L-23.10 6.90L-23.02 6.78L-23.02 6.47L-23.12 6.28L-28.10 -0.12L-27.93 -0.40L-23.43 -6.15L-23.27 -6.45L-23.27 -6.70L-23.32 -6.83L-23.40 -6.90L-23.73 -7.05L-28.43 -7.05L-28.65 -6.95L-28.73 -6.95L-28.95 -6.78L-29.10 -6.50L-30.10 -5.12L-30.73 -4.20L-30.90 -4.00L-31.20 -3.52L-31.38 -3.33L-32.40 -1.85L-32.55 -1.73L-32.67 -1.75L-32.73 -1.80L-32.75 -1.93L-32.73 -6.47L-32.85 -6.80L-32.95 -6.90L-33.30 -7.05L-37.40 -7.05L-37.65 -6.95ZM9.12 -6.83L8.82 -7.03L8.35 -7.08L4.55 -7.05L4.33 -6.95L4.25 -6.95L4.00 -6.70L3.90 -6.42L3.90 -6.25L3.83 -6.03L3.80 -5.75L3.70 -5.38L3.70 -5.22L3.60 -4.88L3.60 -4.70L3.50 -4.38L3.50 -4.15L3.42 -3.95L3.27 -3.00L3.23 -2.90L3.20 -2.62L3.10 -2.27L3.10 -2.10L3.00 -1.77L3.00 -1.55L2.92 -1.35L2.77 -0.40L2.73 -0.30L2.70 -0.03L2.60 0.33L2.60 0.55L2.52 0.80L2.50 1.18L2.42 1.57L2.38 2.58L2.25 2.75L2.10 2.77L2.02 2.75L1.88 2.58L1.77 1.35L1.68 0.93L1.65 0.60L1.57 0.38L1.55 0.10L1.48 -0.12L1.48 -0.28L1.38 -0.57L1.38 -0.72L1.32 -0.82L1.25 -1.30L1.18 -1.50L1.18 -1.65L1.07 -1.95L1.05 -2.23L0.97 -2.42L0.97 -2.58L0.90 -2.77L0.85 -3.15L0.78 -3.35L0.78 -3.50L0.70 -3.70L0.68 -3.98L0.57 -4.28L0.57 -4.42L0.53 -4.53L0.45 -5.00L0.38 -5.20L0.38 -5.35L0.28 -5.65L0.28 -5.80L0.17 -6.12L0.17 -6.28L0.07 -6.60L-0.03 -6.75L-0.25 -6.95L-0.53 -7.05L-4.83 -7.05L-5.17 -6.90L-5.35 -6.72L-5.47 -6.50L-5.50 -6.25L-5.60 -5.95L-5.60 -5.80L-5.70 -5.50L-5.70 -5.35L-5.80 -5.08L-5.80 -4.92L-6.00 -4.17L-6.00 -4.03L-6.10 -3.73L-6.10 -3.58L-6.17 -3.40L-6.22 -3.02L-6.40 -2.40L-6.40 -2.25L-6.50 -1.95L-6.50 -1.80L-6.60 -1.50L-6.60 -1.35L-6.70 -1.07L-6.70 -0.93L-6.80 -0.60L-6.80 -0.45L-6.90 -0.17L-6.90 -0.03L-7.10 0.82L-7.10 1.07L-7.20 1.62L-7.25 2.58L-7.38 2.75L-7.55 2.77L-7.70 2.67L-7.75 2.55L-7.83 1.25L-7.92 0.75L-7.92 0.53L-8.03 0.15L-8.03 -0.07L-8.10 -0.28L-8.12 -0.57L-8.20 -0.78L-8.22 -1.07L-8.30 -1.30L-8.32 -1.57L-8.53 -2.42L-8.53 -2.60L-8.60 -2.83L-8.78 -3.85L-8.82 -3.95L-8.82 -4.12L-8.93 -4.45L-8.95 -4.75L-9.03 -4.95L-9.03 -5.17L-9.10 -5.38L-9.12 -5.67L-9.22 -6.00L-9.22 -6.17L-9.32 -6.50L-9.32 -6.60L-9.43 -6.75L-9.62 -6.92L-9.93 -7.05L-14.15 -7.05L-14.47 -6.92L-14.60 -6.80L-14.65 -6.62L-14.65 -6.30L-14.60 -6.20L-14.60 -6.08L-14.50 -5.83L-14.50 -5.70L-14.40 -5.45L-14.38 -5.22L-14.30 -5.08L-14.28 -4.85L-14.20 -4.70L-14.18 -4.47L-14.10 -4.33L-14.10 -4.20L-13.90 -3.55L-13.90 -3.42L-13.82 -3.27L-13.80 -3.05L-13.72 -2.90L-13.70 -2.67L-13.60 -2.42L-13.55 -2.12L-13.50 -2.05L-13.50 -1.93L-13.40 -1.65L-13.38 -1.45L-13.32 -1.38L-13.30 -1.15L-13.22 -1.00L-13.20 -0.78L-13.15 -0.70L-13.10 -0.40L-13.00 -0.15L-12.97 0.07L-12.90 0.23L-12.88 0.45L-12.80 0.60L-12.80 0.72L-12.60 1.38L-12.60 1.50L-12.50 1.75L-12.47 1.98L-12.32 2.40L-12.28 2.73L-12.20 2.88L-12.20 3.00L-12.00 3.65L-11.97 3.85L-11.93 3.92L-11.90 4.15L-11.82 4.30L-11.80 4.53L-11.70 4.78L-11.70 4.90L-11.60 5.15L-11.57 5.38L-11.50 5.53L-11.50 5.65L-11.32 6.20L-11.30 6.42L-11.22 6.55L-11.20 6.67L-10.97 6.92L-10.82 7.03L-10.40 7.12L-5.42 7.12L-4.97 7.03L-4.88 6.95L-4.62 6.67L-4.62 6.58L-4.55 6.42L-4.53 6.20L-4.42 5.92L-4.42 5.80L-4.22 5.10L-4.22 4.97L-4.12 4.70L-4.12 4.58L-4.03 4.30L-4.03 4.17L-3.73 3.10L-3.62 2.55L-3.42 1.88L-3.42 1.73L-3.33 1.45L-3.33 1.27L-3.25 1.07L-3.23 0.78L-3.12 0.40L-3.10 0.05L-3.02 -0.25L-2.98 -1.05L-2.92 -1.23L-2.75 -1.38L-2.62 -1.38L-2.50 -1.27L-2.42 -1.12L-2.40 -0.42L-2.17 1.00L-2.10 1.23L-2.08 1.52L-2.00 1.73L-2.00 1.88L-1.90 2.17L-1.80 2.73L-1.73 2.90L-1.70 3.15L-1.60 3.42L-1.60 3.58L-1.40 4.28L-1.40 4.40L-1.30 4.70L-1.30 4.83L-1.23 5.00L-1.20 5.25L-1.10 5.53L-1.10 5.67L-1.00 5.95L-1.00 6.10L-0.90 6.38L-0.90 6.50L-0.75 6.80L-0.62 6.92L-0.45 7.03L-0.30 7.05L-0.23 7.10L0.00 7.12L4.90 7.12L5.12 7.10L5.40 7.00L5.67 6.75L5.67 6.70L5.78 6.58L5.78 6.47L5.85 6.33L5.90 6.00L6.05 5.58L6.08 5.35L6.28 4.72L6.30 4.50L6.38 4.35L6.40 4.12L6.47 3.98L6.47 3.85L6.58 3.60L6.62 3.30L6.67 3.23L6.70 3.00L6.78 2.85L6.80 2.62L6.88 2.48L6.88 2.35L6.95 2.17L7.10 1.50L7.35 0.68L7.38 0.47L7.47 0.20L7.47 0.07L7.55 -0.07L7.58 -0.30L7.65 -0.45L7.67 -0.68L7.75 -0.82L7.78 -1.05L7.83 -1.12L7.88 -1.43L7.95 -1.57L7.97 -1.80L8.05 -1.95L8.07 -2.17L8.15 -2.33L8.18 -2.55L8.28 -2.80L8.28 -2.92L8.38 -3.17L8.40 -3.40L8.47 -3.55L8.47 -3.67L8.55 -3.83L8.57 -4.05L8.68 -4.30L8.68 -4.42L8.78 -4.67L8.80 -4.90L8.88 -5.05L8.90 -5.28L8.97 -5.42L8.97 -5.55L9.18 -6.20L9.20 -6.62ZM18.25 -7.05L18.00 -6.88L17.90 -6.70L17.85 -6.45L17.85 -3.80L17.90 -3.52L18.12 -3.27L18.35 -3.17L18.73 -3.12L19.45 -3.12L19.50 -2.98L19.45 -2.90L19.40 -2.62L19.30 -2.45L19.30 -2.38L19.20 -2.15L18.80 -1.50L18.75 -1.32L18.75 -1.12L18.82 -0.93L18.98 -0.78L19.27 -0.57L19.38 -0.55L19.45 -0.47L19.52 -0.47L19.65 -0.38L19.73 -0.38L19.88 -0.30L20.05 -0.28L20.38 -0.30L20.65 -0.42L20.85 -0.57L21.73 -1.45L22.18 -2.08L22.18 -2.12L22.38 -2.42L22.38 -2.50L22.48 -2.65L22.50 -2.80L22.57 -2.90L22.57 -3.00L22.68 -3.23L22.68 -3.35L22.77 -3.65L22.77 -3.90L22.82 -4.17L22.82 -6.53L22.77 -6.72L22.68 -6.88L22.52 -7.00L22.15 -7.12L18.52 -7.12ZM36.75 -6.75L36.60 -6.85L36.20 -6.95L35.98 -6.95L35.65 -7.03L35.20 -7.05L34.58 -7.15L34.25 -7.15L33.58 -7.22L31.40 -7.28L31.38 -7.25L30.57 -7.25L29.68 -7.15L29.40 -7.15L29.10 -7.08L28.75 -7.05L28.40 -6.95L28.25 -6.95L27.98 -6.85L27.85 -6.85L27.60 -6.75L27.50 -6.75L27.30 -6.65L27.20 -6.65L27.02 -6.55L26.95 -6.55L26.27 -6.22L25.77 -5.90L25.20 -5.38L24.90 -5.00L24.77 -4.75L24.70 -4.67L24.60 -4.47L24.57 -4.33L24.50 -4.22L24.50 -4.12L24.40 -3.90L24.40 -3.75L24.32 -3.52L24.27 -3.02L24.30 -2.08L24.40 -1.68L24.40 -1.55L24.50 -1.32L24.50 -1.23L24.73 -0.75L25.12 -0.20L25.48 0.12L26.07 0.53L26.48 0.72L26.62 0.75L26.73 0.82L26.88 0.85L27.00 0.93L27.10 0.93L27.30 1.02L27.40 1.02L27.55 1.10L27.77 1.12L28.05 1.23L28.20 1.23L28.40 1.30L28.70 1.32L28.93 1.40L29.30 1.43L29.68 1.52L29.93 1.52L30.38 1.62L30.60 1.62L30.98 1.73L31.15 1.73L31.35 1.80L31.60 1.82L31.75 1.90L31.95 1.93L32.08 2.00L32.23 2.02L32.35 2.12L32.45 2.15L32.70 2.40L32.80 2.65L32.80 2.90L32.75 3.08L32.65 3.25L32.30 3.55L31.68 3.73L30.90 3.80L29.02 3.80L28.60 3.75L28.20 3.75L27.48 3.65L27.18 3.65L26.70 3.55L26.48 3.55L26.10 3.45L25.88 3.45L25.50 3.35L25.07 3.35L24.75 3.50L24.62 3.65L24.52 3.90L24.38 5.05L24.30 5.33L24.30 5.55L24.20 5.92L24.20 6.45L24.40 6.72L24.55 6.83L24.88 6.92L25.10 6.92L25.57 7.03L25.82 7.03L26.40 7.12L26.70 7.12L27.50 7.22L28.85 7.28L28.88 7.30L29.85 7.30L29.88 7.33L31.50 7.30L31.52 7.28L32.50 7.22L33.08 7.12L33.30 7.12L33.52 7.05L33.92 7.00L34.12 6.92L34.25 6.92L34.50 6.83L34.60 6.83L34.75 6.75L34.92 6.72L35.05 6.65L35.20 6.62L36.25 6.10L36.75 5.72L37.17 5.30L37.48 4.90L37.75 4.38L37.95 3.77L38.05 3.12L38.05 2.17L37.95 1.50L37.67 0.72L37.27 0.12L36.90 -0.25L36.52 -0.53L35.92 -0.85L35.85 -0.85L35.50 -1.02L35.33 -1.05L35.20 -1.12L35.02 -1.15L34.88 -1.23L34.65 -1.25L34.02 -1.43L33.70 -1.45L33.30 -1.55L33.12 -1.55L32.88 -1.62L32.42 -1.68L32.20 -1.75L31.98 -1.75L31.60 -1.85L31.30 -1.88L31.10 -1.95L30.95 -1.95L30.68 -2.05L30.55 -2.05L30.32 -2.15L30.23 -2.15L29.82 -2.35L29.57 -2.58L29.48 -2.75L29.50 -3.17L29.57 -3.30L29.77 -3.50L30.15 -3.67L30.30 -3.67L30.68 -3.77L31.40 -3.80L31.43 -3.83L32.60 -3.83L32.62 -3.80L33.48 -3.77L34.15 -3.67L34.38 -3.67L34.77 -3.58L35.08 -3.55L35.27 -3.48L35.45 -3.48L35.65 -3.40L36.17 -3.40L36.38 -3.50L36.58 -3.75L36.67 -4.15L36.67 -4.38L36.77 -4.75L36.77 -4.97L36.83 -5.10L36.88 -5.55L36.98 -5.95L37.00 -6.17L36.98 -6.47Z'), // centred on 0,0
    wordWidth: 76,
    // legs are cut where they leave the body; they turn around a round joint on that cut
    backHip: { x: -9.8, y: -7.5, r: 1.45 },
    frontHip: { x: 2.95, y: -7.1, r: 1.65 },
    neckTop: { x: 7.9, y: -39.4 },
    neckBottom: { x: 13.0, y: -27.2 },
    neck: { x: 10.4, y: -33.7 },
    beakTip: { x: 28.8, y: -24.0 }
  };

  // The strike pose: head lowered, body tipped forward. The fruit sits where the beak tip lands.
  var STRIKE = { head: 0.9, lean: 0.24 };
  var FRUIT_RX = 6.3, FRUIT_RY = 5.7;
  var FRUIT = (function () {
    var tip = rotAbout(rotAbout(LOGO.beakTip, LOGO.neck, STRIKE.head), { x: 0, y: 0 }, STRIKE.lean);
    var v = (tip.y + FRUIT_RY) / FRUIT_RY;
    return { x: tip.x + FRUIT_RX * Math.sqrt(Math.max(0, 1 - v * v)), y: -FRUIT_RY, contact: tip };
  })();

  // ---------- timeline (seconds) ----------
  var T = {
    walkEnd: 1.1,
    settleEnd: 1.28,
    aimStart: 1.18,   // head goes down
    aimMid: 1.45,     // body leans in until the beak touches the fruit
    flick: 1.58,      // head snaps up
    contact: 1.6,
    flickEnd: 1.68,
    recoverEnd: 2.1,
    impact: 2.04,     // fruit hits the screen
    splatEnd: 2.78,
    logoIn: 2.58,
    revealStart: 3.08,
    end: 3.62
  };

  // ---------- layout: everything is centred ----------
  function layout() {
    var k = Math.min(W / 62, H / 48, 9); // px per logo unit
    var cx = W / 2, cy = H / 2;
    var birdEnd = cx - 5.4 * k; // bird + fruit are 47 units wide, centred on the screen
    return {
      k: k, cx: cx, cy: cy,
      gy: cy + 20 * k,
      birdEnd: birdEnd,
      birdStart: Math.max(birdEnd - 50 * k, -32 * k)
    };
  }

  // ---------- bird ----------
  function birdPose(t, L) {
    var P = { x: L.birdEnd, lean: 0, head: 0, hop: 0, sx: 1, sy: 1, backRot: 0, frontRot: 0, backLift: 0, frontLift: 0 };

    if (t < T.walkEnd) {
      var p = t / T.walkEnd;
      P.x = lerp(L.birdStart, L.birdEnd, ease.outCubic(p));
      var ph = ((P.x - L.birdStart) / (14 * L.k)) * Math.PI * 2;
      var amp = 1 - Math.pow(p, 4);
      P.backRot = 0.38 * Math.sin(ph) * amp;
      P.frontRot = -0.38 * Math.sin(ph) * amp;
      P.backLift = Math.max(0, -Math.cos(ph)) * 1.0 * amp;
      P.frontLift = Math.max(0, Math.cos(ph)) * 1.0 * amp;
      P.hop = -0.8 * Math.abs(Math.sin(ph)) * amp;
      P.lean = 0.025 * Math.sin(ph) * amp;
      P.head = 0.06 * Math.sin(2 * ph) * amp;
    }

    // settle after stopping
    var q = prog(t, T.walkEnd, T.settleEnd);
    if (q > 0 && q < 1) {
      P.sy = 1 - 0.05 * Math.sin(Math.PI * q);
      P.sx = 1 + 0.03 * Math.sin(Math.PI * q);
    }

    if (t >= T.aimStart && t < T.aimMid) {
      var a = ease.inOutSine(prog(t, T.aimStart, T.aimMid));
      P.head = STRIKE.head * a;
      P.lean = -0.03 * a;
    } else if (t >= T.aimMid && t < T.flick) {
      var b = ease.inOutSine(prog(t, T.aimMid, T.flick));
      P.head = STRIKE.head;
      P.lean = lerp(-0.03, STRIKE.lean, b);
    } else if (t >= T.flick && t < T.flickEnd) {
      var f = ease.outCubic(prog(t, T.flick, T.flickEnd));
      P.head = lerp(STRIKE.head, -0.35, f);
      P.lean = lerp(STRIKE.lean, -0.05, f);
    } else if (t >= T.flickEnd) {
      var r = prog(t, T.flickEnd, T.recoverEnd);
      P.head = lerp(-0.35, 0, ease.outBack(r));
      P.lean = lerp(-0.05, 0, ease.outCubic(r));
      P.hop = -1.6 * Math.sin(Math.PI * r);
      P.backRot = 0.15 * Math.sin(Math.PI * r);
      P.frontRot = -0.15 * Math.sin(Math.PI * r);
    }
    return P;
  }

  function drawLeg(path, hip, rot, lift) {
    ctx.save();
    ctx.translate(hip.x, hip.y - lift);
    ctx.rotate(rot);
    ctx.translate(-hip.x, -hip.y);
    ctx.fill(path);
    ctx.stroke(path);
    ctx.restore();
  }

  function neckSector(p, rot) {
    var r = Math.hypot(p.x - LOGO.neck.x, p.y - LOGO.neck.y);
    var a0 = Math.atan2(p.y - LOGO.neck.y, p.x - LOGO.neck.x);
    ctx.moveTo(LOGO.neck.x, LOGO.neck.y);
    ctx.arc(LOGO.neck.x, LOGO.neck.y, r, a0, a0 + rot, rot < 0);
    ctx.closePath();
  }

  function drawBird(P, L) {
    var k = L.k;
    // shadow
    ctx.save();
    ctx.fillStyle = C.shadow;
    var shrink = 1 + P.hop * 0.05;
    ctx.beginPath();
    ctx.ellipse(P.x + 4 * k, L.gy + 0.3 * k, 19 * k * shrink, 1.5 * k * shrink, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.save();
    ctx.translate(P.x, L.gy + P.hop * k);
    ctx.rotate(P.lean);
    ctx.scale(k * P.sx, k * P.sy);
    ctx.fillStyle = C.ink;
    // every part also gets a ~1px outline in the same colour, so the parts overlap
    // and no anti-aliasing seams show where head and legs meet the body
    ctx.strokeStyle = C.ink;
    ctx.lineWidth = 1.2 / k;
    ctx.lineJoin = 'round';

    drawLeg(LOGO.backLeg, LOGO.backHip, P.backRot, P.backLift);
    drawLeg(LOGO.frontLeg, LOGO.frontHip, P.frontRot, P.frontLift);
    // round hip joints hide the cut when legs rotate; they move up with a lifted leg
    ctx.beginPath();
    ctx.arc(LOGO.backHip.x, LOGO.backHip.y - P.backLift, LOGO.backHip.r, 0, Math.PI * 2);
    ctx.moveTo(LOGO.frontHip.x + LOGO.frontHip.r, LOGO.frontHip.y - P.frontLift);
    ctx.arc(LOGO.frontHip.x, LOGO.frontHip.y - P.frontLift, LOGO.frontHip.r, 0, Math.PI * 2);
    ctx.fill();

    ctx.fill(LOGO.body, 'evenodd');
    ctx.stroke(LOGO.body);

    // neck: fill the wedge that opens between body and head when the head turns
    if (Math.abs(P.head) > 0.001) {
      ctx.beginPath();
      neckSector(LOGO.neckTop, P.head);
      neckSector(LOGO.neckBottom, P.head);
      ctx.fill();
      ctx.stroke();
    }
    ctx.save();
    ctx.translate(LOGO.neck.x, LOGO.neck.y);
    ctx.rotate(P.head);
    ctx.translate(-LOGO.neck.x, -LOGO.neck.y);
    ctx.fill(LOGO.head, 'evenodd');
    ctx.stroke(LOGO.head);
    ctx.restore();

    ctx.restore();
  }

  // ---------- kiwi fruit (flat, in the logo style) ----------
  var fuzz = [], speckles = [];
  (function () {
    for (var i = 0; i < 72; i++) fuzz.push({ a: (i / 72) * Math.PI * 2 + rr(-0.03, 0.03), len: rr(0.05, 0.12) });
    for (var j = 0; j < 22; j++) {
      var b = rand() * Math.PI * 2, d = Math.sqrt(rand()) * 0.8;
      speckles.push({ x: Math.cos(b) * d, y: Math.sin(b) * d, r: rr(0.02, 0.045) });
    }
  })();

  function drawFruit(x, y, rx, ry, rot) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rot);
    ctx.scale(rx, ry);
    ctx.fillStyle = C.fruit;
    ctx.beginPath(); ctx.arc(0, 0, 1, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = C.fruitDark;
    ctx.lineWidth = 0.045;
    ctx.lineCap = 'round';
    ctx.beginPath();
    for (var i = 0; i < fuzz.length; i++) {
      var c = Math.cos(fuzz[i].a), s = Math.sin(fuzz[i].a);
      ctx.moveTo(c * 0.97, s * 0.97);
      ctx.lineTo(c * (1 + fuzz[i].len), s * (1 + fuzz[i].len));
    }
    ctx.stroke();
    ctx.fillStyle = C.fruitLight;
    ctx.beginPath(); ctx.ellipse(-0.32, -0.4, 0.42, 0.18, -0.45, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = C.fruitDark;
    for (var j = 0; j < speckles.length; j++) {
      ctx.beginPath(); ctx.arc(speckles[j].x, speckles[j].y, speckles[j].r, 0, Math.PI * 2); ctx.fill();
    }
    ctx.beginPath(); ctx.ellipse(0.985, 0, 0.07, 0.14, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  // ---------- splat (a kiwi slice) ----------
  function makeBlob(waves, arms) {
    var w = [], a = [];
    for (var i = 0; i < waves.length; i++) w.push({ k: waves[i][0], amp: waves[i][1], ph: rand() * Math.PI * 2 });
    for (var j = 0; j < arms; j++) a.push({ ang: rand() * Math.PI * 2, amp: rr(0.14, 0.36), width: rr(0.035, 0.075), tip: rr(0.05, 0.09) });
    return { waves: w, arms: a };
  }
  var splatShape = makeBlob([[3, 0.05], [5, 0.045], [7, 0.03], [11, 0.02]], 12);
  var innerShape = makeBlob([[4, 0.05], [6, 0.04], [9, 0.025]], 0);
  var coreShape = makeBlob([[3, 0.06], [5, 0.04], [8, 0.02]], 0);
  var holeShape = makeBlob([[3, 0.06], [5, 0.05], [8, 0.03], [13, 0.015]], 0);

  var seeds = [], rays = [], droplets = [];
  (function () {
    for (var i = 0; i < 84; i++) {
      seeds.push({ a: (i / 84) * Math.PI * 2 + rr(-0.03, 0.03), d: rr(0.33, 0.46), len: rr(0.022, 0.034), wid: rr(0.009, 0.013), tilt: rr(-0.25, 0.25) });
    }
    for (var j = 0; j < 56; j++) rays.push({ a: (j / 56) * Math.PI * 2 + rr(-0.04, 0.04), end: rr(0.55, 0.78) });
    for (var k = 0; k < 30; k++) droplets.push({ a: rand() * Math.PI * 2, d: rr(1.12, 1.85), s: rr(0.018, 0.055) });
  })();

  function blobRadius(shape, theta) {
    var r = 1, i;
    for (i = 0; i < shape.waves.length; i++) r += shape.waves[i].amp * Math.sin(shape.waves[i].k * theta + shape.waves[i].ph);
    for (i = 0; i < shape.arms.length; i++) {
      var d = Math.atan2(Math.sin(theta - shape.arms[i].ang), Math.cos(theta - shape.arms[i].ang));
      r += shape.arms[i].amp * Math.exp(-(d * d) / (2 * shape.arms[i].width * shape.arms[i].width));
    }
    return r;
  }
  function blobPath(shape, x, y, R) {
    var n = 200;
    ctx.beginPath();
    for (var i = 0; i <= n; i++) {
      var th = (i / n) * Math.PI * 2, r = R * blobRadius(shape, th);
      if (i === 0) ctx.moveTo(x + Math.cos(th) * r, y + Math.sin(th) * r);
      else ctx.lineTo(x + Math.cos(th) * r, y + Math.sin(th) * r);
    }
    ctx.closePath();
  }

  function drawSplat(x, y, R, out) {
    ctx.fillStyle = C.flesh;
    for (var i = 0; i < droplets.length; i++) {
      var d = droplets[i], dist = R * lerp(0.85, d.d, out);
      ctx.beginPath();
      ctx.arc(x + Math.cos(d.a) * dist, y + Math.sin(d.a) * dist, Math.max(1.5, R * d.s), 0, Math.PI * 2);
      ctx.fill();
    }
    blobPath(splatShape, x, y, R);
    ctx.fill();
    for (var a = 0; a < splatShape.arms.length; a++) {
      var arm = splatShape.arms[a], rt = R * blobRadius(splatShape, arm.ang);
      ctx.beginPath();
      ctx.arc(x + Math.cos(arm.ang) * rt, y + Math.sin(arm.ang) * rt, R * arm.tip, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = C.fleshLight;
    blobPath(innerShape, x, y, R * 0.74);
    ctx.fill();
    ctx.strokeStyle = 'rgba(244,240,206,0.35)';
    ctx.lineWidth = Math.max(1, R * 0.006);
    ctx.lineCap = 'round';
    ctx.beginPath();
    for (var r = 0; r < rays.length; r++) {
      var ray = rays[r];
      ctx.moveTo(x + Math.cos(ray.a) * R * 0.27, y + Math.sin(ray.a) * R * 0.27);
      ctx.lineTo(x + Math.cos(ray.a) * R * ray.end, y + Math.sin(ray.a) * R * ray.end);
    }
    ctx.stroke();
    ctx.fillStyle = C.coreEdge;
    blobPath(coreShape, x, y, R * 0.3);
    ctx.fill();
    ctx.fillStyle = C.core;
    blobPath(coreShape, x, y, R * 0.26);
    ctx.fill();
    ctx.fillStyle = C.seed;
    ctx.beginPath();
    for (var s = 0; s < seeds.length; s++) {
      var sd = seeds[s], sx = x + Math.cos(sd.a) * R * sd.d, sy = y + Math.sin(sd.a) * R * sd.d;
      ctx.moveTo(sx + R * sd.len, sy);
      ctx.ellipse(sx, sy, R * sd.len, R * sd.wid, sd.a + sd.tilt, 0, Math.PI * 2);
    }
    ctx.fill();
  }

  function drawWord(x, y, alpha, scale) {
    if (alpha <= 0) return;
    var width = Math.min(W * 0.58, 440);
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(x, y);
    ctx.scale(scale * width / LOGO.wordWidth, scale * width / LOGO.wordWidth);
    ctx.fillStyle = C.ink;
    ctx.fill(LOGO.word);
    ctx.restore();
  }

  // ---------- frame ----------
  function render(t) {
    var L = layout(), k = L.k;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.globalCompositeOperation = 'source-over';
    ctx.globalAlpha = 1;
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);

    var dx = L.cx, dy = L.cy;
    var Rmax = Math.hypot(W / 2, H / 2) / 0.8 + 10;
    var fruitX = L.birdEnd + FRUIT.x * k, fruitY = L.gy + FRUIT.y * k;

    if (t < T.impact + 0.5) {
      // fruit shadow + fruit at rest (pops in at the start)
      var pop = ease.outBack(prog(t, 0.05, 0.4));
      var shadowA = t < T.contact ? 1 : 1 - prog(t, T.contact, T.contact + 0.25);
      if (shadowA > 0) {
        ctx.fillStyle = C.shadow;
        ctx.globalAlpha = shadowA;
        ctx.beginPath();
        ctx.ellipse(fruitX, L.gy + 0.3 * k, FRUIT_RX * k * pop, 1.1 * k * pop, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      drawBird(birdPose(t, L), L);
      // veil: bird fades in at the start and recedes while the fruit flies at the viewer
      var veil = Math.max(1 - clamp(t / 0.22, 0, 1), ease.inOutSine(prog(t, T.contact + 0.12, T.impact - 0.04)) * 0.92);
      if (veil > 0) {
        ctx.globalAlpha = veil;
        ctx.fillStyle = C.bg;
        ctx.fillRect(0, 0, W, H);
        ctx.globalAlpha = 1;
      }
      if (t < T.contact) {
        var squash = t > T.flick ? prog(t, T.flick, T.contact) : 0;
        drawFruit(fruitX, fruitY + FRUIT_RY * k * 0.06 * squash, FRUIT_RX * k * pop * (1 + 0.08 * squash), FRUIT_RY * k * pop * (1 - 0.1 * squash), 0);
      }
    }

    // impact lines where the beak hits
    if (t >= T.contact && t < T.contact + 0.22) {
      var ip = prog(t, T.contact, T.contact + 0.22);
      var hx = L.birdEnd + FRUIT.contact.x * k, hy = L.gy + FRUIT.contact.y * k;
      var base = Math.atan2(hy - fruitY, hx - fruitX);
      ctx.strokeStyle = C.ink;
      ctx.lineCap = 'round';
      ctx.lineWidth = 0.75 * k;
      ctx.globalAlpha = 1 - ip;
      ctx.beginPath();
      for (var i = -2; i <= 2; i++) {
        var a = base + i * 0.38, r0 = (1 + ip * 1.6) * k, r1 = r0 + (3.6 - Math.abs(i) * 0.7) * k * (1 - ip * 0.4);
        ctx.moveTo(hx + Math.cos(a) * r0, hy + Math.sin(a) * r0);
        ctx.lineTo(hx + Math.cos(a) * r1, hy + Math.sin(a) * r1);
      }
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // fruit flying at the screen
    if (t >= T.contact && t < T.impact) {
      var p = prog(t, T.contact, T.impact);
      var s = ease.outSine(p);
      var c1x = dx + 6 * k, c1y = L.gy - 66 * k; // up over the bird's head, then down at the viewer
      var fx = (1 - s) * (1 - s) * fruitX + 2 * (1 - s) * s * c1x + s * s * dx;
      var fy = (1 - s) * (1 - s) * fruitY + 2 * (1 - s) * s * c1y + s * s * dy;
      var grow = ease.inQuad(p);
      var big = Math.min(W, H) * 0.14;
      drawFruit(fx, fy, lerp(FRUIT_RX * k, big, grow), lerp(FRUIT_RY * k, big * 0.9, grow), -p * Math.PI * 2.4);
    }

    // splat in the centre
    if (t >= T.impact) {
      var sp = prog(t, T.impact, T.splatEnd);
      var R0 = Math.min(W, H) * 0.14, Rs = Math.min(W, H) * 0.34, R;
      if (sp < 0.28) R = lerp(R0, Rs, ease.outBack(sp / 0.28));
      else if (sp < 0.46) R = Rs * (1 + 0.05 * ease.outQuad((sp - 0.28) / 0.18));
      else R = lerp(Rs * 1.05, Rmax, ease.inOutCubic((sp - 0.46) / 0.54));
      drawSplat(dx, dy, R, ease.outCubic(clamp(sp / 0.3, 0, 1)));
    }

    if (t >= T.logoIn) {
      var la = ease.outCubic(prog(t, T.logoIn, T.logoIn + 0.35));
      var fade = 1 - prog(t, T.revealStart - 0.15, T.revealStart + 0.05);
      drawWord(dx, dy, la * fade, lerp(0.85, 1, ease.outBack(la)));
    }

    // reveal the page through a hole that grows from the centre
    if (t >= T.revealStart) {
      var rp = ease.inCubic(prog(t, T.revealStart, T.end));
      ctx.globalCompositeOperation = 'destination-out';
      ctx.fillStyle = '#000';
      blobPath(holeShape, dx, dy, Math.max(0.5, rp * Rmax * 1.3));
      ctx.fill();
      ctx.globalCompositeOperation = 'source-over';
    }
  }

  // ---------- loop ----------
  var start = null, offset = 0, finished = false;
  function finish() {
    if (finished) return;
    finished = true;
    window.removeEventListener('resize', resize);
    if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
  }
  function frame(now) {
    if (finished) return;
    if (start === null) start = now;
    var t = (now - start) / 1000 + offset;
    if (t >= T.end) { finish(); return; }
    render(t);
    requestAnimationFrame(frame);
  }
  // Tap / click skips to the reveal
  canvas.addEventListener('pointerdown', function () {
    if (start === null) return;
    var t = (performance.now() - start) / 1000 + offset;
    if (t < T.revealStart) offset += T.revealStart - t;
  });
  render(0);
  requestAnimationFrame(frame);
  setTimeout(finish, 8000); // never block the page
})();
