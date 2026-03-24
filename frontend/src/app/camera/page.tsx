"use client";

import { useState, useCallback, useRef } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function CameraStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  const { lastMessage, readyState } = useWebSocket("/py/ws", {
    shouldReconnect: () => true,
  });

  if (imgRef.current?.src) {
    URL.revokeObjectURL(imgRef.current.src);
  }
  if (lastMessage?.data instanceof Blob) {
    const url = URL.createObjectURL(lastMessage.data);
    if (imgRef.current) imgRef.current.src = url;
  }

  const toggleStream = useCallback(async () => {
    const action = isStreaming ? "stop" : "start";
    await fetch(`/py/${action}`, { method: "POST" });
    setIsStreaming(!isStreaming);
  }, [isStreaming]);

  const connectionStatus = ReadyState[readyState];

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

        <div className="relative bg-gray-100 aspect-video">
          {readyState !== ReadyState.OPEN && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-gray-500">{connectionStatus}...</span>
            </div>
          )}
          <img
            ref={imgRef}
            alt="JPEG Stream"
            className="w-full h-full object-contain"
          />
        </div>
      </CardContent>
    </Card>
  );
}
