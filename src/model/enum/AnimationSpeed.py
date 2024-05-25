from enum import Enum

animation_speed_duration = {
    'slower': 3000,
    'slow': 2000,
    'normal': 1000,
    'fast': 800,
    'faster': 500,
}


class AnimationSpeed(Enum):

    SLOWER = 'slower'   # 3s
    SLOW = 'slow'       # 2s
    NORMAL = 'normal'   # 1s
    FAST = 'fast'       # 800ms
    FASTER = 'faster'   # 500ms
