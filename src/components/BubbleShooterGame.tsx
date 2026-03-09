'use client';

// ============================================================
// BubbleShooterGame — Canvas-based game with full game loop
// ============================================================

import {
  useEffect, useRef, useState, useCallback, type MouseEvent, type TouchEvent,
} from 'react';
import { AnimatePresence, motion } from 'framer-motion';

import {
  BubbleColor, Difficulty, FallingBubble, GameConfig, GameData, GamePhase, Particle, PopEffect,
} from '@/types/game';
import {
  DIFFICULTY_SETTINGS, getBubbleCenter, findNearestGridCell,
  createInitialGrid, createRandomRow, isGridEmpty, hasBubblePastRow,
  getColsForRow, ensureGridRows,
} from '@/lib/grid';
import { findCluster, findFloatingBubbles, removeBubbles } from '@/lib/matching';
import { moveProjectile, shouldSnap, getVelocityFromAngle, getAimAngle, traceAimPath } from '@/lib/physics';
import { BUBBLE_COLORS, randomColor } from '@/lib/colors';
import { useSound } from '@/hooks/useSound';
import { useHighScore } from '@/hooks/useHighScore';

import StartScreen from './StartScreen';
import EndScreen   from './EndScreen';
import PauseMenu   from './PauseMenu';

// ── Constants ────────────────────────────────────────────────
const MAX_GRID_ROWS     = 20;   // grid never grows beyond this
const POP_LIFETIME      = 40;   // frames a pop effect lives
const FALLING_LIFETIME  = 60;   // frames a falling bubble lives
const PARTICLES_PER_POP = 8;    // particles per bubble in a cluster
const SCORE_PER_BUBBLE  = 10;   // base score
const SCORE_PER_FALL    = 5;    // bonus per falling bubble
const LEVEL_SCORE_STEP  = 400;  // score per level-up

// ── Helpers ──────────────────────────────────────────────────

/** Build a GameConfig from current canvas dimensions */
function buildConfig(canvas: HTMLCanvasElement): GameConfig {
  const W = canvas.width;
  const H = canvas.height;
  // Bubble radius adapts to canvas width (max 22 on desktop)
  const bubbleRadius = Math.min(Math.floor(W / (9 * 2 + 1)), 22);
  const rowHeight    = bubbleRadius * Math.sqrt(3);
  const gridTop      = bubbleRadius + 8;
  const shooterY     = H - bubbleRadius * 3.5;

  return { bubbleRadius, rowHeight, gridTop, shooterX: W / 2, shooterY, canvasWidth: W, canvasHeight: H };
}

/** Create a blank game data object */
function createGameData(difficulty: Difficulty, config: GameConfig): GameData {
  const settings  = DIFFICULTY_SETTINGS[difficulty];
  const colors    = settings.colors;
  const grid      = ensureGridRows(createInitialGrid(difficulty, colors), MAX_GRID_ROWS);
  const nextColor = randomColor(colors);

  return {
    grid, projectile: null, nextColor,
    score: 0, shots: 0, level: 1,
    difficulty, phase: 'playing',
    popEffects: [], fallingBubbles: [],
    aimAngle: -Math.PI / 2,
    newBubbleRow: false,
  };
}

/** Generate particle burst for a popped bubble */
function makePop(x: number, y: number, color: BubbleColor): PopEffect {
  const { particle } = BUBBLE_COLORS[color];
  const particles: Particle[] = Array.from({ length: PARTICLES_PER_POP }, () => {
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 4;
    return {
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      alpha: 1,
      size: 3 + Math.random() * 4,
      color: particle,
    };
  });
  return { x, y, color, particles, age: 0 };
}

// ── Draw helpers ──────────────────────────────────────────────

