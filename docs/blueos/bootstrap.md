# BlueOS Bootstrap Configuration

## Overview

BlueOS runs as a Docker container, and its bootstrap system manages container creation and startup.
It uses its own bootstrap JSON configuration file rather than docker-compose.

## Configuration File Location

```sh
/root/.config/blueos/bootstrap/startup.json
```

- The host's `/root/.config/blueos` is bind-mounted to `/root/.config` inside the container.

## startup.json Structure

```json
{
  "core": {
    "tag": "1.4.3",
    "image": "bluerobotics/blueos-core",
    "enabled": true,
    "webui": false,
    "network": "host",
    "binds": {
      "/dev/": { "bind": "/dev/", "mode": "rw" },
      "/sys/": { "bind": "/sys/", "mode": "rw" },
      "/var/run/wpa_supplicant": {
        "bind": "/var/run/wpa_supplicant",
        "mode": "rw"
      },
      "/tmp/wpa_playground": { "bind": "/tmp/wpa_playground", "mode": "rw" },
      "/var/run/docker.sock": { "bind": "/var/run/docker.sock", "mode": "rw" },
      "/var/logs/blueos": { "bind": "/var/logs/blueos", "mode": "rw" },
      "/run/udev": { "bind": "/run/udev", "mode": "ro" },
      "/home/pi/.ssh": { "bind": "/home/pi/.ssh", "mode": "rw" },
      "/home/pi/.docker": { "bind": "/home/pi/.docker", "mode": "rw" },
      "/root/.docker": { "bind": "/root/.docker", "mode": "rw" },
      "/etc/blueos": { "bind": "/etc/blueos", "mode": "rw" },
      "/etc/machine-id": { "bind": "/etc/machine-id", "mode": "ro" },
      "/etc/dhcpcd.conf": { "bind": "/etc/dhcpcd.conf", "mode": "rw" },
      "/usr/blueos/userdata": { "bind": "/usr/blueos/userdata", "mode": "rw" },
      "/usr/blueos/extensions": {
        "bind": "/usr/blueos/extensions",
        "mode": "rw"
      },
      "/usr/blueos/bin": { "bind": "/usr/blueos/bin", "mode": "rw" },
      "/etc/resolv.conf.host": {
        "bind": "/etc/resolv.conf.host",
        "mode": "ro"
      },
      "/var/run/dbus": { "bind": "/var/run/dbus", "mode": "rw" }
    },
    "privileged": true
  }
}
```

## Adding Environment Variables

Add an `environment` key to `startup.json`.

### Example: Disabling the Video Service

```json
{
    "core": {
        "tag": "1.4.3",
        "image": "bluerobotics/blueos-core",
        "enabled": true,
        "webui": false,
        "network": "host",
        "environment": [
            "BLUEOS_DISABLE_SERVICES=video"
        ],
        "binds": {
            ...
        },
        "privileged": true
    }
}
```

Add the `"environment"` entry below `"network": "host",`.

### Application Procedure

```bash
# 1. Backup
cp /root/.config/blueos/bootstrap/startup.json /root/.config/blueos/bootstrap/startup.json.bak

# 2. Edit
vi /root/.config/blueos/bootstrap/startup.json

# 3. Restart
docker restart blueos-core
# Or reboot the RPi (bootstrap will recreate the container with the new settings)

# 4. Verify
docker inspect blueos-core --format '{{json .Config.Env}}' | python3 -m json.tool
```

## BLUEOS_DISABLE_SERVICES

An environment variable used by the `start-blueos-core` script to disable specified services.

```bash
# Internal logic in start-blueos-core
BLUEOS_DISABLE_SERVICES=${BLUEOS_DISABLE_SERVICES:-""}
BLUEOS_DISABLE_SERVICES=${BLUEOS_DISABLE_SERVICES// /,}

# Check during service creation
if [[ $BLUEOS_DISABLE_SERVICES == *"$1"* ]]; then
    echo "Service: $1 is disabled"
    ...
    return
fi
```

- Multiple services can be specified using commas or spaces: `"BLUEOS_DISABLE_SERVICES=video,wifi"`
- Uses substring matching, so be careful to avoid overlapping service names.

### Available Services

| Service Name   | Description                               |
| -------------- | ----------------------------------------- |
| autopilot      | ArduPilot manager                         |
| cable_guy      | Network cable management                  |
| video          | mavlink-camera-manager (camera/streaming) |
| mavlink2rest   | MAVLink REST API                          |
| kraken         | Service manager                           |
| wifi           | WiFi management                           |
| zenohd         | Zenoh communication                       |
| beacon         | Network beacon                            |
| bridget        | Bridge management                         |
| commander      | Command executor                          |
| nmea_injector  | NMEA data injection                       |
| helper         | System helper                             |
| iperf3         | Network speed testing                     |
| linux2rest     | System information REST API               |
| filebrowser    | File browser web UI                       |
| versionchooser | Version management UI                     |
| pardal         | Notification service                      |
| ping           | Sonar ping management                     |
| ttyd           | Web terminal                              |
| nginx          | Web server / reverse proxy                |
| log_zipper     | Log compression                           |
| bag_of_holding | Data storage                              |

## Container Runtime Information

- Image: `bluerobotics/blueos-core:1.4.3`
- Network: host mode
- Start command: `/bin/bash -i -c "/usr/bin/start-blueos-core && sleep infinity"`
- Privileged mode: enabled (full access to all host devices)
