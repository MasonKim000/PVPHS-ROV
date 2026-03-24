"use client";

import { useState, useEffect, useRef } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Camera, Loader2, Pause, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CameraStream() {
  const [streamEnabled, setStreamEnabled] = useState(true);
  const [imgSrc, setImgSrc] = useState("");
  const prevUrlRef = useRef("");

  const wsUrl =
    typeof window !== "undefined"
      ? `ws://${window.location.hostname}:8000/ws`
      : "ws://localhost:8000/ws";

  const { lastMessage, readyState } = useWebSocket(
    wsUrl,
    {
      shouldReconnect: () => true,
      reconnectAttempts: 10,
      reconnectInterval: 3000,
      retryOnError: true,
    },
    streamEnabled,
  );

  useEffect(() => {
    if (lastMessage?.data instanceof Blob) {
      const url = URL.createObjectURL(lastMessage.data);
      setImgSrc(url);
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
      prevUrlRef.current = url;
    }
  }, [lastMessage]);

  useEffect(() => {
    return () => {
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
    };
  }, []);

  useEffect(() => {
    if (!streamEnabled) {
      setImgSrc("");
      if (prevUrlRef.current) {
        URL.revokeObjectURL(prevUrlRef.current);
        prevUrlRef.current = "";
      }
    }
  }, [streamEnabled]);

  const hasFrame = imgSrc !== "";

  const statusText = {
    [ReadyState.CONNECTING]: "CONNECTING",
    [ReadyState.OPEN]: "STREAMING",
    [ReadyState.CLOSING]: "CLOSING",
    [ReadyState.CLOSED]: "DISCONNECTED",
    [ReadyState.UNINSTANTIATED]: "IDLE",
  }[readyState];

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Live Stream</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Status: {streamEnabled ? statusText : "PAUSED"}
          </span>
          <Button
            onClick={() => setStreamEnabled((prev) => !prev)}
            variant={streamEnabled ? "destructive" : "default"}
          >
            {streamEnabled ? (
              <>
                <Pause className="mr-1 h-4 w-4" /> Pause
              </>
            ) : (
              <>
                <Play className="mr-1 h-4 w-4" /> Resume
              </>
            )}
          </Button>
        </div>

        <div className="relative bg-gray-900 aspect-video rounded-md overflow-hidden">
          {!streamEnabled && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
              <Camera className="text-gray-500" size={48} strokeWidth={1.5} />
              <span className="text-gray-500 text-sm">Stream paused</span>
            </div>
          )}
          {streamEnabled && !hasFrame && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
              <Loader2
                className="animate-spin text-gray-400"
                size={40}
                strokeWidth={2}
              />
              <span className="text-gray-400 text-sm">
                {readyState === ReadyState.OPEN
                  ? "Waiting for frames..."
                  : "Connecting..."}
              </span>
            </div>
          )}
          {hasFrame && (
            <img
              src={imgSrc}
              alt="Live Stream"
              className="w-full h-full object-contain"
            />
          )}
        </div>
      </CardContent>
    </Card>
  );
}
