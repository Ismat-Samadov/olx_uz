// ============================================================
// Grid Management: layout, snapping, adjacency, creation
// ============================================================

import { BubbleColor, Difficulty, DifficultySettings, GameConfig } from '@/types/game';
import { randomColor } from './colors';

// --------------- Grid constants ---------------
/** Bubbles per even row (0, 2, 4 …) */
export const COLS_EVEN = 9;
/** Bubbles per odd row  (1, 3, 5 …) — offset by one radius */
export const COLS_ODD  = 8;

// --------------- Difficulty presets ---------------
export const DIFFICULTY_SETTINGS: Record<Difficulty, DifficultySettings> = {
  easy: {
    label: 'Easy',
    colors: ['red', 'blue', 'green'],
    initialRows: 5,
    shotsPerDescend: 8,
    maxRows: 13,
  },
  medium: {
    label: 'Medium',
    colors: ['red', 'blue', 'green', 'yellow'],
    initialRows: 6,
    shotsPerDescend: 6,
    maxRows: 12,
  },
  hard: {
    label: 'Hard',
    colors: ['red', 'blue', 'green', 'yellow', 'purple', 'cyan'],
    initialRows: 7,
    shotsPerDescend: 4,
    maxRows: 11,
  },
};

// --------------- Layout helpers ---------------

/** Returns the number of columns for a given row index */
export function getColsForRow(row: number): number {
  return row % 2 === 0 ? COLS_EVEN : COLS_ODD;
}

/**
 * Calculate the pixel centre of a bubble at (row, col).
 * Grid is horizontally centred inside the canvas.
 */
export function getBubbleCenter(
  row: number,
  col: number,
  config: GameConfig,
): { cx: number; cy: number } {
  const { bubbleRadius, rowHeight, gridTop, canvasWidth } = config;

  // Pixel width consumed by an even row: 9 bubbles × diameter
  const gridWidth = COLS_EVEN * 2 * bubbleRadius;
  const gridLeft  = (canvasWidth - gridWidth) / 2;

  // Odd rows are offset half a diameter to the right → hexagonal packing
  const xOffset = row % 2 === 0 ? 0 : bubbleRadius;
  const cx = gridLeft + xOffset + col * 2 * bubbleRadius + bubbleRadius;
  const cy = gridTop  + row * rowHeight;

  return { cx, cy };
}

// --------------- Grid cell helpers ---------------

/** True when (row, col) is inside the grid and contains a bubble */
export function hasBubble(
  grid: (BubbleColor | null)[][],
  row: number,
  col: number,
): boolean {
  if (row < 0 || row >= grid.length) return false;
  const cols = getColsForRow(row);
  if (col < 0 || col >= cols) return false;
  return grid[row][col] !== null;
}

/** Return the color at (row, col), or null if empty / out-of-bounds */
export function getColor(
  grid: (BubbleColor | null)[][],
  row: number,
  col: number,
): BubbleColor | null {
  if (row < 0 || row >= grid.length) return null;
  const cols = getColsForRow(row);
  if (col < 0 || col >= cols) return null;
  return grid[row][col];
}

/** True when every cell in the grid is empty */
export function isGridEmpty(grid: (BubbleColor | null)[][]): boolean {
  return grid.every(row => row.every(cell => cell === null));
}

/** True when any filled bubble exists at or beyond maxRow */
export function hasBubblePastRow(
  grid: (BubbleColor | null)[][],
  maxRow: number,
): boolean {
  for (let r = maxRow; r < grid.length; r++) {
    if (grid[r].some(c => c !== null)) return true;
  }
  return false;
}

// --------------- Hex adjacency ---------------

/**
 * Returns the 6 hex-neighbours of (row, col).
 * Handles both even and odd row offsets. Negative / over-bound indices
 * are included — callers must validate with hasBubble / getColor.
 */
