"use client";

import { useState, useCallback } from "react";
import { Camera, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CameraStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [hasFrame, setHasFrame] = useState(false);

  const mjpegUrl =
    typeof window !== "undefined"
      ? `http://${window.location.hostname}:8000/mjpeg`
      : "";

  const toggleStream = useCallback(async () => {
    const action = isStreaming ? "stop" : "start";
    try {
      const res = await fetch(`/py/${action}`, { method: "POST" });
      if (!res.ok) return;
      setIsStreaming(!isStreaming);
      setHasFrame(false);
    } catch {
      // network error — do not toggle state
    }
  }, [isStreaming]);

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>JPEG Stream</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Status: {isStreaming ? "STREAMING" : "IDLE"}
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
              <span className="text-gray-400 text-sm">Connecting...</span>
            </div>
          )}
          {isStreaming && (
            <img
              src={mjpegUrl}
              alt="JPEG Stream"
              onLoad={() => { if (!hasFrame) setHasFrame(true); }}
              className={`w-full h-full object-contain ${!hasFrame ? "hidden" : ""}`}
            />
          )}
        </div>
      </CardContent>
    </Card>
  );
}
