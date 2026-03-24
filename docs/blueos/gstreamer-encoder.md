# BlueOS GStreamer Encoder Configuration

## Root Cause

When BlueOS starts, the following option is applied to mavlink-camera-manager:

```
--gst-feature-rank omxh264enc=0,v4l2h264enc=250,x264enc=260
```

## Encoder Details

| Encoder       | Type         | Priority          | Description                 |
| ------------- | ------------ | ----------------- | --------------------------- |
| `omxh264enc`  | Hardware     | 0 (disabled)      | RPi GPU encoder (legacy)    |
| `v4l2h264enc` | Hardware     | 250               | V4L2-based hardware encoder |
| `x264enc`     | **Software** | **260 (highest)** | CPU encoder                 |

> A higher number means higher priority. As a result, **the software encoder (x264enc) is always selected**.

## Problem

- High CPU usage
- Increased streaming latency
- On RPi4, cpu1 reaches 100% utilization

## Solution -- Prioritize the Hardware Encoder

Modify the `start-blueos-core` file (`/usr/bin/start-blueos-core`) as follows:

### Original Setting

```
--gst-feature-rank omxh264enc=0,v4l2h264enc=250,x264enc=260
```

### Updated Setting (Hardware Preferred)

```
--gst-feature-rank omxh264enc=0,v4l2h264enc=300,x264enc=0
```

## Using Camera Without Navigator

mavlink-camera-manager attempts to connect to MAVLink (port 5777).
Without Navigator, the connection fails, preventing stream registration, which causes streams to appear and disappear intermittently.

### Resolution Steps

**1. Enter the blueos-core Container**

```bash
docker exec -it blueos-core sh
```

**2. Disable Camera Manager**

Edit `startup.json` as described in [./blueos-bootstrap.md](../blueos-bootstrap.md) to add the `BLUEOS_DISABLE_SERVICES=video` environment variable.

**3. Stream Directly with GStreamer (H264 Camera)**

```bash
docker exec -it blueos-core sh

gst-launch-1.0 v4l2src device=/dev/video0 \
  ! video/x-h264,width=640,height=480,framerate=30/1 \
  ! h264parse \
  ! rtph264pay config-interval=1 pt=96 \
  ! udpsink host=192.168.254.214 port=5600
```

**3-1. Stream Directly with GStreamer (MJPG Camera)**

```bash
docker exec -it blueos-core sh

gst-launch-1.0 v4l2src device=/dev/video0 \
  ! image/jpeg,width=1280,height=720,framerate=30/1 \
  ! rtpjpegpay \
  ! udpsink host=192.168.254.214 port=5600
```

## Viewing the Stream on a PC

### Create an SDP File (for H264)

```bash
cat > /tmp/stream.sdp << 'EOF'
v=0
o=- 0 0 IN IP4 127.0.0.1
s=No Name
c=IN IP4 0.0.0.0
t=0 0
m=video 5600 RTP/AVP 96
a=rtpmap:96 H264/90000
a=fmtp:96 packetization-mode=1
EOF
```

### Create an SDP File (for MJPG)

```bash
cat > /tmp/stream-mjpg.sdp << 'EOF'
v=0
o=- 0 0 IN IP4 127.0.0.1
s=No Name
c=IN IP4 0.0.0.0
t=0 0
m=video 5600 RTP/AVP 26
a=rtpmap:26 JPEG/90000
EOF
```

### Play with ffplay (Low Latency)

```bash
ffplay -probesize 32 \
  -analyzeduration 0 \
  -fflags nobuffer \
  -fflags flush_packets \
  -flags low_delay \
  -framedrop \
  -protocol_whitelist file,udp,rtp,crypto,data \
  /tmp/stream-mjpg.sdp
```

## Important Notes

- Camera Manager is re-enabled when BlueOS restarts.
- To permanently disable it, either repeat step 2 each time or set the `BLUEOS_DISABLE_SERVICES=video` environment variable.
- If Navigator is connected, Camera Manager works normally without these workarounds.

## Current Status Summary

| Item           | Details                                             |
| -------------- | --------------------------------------------------- |
| BlueOS Version | 1.4.3                                               |
| Hardware       | Raspberry Pi 4B                                     |
| Camera         | USB UVC webcam (MJPG/YUYV supported)                |
| Navigator      | Not installed                                       |
| Resolution     | Disable Camera Manager + direct GStreamer streaming |
