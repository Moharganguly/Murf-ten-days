"use client";

import { LiveKitRoom, RoomAudioRenderer, StartAudio, useVoiceAssistant } from "@livekit/components-react";
import { useCallback, useState } from "react";

function VoiceAssistantUI() {
  const { state, audioTrack } = useVoiceAssistant();
  
  return (
    <div className="space-y-4">
      <RoomAudioRenderer />
      <StartAudio
        label="🎤 Click to Enable Audio"
        className="w-full py-4 text-xl font-bold bg-green-500 hover:bg-green-600 text-white rounded-lg transition-all"
      />
      
      {/* Connection Status */}
      <div className="text-center space-y-2">
        <p className="text-white text-lg">
          🎧 Status: <span className="font-bold text-green-400">{state}</span>
        </p>
        <p className="text-gray-400 text-sm">
          {audioTrack ? "🔊 Audio connected" : "🔇 Waiting for audio..."}
        </p>
      </div>
    </div>
  );
}

export default function Home() {
  const [connectionDetails, updateConnectionDetails] = useState<{
    url: string;
    token: string;
    shouldConnect: boolean;
  }>({
    url: "",
    token: "",
    shouldConnect: false,
  });

  const [playerName, setPlayerName] = useState("");
  const [messages, setMessages] = useState<Array<{ role: string; content: string; timestamp: string }>>([]);

  const handleConnect = useCallback(async () => {
    if (!playerName.trim()) {
      alert("Please enter your name!");
      return;
    }

    try {
      const url = new URL(
        process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ?? "/api/connection-details",
        window.location.origin
      );

      const response = await fetch(url.toString(), {
        method: "POST",
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const connectionDetailsData = await response.json();

      updateConnectionDetails({
        url: connectionDetailsData.serverUrl,
        token: connectionDetailsData.participantToken,
        shouldConnect: true,
      });

      // Add welcome message
      setMessages([{
        role: "system",
        content: "🎭 Connected to IMPROV BATTLE! The host will greet you shortly...",
        timestamp: new Date().toLocaleTimeString()
      }]);
    } catch (error) {
      console.error("Failed to connect:", error);
      alert("Failed to connect. Please try again.");
    }
  }, [playerName]);

  const handleDisconnect = useCallback(() => {
    updateConnectionDetails({
      url: "",
      token: "",
      shouldConnect: false,
    });
    setMessages([]);
    setPlayerName("");
  }, []);

  // Simulate adding messages (in real implementation, you'd use LiveKit transcription events)
  const addMessage = useCallback((role: string, content: string) => {
    setMessages(prev => [...prev, {
      role,
      content,
      timestamp: new Date().toLocaleTimeString()
    }]);
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-br from-purple-900 via-pink-800 to-red-900">
      <div className="w-full max-w-4xl">
        {!connectionDetails.shouldConnect ? (
          // Landing Page - Improv Battle Theme
          <div className="text-center space-y-8 animate-fade-in">
            {/* Show Title */}
            <div className="space-y-4">
              <h1 className="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 animate-pulse drop-shadow-2xl">
                🎭 IMPROV BATTLE 🎭
              </h1>
              <p className="text-2xl font-bold text-yellow-300 tracking-wide">
                The Ultimate Voice Improv Game Show!
              </p>
            </div>

            {/* Game Description */}
            <div className="bg-black/40 backdrop-blur-md rounded-2xl p-8 border-4 border-yellow-400 shadow-2xl">
              <h2 className="text-3xl font-bold text-white mb-4">🎤 How to Play:</h2>
              <ul className="text-left text-lg text-gray-200 space-y-3">
                <li className="flex items-start gap-3">
                  <span className="text-2xl">1️⃣</span>
                  <span>Get a <strong className="text-yellow-300">wild improv scenario</strong> from the host</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-2xl">2️⃣</span>
                  <span>Act it out with your <strong className="text-pink-300">voice</strong> for 30 seconds</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-2xl">3️⃣</span>
                  <span>Hear the host&apos;s <strong className="text-purple-300">honest reaction</strong></span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-2xl">4️⃣</span>
                  <span>Complete <strong className="text-green-300">4 rounds</strong> and get your improv profile!</span>
                </li>
              </ul>
            </div>

            {/* Name Input */}
            <div className="space-y-4">
              <label htmlFor="playerName" className="block text-2xl font-bold text-white">
                Enter Your Stage Name:
              </label>
              <input
                id="playerName"
                type="text"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleConnect()}
                placeholder="e.g., Comedy Genius"
                className="w-full px-6 py-4 text-2xl font-bold text-center bg-white/90 border-4 border-yellow-400 rounded-xl focus:outline-none focus:ring-4 focus:ring-pink-400 placeholder-gray-500"
              />
            </div>

            {/* Start Button */}
            <button
              onClick={handleConnect}
              className="w-full py-6 text-3xl font-black text-white bg-gradient-to-r from-pink-500 via-red-500 to-yellow-500 rounded-xl hover:scale-105 transform transition-all duration-200 shadow-2xl border-4 border-white hover:border-yellow-300 animate-bounce"
            >
              🎬 START IMPROV BATTLE! 🎬
            </button>

            {/* Warning */}
            <p className="text-sm text-gray-300 italic">
              ⚠️ Warning: May cause uncontrollable laughter and creative genius!
            </p>
          </div>
        ) : (
          // In-Game UI
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Controls & Messages */}
            <div className="space-y-6">
              {/* Live Status */}
              <div className="bg-red-600 text-white text-center py-4 rounded-xl font-black text-2xl animate-pulse border-4 border-white">
                🔴 LIVE
              </div>

              {/* Player Info */}
              <div className="bg-black/60 backdrop-blur-md rounded-xl p-6 border-2 border-pink-400">
                <p className="text-xl text-white text-center">
                  🎭 <span className="font-black text-yellow-300 text-2xl">{playerName}</span>
                </p>
              </div>

              {/* Stop Button */}
              <button
                onClick={handleDisconnect}
                className="w-full py-4 text-xl font-bold text-white bg-red-600 hover:bg-red-700 rounded-xl transition-all border-2 border-white hover:scale-105 transform"
              >
                🛑 STOP BATTLE
              </button>

              {/* Instructions */}
              <div className="bg-purple-900/60 backdrop-blur-md rounded-xl p-6 border-2 border-purple-400">
                <h3 className="text-xl font-bold text-white mb-3">📢 Quick Tips:</h3>
                <ul className="text-gray-200 space-y-2 text-sm">
                  <li>✅ Listen to the scenario</li>
                  <li>🎤 Commit to your character</li>
                  <li>🎭 Be creative and have fun!</li>
                  <li>🛑 Say &quot;end scene&quot; when done</li>
                </ul>
              </div>
            </div>

            {/* Right Column - LiveKit & Transcript */}
            <div className="space-y-6">
              {/* LiveKit Room */}
              <div className="bg-black/80 rounded-xl p-6 border-4 border-yellow-400 shadow-2xl">
                <LiveKitRoom
                  serverUrl={connectionDetails.url}
                  token={connectionDetails.token}
                  connect={connectionDetails.shouldConnect}
                  audio={true}
                  video={false}
                >
                  <VoiceAssistantUI />
                </LiveKitRoom>
              </div>

              {/* Message/Transcript Box */}
              <div className="bg-black/80 backdrop-blur-md rounded-xl border-4 border-pink-400 overflow-hidden">
                <div className="bg-pink-600 px-6 py-3 border-b-4 border-pink-400">
                  <h3 className="text-xl font-bold text-white">💬 Conversation Log</h3>
                </div>
                
                <div className="h-96 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                  {messages.length === 0 ? (
                    <div className="text-center text-gray-400 py-20">
                      <p className="text-lg">🎤 Waiting for the show to begin...</p>
                      <p className="text-sm mt-2">Messages will appear here</p>
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-lg ${
                          msg.role === "host" 
                            ? "bg-purple-600/40 border-l-4 border-purple-400" 
                            : msg.role === "player"
                            ? "bg-green-600/40 border-l-4 border-green-400"
                            : "bg-blue-600/40 border-l-4 border-blue-400"
                        }`}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-bold text-white">
                            {msg.role === "host" ? "🎭 Host" : msg.role === "player" ? "🎤 You" : "ℹ️ System"}
                          </span>
                          <span className="text-xs text-gray-300">{msg.timestamp}</span>
                        </div>
                        <p className="text-gray-100">{msg.content}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="mt-12 text-gray-400 text-center">
        <p>Built with Murf AI • LiveKit • Google Gemini</p>
        <p className="text-sm mt-2">Day 10 - Voice Improv Battle Challenge</p>
      </footer>

      {/* Custom Scrollbar Styles */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(236, 72, 153, 0.6);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(236, 72, 153, 0.8);
        }
      `}</style>
    </main>
  );
}
