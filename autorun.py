# =============================================================================
# Drill #11 - 소년 자동 무적 런(AutoRun) 상태 추가
# 2D 게임 프로그래밍 / pico2d
#
# animation_sheet.png (802x402) 행 구조 - 시트를 직접 잘라서 확인한 결과:
#   clip_draw bottom=300 : Idle 오른쪽 보기
#   clip_draw bottom=200 : Idle 왼쪽 보기
#   clip_draw bottom=100 : Run  오른쪽 달리기
#   clip_draw bottom=  0 : Run  왼쪽 달리기
#   프레임 크기 100x100, 가로 8프레임
#
# 조작: 좌/우 방향키 = Run, 'a' = AutoRun, ESC = 종료
# =============================================================================

from pico2d import *

CANVAS_W, CANVAS_H = 800, 600

# ---- 속도는 픽셀/초로 정의한다 (프레임 독립 이동) ----
PIXEL_PER_METER = 10.0 / 0.3                      # 10픽셀 = 30cm
RUN_SPEED_KMPH = 20.0                             # 일반 Run 속도
RUN_SPEED_PPS = (RUN_SPEED_KMPH * 1000.0 / 3600.0) * PIXEL_PER_METER

AUTO_RUN_SPEED_PPS = RUN_SPEED_PPS * 2.0          # 요구3: 더 빠르게
AUTO_RUN_SCALE = 1.5                              # 요구3: 더 크게
AUTO_RUN_DURATION = 5.0                           # 요구5: 5초 경과 시 Idle 복귀

TIME_PER_ACTION = 0.5                             # 한 동작(8프레임)에 걸리는 시간
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

FRAME_SIZE = 100
GROUND_Y = 90


# =============================================================================
# 이벤트 추상화 : SDL 이벤트를 (종류, 값) 튜플로 바꿔서 상태머신에 넣는다
# =============================================================================
def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def time_out(e):
    return e[0] == 'TIME_OUT'


# =============================================================================
# 상태 클래스 : 각각 enter / exit / do / draw 를 가진다
# =============================================================================
class Idle:
    @staticmethod
    def enter(boy, e):
        boy.dir = 0
        boy.frame = 0
        boy.speed = 0.0
        boy.scale = 1.0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION

    @staticmethod
    def draw(boy):
        row = 300 if boy.face_dir == 1 else 200
        boy.image.clip_draw(int(boy.frame) * FRAME_SIZE, row,
                            FRAME_SIZE, FRAME_SIZE, boy.x, boy.y)


class Run:
    @staticmethod
    def enter(boy, e):
        # 어떤 방향키 이벤트로 들어왔는지에 따라 진행 방향을 정한다
        if right_down(e) or left_up(e):
            boy.dir, boy.face_dir = 1, 1
        elif left_down(e) or right_up(e):
            boy.dir, boy.face_dir = -1, -1
        boy.speed = RUN_SPEED_PPS
        boy.scale = 1.0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        boy.x += boy.dir * boy.speed * game_framework.frame_time
        # 일반 Run은 화면 밖으로 나가지 않게 clamp (방향 전환은 하지 않음)
        half = FRAME_SIZE * boy.scale * 0.5
        boy.x = clamp(half, boy.x, CANVAS_W - half)

    @staticmethod
    def draw(boy):
        row = 100 if boy.face_dir == 1 else 0
        boy.image.clip_draw(int(boy.frame) * FRAME_SIZE, row,
                            FRAME_SIZE, FRAME_SIZE, boy.x, boy.y)


