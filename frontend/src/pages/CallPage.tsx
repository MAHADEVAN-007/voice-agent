import { useLocation, Navigate } from "react-router-dom";
import { useAgent, useSession, useTranscriptions } from "@livekit/components-react";
import { Room, TokenSource } from "livekit-client";
import { AgentSessionProvider } from "@/components/agent-session-provider";
import { AgentChatTranscript } from "@/components/agent-chat-transcript";
import CallStatus from "@/components/CallStatus";
import { useEffect, useState, useCallback, useRef } from "react";

export default function CallPage() {
  const location = useLocation();
  const state = location.state as { token?: string; wsUrl?: string } | null;

  if (!state?.token || !state?.wsUrl) {
    return <Navigate to="/" replace />;
  }

  return <CallConnected token={state.token} wsUrl={state.wsUrl} />;
}

function CallConnected({ token, wsUrl }: { token: string; wsUrl: string }) {
  const roomRef = useRef(new Room());
  const tokenSourceRef = useRef(TokenSource.literal({ serverUrl: wsUrl, participantToken: token }));
  const session = useSession(tokenSourceRef.current, { room: roomRef.current });
  const [callEnded, setCallEnded] = useState(false);
  const wasConnected = useRef(false);

  useEffect(() => {
    session.start({ tracks: { microphone: { enabled: true } } });
    return () => { session.end(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

    useEffect(() => {
    if (session.isConnected) {
      wasConnected.current = true;
    } else if (wasConnected.current) {
      setCallEnded(true);
    }
  }, [session.isConnected]);

  const handleDisconnect = useCallback(() => {
    setCallEnded(true);
    session.end();
  }, [session]);

  if (callEnded) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <p className="text-xl text-neutral-400">Call ended</p>
          <a href="/" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-xl">Back to Home</a>
        </div>
      </div>
    );
  }

  if (!session.isConnected) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center p-4">
        <p>Connecting...</p>
      </div>
    );
  }

  return (
    <AgentSessionProvider session={session} muted={true}>
      <CallUI onDisconnect={handleDisconnect} />
    </AgentSessionProvider>
  );
}
function CallUI({ onDisconnect }: { onDisconnect: () => void }) {
  const agent = useAgent();
  const transcriptions = useTranscriptions();
  const messages = transcriptions.reduce((acc, t) => {
    const existing = acc.findIndex(m => m.id === t.streamInfo.id);
    if (existing >= 0) {
      acc[existing] = { ...acc[existing], message: t.text };
    } else {
      acc.push({ id: t.streamInfo.id, timestamp: t.streamInfo.timestamp, message: t.text, type: 'agentTranscript' as const });
    }
    return acc;
  }, [] as { id: string; timestamp: number; message: string; type: 'agentTranscript' }[]);

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center p-4">
      <div className="w-full max-w-md space-y-4">
        <CallStatus state={agent.state} />
        <AgentChatTranscript agentState={agent.state} messages={messages} />
        <button onClick={onDisconnect} className="bg-red-600 hover:bg-red-700 text-white font-semibold px-8 py-3 rounded-xl text-lg w-full">
          End Call
        </button>
      </div>
    </div>
  );
}