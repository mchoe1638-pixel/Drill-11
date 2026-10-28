# Drill #11 — 소년 자동 무적 런(AutoRun) 상태 추가

## 레퍼런스 (먼저 읽어라)
- @AGENTS.md — 이 프로젝트 규칙. pico2d다, pygame 아니다. 여기 어긋나면 틀린 코드다.
- @drill11.py — 수정할 베이스 코드 (Grass + Boy + game loop)
- @animation_sheet.png — 스프라이트 시트. 각 프레임 100x100.
  행(bottom y)별로 어떤 동작인지 네가 직접 clip_draw 값 바꿔가며 확인하고,
  확인 결과를 코드 주석에 남겨라. 추측해서 넘어가지 마라.

## 요구사항 (채점 기준이다, 하나도 빠뜨리지 마라)
소년에게 상태 머신을 구현하고 AutoRun 상태를 추가한다.

상태: Idle, Run, AutoRun  (※ Sleep은 이번 과제 범위 아님)

1. Idle 상태에서 'a' 키를 누르면 AutoRun 상태로 전이한다. (1점)
2. AutoRun 상태에서는 키 입력 없이 좌/우로 계속 자동 이동한다.
3. AutoRun 상태의 소년은 Run 상태보다 **속도가 빠르고 크기가 커야 한다**. (1점)
   - 크기는 clip_draw의 w,h 인자를 키워서 처리 (예: 100x100 → 150x150)
4. AutoRun 상태에서 화면 좌/우측 끝에 닿으면 **자동으로 방향 전환**한다. (1점)
   - 캔버스 800x600 기준, 캐릭터 폭의 절반을 고려해서 끝 판정
5. AutoRun 상태 진입 후 **5초 이상 경과하면 Idle 상태로 복귀**한다. (1점)
   - 반드시 get_time() 기반으로 실제 경과 시간 측정. 프레임 카운트로 세지 마라.
6. AutoRun 상태에서 방향키(←/→)가 눌리면 AutoRun이 취소되고,
   눌린 방향으로 움직이는 일반 Run 상태로 전이한다.
7. **AutoRun은 반드시 별도의 상태 클래스로 구현한다.** (필수 조건)
   - Idle, Run, AutoRun 각각 독립 클래스
   - 각 클래스는 enter(boy, e), exit(boy, e), do(boy), draw(boy)를 가진다
   - 전이 테이블(dict)로 상태 전환을 관리한다
   - if/elif로 상태 분기하는 방식은 금지. 과제 조건 위반이다.

## 구현 제약
- 이벤트는 (type, value) 튜플로 추상화하고, right_down/left_down/right_up/left_up/
  a_down 같은 판별 함수로 전이 테이블 키를 만들어라.
- 이동은 반드시 프레임 독립적으로: 픽셀/초 속도 상수 × frame_time.
  AGENTS.md 규칙이다. 프레임당 고정 픽셀 이동 금지.
- 리소스(load_image)는 클래스 변수로 1회만 로딩.
- 기존 Grass, reset_world/update_world/render_world 구조는 유지하고,
  요청하지 않은 리팩터링은 하지 마라.

## 산출물
1. `drill11.py` — 실행 가능한 완성 코드
2. `state_diagram.md` — Mermaid stateDiagram-v2로 상태 다이어그램 작성
   (Idle/Run/AutoRun 3개 상태, 모든 전이에 트리거 이벤트 라벨 표기:
    'a' 누름, 5초 경과, 방향키 누름/뗌)
3. `state_diagram.png` — 위 다이어그램을 이미지로 렌더링해서 저장.
   **제출물에 이미지 파일이 반드시 포함돼야 한다 (1점).**
   (mermaid CLI가 없으면 설치 여부를 나에게 물어보고,
    설치가 어려우면 대안 방법을 제안해라)
4. `README.md` — 과제 개요, 상태별 동작 설명, 조작법(a/←/→/ESC),
   실행 방법, 상태 다이어그램 이미지 삽입, 채점 기준 6항목 대응표

## 작업 순서
1. AGENTS.md와 drill11.py를 먼저 읽고, 스프라이트 시트 행 구조를 확인한다
2. 구현 계획을 3줄로 요약만 하고 바로 구현에 들어가라. 승인 기다리지 마라.
3. 승인 후 구현
4. 검증은 두 단계로:
   (a) `.venv\Scripts\python.exe -m py_compile drill11.py` 로 문법 확인
   (b) 게임 루프를 직접 실행하지 마라. 무한 루프라 네 쪽에서 멈춘다.
       대신 "실행해봐라"라고 나에게 말하고 기다려라. 내가 돌려보고 결과를 알려준다.
5. 산출물 4개 생성