// ============================================================
// Game Types & Interfaces
// ============================================================

/** Available bubble colors in the neon theme */
export type BubbleColor = 'red' | 'blue' | 'green' | 'yellow' | 'purple' | 'cyan';

/** Game phases / screens */
export type GamePhase = 'start' | 'playing' | 'paused' | 'won' | 'lost';

/** Difficulty levels */
export type Difficulty = 'easy' | 'medium' | 'hard';

/** Settings per difficulty */
export interface DifficultySettings {
  label: string;
  colors: BubbleColor[];
  initialRows: number;
  shotsPerDescend: number; // shots before the grid moves down one row
  maxRows: number;         // game-over row threshold
}

/** Active projectile flying through the air */
export interface Projectile {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: BubbleColor;
}

/** Particle for pop / explosion effect */
export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  alpha: number;
  size: number;
  color: string;
}

/** Pop animation: bubbles exploding into particles */
export interface PopEffect {
  x: number;
  y: number;
  color: BubbleColor;
  particles: Particle[];
  age: number; // frames elapsed since creation
}

/** A bubble that has been disconnected and is falling off screen */
export interface FallingBubble {
  x: number;
  y: number;
  color: BubbleColor;
  vy: number;
  age: number;
}

/** Canvas-derived constants calculated at runtime */
export interface GameConfig {
  bubbleRadius: number;
  rowHeight: number;    // vertical distance between row centers (= radius * sqrt(3))
  gridTop: number;      // y of row-0 bubble centres
  shooterX: number;
  shooterY: number;
  canvasWidth: number;
  canvasHeight: number;
}

/** Complete mutable game state (kept in a ref for performance) */
export interface GameData {
  grid: (BubbleColor | null)[][];
  projectile: Projectile | null;
  nextColor: BubbleColor;
  score: number;
  shots: number;  // shots since last descend
  level: number;
  difficulty: Difficulty;
  phase: GamePhase;
  popEffects: PopEffect[];
  fallingBubbles: FallingBubble[];
  aimAngle: number; // radians, measured from positive-x axis
  newBubbleRow: boolean; // flag: a new row was just added (for animation)
}
