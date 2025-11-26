// app/api/connection-details/route.ts
import { NextResponse } from "next/server";
import { AccessToken, VideoGrant } from "livekit-server-sdk";
import { RoomConfiguration, RoomAgentDispatch } from "@livekit/protocol";

export async function POST(request: Request) {
  // 🔥 Trim whitespace and validate URL format
  const livekitUrl = process.env.LIVEKIT_URL?.trim();
  const apiKey = process.env.LIVEKIT_API_KEY?.trim();
  const apiSecret = process.env.LIVEKIT_API_SECRET?.trim();
  const defaultAgentName = process.env.LIVEKIT_AGENT_NAME?.trim() || "sdr-agent";

  // 🔥 Enhanced validation
  if (!livekitUrl || !apiKey || !apiSecret) {
    console.error("❌ Missing LiveKit env vars", {
      livekitUrl: livekitUrl || "MISSING",
      apiKey: !!apiKey,
      apiSecret: !!apiSecret,
    });
    return NextResponse.json(
      { error: "Server not configured correctly" },
      { status: 500 }
    );
  }

  // 🔥 Validate URL format
  if (!livekitUrl.startsWith("ws://") && !livekitUrl.startsWith("wss://")) {
    console.error("❌ Invalid LIVEKIT_URL format:", livekitUrl);
    return NextResponse.json(
      { error: "Invalid LiveKit URL format. Must start with ws:// or wss://" },
      { status: 500 }
    );
  }

  // 👇 Safely read request body
  let agentName = defaultAgentName;
  try {
    const body = await request.json();
    if (body?.room_config?.agents?.[0]?.agent_name) {
      agentName = body.room_config.agents[0].agent_name;
    }
  } catch (e) {
    // No body or invalid JSON - use default agent name
    console.log("⚠️ No request body, using default agent name:", defaultAgentName);
  }

  try {
    // Random room + identity
    const roomName = `sdr-room-${Math.random().toString(36).slice(2, 8)}`;
    const identity = `user-${Math.random().toString(36).slice(2, 8)}`;

    console.log(`🚀 Creating room: ${roomName} for user: ${identity}`);
    console.log(`🤖 Dispatching agent: ${agentName}`);

    // Create access token for this user
    const at = new AccessToken(apiKey, apiSecret, { identity });

    const videoGrant: VideoGrant = {
      roomJoin: true,
      room: roomName,
    };
    at.addGrant(videoGrant);

    // Tell LiveKit to dispatch our Python agent into this room
    const roomConfig = new RoomConfiguration({
      agents: [
        new RoomAgentDispatch({
          agentName, // must match your Python worker's agent_name
        }),
      ],
      departureTimeout: 180,
      emptyTimeout: 5,
    });

    at.roomConfig = roomConfig;

    const token = await at.toJwt();

    console.log(`✅ Token created for room: ${roomName} with agent: ${agentName}`);

    // 🔥 Return correct field names
    return NextResponse.json({
      serverUrl: livekitUrl,
      participantToken: token,
      roomName,
    });
  } catch (err) {
    console.error("❌ Error creating LiveKit token / roomConfig:", err);
    return NextResponse.json(
      { error: "Failed to create connection details" },
      { status: 500 }
    );
  }
}

// Optional: reject GET cleanly
export async function GET() {
  return NextResponse.json(
    { error: "Use POST for connection details" },
    { status: 405 }
  );
}
