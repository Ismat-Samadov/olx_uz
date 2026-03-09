// ============================================================
// Neon Cyberpunk Color Palette
// ============================================================

import { BubbleColor } from '@/types/game';

/** Visual properties for each bubble color */
export const BUBBLE_COLORS: Record<
  BubbleColor,
  { fill: string; glow: string; dark: string; particle: string }
> = {
  red:    { fill: '#ff3366', glow: '#ff0044', dark: '#7a001f', particle: '#ff6699' },
  blue:   { fill: '#00aaff', glow: '#0077ff', dark: '#003d7a', particle: '#55ccff' },
  green:  { fill: '#00ff88', glow: '#00cc66', dark: '#006633', particle: '#66ffaa' },
  yellow: { fill: '#ffee00', glow: '#ffcc00', dark: '#665a00', particle: '#fff066' },
  purple: { fill: '#cc44ff', glow: '#aa00ff', dark: '#4a0066', particle: '#dd88ff' },
  cyan:   { fill: '#00ffee', glow: '#00ddcc', dark: '#005951', particle: '#66fff9' },
};

/** All possible colors */
export const ALL_COLORS: BubbleColor[] = ['red', 'blue', 'green', 'yellow', 'purple', 'cyan'];

/** Pick a random color from an array */
export function randomColor(colors: BubbleColor[]): BubbleColor {
  return colors[Math.floor(Math.random() * colors.length)];
}