function drawBubble(
  ctx: CanvasRenderingContext2D,
  cx: number, cy: number,
  radius: number,
  color: BubbleColor,
  alpha = 1,
): void {
  const { fill, glow, dark } = BUBBLE_COLORS[color];
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.shadowBlur  = 18;
  ctx.shadowColor = glow;

  // Main gradient
  const grad = ctx.createRadialGradient(
    cx - radius * 0.3, cy - radius * 0.35, radius * 0.05,
    cx, cy, radius,
  );
  grad.addColorStop(0, '#ffffffcc');
  grad.addColorStop(0.25, fill);
  grad.addColorStop(1, dark);

  ctx.beginPath();
  ctx.arc(cx, cy, radius - 1, 0, Math.PI * 2);
  ctx.fillStyle = grad;
  ctx.fill();

  // Outline
  ctx.shadowBlur  = 0;
  ctx.strokeStyle = `${glow}88`;
  ctx.lineWidth   = 1.5;
  ctx.stroke();

  // Specular highlight
  const shine = ctx.createRadialGradient(
    cx - radius * 0.38, cy - radius * 0.38, 0,
    cx - radius * 0.38, cy - radius * 0.38, radius * 0.55,
  );
  shine.addColorStop(0, 'rgba(255,255,255,0.55)');
  shine.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.beginPath();
  ctx.arc(cx, cy, radius - 1, 0, Math.PI * 2);
  ctx.fillStyle = shine;
  ctx.fill();

  ctx.restore();
}

