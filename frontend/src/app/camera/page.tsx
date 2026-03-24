"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Camera, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function revokeImgSrc(img: HTMLImageElement | null) {
  if (img?.src?.startsWith("blob:")) {
    URL.revokeObjectURL(img.src);
    img.src = "";
  }
}

export default function CameraStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [hasFrame, setHasFrame] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  const wsUrl = isStreaming
    ? typeof window !== "undefined"
      ? `ws://${window.location.hostname}:8000/ws`
      : null
    : null;

  const { lastMessage, readyState } = useWebSocket(wsUrl, {
    shouldReconnect: () => isStreaming,
  });

  useEffect(() => {
    if (!isStreaming) {
      setHasFrame(false);
      revokeImgSrc(imgRef.current);
    }
  }, [isStreaming]);

  useEffect(() => {
    if (lastMessage?.data instanceof Blob) {
      revokeImgSrc(imgRef.current);
      const url = URL.createObjectURL(lastMessage.data);
      if (imgRef.current) {
        imgRef.current.src = url;
        if (!hasFrame) setHasFrame(true);
      }
    }
  }, [lastMessage, hasFrame]);

  useEffect(() => {
    const img = imgRef.current;
    return () => revokeImgSrc(img);
  }, []);

  const toggleStream = useCallback(async () => {
    const action = isStreaming ? "stop" : "start";
    try {
      const res = await fetch(`/py/${action}`, { method: "POST" });
      if (!res.ok) return;
      revokeImgSrc(imgRef.current);
      setIsStreaming(!isStreaming);
    } catch {
      // network error — do not toggle state
    }
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

        <div className="relative bg-gray-900 aspect-video rounded-md overflow-hidden">
          {!isStreaming && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
              <Camera className="text-gray-500" size={48} strokeWidth={1.5} />
              <span className="text-gray-500 text-sm">
                Press Start to begin streaming
              </span>
            </div>
          )}
          {isStreaming && !hasFrame && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
              <Loader2
                className="animate-spin text-gray-400"
                size={40}
                strokeWidth={2}
              />
              <span className="text-gray-400 text-sm">
                {connectionStatus}...
              </span>
            </div>
          )}
          <img
            ref={imgRef}
            alt="JPEG Stream"
            className={`w-full h-full object-contain ${!hasFrame ? "hidden" : ""}`}
          />
        </div>
      </CardContent>
    </Card>
  );
}
