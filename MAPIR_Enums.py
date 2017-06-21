from enum import IntEnum

class eRequest(IntEnum):

    RQ_RECEIVE_EVENT = 0
    RQ_SET_COMMAND = 1
    RQ_WRITE_REGISTER = 2
    RQ_WRITE_BLOCK = 3
    RQ_READ_REGISTER = 4
    RQ_READ_BLOCK = 5
    RQ_SELECT_CAMERA = 6
class eStatus(IntEnum):
    ST_OK = 0
    ST_CODE_NOT_SUPPORTED = 1
    ST_CODE_FOR_BLOCK_REG = 2
    ST_CODE_FOR_SINGLE_REG = 3
    ST_CODE_FOR_READ_ONLY_REG = 4
    ST_CODE_NOT_AVAIL_FOR_SENSOR = 5
    ST_VALUE_OUT_OF_RANGE = 6
    ST_VALUE_NOT_AVAIL_FOR_SENSOR = 7
    ST_LENGTH_INCORRECT = 8
    ST_TIMEOUT = 9
    ST_CAMERA_ID_NOT_RECOGNIZED = 10
    ST_CAMERA_NOT_FUNCTIONAL = 11
    ST_EVENT_NOT_IN_QUEUE = 12
class eMode(IntEnum):
    MD_REBOOT = 0
    MD_TRANSFER = 1
    MD_PLAY = 2
    MD_RECORD = 3
    MD_CAPTURE = 4
    MD_STILL_TIME = 5
    MD_VIEW = 6
    NR_OF_MODES = 7
class eTrigger_Mode(IntEnum):
    TMD_RECORD_VIDEO = 0
    TMD_RECORD_VIDEO_LOOPING = 1
    TMD_CAPTURE = 2
    TMD_BURST = 3
    TMD_CONTINUOUS = 4
    TMD_TIME_LAPSE = 5
    TMD_NR_OF_MODES = 6
class eProcess(IntEnum):
    # MD_REBOOT
    PR_REBOOT = 0
    # MD_TRANSFER
    PR_TRANSFER = 1
    # MD_PLAY
    PR_PLAY = 2
    # MD_RECORD
    PR_VIDEO = 3
    PR_LOOPING_VIDEO = 4
    # MD_CAPTURE
    PR_PHOTO = 5
    PR_BURST = 6
    PR_CONTINUOUS = 7
    PR_TIME_LAPSE = 8
    # MD_STILL_TIME
    PR_STILL_TIME = 9
    # MD_VIEW
    PR_IDLE_ON_REQUEST = 10
    PR_IDLE_ON_COMPLETION = 11
    PR_IDLE_ON_MEM_ALMOST_FULL = 12
    NR_OF_PROCESSES = 13
class eEvent(IntEnum):
    EV_CAMERA_DEVICE_READY  = 1
#  EV_MODE_CHANGED = ()
    EV_PROCESS_CHANGED = 2
    EV_FOCUS_COMPLETE = 3
    EV_INVERSION_COMPLETE = 4
    EV_ZOOM_POS_CHANGED = 5
    EV_DETECTED_FACES_CHANGED = 6
class eCommand(IntEnum):
    CM_TRANSFER_MODE        = 1
    CM_PLAY_MODE = 2
    CM_RESET_CAMERA = 3
    CM_RECORD_VIDEO         = 11
    CM_RECORD_LOOPING_VIDEO = 12
    CM_CAPTURE_PHOTO = 13
    CM_BURST = 14
    CM_CONTINUOUS = 15
    CM_TIME_LAPSE = 16
    CM_ZOOM                 = 21
    CM_AUTO_FOCUS = 22
    CM_MANUAL_FOCUS = 23
    CM_BROWSE               = 31
    CM_REPRODUCE = 32
    CM_SAVE_SETTINGS        = 41
    CM_SET_CAN_PARAMS = 42
