// ============================================================
// Projectile Physics: movement, wall bouncing, aim angle
// ============================================================

import { Projectile, GameConfig } from '@/types/game';
import { getBubbleCenter } from './grid';
import { BubbleColor } from '@/types/game';

/** Pixels the projectile travels per frame at 60 fps */
const SPEED = 14;

/** Convert an aim angle (radians) to a velocity vector */
export function getVelocityFromAngle(angle: number): { vx: number; vy: number } {
  return {
    vx: Math.cos(angle) * SPEED,
    vy: Math.sin(angle) * SPEED,
  };
}

/**
 * Compute the aim angle from the shooter to a pointer/touch position.
 * Clamped so the player cannot shoot downward or perfectly horizontal.
 */
export function getAimAngle(
  shooterX: number,
  shooterY: number,
  targetX: number,
  targetY: number,
): number {
  const raw = Math.atan2(targetY - shooterY, targetX - shooterX);
  // Allow roughly ±80° from straight up (−π/2)
  const MIN = -Math.PI + 0.18;  // ~−169°
  const MAX = -0.18;             // ~−10°
  return Math.max(MIN, Math.min(MAX, raw));
}

/**
 * Advance the projectile by one frame and reflect off the left/right walls.
 */
export function moveProjectile(proj: Projectile, config: GameConfig): Projectile {
  let { x, y, vx, vy } = proj;
  const { bubbleRadius, canvasWidth } = config;

  x += vx;
  y += vy;

  if (x - bubbleRadius < 0) {
    x  =  bubbleRadius;
    vx =  Math.abs(vx);
  }
  if (x + bubbleRadius > canvasWidth) {
    x  = canvasWidth - bubbleRadius;
    vx = -Math.abs(vx);
  }

  return { ...proj, x, y, vx, vy };
}

/**
 * Return true when the projectile should snap to the grid:
 *   • it has touched the top wall, OR
 *   • it is within collision distance of an existing bubble.
 */
export function shouldSnap(
  proj: Projectile,
  grid: (BubbleColor | null)[][],
  config: GameConfig,
): boolean {
  const { bubbleRadius, gridTop } = config;

  // Hit the ceiling
  if (proj.y - bubbleRadius <= gridTop) return true;

  // Collision with an existing bubble
  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < grid[r].length; c++) {
      if (grid[r][c] === null) continue;
      const { cx, cy } = getBubbleCenter(r, c, config);
      if (Math.hypot(proj.x - cx, proj.y - cy) < bubbleRadius * 1.95) return true;
    }
  }

  return false;
}

/**
 * Trace the aim guide path (with wall reflections) up to `maxSegments` bounces.
 * Returns an array of [x,y] waypoints.
 */
export function traceAimPath(
  startX: number,
  startY: number,
  angle: number,
  config: GameConfig,
  maxSegments = 3,
): [number, number][] {
  const { bubbleRadius, canvasWidth, gridTop } = config;
  const path: [number, number][] = [[startX, startY]];

  let x  = startX;
  let y  = startY;
  let dx = Math.cos(angle);
  let dy = Math.sin(angle);

  for (let seg = 0; seg < maxSegments; seg++) {
    // Steps per segment: enough to reach either wall or ceiling
    const stepsToTop   = dy < 0 ? (y - gridTop - bubbleRadius)   / (-dy) : Infinity;
    const stepsToLeft  = dx < 0 ? (x - bubbleRadius)             / (-dx) : Infinity;
    const stepsToRight = dx > 0 ? (canvasWidth - bubbleRadius - x) / dx  : Infinity;

    const steps = Math.min(stepsToTop, stepsToLeft, stepsToRight);

    x += dx * steps;
    y += dy * steps;
    path.push([x, y]);

    if (y <= gridTop + bubbleRadius) break; // reached the ceiling
    dx = -dx;                               // bounce off wall
  }

  return path;
}
