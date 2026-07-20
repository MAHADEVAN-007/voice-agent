import { useState, useEffect, useRef } from "react";

const STATUS: Record<string, { label: string; color: string }> = {
  disconnected:          { label: "Call ended",     color: "bg-neutral-500" },
  connecting:            { label: "Connecting...",   color: "bg-yellow-500" },
  "pre-connect-buffering": { label: "Preparing...",   color: "bg-yellow-500" },
  initializing:          { label: "Initializing...", color: "bg-yellow-500" },
  idle:                  { label: "Agent ready",     color: "bg-green-500" },
  listening:             { label: "In call",         color: "bg-green-500" },
  thinking:              { label: "In call",         color: "bg-green-500" },
  speaking:              { label: "In call",         color: "bg-green-500" },
  failed:                { label: "Call failed",     color: "bg-red-500" },
};

export default function CallStatus({ state }: { state: string }) {
  const [elapsed, setElapsed] = useState(0);
  const startRef = useRef<number | null>(null);

  useEffect(() => {
    if (state === "listening" || state === "speaking" || state === "thinking") {
      if (!startRef.current) startRef.current = Date.now();
      const id = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startRef.current!) / 1000));
      }, 1000);
      return () => clearInterval(id);
    }
    if (state === "disconnected" || state === "failed") {
      startRef.current = null;
      setElapsed(0);
    }
  }, [state]);

  const info = STATUS[state] || { label: state, color: "bg-neutral-500" };
  const m = Math.floor(elapsed / 60);
  const s = elapsed % 60;
  const timer = elapsed > 0 ? `${m}:${s.toString().padStart(2, "0")}` : null;

  return (
    <div className="flex items-center gap-3 p-4 rounded-lg bg-neutral-900">
      <span className={`w-3 h-3 rounded-full ${info.color}`} />
      <span className="text-neutral-300">{info.label}</span>
      {timer && <span className="text-neutral-500 ml-auto font-mono">{timer}</span>}
    </div>
  );
}