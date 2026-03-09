'use client';

// ============================================================
// useHighScore — per-difficulty high-score persistence
// ============================================================

import { useState, useEffect, useCallback } from 'react';
import { Difficulty } from '@/types/game';

const LS_KEY = 'bubbleShooter_highScores';

type Scores = Record<Difficulty, number>;

function load(): Scores {
  if (typeof window === 'undefined') return { easy: 0, medium: 0, hard: 0 };
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) ?? 'null') ?? { easy: 0, medium: 0, hard: 0 };
  } catch {
    return { easy: 0, medium: 0, hard: 0 };
  }
}

export function useHighScore(difficulty: Difficulty) {
  const [scores, setScores] = useState<Scores>({ easy: 0, medium: 0, hard: 0 });

  // Hydrate from localStorage on client
  useEffect(() => { setScores(load()); }, []);

  const update = useCallback(
    (score: number) => {
      setScores(prev => {
        if (score <= prev[difficulty]) return prev;
        const next = { ...prev, [difficulty]: score };
        try { localStorage.setItem(LS_KEY, JSON.stringify(next)); } catch { /* noop */ }
        return next;
      });
    },
    [difficulty],
  );

  return { highScore: scores[difficulty], updateHighScore: update };
}
