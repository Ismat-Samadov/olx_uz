// ============================================================
// Procedural Sound Effects (Web Audio API — no external assets)
// ============================================================

let _ctx: AudioContext | null = null;

function ctx(): AudioContext {
  if (!_ctx) _ctx = new AudioContext();
  // Browsers suspend AudioContext until a user gesture
  if (_ctx.state === 'suspended') _ctx.resume();
  return _ctx;
}

/** Create a simple envelope-shaped oscillator */
function tone(
  type: OscillatorType,
  freq: number,
  startFreq: number | null,
  gain: number,
  duration: number,
  offset = 0,
): void {
  const c   = ctx();
  const now = c.currentTime + offset;

  const osc = c.createOscillator();
  const g   = c.createGain();
  osc.connect(g);
  g.connect(c.destination);

  osc.type = type;
  osc.frequency.setValueAtTime(startFreq ?? freq, now);
  if (startFreq !== null) {
    osc.frequency.exponentialRampToValueAtTime(freq, now + duration * 0.7);
  }

  g.gain.setValueAtTime(gain, now);
  g.gain.exponentialRampToValueAtTime(0.001, now + duration);

  osc.start(now);
  osc.stop(now + duration + 0.01);
}

/** Bubble shoot: short downward sweep */
export function playShootSound(): void {
  try { tone('sine', 180, 420, 0.18, 0.12); } catch { /* noop */ }
}

/** Bubble pop: stacked plops, louder for bigger combos */
export function playPopSound(count: number): void {
  try {
    const bursts = Math.min(count, 6);
    for (let i = 0; i < bursts; i++) {
      tone('sine', 900 + i * 120, null, 0.14, 0.09, i * 0.03);
    }
    if (count >= 5) {
      // Extra sparkle for big combos
      tone('sawtooth', 1400, 600, 0.08, 0.25, 0.05);
    }
  } catch { /* noop */ }
}

/** Bubble lands without popping */
export function playLandSound(): void {
  try { tone('sine', 280, 380, 0.12, 0.07); } catch { /* noop */ }
}

/** Grid descends — low rumble */
export function playDescendSound(): void {
  try { tone('sawtooth', 80, 140, 0.08, 0.22); } catch { /* noop */ }
}

/** Game over — descending ominous chords */
export function playGameOverSound(): void {
  try {
    [400, 300, 220, 160].forEach((f, i) =>
      tone('sawtooth', f, null, 0.13, 0.35, i * 0.18),
    );
  } catch { /* noop */ }
}

/** Victory fanfare — ascending major arpeggio */
export function playWinSound(): void {
  try {
    [523, 659, 784, 1047].forEach((f, i) =>
      tone('sine', f, null, 0.18, 0.28, i * 0.1),
    );
  } catch { /* noop */ }
}
