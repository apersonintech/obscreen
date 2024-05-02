from enum import Enum


class AnimationSpeed(Enum):

    SLOWER = 'slower'
    SLOW = 'slow'
    NORMAL = 'normal'
    FAST = 'fast'
    FASTER = 'faster'

    @staticmethod
    def get_values(lang_map: dict) -> dict:
        if lang_map is None:
            return {}

        return {
            AnimationSpeed.SLOWER.value: lang_map['enum_animation_speed_slower'],   # 3s
            AnimationSpeed.SLOW.value: lang_map['enum_animation_speed_slow'],       # 2s
            AnimationSpeed.NORMAL.value: lang_map['enum_animation_speed_normal'],   # 1s
            AnimationSpeed.FAST.value: lang_map['enum_animation_speed_fast'],       # 800ms
            AnimationSpeed.FASTER.value: lang_map['enum_animation_speed_faster']    # 500ms
        }
