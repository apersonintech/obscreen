from enum import Enum


class AnimationEntranceEffect(Enum):

    BACK_IN_DOWN = 'backInDown'
    BACK_IN_LEFT = 'backInLeft'
    BACK_IN_RIGHT = 'backInRight'
    BACK_IN_UP = 'backInUp'

    BOUNCE_IN = 'bounceIn'
    BOUNCE_IN_DOWN = 'bounceInDown'
    BOUNCE_IN_LEFT = 'bounceInLeft'
    BOUNCE_IN_RIGHT = 'bounceInRight'
    BOUNCE_IN_UP = 'bounceInUp'

    FADE_IN = 'fadeIn'
    FADE_IN_DOWN = 'fadeInDown'
    FADE_IN_DOWN_BIG = 'fadeInDownBig'
    FADE_IN_LEFT = 'fadeInLeft'
    FADE_IN_LEFT_BIG = 'fadeInLeftBig'
    FADE_IN_RIGHT = 'fadeInRight'
    FADE_IN_RIGHT_BIG = 'fadeInRightBig'
    FADE_IN_UP = 'fadeInUp'
    FADE_IN_UP_BIG = 'fadeInUpBig'
    FADE_IN_TOP_LEFT = 'fadeInTopLeft'
    FADE_IN_TOP_RIGHT = 'fadeInTopRight'
    FADE_IN_BOTTOM_LEFT = 'fadeInBottomLeft'
    FADE_IN_BOTTOM_RIGHT = 'fadeInBottomRight'

    FLIP = 'flip'
    FLIP_IN_X = 'flipInX'
    FLIP_IN_Y = 'flipInY'

    LIGHT_SPEED_IN_RIGHT = 'lightSpeedInRight'
    LIGHT_SPEED_IN_LEFT = 'lightSpeedInLeft'

    ROTATE_IN = 'rotateIn'
    ROTATE_IN_DOWN_LEFT = 'rotateInDownLeft'
    ROTATE_IN_DOWN_RIGHT = 'rotateInDownRight'
    ROTATE_IN_UP_LEFT = 'rotateInUpLeft'
    ROTATE_IN_UP_RIGHT = 'rotateInUpRight'

    ROLL_IN = 'rollIn'
    JACK_IN_THE_BOX = 'jackInTheBox'

    ZOOM_IN = 'zoomIn'
    ZOOM_IN_DOWN = 'zoomInDown'
    ZOOM_IN_LEFT = 'zoomInLeft'
    ZOOM_IN_RIGHT = 'zoomInRight'
    ZOOM_IN_UP = 'zoomInUp'

    SLIDE_IN_DOWN = 'slideInDown'
    SLIDE_IN_LEFT = 'slideInLeft'
    SLIDE_IN_RIGHT = 'slideInRight'
    SLIDE_IN_UP = 'slideInUp'
    