class AutoRun:
    """요구7: AutoRun은 반드시 별도의 상태 클래스로 구현."""

    @staticmethod
    def enter(boy, e):
        boy.dir = boy.face_dir                 # 보고 있던 방향으로 자동 출발
        boy.speed = AUTO_RUN_SPEED_PPS         # 요구3: 더 빠르게
        boy.scale = AUTO_RUN_SCALE             # 요구3: 더 크게
        boy.auto_start_time = get_time()       # 요구5: 실제 경과 시간 기준
        boy.auto_timeout_fired = False

    @staticmethod
    def exit(boy, e):
        # 타이머를 확실히 무효화한다.
        # 이걸 빼먹으면 방향키로 Run에 들어간 뒤에도 TIME_OUT이 날아와
        # 달리는 도중 Idle로 튀는 버그가 생긴다.
        boy.auto_start_time = None
        boy.auto_timeout_fired = True
        boy.scale = 1.0

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        boy.x += boy.dir * boy.speed * game_framework.frame_time

        # 요구4: 화면 좌/우측 끝에서 자동 방향 전환 (확대된 크기를 반영)
        half = FRAME_SIZE * boy.scale * 0.5
        if boy.x < half:
            boy.x = half
            boy.dir = 1
            boy.face_dir = 1
        elif boy.x > CANVAS_W - half:
            boy.x = CANVAS_W - half
            boy.dir = -1
            boy.face_dir = -1

        # 요구5: 5초 이상 경과하면 Idle로 복귀
        if (not boy.auto_timeout_fired
                and boy.auto_start_time is not None
                and get_time() - boy.auto_start_time >= AUTO_RUN_DURATION):
            boy.auto_timeout_fired = True
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        row = 100 if boy.face_dir == 1 else 0
        size = FRAME_SIZE * boy.scale
        # 커진 만큼 위로 올려서 발이 땅에 붙어 보이게 한다
        draw_y = boy.y + (size - FRAME_SIZE) * 0.5
        boy.image.clip_draw(int(boy.frame) * FRAME_SIZE, row,
                            FRAME_SIZE, FRAME_SIZE, boy.x, draw_y, size, size)


# =============================================================================
# 상태 머신 : 전이 테이블(dict)로만 상태를 바꾼다 (if/elif 분기 금지)
# =============================================================================
class StateMachine:
    def __init__(self, obj):
        self.obj = obj
        self.cur_state = Idle
        self.transitions = {}
        self.event_que = []

    def start(self, state):
        self.cur_state = state
        self.cur_state.enter(self.obj, ('START', 0))

    def set_transitions(self, transitions):
        self.transitions = transitions

    def add_event(self, e):
        self.event_que.append(e)

    def update(self):
        self.cur_state.do(self.obj)
        if self.event_que:
            e = self.event_que.pop(0)
            for check_event, next_state in self.transitions[self.cur_state].items():
                if check_event(e):
                    self.cur_state.exit(self.obj, e)
                    self.cur_state = next_state
                    self.cur_state.enter(self.obj, e)
                    return

    def draw(self):
        self.cur_state.draw(self.obj)


# =============================================================================
# 게임 오브젝트
# =============================================================================
class Grass:
    image = None

    def __init__(self):
        if Grass.image is None:                 # 리소스는 클래스 변수로 1회만 로딩
            Grass.image = load_image('grass.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 30)


class Boy:
    image = None

    def __init__(self):
        if Boy.image is None:
            Boy.image = load_image('animation_sheet.png')
        self.x, self.y = CANVAS_W // 2, GROUND_Y
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.speed = 0.0
        self.scale = 1.0
        self.auto_start_time = None
        self.auto_timeout_fired = True

        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions({
            Idle:    {right_down: Run,  left_down: Run,
                      right_up:   Run,  left_up:   Run,
                      a_down:     AutoRun},
            # Run 중에도 'a'를 누르면 AutoRun으로 전이한다.
            # (방향키를 누르고 있는 상태에서 a를 눌러도 적용되도록)
            Run:     {right_down: Idle, left_down: Idle,
                      right_up:   Idle, left_up:   Idle,
                      a_down:     AutoRun},
            # 요구6: AutoRun 중 방향키를 누르면 그 방향 Run으로 전이
            AutoRun: {time_out:   Idle,
                      right_down: Run,  left_down: Run},
        })

    def handle_event(self, event):
        self.state_machine.add_event(('INPUT', event))

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()


# =============================================================================
# 프레임 타임 관리
# =============================================================================
class game_framework:
    frame_time = 0.0
    _last_time = 0.0

    @staticmethod
    def init_time():
        game_framework._last_time = get_time()

    @staticmethod
    def tick():
        now = get_time()
        game_framework.frame_time = now - game_framework._last_time
        game_framework._last_time = now


# =============================================================================
# 월드 / 게임 루프
# =============================================================================
running = True
world = []
boy = None


def handle_events():
    global running
    for event in get_events():
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            boy.handle_event(event)


def reset_world():
    global world, boy
    world = []
    world.append(Grass())
    boy = Boy()
    world.append(boy)


def update_world():
    for o in world:
        o.update()


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


def main():
    global running
    open_canvas(CANVAS_W, CANVAS_H)
    reset_world()
    game_framework.init_time()
    while running:
        game_framework.tick()
        handle_events()
        update_world()
        render_world()
        delay(0.01)
    close_canvas()


if __name__ == '__main__':
    main()