export function getAdjacentCells(
  row: number,
  col: number,
): { row: number; col: number }[] {
  const adj: { row: number; col: number }[] = [];

  // Left / right in the same row
  adj.push({ row, col: col - 1 });
  adj.push({ row, col: col + 1 });

  if (row % 2 === 0) {
    // Even row: upper-left, upper-right, lower-left, lower-right
    adj.push({ row: row - 1, col: col - 1 });
    adj.push({ row: row - 1, col: col     });
    adj.push({ row: row + 1, col: col - 1 });
    adj.push({ row: row + 1, col: col     });
  } else {
    // Odd row: shifted right
    adj.push({ row: row - 1, col: col     });
    adj.push({ row: row - 1, col: col + 1 });
    adj.push({ row: row + 1, col: col     });
    adj.push({ row: row + 1, col: col + 1 });
  }

  return adj;
}

// --------------- Snap-to-grid ---------------

/**
 * Given the pixel position where a projectile should stop,
 * return the nearest empty grid cell that is adjacent to an
 * existing bubble (or is in row 0).
 *
 * Returns null if no suitable cell is found.
 */
export function findNearestGridCell(
  px: number,
  py: number,
  grid: (BubbleColor | null)[][],
  config: GameConfig,
): { row: number; col: number } | null {
  const { rowHeight, gridTop, bubbleRadius } = config;

  // Estimate the row the projectile is near
  const rowEst  = (py - gridTop) / rowHeight;
  const rowMin  = Math.max(0, Math.floor(rowEst) - 1);
  // Allow snapping to one row beyond the current grid length
  const rowMax  = Math.min(grid.length, Math.ceil(rowEst) + 2);

  const candidates: { row: number; col: number; dist: number }[] = [];

  for (let r = rowMin; r <= rowMax; r++) {
    const cols = getColsForRow(r);

    for (let c = 0; c < cols; c++) {
      // Cell must be empty
      if (grid[r]?.[c] !== null && grid[r]?.[c] !== undefined) continue;

      // Must be row 0 OR adjacent to a filled bubble
      let eligible = r === 0;
      if (!eligible) {
        for (const adj of getAdjacentCells(r, c)) {
          if (hasBubble(grid, adj.row, adj.col)) { eligible = true; break; }
        }
      }
      if (!eligible) continue;

      const { cx, cy } = getBubbleCenter(r, c, config);
      const dist = Math.hypot(px - cx, py - cy);
      candidates.push({ row: r, col: c, dist });
    }
  }

  if (candidates.length === 0) return null;
  candidates.sort((a, b) => a.dist - b.dist);

  // Reject if the best candidate is suspiciously far away
  if (candidates[0].dist > bubbleRadius * 3) return null;

  return { row: candidates[0].row, col: candidates[0].col };
}

// --------------- Grid creation ---------------

/** Create the initial bubble grid for the chosen difficulty */
export function createInitialGrid(
  difficulty: Difficulty,
  colors: BubbleColor[],
): (BubbleColor | null)[][] {
  const { initialRows } = DIFFICULTY_SETTINGS[difficulty];
  const grid: (BubbleColor | null)[][] = [];

  for (let r = 0; r < initialRows; r++) {
    const cols = getColsForRow(r);
    grid.push(Array.from({ length: cols }, () => randomColor(colors)));
  }
  return grid;
}

/** Create one new random row (used when the grid descends) */
export function createRandomRow(rowIndex: number, colors: BubbleColor[]): (BubbleColor | null)[] {
  const cols = getColsForRow(rowIndex);
  return Array.from({ length: cols }, () => randomColor(colors));
}

/**
 * Ensure the grid has at least `numRows` rows, padding
 * with all-null rows at the bottom as needed.
 */
export function ensureGridRows(
  grid: (BubbleColor | null)[][],
  numRows: number,
): (BubbleColor | null)[][] {
  const result = [...grid];
  while (result.length < numRows) {
    const r = result.length;
    result.push(Array(getColsForRow(r)).fill(null));
  }
  return result;
}
