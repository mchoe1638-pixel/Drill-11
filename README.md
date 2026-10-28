# Drill #11 — 소년 자동 무적 런(AutoRun) 상태 추가

2D 게임 프로그래밍 / pico2d
학번 2023184043 최명규

## 과제 개요

소년 캐릭터에 상태 머신을 적용하고, 기존 Idle / Run 에 더해
**AutoRun(자동 무적 런)** 상태를 별도의 상태 클래스로 추가한다.

AutoRun 은 키 입력 없이 좌우로 자동 이동하며, 일반 Run 보다 빠르고 크다.
화면 끝에 닿으면 스스로 방향을 바꾸고, 5초가 지나면 Idle 로 돌아간다.
도중에 방향키를 누르면 AutoRun 이 취소되고 그 방향의 Run 으로 전이한다.

## 실행 방법

전역 python 에는 pico2d 가 설치되어 있지 않다. 반드시 venv 의 python 으로 실행한다.

```
cd C:\Users\chlau\Desktop\2dGameProgramming\Drill#11
..\2dGameProgramming\.venv\Scripts\python.exe autorun.py
```

## 조작법

| 키 | 동작 |
|---|---|
| → | 오른쪽으로 Run |
| ← | 왼쪽으로 Run |
| a | AutoRun 시작 (Idle 중에도, 방향키를 누르고 있는 Run 중에도 동작) |
| ESC | 종료 |

## 상태 다이어그램

![상태 다이어그램](state_diagram.png)

Mermaid 원본은 [state_diagram.md](state_diagram.md) 참조.

## 상태별 동작

### Idle
제자리 대기. 마지막으로 보던 방향의 대기 애니메이션을 재생한다.
방향키를 누르면 Run, `a` 키를 누르면 AutoRun 으로 전이한다.

### Run
눌린 방향으로 `RUN_SPEED_PPS`(20km/h 환산) 속도로 이동한다.
화면 밖으로 나가지 않도록 좌우 끝에서 위치를 clamp 하되, 방향 전환은 하지 않는다.
Run 중에 `a` 를 누르면 AutoRun 으로 전이한다.

### AutoRun
- 진입 시점의 `face_dir` 방향으로 자동 출발한다.
- 속도는 Run 의 **2배**, 크기는 **1.5배(150x150)** 로 그린다.
  확대된 만큼 draw 의 y 를 올려서 발이 땅에 붙어 보이게 보정했다.
- 화면 좌/우측 끝에 닿으면 `dir` 과 `face_dir` 을 뒤집어 **자동 방향 전환**한다.
  이때 끝 판정은 확대된 폭의 절반(75px)을 기준으로 한다.
- 진입 시 `get_time()` 을 기록하고, 경과가 5초 이상이면 `TIME_OUT` 이벤트를
  스스로 상태 머신 큐에 넣어 Idle 로 복귀한다.

## 채점 기준 대응표

| 채점 기준 | 배점 | 구현 위치 |
|---|---|---|
| 'a' 누르면 AutoRun 상태 이동 | 1점 | `Boy.set_transitions` 의 `Idle: {a_down: AutoRun}`, `Run: {a_down: AutoRun}` |
| 5초 이상 경과하면 Idle 복귀 | 1점 | `AutoRun.do` 의 `get_time() - auto_start_time >= AUTO_RUN_DURATION` |
| AutoRun 에서 속도 빨라지고 크기 커짐 | 1점 | `AutoRun.enter` 의 `AUTO_RUN_SPEED_PPS`, `AUTO_RUN_SCALE` / `AutoRun.draw` |
| AutoRun 에서 좌우측 끝 자동 방향 전환 | 1점 | `AutoRun.do` 의 경계 판정 분기 |
| 상태 다이어그램 | 1점 | `state_diagram.png`, `state_diagram.md` |
| AutoRun 상태 클래스 별도 구현 (필수) | — | `class AutoRun` (enter/exit/do/draw) |

## 구현 노트

