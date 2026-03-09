// Root page — mounts the game full-screen
import BubbleShooterGame from '@/components/BubbleShooterGame';

export default function Home() {
  return (
    // Full-viewport container; no scroll, no overflow
    <main className="fixed inset-0 overflow-hidden bg-[#07071a]">
      <BubbleShooterGame />
    </main>
  );
}
