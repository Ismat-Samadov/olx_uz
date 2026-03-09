'use client';

// ============================================================
// useSound — mutable mute toggle + typed sound dispatchers
// ============================================================

import { useState, useCallback, useRef } from 'react';
import {
  playShootSound,
  playPopSound,
  playLandSound,
  playGameOverSound,
  playWinSound,
  playDescendSound,
} from '@/lib/sounds';

export function useSound() {
  const [muted, setMuted] = useState(false);

  // Keep a ref so callbacks never close over stale state
  const mutedRef = useRef(false);
  mutedRef.current = muted;

  const toggleMute = useCallback(() => setMuted(m => !m), []);

  const shoot   = useCallback(() => { if (!mutedRef.current) playShootSound(); }, []);
  const pop     = useCallback((n: number) => { if (!mutedRef.current) playPopSound(n); }, []);
  const land    = useCallback(() => { if (!mutedRef.current) playLandSound(); }, []);
  const gameOver= useCallback(() => { if (!mutedRef.current) playGameOverSound(); }, []);
  const win     = useCallback(() => { if (!mutedRef.current) playWinSound(); }, []);
  const descend = useCallback(() => { if (!mutedRef.current) playDescendSound(); }, []);

  return { muted, toggleMute, shoot, pop, land, gameOver, win, descend };
}