### 상태 머신 구조
`StateMachine` 이 전이 테이블(dict)만 보고 상태를 바꾼다.
`if 상태 == ...` 형태의 분기는 쓰지 않았다.
각 상태 클래스는 `enter / exit / do / draw` 네 개의 staticmethod 를 가진다.

### 프레임 독립 이동
속도는 픽셀/초 상수로 정의하고 매 프레임 `frame_time` 을 곱한다.
`game_framework.tick()` 이 `get_time()` 차이로 `frame_time` 을 갱신한다.
프레임당 고정 픽셀 이동은 쓰지 않았다. 5초 판정도 프레임 카운트가 아니라
실제 경과 시간 기준이다.

### 스프라이트 시트 행 구조 확인
`animation_sheet.png`(802x402)의 행 배치를 추측하지 않고 시트를 잘라서 직접 확인했다.

| clip_draw bottom | 내용 |
|---|---|
| 300 | Idle 오른쪽 |
| 200 | Idle 왼쪽 |
| 100 | Run 오른쪽 |
| 0 | Run 왼쪽 |

캐릭터가 모자를 뒤로 쓰고 있어서 모자챙 방향과 진행 방향이 반대다.
모자(초록)와 얼굴(살색) 픽셀의 x 중심을 비교해 얼굴이 있는 쪽을 정면으로 판정했다.

### AutoRun 타이머 무효화
`AutoRun.exit` 에서 `auto_start_time = None`, `auto_timeout_fired = True` 로
타이머를 끈다. 이 처리를 빼면 방향키로 Run 에 들어간 뒤에도 남아있던
TIME_OUT 이 날아와 달리는 도중 Idle 로 튀는 버그가 생긴다.
상태 머신에서 타이머를 쓸 때 가장 흔한 실수 지점이라 enter 와 exit 를 쌍으로 맞췄다.

## AI 활용 및 검증 과정

AI(Claude)로 초기 구현을 생성한 뒤, 직접 실행해 동작을 검증하고 수정했다.

### 1차 구현 후 실행 테스트에서 발견한 문제
**증상:** 방향키를 누르고 있는 상태에서 `a` 를 누르면 AutoRun 으로 전환되지 않고
계속 Run 상태로 달렸다.

**원인:** 전이 테이블에서 `a_down` 을 `Idle` 상태에만 등록해 두었다.
과제 명세가 "Idle 상태에서 'a'키를 누르면" 이라고 되어 있어 AI 가 Idle 에만 넣은 것인데,
실제로 플레이해 보면 방향키를 누르고 있는 동안에는 상태가 Run 이라서
`a` 입력이 전이 테이블에서 매칭되지 않고 그대로 버려졌다.
상태 머신에서 이벤트가 '무시'되는 경우는 에러가 나지 않기 때문에
코드만 읽어서는 드러나지 않고, 실행해 봐야 발견되는 종류의 문제였다.

**수정:** `Run` 상태의 전이 테이블에도 `a_down: AutoRun` 을 추가했다.
이에 맞춰 상태 다이어그램에도 `Run --> AutoRun` 전이를 추가해
코드와 다이어그램이 일치하도록 함께 갱신했다.

### AI 결과를 그대로 쓰지 않고 검증한 부분
- **스프라이트 시트 행 구조:** AI 가 추측으로 `clip_draw` 의 bottom 값을 쓰지 않도록,
  시트를 프레임 단위로 잘라 모자와 얼굴 픽셀 위치를 비교해 방향을 판정한 뒤
  그 결과를 코드 주석에 근거와 함께 남겼다.
- **AutoRun 타이머:** AutoRun 에서 방향키로 Run 에 진입한 뒤에도 남은 TIME_OUT 이
  날아와 달리는 도중 Idle 로 튀는 버그가 생길 수 있는 구조라,
  `AutoRun.exit` 에서 타이머를 무효화하도록 하고 실제로 눌러서 확인했다.
- **확대 시 접지:** AutoRun 에서 크기를 1.5배로 키우면 발이 땅에 묻히므로
  draw 의 y 를 보정했고, 화면 끝 판정도 확대된 폭 기준으로 바꿨다.
