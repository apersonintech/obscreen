from enum import Enum


class AnimationExitEffect(Enum):

    NONE = 'none'

    BACK_OUT_DOWN = 'backOutDown'
    BACK_OUT_LEFT = 'backOutLeft'
    BACK_OUT_RIGHT = 'backOutRight'
    BACK_OUT_UP = 'backOutUp'

    BOUNCE_OUT = 'bounceOut'
    BOUNCE_OUT_DOWN = 'bounceOutDown'
    BOUNCE_OUT_LEFT = 'bounceOutLeft'
    BOUNCE_OUT_RIGHT = 'bounceOutRight'
    BOUNCE_OUT_UP = 'bounceOutUp'

    FADE_OUT = 'fadeOut'
    FADE_OUT_DOWN = 'fadeOutDown'
    FADE_OUT_DOWN_BIG = 'fadeOutDownBig'
    FADE_OUT_LEFT = 'fadeOutLeft'
    FADE_OUT_LEFT_BIG = 'fadeOutLeftBig'
    FADE_OUT_RIGHT = 'fadeOutRight'
    FADE_OUT_RIGHT_BIG = 'fadeOutRightBig'
    FADE_OUT_UP = 'fadeOutUp'
    FADE_OUT_UP_BIG = 'fadeOutUpBig'
    FADE_OUT_TOP_LEFT = 'fadeOutTopLeft'
    FADE_OUT_TOP_RIGHT = 'fadeOutTopRight'
    FADE_OUT_BOTTOM_LEFT = 'fadeOutBottomLeft'
    FADE_OUT_BOTTOM_RIGHT = 'fadeOutBottomRight'

    FLIP = 'flip'
    FLIP_OUT_X = 'flipOutX'
    FLIP_OUT_Y = 'flipOutY'

    LIGHT_SPEED_OUT_RIGHT = 'lightSpeedOutRight'
    LIGHT_SPEED_OUT_LEFT = 'lightSpeedOutLeft'

    ROTATE_OUT = 'rotateOut'
    ROTATE_OUT_DOWN_LEFT = 'rotateOutDownLeft'
    ROTATE_OUT_DOWN_RIGHT = 'rotateOutDownRight'
    ROTATE_OUT_UP_LEFT = 'rotateOutUpLeft'
    ROTATE_OUT_UP_RIGHT = 'rotateOutUpRight'

    ROLL_OUT = 'rollOut'
    HINGE = 'hinge'

    ZOOM_OUT = 'zoomOut'
    ZOOM_OUT_DOWN = 'zoomOutDown'
    ZOOM_OUT_LEFT = 'zoomOutLeft'
    ZOOM_OUT_RIGHT = 'zoomOutRight'
    ZOOM_OUT_UP = 'zoomOutUp'

    SLIDE_OUT_DOWN = 'slideOutDown'
    SLIDE_OUT_LEFT = 'slideOutLeft'
    SLIDE_OUT_RIGHT = 'slideOutRight'
    SLIDE_OUT_UP = 'slideOutUp'

    @staticmethod
    def get_values() -> dict:
        values = {}

        for enum_item in AnimationExitEffect:
            values[enum_item.value] = enum_item.value

        return values