class eRegister(IntEnum):
    # PASSIVE
    RG_VIDEO_RESOLUTION     = 1
    RG_LOOPING_INTERVAL = 2
    RG_VIDEO_FORMAT = 3
    RG_VIDEO_COMPRESSION = 4
    RG_PHOTO_RESOLUTION     = 11
    RG_PHOTO_STILL_TIME = 12
    RG_PHOTO_FORMAT = 13
    RG_PHOTO_COMPRESSION = 14
    RG_BURST_INTERVAL       = 21
    RG_TIME_LAPSE_INTERVAL = 22
    RG_MODE                 = 31
    RG_PROCESS = 32
    RG_HARDWARE_ID = 33
    RG_FIRMWARE_ID = 34
    RG_SENSOR_ID = 35
    RG_LENS_ID = 36
    RG_NEW_LENS_DATA = 37
    RG_CAMERA_SETTING = 38
    RG_MEDIA_FILES_CNT = 39
    RG_MEDIA_FILE_NAME_A = 40
    RG_MEDIA_FILE_NAME_B = 41
    RG_MEDIA_FILE_NAME_C = 42
    RG_CAN_BIT_RATE_1 = 43
    RG_CAN_BIT_RATE_2 = 44
    RG_CAN_SAMPLE_POINT_1 = 45
    RG_CAN_SAMPLE_POINT_2 = 46
    RG_CAN_NODE_ID = 47
    RG_CAMERA_LINK_ID = 48
    RG_CAMERA_ID = 49
    RG_CAMERA_ID_2 = 50
    RG_CAMERA_ID_3 = 51
    RG_CAMERA_ID_4 = 52
    RG_CAMERA_ID_5 = 53
    RG_CAMERA_ID_6 = 54
    RG_REALTIME_CLOCK = 55
    RG_BEEPER_ENABLE = 56
    RG_CAN_TEST_ENABLE = 57
    RG_CAMERA_ARRAY_TYPE = 58
    RG_MANUAL_FOCUS_STEP    = 61
    RG_ZOOM_FACTOR = 62
    RG_ZOOM_SPEED = 63
    RG_CURRENT_ZOOM_FACTOR = 64
    RG_MAIN_FACE_FRM_COLOR  = 71
    RG_OTHER_FACE_FRM_COLOR = 72
    RG_NUMBER_OF_FACES = 73
    RG_FACES_FRAME_DATA = 74
    RG_CVBS_PLAY_FORMAT     = 81
    # INTERNAL
    RG_UNIQUE_ID = 82
    RG_UNIQUE_ID_2 = 83
    RG_UNIQUE_ID_3 = 84
    RG_UNIQUE_ID_4 = 85
    RG_FOLDER_CNT = 86
    RG_FOLDER_CNT_2 = 87
    RG_FILE_CNT = 88
    RG_FILE_CNT_2 = 89
    RG_FILE_CNT_3 = 90
    RG_FILE_CNT_4 = 91
    # ACTIVE
    RG_VIDEO_FRAME_RATE     = 101
    RG_SHUTTER              = 111
    RG_DAC                  = 121
    RG_HDMI = 122
    RG_DAC_LINK = 123
    RG_TRIGGER_MODE         = 130
    RG_PWM_TRIGGER = 131
    RG_WHITE_BALANCE        = 141
    RG_COLOR = 142
    RG_ISO = 143
    RG_EV_CORRECTION = 144
    RG_SHARPNESS = 145
    RG_CONTRAST = 146
    RG_BRIGHTNESS = 147
    RG_PICTURE_INVERSION = 148
    RG_IMAGE_STABILIZATION  = 151
    RG_NOISE_REDUCTION = 152
    RG_FLICKER_CORRECTION = 153
    RG_FORCE_BACKLIGHT = 154
    RG_FACE_DETECTION       = 171
    RG_ACTIVE_CAMERA_SOURCE = 191
    # LED (PASSIVE)
    RG_PROCES_1_LED_COLOR   = 201
    # SIZE
    RG_SIZE     = 214
class e_MANUAL_FOCUS(IntEnum):
    MF_MACRO = 0
    MF_TO_MACRO = 1
    MF_INFINITY = 2
    MF_TO_INFINITY = 3
class e_PHOTO_VIDEO(IntEnum):
    PV_PHOTO = 0
    PV_VIDEO = 1
    PV_BURST = 2
    PV_TIME_LAPSE = 3
    PV_CONTINUOUS = 4
class e_BROWSE(IntEnum):
    BR_PREVIOUS = 0
    BR_NEXT = 1
class eColors(IntEnum):
    COL_GREEN = 0
    COL_BLUE = 1
    COL_RED = 2
    COL_YELLOW = 3
    COL_BAIGE = 4
    COL_ORANGE = 5
    COL_BROWN = 6
    COL_MAGENTA = 7
    COL_GOLD = 8
    COL_SILVER = 9
    COL_PURPLE = 10
    COL_PINK = 12
    COL_LIME = 13
    COL_CYAN = 14
    COL_NAVY = 15
class e_LHM(IntEnum):
    LHM_LOW = 0
    LHM_MEDIUM_LOW = 1
    LHM_MEDIUM = 2
    LHM_MEDIUM_HIGH = 3
    LHM_HIGH = 4
class e_PICTURE_INVERSION(IntEnum):
    PI_NO = 0
    PI_MIRROR = 1
    PI_FLIP = 2
    PI_BOTH = 3
class e_COMPRESSION(IntEnum):
    CMP_NO = 0
    CMP_LOW = 1
    CMP_MEDIUM = 2
    CMP_HIGH = 3
    CMP_MAXIMAL = 4
class e_VIDEO_FORMAT(IntEnum):
    VF_H264 = 0
    VF_MJPEG = 1
class e_PHOTO_FORMAT(IntEnum):
    PF_TIFF = 0
    PF_RAW = 1
class e_CVBS_FORMAT(IntEnum):
    CF_PAL = 0
    CF_NTSC = 1
class e_WHITE_BALANCE(IntEnum):
    WB_AUTO = 0
    WB_WARM = 1
    WB_COOL = 2
    WB_NATIVE = 3
class e_PHOTO_COLOR(IntEnum):
    PC_BEST = 0
    PC_GRAY = 1
    PC_POOR = 2
    PC_RICH = 3
class e_VIDEO_RESOLUTION(IntEnum):
    VR_WVGA = 0
    VR_FULLHD = 1
    VR_2K = 2
    VR_4K = 3
class e_SENSOR(IntEnum):
    SE_R2D2 = 0
    SE_C3PO = 1
    SE_AR0134 = 2
    SE_IMX249LQJ = 3