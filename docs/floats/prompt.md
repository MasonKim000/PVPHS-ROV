# floats Prompt

copy pdf then add to chat

```text
please review this document
let's use english for all communication
```

```text
Identify all the implementation requirements from this document and save them to implement.md.
```

```markdown
/clear
넌 뛰어난 Python developer야.
Float Mission Station 프로그램을 만들어줘.

목표: Float의 자동 깊이 제어를 시뮬레이션하고,
센서 데이터를 실시간으로 시각화하는 프로그램.
컴퓨터에서 먼저 테스트하고, 나중에 실제 하드웨어로 교체할 수 있는 구조.

## 핵심 아키텍처 (제어 루프)

센서(깊이) -> Controller(PID) -> 부력 엔진 명령 -> Float -> 센서(깊이)

- FloatHardware ABC: 실제 Float 하드웨어 인터페이스
  - read_sensors() -> depth, pressure
  - send_command(buoyancy_pct) -> 부력 엔진 제어 (-100~+100%)
  - SimulatedFloat: 물리 모델 구현체 (부력/드래그/관성 시뮬레이션)
  - 나중에 SerialFloat 등으로 실제 하드웨어 연결

- Controller: 미션 시퀀서 + PID 깊이 제어
  - 미션 단계 자동 진행: DEPLOY -> DESCEND(2.5m) -> HOLD 30s -> ASCEND(0.4m)
    -> HOLD 30s -> (2차 반복) -> SURFACE
  - PID 컨트롤러가 목표 깊이와 현재 깊이를 비교해서 부력 엔진 명령을 자동
    생성
  - 5초 간격으로 data packet 생성

- DataSource ABC: 데이터 수신 인터페이스 (기존 유지)
  - ControlledSource: Controller + SimulatedFloat를 연결하는 구현체

## UI 방식

- matplotlib + FuncAnimation 기반 실시간 애니메이션
  (PySide6/tkinter 사용하지 않음)
- 2x2 subplot 레이아웃:
  - [0,0] Depth vs Time 그래프 (X=시간, Y=깊이, Y축 반전,
    목표 깊이 구간 색상 밴드 표시)
  - [0,1] Pool Cross-Section (풀 단면도에서 Float 위치를
    실시간 애니메이션)
  - [1,0] 압력-시간 그래프
  - [1,1] Mission Status 텍스트 패널 (monospace 폰트,
    Phase/Time/Depth/Pressure/Buoyancy Command/PID Output/Packets 등)
- 실행하면 바로 시뮬레이션 시작, 별도 버튼 없음
- figsize=(14, 9), tight_layout

## 기능

- Float 센서 데이터를 실시간으로 화면에 표시
- 깊이-시간 그래프 생성 (최소 20개 데이터 포인트)
- 목표 깊이 구간 표시 (2.5m +-0.33m 파란 밴드, 0.4m +-0.33m 초록 밴드)
- PID 컨트롤러가 자동으로 부력 엔진을 제어하여 목표 깊이 도달/유지
- 시뮬레이션 모드: SimulatedFloat 물리 모델로 컴퓨터에서 테스트
- CLI 인자로 company number, 시뮬레이션 속도, PID 게인 등 설정 가능
- FloatHardware ABC 추가 (센서 읽기 + 부력 명령 전송)
- Controller 추가 (미션 시퀀서 + PID 자동 제어)
- SimulatedFloat 물리 모델 (가짜 데이터 생성이 아닌 물리 시뮬레이션)
- Status 패널에 Buoyancy Command / PID Output 표시

## 조건

- uv init으로 프로젝트 시작
- 의존성: matplotlib, numpy만 사용
- 상세 미션 스펙은 implement.md 참고

Project directory : /Users/ragon/Desktop/GitHub/PVPHS-ROV/float-station
```

```sh
아직 플랜을 만들고 싶어 . 어떻게 할거야?
```

```text
구현해라
```
