// ============================================================
// Bubble Matching: cluster detection & floating-bubble removal
// ============================================================

import { BubbleColor } from '@/types/game';
import { getAdjacentCells, hasBubble, getColor } from './grid';

/** BFS flood-fill: find all same-colour bubbles connected to (startRow, startCol) */
export function findCluster(
  grid: (BubbleColor | null)[][],
  startRow: number,
  startCol: number,
): { row: number; col: number }[] {
  const targetColor = grid[startRow]?.[startCol];
  if (!targetColor) return [];

  const visited  = new Set<string>();
  const cluster: { row: number; col: number }[] = [];
  const queue: { row: number; col: number }[] = [{ row: startRow, col: startCol }];

  while (queue.length > 0) {
    const { row, col } = queue.shift()!;
    const key = `${row},${col}`;
    if (visited.has(key)) continue;
    visited.add(key);

    if (getColor(grid, row, col) !== targetColor) continue;
    cluster.push({ row, col });

    for (const adj of getAdjacentCells(row, col)) {
      const adjKey = `${adj.row},${adj.col}`;
      if (!visited.has(adjKey) && getColor(grid, adj.row, adj.col) === targetColor) {
        queue.push(adj);
      }
    }
  }

  return cluster;
}

/**
 * BFS from the top row to find bubbles connected to the ceiling.
 * Returns every filled bubble NOT reachable from row 0 (i.e. floating).
 */
export function findFloatingBubbles(
  grid: (BubbleColor | null)[][],
): { row: number; col: number }[] {
  const connected = new Set<string>();
  const queue: { row: number; col: number }[] = [];

  // Seed with all filled cells in row 0
  if (grid[0]) {
    for (let c = 0; c < grid[0].length; c++) {
      if (grid[0][c] !== null) {
        queue.push({ row: 0, col: c });
        connected.add(`0,${c}`);
      }
    }
  }

  while (queue.length > 0) {
    const { row, col } = queue.shift()!;
    for (const adj of getAdjacentCells(row, col)) {
      const key = `${adj.row},${adj.col}`;
      if (!connected.has(key) && hasBubble(grid, adj.row, adj.col)) {
        connected.add(key);
        queue.push(adj);
      }
    }
  }

  // Collect every filled bubble that is NOT connected
  const floating: { row: number; col: number }[] = [];
  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < grid[r].length; c++) {
      if (grid[r][c] !== null && !connected.has(`${r},${c}`)) {
        floating.push({ row: r, col: c });
      }
    }
  }
  return floating;
}

/** Remove the given cells from the grid (set to null) */
export function removeBubbles(
  grid: (BubbleColor | null)[][],
  cells: { row: number; col: number }[],
): void {
  for (const { row, col } of cells) {
    if (grid[row] !== undefined) {
      grid[row][col] = null;
    }
  }
}
