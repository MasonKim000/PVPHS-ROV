# AI 물체 감지 가이드

## 이게 뭐하는 건가요?

카메라 스트리밍에서 AI(YOLOv8)를 사용해 실시간으로 물체를 감지합니다.
감지를 켜면, 카메라가 인식한 물체(사람, 컵, 휴대폰 등) 주위에
네모 박스와 이름표를 그려서 영상에 보여줍니다.

## 작동 원리 (쉬운 설명)

```
카메라가 사진(프레임) 한 장을 찍음
        |
        v
YOLO AI 모델이 사진을 분석
        |
        v
찾은 물체에 네모 박스 + 이름표를 그림
        |
        v
결과가 그려진 사진을 브라우저로 전송
```

**YOLO** (You Only Look Once, "한 번만 보면 됨")는 80가지 이상의 물체를 인식할 수 있는 AI 모델입니다.
우리는 라즈베리파이에서 돌릴 수 있도록 가장 작은 버전인 **YOLOv8n** ("n" = nano, 초소형)을 사용합니다.

## NCNN - 더 빠르게 만들기

YOLO 모델은 원래 PyTorch 형식(`.pt`)인데, 라즈베리파이에서는 느립니다.
이걸 **NCNN** 형식으로 변환하면 파이의 ARM CPU에 최적화되어 훨씬 빨라집니다.

| 형식 | 파이에서 속도 |
|------|-------------|
| `.pt` (PyTorch) | ~1-2 FPS (슬라이드쇼 수준) |
| NCNN | ~5-8 FPS (쓸만함) |

변환 방법 (처음 한 번만 하면 됨):

```sh
uv run python convert.py
```

이렇게 하면 `yolov8n_ncnn_model/` 폴더가 생기고, 서버가 자동으로 이 모델을 사용합니다.

## API 사용법

| 동작 | 명령어 |
|------|--------|
| 감지 켜기 | `curl -X POST http://localhost:8000/detect/on` |
| 감지 끄기 | `curl -X POST http://localhost:8000/detect/off` |
| 상태 확인 | `curl http://localhost:8000/detect/status` |

감지는 **기본적으로 꺼져 있습니다**. 필요할 때만 켜세요.

## 주의사항

- 감지를 켜면 CPU를 많이 사용합니다 (~100%). 안 쓸 때는 꺼두세요.
- 모델 파일(`yolov8n.pt`, `yolov8n_ncnn_model/`)은 git에 포함되지 않습니다. 새 파이에서는 `convert.py`를 실행해야 합니다.
- YOLO가 감지할 수 있는 물체는 80종류 (사람, 자동차, 동물, 가구 등). 전체 목록: https://docs.ultralytics.com/datasets/detect/coco/

## 새 라즈베리파이에서 설정하기

```sh
cd backend
uv sync                       # 모든 패키지 설치
apt install -y libgl1          # OpenCV에 필요한 시스템 라이브러리
uv run python convert.py       # YOLO 모델 다운로드 + 변환
uv run uvicorn main:app --host 0.0.0.0 --port 8000  # 서버 시작
```
