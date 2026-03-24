"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function CameraStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [hasFrame, setHasFrame] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (isStreaming) {
      setWsUrl(`ws://${window.location.hostname}:8000/ws`);
    } else {
      setWsUrl(null);
      setHasFrame(false);
      if (imgRef.current) {
        if (imgRef.current.src) {
          URL.revokeObjectURL(imgRef.current.src);
        }
        imgRef.current.src = "";
      }
    }
  }, [isStreaming]);

  const { lastMessage, readyState } = useWebSocket(wsUrl, {
    shouldReconnect: () => isStreaming,
  });

  useEffect(() => {
    if (lastMessage?.data instanceof Blob) {
      const url = URL.createObjectURL(lastMessage.data);
      if (imgRef.current) {
        if (imgRef.current.src) {
          URL.revokeObjectURL(imgRef.current.src);
        }
        imgRef.current.src = url;
        setHasFrame(true);
      }
    }
  }, [lastMessage]);

  const toggleStream = useCallback(async () => {
    if (!isStreaming && imgRef.current) {
      imgRef.current.src = "";
    }
    const action = isStreaming ? "stop" : "start";
    await fetch(`/py/${action}`, { method: "POST" });
    setIsStreaming(!isStreaming);
  }, [isStreaming]);

  const connectionStatus = isStreaming ? ReadyState[readyState] : "IDLE";

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>JPEG Stream</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Status: {connectionStatus}
          </span>
          <Button
            onClick={toggleStream}
            variant={isStreaming ? "destructive" : "default"}
          >
            {isStreaming ? "Stop" : "Start"} Stream
          </Button>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="relative bg-gray-900 aspect-video rounded-md overflow-hidden">
          {!isStreaming && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-gray-500"
              >
                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z" />
                <circle cx="12" cy="13" r="3" />
              </svg>
              <span className="text-gray-500 text-sm">Press Start to begin streaming</span>
            </div>
          )}
          {isStreaming && readyState !== ReadyState.OPEN && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-gray-400">{connectionStatus}...</span>
            </div>
          )}
          <img
            ref={imgRef}
            alt="JPEG Stream"
            className={`w-full h-full object-contain ${!isStreaming ? "hidden" : ""}`}
          />
        </div>
      </CardContent>
    </Card>
  );
}
