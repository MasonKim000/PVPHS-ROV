# MATE Floats 2026 "Under the Ice" - Implementation Requirements

Total: 70 points

## 1. Scoring Summary

| #   | Item                            | Points | Condition                               |
| --- | ------------------------------- | ------ | --------------------------------------- |
| 1   | Float 설계 및 제작              | 5      | DOC-004 제출 + 미션 스테이션에 운반     |
| 2   | 배치 후 통신 (하강 전)          | 5      | 수신기에 data packet 1개 이상 표시      |
| 3   | 1차 프로필 완료 (부력 엔진)     | 10     | 2.5m까지 하강 후 40cm까지 상승          |
| 3a  | 1차 프로필 완료 (다른 메커니즘) | 5      | 위와 동일하나 부력 엔진 미사용          |
| 4   | 1차 프로필 - 2.5m 깊이 유지     | 5      | 30초간 2.5m (+/- 33cm) 유지             |
| 5   | 1차 프로필 - 40cm 깊이 유지     | 5      | 30초간 40cm (+/- 33cm) 유지             |
| 6   | 1차 프로필 - 수면/얼음 접촉     | -5     | 수면 돌파 또는 얼음 접촉 시 감점        |
| 7   | 2차 프로필 완료 (부력 엔진)     | 10     | 2.5m까지 하강 후 40cm까지 상승          |
| 7a  | 2차 프로필 완료 (다른 메커니즘) | 5      | 위와 동일하나 부력 엔진 미사용          |
| 8   | 2차 프로필 - 2.5m 깊이 유지     | 5      | 30초간 2.5m (+/- 33cm) 유지             |
| 9   | 2차 프로필 - 40cm 깊이 유지     | 5      | 30초간 40cm (+/- 33cm) 유지             |
| 10  | 2차 프로필 - 수면/얼음 접촉     | -5     | 수면 돌파 또는 얼음 접촉 시 감점        |
| 11  | 회수 후 전체 데이터 전송        | 10     | 모든 data packet 전송 (5초 간격)        |
| 11a | 회수 후 일부 데이터 전송        | 5      | 최소 1개 data packet 전송               |
| 12  | 깊이-시간 그래프                | 10     | X=시간, Y=깊이, 최소 20개 데이터 포인트 |
| 12a | MATE 데이터로 그래프 (대체)     | 10     | Float 미제작 또는 데이터 전송 실패 시   |

## 2. Mission Procedure (순서)

1. **DOC-004 제출** — 대회 전 비ROV 장치 설계 문서 제출
2. **Float 배치** — 수면에 손으로 투하 (hand-launch)
3. **배치 후 통신** — 수신기에 data packet 전송 확인 (하강 전 필수)
4. **1차 Vertical Profile**
   - 수면에서 2.5m까지 하강
   - 2.5m에서 30초간 깊이 유지
   - 40cm까지 상승 (수면 돌파 금지)
   - 40cm에서 30초간 깊이 유지
5. **2차 Vertical Profile** — 1차와 동일한 과정 반복
6. **Float 회수** — Regional: 자체 ROV로 회수 / World: MATE ROV가 회수
7. **데이터 전송** — 회수 후 무선으로 수신기에 data packet 전송
8. **그래프 작성** — 수신 데이터로 깊이-시간 그래프 작성

## 3. Float Physical Specifications

| Spec         | Value                                   |
| ------------ | --------------------------------------- |
| 최대 높이    | 1m 미만 (안테나 포함)                   |
| 최대 직경/폭 | 18cm 미만                               |
| 수면 연결    | 금지 (에어라인, 로프, 테더 불가)        |
| 분리/확장    | 금지 (분리되는 구획, 1m 초과 확장 불가) |
| 카메라       | 금지 (ELEC-NRD-002)                     |

### Recovery Feature (2026 신규, 필수)