function drawBackground(ctx: CanvasRenderingContext2D, W: number, H: number): void {
  const bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0, '#06061a');
  bg.addColorStop(1, '#10082a');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // Subtle dot-grid
  ctx.fillStyle = 'rgba(255,255,255,0.025)';
  const spacing = 28;
  for (let x = spacing / 2; x < W; x += spacing) {
    for (let y = spacing / 2; y < H; y += spacing) {
      ctx.beginPath();
      ctx.arc(x, y, 1.2, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

function drawAimGuide(
  ctx: CanvasRenderingContext2D,
  path: [number, number][],
  color: BubbleColor,
): void {
  if (path.length < 2) return;
  const { glow } = BUBBLE_COLORS[color];

  ctx.save();
  ctx.setLineDash([8, 10]);
  ctx.lineWidth   = 2.5;
  ctx.strokeStyle = `${glow}99`;
  ctx.shadowBlur  = 8;
  ctx.shadowColor = glow;

  ctx.beginPath();
  ctx.moveTo(path[0][0], path[0][1]);
  for (let i = 1; i < path.length; i++) ctx.lineTo(path[i][0], path[i][1]);
  ctx.stroke();
  ctx.restore();
}

function drawShooter(
  ctx: CanvasRenderingContext2D,
  config: GameConfig,
  angle: number,
  nextColor: BubbleColor,
): void {
  const { shooterX, shooterY, bubbleRadius } = config;
  const { glow } = BUBBLE_COLORS[nextColor];
  const barrelLen = bubbleRadius * 2.2;

  ctx.save();

  // Barrel
  ctx.translate(shooterX, shooterY);
  ctx.rotate(angle + Math.PI / 2);

  const barrelGrad = ctx.createLinearGradient(-6, 0, 6, 0);
  barrelGrad.addColorStop(0, '#334');
  barrelGrad.addColorStop(0.5, '#aac');
  barrelGrad.addColorStop(1, '#334');

  ctx.shadowBlur  = 12;
  ctx.shadowColor = glow;
  ctx.fillStyle   = barrelGrad;
  ctx.beginPath();
  ctx.roundRect(-6, -barrelLen, 12, barrelLen, 4);
  ctx.fill();

  ctx.restore();

  // Base platform
  ctx.save();
  ctx.shadowBlur  = 16;
  ctx.shadowColor = glow;
  const baseGrad  = ctx.createRadialGradient(shooterX, shooterY, 0, shooterX, shooterY, bubbleRadius * 1.4);
  baseGrad.addColorStop(0, '#334466');
  baseGrad.addColorStop(1, '#112233');
  ctx.beginPath();
  ctx.arc(shooterX, shooterY, bubbleRadius * 1.4, 0, Math.PI * 2);
  ctx.fillStyle = baseGrad;
  ctx.fill();
  ctx.restore();

  // Next-bubble preview (inside base)
  drawBubble(ctx, shooterX, shooterY, bubbleRadius * 0.75, nextColor);
}

function drawHUD(
  ctx: CanvasRenderingContext2D,
  config: GameConfig,
  score: number,
  level: number,
  highScore: number,
  shots: number,
  shotsPerDescend: number,
): void {
  const { canvasWidth, bubbleRadius } = config;
  const y = bubbleRadius * 0.9;

  ctx.save();
  ctx.font      = `bold ${Math.round(bubbleRadius * 0.85)}px 'Courier New', monospace`;
  ctx.textAlign = 'left';

  // Score
  ctx.fillStyle = '#00ffee';
  ctx.fillText(`SCORE ${score.toString().padStart(6, '0')}`, 12, y);

  // Level (centre)
  ctx.textAlign = 'center';
  ctx.fillStyle = '#cc44ff';
  ctx.fillText(`LVL ${level}`, canvasWidth / 2, y);

  // High-score (right)
  ctx.textAlign = 'right';
  ctx.fillStyle = '#ffee00';
  ctx.fillText(`BEST ${highScore.toString().padStart(6, '0')}`, canvasWidth - 12, y);

  // Shot progress bar (thin bar just below HUD)
  const barY  = bubbleRadius * 1.7;
  const barW  = canvasWidth - 24;
  const barH  = 4;
  const prog  = shots / shotsPerDescend;
  ctx.fillStyle = 'rgba(255,255,255,0.1)';
  ctx.beginPath();
  ctx.roundRect(12, barY, barW, barH, 2);
  ctx.fill();
  ctx.fillStyle = prog > 0.75 ? '#ff3366' : '#00ffee';
  ctx.beginPath();
  ctx.roundRect(12, barY, barW * prog, barH, 2);
  ctx.fill();

  ctx.restore();
}

function drawDangerLine(
  ctx: CanvasRenderingContext2D,
  config: GameConfig,
  maxRows: number,
): void {
  const { gridTop, rowHeight, canvasWidth, bubbleRadius } = config;
  const dangerY = gridTop + maxRows * rowHeight - rowHeight / 2;

  ctx.save();
  ctx.setLineDash([6, 6]);
  ctx.lineWidth   = 1.5;
  ctx.strokeStyle = 'rgba(255, 50, 50, 0.5)';
  ctx.shadowBlur  = 6;
  ctx.shadowColor = '#ff2222';
  ctx.beginPath();
  ctx.moveTo(0, dangerY);
  ctx.lineTo(canvasWidth, dangerY);
  ctx.stroke();
  ctx.restore();
}

// ── Main component ────────────────────────────────────────────

export default function BubbleShooterGame() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gsRef     = useRef<GameData | null>(null);        // mutable game state
  const cfgRef    = useRef<GameConfig | null>(null);      // canvas config
  const rafRef    = useRef<number>(0);
  const wrapperRef= useRef<HTMLDivElement>(null);

  // React state for UI re-renders
  const [uiPhase,     setUiPhase]     = useState<GamePhase>('start');
  const [uiScore,     setUiScore]     = useState(0);
  const [uiLevel,     setUiLevel]     = useState(1);
  const [uiNextColor, setUiNextColor] = useState<BubbleColor>('cyan');
  const [uiDifficulty,setUiDifficulty]= useState<Difficulty>('medium');

  const sound = useSound();
  const { highScore, updateHighScore } = useHighScore(uiDifficulty);

  // ── Game initialisation ──────────────────────────────────

  const initGame = useCallback((difficulty: Difficulty) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const config = buildConfig(canvas);
    cfgRef.current = config;

    const gs = createGameData(difficulty, config);
    gsRef.current = gs;

    setUiPhase('playing');
    setUiScore(0);
    setUiLevel(1);
    setUiNextColor(gs.nextColor);
    setUiDifficulty(difficulty);
  }, []);

  // ── Shoot projectile ─────────────────────────────────────

  const shoot = useCallback(() => {
    const gs  = gsRef.current;
    const cfg = cfgRef.current;
    if (!gs || !cfg || gs.phase !== 'playing' || gs.projectile) return;

    const vel = getVelocityFromAngle(gs.aimAngle);
    gs.projectile = {
      x: cfg.shooterX,
      y: cfg.shooterY,
      vx: vel.vx,
      vy: vel.vy,
      color: gs.nextColor,
    };

    // Pick next colour from difficulty colours
    const settings = DIFFICULTY_SETTINGS[gs.difficulty];
    gs.nextColor = randomColor(settings.colors);
    setUiNextColor(gs.nextColor);
    sound.shoot();
  }, [sound]);

  // ── Pointer / touch helpers ──────────────────────────────

  const updateAim = useCallback((clientX: number, clientY: number) => {
    const gs  = gsRef.current;
    const cfg = cfgRef.current;
    const canvas = canvasRef.current;
    if (!gs || !cfg || !canvas || gs.phase !== 'playing') return;

    const rect  = canvas.getBoundingClientRect();
    const scaleX = canvas.width  / rect.width;
    const scaleY = canvas.height / rect.height;
    const px = (clientX - rect.left) * scaleX;
    const py = (clientY - rect.top)  * scaleY;

    gs.aimAngle = getAimAngle(cfg.shooterX, cfg.shooterY, px, py);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent<HTMLCanvasElement>) => {
    updateAim(e.clientX, e.clientY);
  }, [updateAim]);

  const handleClick = useCallback((e: MouseEvent<HTMLCanvasElement>) => {
    updateAim(e.clientX, e.clientY);
    shoot();
  }, [updateAim, shoot]);

  const handleTouchMove = useCallback((e: TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const t = e.touches[0];
    if (t) updateAim(t.clientX, t.clientY);
  }, [updateAim]);

  const handleTouchEnd = useCallback((e: TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    shoot();
  }, [shoot]);

  // ── Process snapped projectile ───────────────────────────

  const processSnap = useCallback((snapRow: number, snapCol: number) => {
    const gs  = gsRef.current;
    const cfg = cfgRef.current;
    if (!gs || !cfg || !gs.projectile) return;

    const color = gs.projectile.color;

    // Place bubble in grid
    while (gs.grid.length <= snapRow) {
      const r = gs.grid.length;
      gs.grid.push(Array(getColsForRow(r)).fill(null));
    }
    gs.grid[snapRow][snapCol] = color;
    gs.projectile = null;

    // Count shots, check descend
    gs.shots++;
    const settings = DIFFICULTY_SETTINGS[gs.difficulty];
    if (gs.shots >= settings.shotsPerDescend) {
      gs.shots = 0;
      // Add a new row at the top (grid shifts down)
      const newRow = createRandomRow(0, settings.colors);
      gs.grid.unshift(newRow);
      // Keep grid from growing too large
      while (gs.grid.length > MAX_GRID_ROWS) gs.grid.pop();
      gs.newBubbleRow = true;
      sound.descend();

      if (hasBubblePastRow(gs.grid, settings.maxRows)) {
        gs.phase = 'lost';
        setUiPhase('lost');
        updateHighScore(gs.score);
        sound.gameOver();
        return;
      }
    }

    // Match cluster
    const cluster = findCluster(gs.grid, snapRow, snapCol);
    if (cluster.length >= 3) {
      // Score
      const multiplier = Math.max(1, Math.round(cluster.length / 3));
      const gained = cluster.length * SCORE_PER_BUBBLE * multiplier;

      // Build pop effects
      for (const { row, col } of cluster) {
        const { cx, cy } = getBubbleCenter(row, col, cfg);
        gs.popEffects.push(makePop(cx, cy, color));
      }

      removeBubbles(gs.grid, cluster);
      sound.pop(cluster.length);

      // Find & drop floating bubbles
      const floating = findFloatingBubbles(gs.grid);
      let floatScore = 0;
      for (const { row, col } of floating) {
        const floatColor = gs.grid[row][col]!;
        const { cx, cy } = getBubbleCenter(row, col, cfg);
        gs.fallingBubbles.push({ x: cx, y: cy, color: floatColor, vy: 2, age: 0 });
        floatScore += SCORE_PER_FALL;
      }
      removeBubbles(gs.grid, floating);

      gs.score += gained + floatScore;

      // Level up
      const newLevel = Math.floor(gs.score / LEVEL_SCORE_STEP) + 1;
      if (newLevel > gs.level) { gs.level = newLevel; setUiLevel(newLevel); }

      setUiScore(gs.score);
      updateHighScore(gs.score);

      // Win condition
      if (isGridEmpty(gs.grid)) {
        gs.phase = 'won';
        setUiPhase('won');
        sound.win();
        return;
      }
    } else {
      sound.land();
    }

    // Game-over check after placing
    if (hasBubblePastRow(gs.grid, settings.maxRows)) {
      gs.phase = 'lost';
      setUiPhase('lost');
      updateHighScore(gs.score);
      sound.gameOver();
    }
  }, [sound, updateHighScore]);

  // ── Game loop ────────────────────────────────────────────

  const gameLoop = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx    = canvas?.getContext('2d');
    const gs     = gsRef.current;
    const cfg    = cfgRef.current;

    if (!canvas || !ctx || !gs || !cfg) {
      rafRef.current = requestAnimationFrame(gameLoop);
      return;
    }

    const W = canvas.width;
    const H = canvas.height;

    // ── UPDATE ──

    if (gs.phase === 'playing') {
      // Move projectile
      if (gs.projectile) {
        gs.projectile = moveProjectile(gs.projectile, cfg);

        if (shouldSnap(gs.projectile, gs.grid, cfg)) {
          // Find snap cell
          const cell = findNearestGridCell(
            gs.projectile.x, gs.projectile.y, gs.grid, cfg,
          );
          if (cell) {
            processSnap(cell.row, cell.col);
          } else {
            // No valid cell — discard projectile
            gs.projectile = null;
          }
        }
      }

      // Age pop effects
      gs.popEffects = gs.popEffects.filter(e => e.age < POP_LIFETIME);
      for (const e of gs.popEffects) {
        e.age++;
        for (const p of e.particles) {
          p.x    += p.vx;
          p.y    += p.vy;
          p.vy   += 0.15; // gravity
          p.vx   *= 0.97;
          p.alpha = 1 - e.age / POP_LIFETIME;
        }
      }

      // Age falling bubbles
      gs.fallingBubbles = gs.fallingBubbles.filter(b => b.age < FALLING_LIFETIME);
      for (const b of gs.fallingBubbles) {
        b.age++;
        b.vy += 0.4;
        b.y  += b.vy;
      }
    }

    // ── RENDER ──
    drawBackground(ctx, W, H);

    // Grid bubbles
    for (let r = 0; r < gs.grid.length; r++) {
      for (let c = 0; c < gs.grid[r].length; c++) {
        const color = gs.grid[r][c];
        if (!color) continue;
        const { cx, cy } = getBubbleCenter(r, c, cfg);
        if (cy > H + cfg.bubbleRadius) continue; // off-screen
        drawBubble(ctx, cx, cy, cfg.bubbleRadius, color);
      }
    }

    // Danger line
    const settings = DIFFICULTY_SETTINGS[gs.difficulty];
    drawDangerLine(ctx, cfg, settings.maxRows);

    // Pop particles
    for (const e of gs.popEffects) {
      for (const p of e.particles) {
        ctx.save();
        ctx.globalAlpha = p.alpha;
        ctx.shadowBlur  = 10;
        ctx.shadowColor = p.color;
        ctx.fillStyle   = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * (1 - e.age / POP_LIFETIME), 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    // Falling bubbles
    for (const b of gs.fallingBubbles) {
      const alpha = 1 - b.age / FALLING_LIFETIME;
      drawBubble(ctx, b.x, b.y, cfg.bubbleRadius * 0.85, b.color, alpha);
    }

    // Aim guide (only when no projectile in flight)
    if (!gs.projectile && gs.phase === 'playing') {
      const path = traceAimPath(cfg.shooterX, cfg.shooterY, gs.aimAngle, cfg);
      drawAimGuide(ctx, path, gs.nextColor);
    }

    // Projectile
    if (gs.projectile) {
      drawBubble(ctx, gs.projectile.x, gs.projectile.y, cfg.bubbleRadius, gs.projectile.color);
    }

    // Shooter
    drawShooter(ctx, cfg, gs.aimAngle, gs.nextColor);

    // HUD
    drawHUD(ctx, cfg, gs.score, gs.level, highScore, gs.shots, settings.shotsPerDescend);

    rafRef.current = requestAnimationFrame(gameLoop);
  }, [processSnap, highScore]);

  // ── Resize handler ───────────────────────────────────────

  useEffect(() => {
    const canvas  = canvasRef.current;
    const wrapper = wrapperRef.current;
    if (!canvas || !wrapper) return;

    const resize = () => {
      canvas.width  = wrapper.clientWidth;
      canvas.height = wrapper.clientHeight;
      cfgRef.current = buildConfig(canvas);
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(wrapper);
    return () => ro.disconnect();
  }, []);

  // ── Game loop lifecycle ──────────────────────────────────

  useEffect(() => {
    rafRef.current = requestAnimationFrame(gameLoop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [gameLoop]);

  // ── Keyboard shortcuts ───────────────────────────────────

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const gs = gsRef.current;
      if (!gs) return;

      if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') {
        if (gs.phase === 'playing') {
          gs.phase = 'paused';
          setUiPhase('paused');
        } else if (gs.phase === 'paused') {
          gs.phase = 'playing';
          setUiPhase('playing');
        }
      }
      if (e.key === 'm' || e.key === 'M') sound.toggleMute();
      if (e.key === ' ') { e.preventDefault(); shoot(); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [shoot, sound]);

  // ── Pause / resume callbacks ─────────────────────────────

  const handlePause = useCallback(() => {
    const gs = gsRef.current;
    if (!gs || gs.phase !== 'playing') return;
    gs.phase = 'paused';
    setUiPhase('paused');
  }, []);

  const handleResume = useCallback(() => {
    const gs = gsRef.current;
    if (!gs || gs.phase !== 'paused') return;
    gs.phase = 'playing';
    setUiPhase('playing');
  }, []);

  const handleMenu = useCallback(() => {
    const gs = gsRef.current;
    if (gs) gs.phase = 'start';
    setUiPhase('start');
  }, []);

  const handleStart = useCallback((diff: Difficulty) => {
    initGame(diff);
  }, [initGame]);

  const handleRestart = useCallback(() => {
    const gs = gsRef.current;
    if (!gs) return;
    initGame(gs.difficulty);
  }, [initGame]);

  // ── Mobile aim buttons ───────────────────────────────────

  const aimIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startAimLeft = useCallback(() => {
    aimIntervalRef.current = setInterval(() => {
      const gs = gsRef.current;
      if (gs) gs.aimAngle = Math.max(-Math.PI + 0.18, gs.aimAngle - 0.04);
    }, 16);
  }, []);

  const startAimRight = useCallback(() => {
    aimIntervalRef.current = setInterval(() => {
      const gs = gsRef.current;
      if (gs) gs.aimAngle = Math.min(-0.18, gs.aimAngle + 0.04);
    }, 16);
  }, []);

  const stopAim = useCallback(() => {
    if (aimIntervalRef.current) {
      clearInterval(aimIntervalRef.current);
      aimIntervalRef.current = null;
    }
  }, []);

  // ── Render ───────────────────────────────────────────────

  return (
    <div className="relative w-full h-full flex flex-col bg-[#07071a] overflow-hidden select-none">

      {/* Top control bar (shown during gameplay) */}
      <AnimatePresence>
        {(uiPhase === 'playing' || uiPhase === 'paused') && (
          <motion.div
            key="topbar"
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -50, opacity: 0 }}
            className="flex items-center justify-between px-4 py-2 bg-black/30 backdrop-blur border-b border-white/5 z-10 shrink-0"
          >
            {/* Mute */}
            <button
              onClick={sound.toggleMute}
              className="text-xl w-9 h-9 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors"
              title="Toggle sound (M)"
            >
              {sound.muted ? '🔇' : '🔊'}
            </button>

            {/* Title */}
            <span className="text-xs font-bold tracking-widest text-slate-400 uppercase">
              Bubble Shooter
            </span>

            {/* Pause */}
            <button
              onClick={uiPhase === 'paused' ? handleResume : handlePause}
              className="text-xl w-9 h-9 flex items-center justify-center rounded-lg hover:bg-white/10 transition-colors"
              title="Pause (P)"
            >
              {uiPhase === 'paused' ? '▶' : '⏸'}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Canvas area */}
      <div ref={wrapperRef} className="relative flex-1 overflow-hidden">
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onClick={handleClick}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          className="block w-full h-full cursor-crosshair touch-none"
        />

        {/* Overlays */}
        <AnimatePresence>
          {uiPhase === 'start' && (
            <motion.div key="start" className="absolute inset-0">
              <StartScreen onStart={handleStart} />
            </motion.div>
          )}
        </AnimatePresence>

        <PauseMenu
          visible={uiPhase === 'paused'}
          onResume={handleResume}
          onMenu={handleMenu}
        />

        <AnimatePresence>
          {(uiPhase === 'won' || uiPhase === 'lost') && (
            <motion.div key="end" className="absolute inset-0">
              <EndScreen
                phase={uiPhase}
                score={uiScore}
                highScore={highScore}
                difficulty={uiDifficulty}
                onRestart={handleRestart}
                onMenu={handleMenu}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Mobile controls bar */}
      <AnimatePresence>
        {(uiPhase === 'playing' || uiPhase === 'paused') && (
          <motion.div
            key="mobilectrl"
            initial={{ y: 80, opacity: 0 }}
            animate={{ y: 0,  opacity: 1 }}
            exit={{ y: 80,    opacity: 0 }}
            className="sm:hidden flex items-center justify-between px-6 py-3 bg-black/40 backdrop-blur border-t border-white/5 shrink-0 z-10"
          >
            {/* Aim Left */}
            <button
              onPointerDown={startAimLeft}
              onPointerUp={stopAim}
              onPointerLeave={stopAim}
              className="w-14 h-14 rounded-2xl bg-white/10 active:bg-white/20 border border-white/20 flex items-center justify-center text-2xl font-bold text-cyan-400 transition-colors"
            >
              ◀
            </button>

            {/* Shoot */}
            <button
              onPointerDown={shoot}
              className="w-20 h-20 rounded-full bg-cyan-500/20 active:bg-cyan-500/40 border-2 border-cyan-400 flex items-center justify-center text-2xl transition-colors shadow-lg shadow-cyan-500/30"
            >
              🎯
            </button>

            {/* Aim Right */}
            <button
              onPointerDown={startAimRight}
              onPointerUp={stopAim}
              onPointerLeave={stopAim}
              className="w-14 h-14 rounded-2xl bg-white/10 active:bg-white/20 border border-white/20 flex items-center justify-center text-2xl font-bold text-cyan-400 transition-colors"
            >
              ▶
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