- 최소 5cm 폭
- Float에서 최소 5cm 돌출
- MATE ROV가 잡을 수 있는 형태 (예: 로프 루프, U-bolt #310 이상, 기타)
- 18cm 직경 제한 초과 가능
- 이중화 권장 (빠른 회수 = 더 많은 데이터 처리 시간)

## 4. Electrical / Battery Specifications

### Power Rules

| Rule      | Value                                                 |
| --------- | ----------------------------------------------------- |
| 최대 전압 | 12 VDC                                                |
| 최대 전류 | 5A                                                    |
| 퓨즈      | 단일 퓨즈 필수, 배터리 양극 5cm 이내 설치             |
| 퓨즈 종류 | Cartridge, ATO blade, MINI blade (1A/2A/3A/4A/5A)     |
| 퓨즈 검사 | 투명 하우징 또는 하우징 제거 후 즉시 확인 가능해야 함 |
| 수면 전원 | 금지 (온보드 배터리만 사용)                           |

### Allowed Batteries

| Battery Type     | Max Fuse Size |
| ---------------- | ------------- |
| NiMH AA          | 2.0A          |
| NiMH C or D      | 5.0A          |
| NiMH 9V          | 200mA         |
| NiMH 12V (brick) | 5.0A          |
| AGM 12V          | 5.0A          |

- Alkaline 금지
- LiPo 금지
- 12V 야외용 충전식 금지
- 소형 button battery는 타이밍 장치 전용으로 허용
- 배터리는 컨테이너 내부에 고정 필수

### Parallel Battery Rules

- 병렬 시 총 전류 5A 초과 불가
- 병렬 시 퓨즈 크기 = 개별 퓨즈 x 병렬 수
- 다중 배터리 팩: 공통 음극 단자에 5A 이하 퓨즈 + 각 팩에 개별 퓨즈

### FLA (Full Load Amps) 측정 필수

- **대기 모드** (모터 OFF) 측정
- **부력 변경 모드** (모터 ON) 측정
- 측정값으로 퓨즈 크기 결정

## 5. Buoyancy Engine

### Definition

부력 엔진 = Float 내부에서 외부로 유체를 이동시켜 해수를 배수(displace)하고 Float 밀도를 변경하는 장치

- 모터로 공기/액체를 이동 = 부력 엔진 (O)
- 모터로 프로펠러/워터젯 = 부력 엔진 아님 (X) -> 감점 아닌 5점 (10점 대신)

## 6. Data Communication

### Defined Data Packet (필수 전송 항목)

1. **Company number** — MATE에서 대회 전 제공
2. **Time data** — UTC / local / float time (기록 시작 이후 시간)
3. **Pressure data** — pa 또는 kpa 단위
4. **Depth data** — m 또는 cm 단위
5. **추가 데이터** — 태스크 완수에 필요한 추가 항목

예시: `EX01 1:51:42 UTC 9.8 kpa 1.00 meters`

### Communication Requirements

- Float에 송신기, 미션 스테이션에 수신기 — 둘 다 자체 제작
- 수신기는 Float 이외의 소스에서 수신하면 안 됨
- 다른 팀도 동시에 전송하므로 간섭 대책 필요
- 배치 후 하강 전에 최소 1개 data packet 전송 필수
- 회수 후 무선으로 data packet 전송

### Scoring Detail

- 전체 data packet 전송 (5초 간격 모든 프로필): 10점
- 최소 1개 data packet 전송 (프로필 하강 이후): 5점

## 7. Depth Maintenance Specifications

### 2.5m Depth Hold

| Parameter        | Value                                 |
| ---------------- | ------------------------------------- |
| 목표 깊이        | 2.5m (Float 하단 기준)                |
| 허용 범위        | 2.27m ~ 2.83m (+/- 33cm)              |
| 유지 시간        | 30초                                  |
| 필요 data packet | 7개 연속 (0, 5, 10, 15, 20, 25, 30초) |
| 범위 이탈 시     | 전체 30초 재시작                      |

### 40cm Depth Hold

| Parameter        | Value                                 |
| ---------------- | ------------------------------------- |
| 목표 깊이        | 40cm (Float 상단 기준)                |
| 허용 범위        | 0.07m ~ 0.73m (+/- 33cm)              |
| 유지 시간        | 30초                                  |
| 필요 data packet | 7개 연속 (0, 5, 10, 15, 20, 25, 30초) |
| 범위 이탈 시     | 전체 30초 재시작                      |

### Sensor Offset

- 깊이/압력 센서가 Float 하단/상단에 없을 경우, offset을 심판에게 사전 고지
- 예: 센서가 하단에서 25cm 위 -> 2.5m 기준은 센서 위치 2.25m, 범위 1.92m ~ 2.58m

## 8. Graph Requirements

- X축: 시간
- Y축: 깊이
- 최소 20개 data point 필요
- 컴퓨터/디바이스로 작성 (수작업 그래프 불가)
- 데이터 포인트 수동 입력/붙여넣기 허용

## 9. Safety Specifications

### Pressure Relief (ELEC-NRD-006)

두 가지 방법 중 택1:

1. **압력 릴리프 홀** — 최소 2.5cm 직경, 고무 마개로 마찰 끼움 (나사/체결 금지)
2. **팝오프 엔드캡** — 가압 시 빠지는 구조, 실링 직경 2.5cm 이상

- 하우징에 체결 장치(fastener) 사용 금지
- 압력 릴리프 밸브 사용 불가 (현장 테스트 불가)
- 조임 메커니즘 (호스 클램프, Twist-Tite) 사용 불가

## 10. DOC-004 Submission Requirements (2+1 pages)

### 본문 (2페이지)

- Float 사진 또는 다이어그램
- 사용 배터리 종류
- 모든 배터리 팩 사진
- 퓨즈 사진
- FLA 측정값 (대기 모드 + 부력 변경 모드)에 기반한 퓨즈 결정
- 부력 엔진 또는 다른 메커니즘 설명
- 수신기와의 통신 방식 설명 (배치 후 명령 전송 포함)
- 배터리 팩 설계 설명 (FLA 및 전압 요구사항)

### SID (1페이지)

- 표준 퓨즈 심볼이 포함된 회로도
- FLA 퓨즈 측정값

## 11. Competition-Specific Notes

### Regional Competition

- 얼음 = 수면으로 가정 (시뮬레이션)
- 15분 제한 (float 회수 + 데이터 전송 + 그래프 작성 포함)
- 자체 ROV로 float 회수
- Regional coordinator에게 풀 깊이 확인 (2.5m 미만일 수 있음)

### World Championship (NRC Ice Tank)

- 실제 얼음 (1~5cm 두께)
- 1m x 1m 구멍으로 float 투하
- EGADS 수용액 (비중 약 1.025)
- MATE ROV가 float 회수 (회수 중 미션 타임 정지)
- 방한 장비 준비 필요 (장갑 등)

## 12. Visual Cues (Optional)

- LED 등으로 깊이 도달 상태를 수면에서 확인 가능
- 예: 파란색 LED = 2.5m 범위, 초록색 LED = 0.4m 범위
- 점수에 영향 없음, 회수 시점 판단에 도움

## 13. Additional Rules

- 프로필 간 mix and match 금지 (각 프로필은 전체로 평가)
- 2회 프로필 후 추가 프로필 시도 가능 (더 높은 점수 프로필로 교체 가능)
- Float가 하강 전에 통신 실패 시 회수 후 수리 가능
- Float가 통신 없이 하강하면 통신 점수 불가, 나머지 태스크 계속 가능
- MATE 데이터 요청 시, 전체 데이터 전송 점수 + 자체 데이터 그래프 점수 포기
