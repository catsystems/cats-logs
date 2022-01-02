from enum import IntEnum

FLIGHT_MAP = {
    0: 'INVALID',
    1: 'MOVING',
    2: 'READY',
    3: 'THRUSTING_1',
    4: 'THRUSTING_2',
    5: 'COASTING',
    6: 'TRANSONIC_1',
    7: 'SUPERSONIC',
    8: 'TRANSONIC_2',
    9: 'APOGEE',
    10: 'DROGUE',
    11: 'MAIN',
    12: 'TOUCHDOWN',
    #0x7FFFFFFF: 'HEHE2'
}

DROP_MAP = {
    0: 'INVALID',
    1: 'MOVING',
    2: 'READY',
    3: 'DROGUE CHUTE',
    4: 'MAIN CHUTE',
    #0x7FFFFFFF: 'HEHE'
}

EVENT_MAP = {
    0: 'EV_MOVING',
    1: 'EV_READY',
    2: 'EV_LIFTOFF',
    3: 'EV_MAX_V',
    4: 'EV_APOGEE',
    5: 'EV_POST_APOGEE',
    6: 'EV_TOUCHDOWN',
    7: 'EV_CUSTOM_1',
    8: 'EV_CUSTOM_2',
    9: 'EV_MACHTIMER',
    #0xFFFFFFFF: 'EV_HEHE'
}

ERROR_MAP = {
    0x01 : 'ERR_NO_CONFIG',
    0x02 : 'ERR_NO_PYRO',
    0x04 : 'ERR_LOG_FULL',
    0x08 : 'ERR_USB_CONNECTED',
    0x10 : 'ERR_BAT_LOW',
    0x20 : 'ERR_BAT_CRITICAL',
    0x40 : 'ERR_IMU',
    0x200 : 'ERR_BARO',
    0x400 : 'ERR_MAG',
    0x800 : 'ERR_ACC',
    0x1000 : 'ERR_FILTER_ACC',
    0x2000 : 'ERR_FILTER_HEIGHT',
    0x4000 : 'ERR_HARD_FAULT',
    #0xFFFFFFFF: 'ERR_HEHE'
}


class REC_TYPE(IntEnum):
  IMU                = 1 << 4   # 0x20
  BARO               = 1 << 5   # 0x40
  MAGNETO            = 1 << 6   # 0x80
  ACCELEROMETER      = 1 << 7   # 0x100
  FLIGHT_INFO        = 1 << 8   # 0x200
  ORIENTATION_INFO   = 1 << 9   # 0x400
  FILTERED_DATA_INFO = 1 << 10  # 0x800
  FLIGHT_STATE       = 1 << 11  # 0x1000
  SENSOR_INFO        = 1 << 12  # 0x2000
  EVENT_INFO         = 1 << 13  # 0x4000
  ERROR_INFO         = 1 << 14  # 0x8000

REC_ID_MASK = 0x0000000F

def get_id_from_record_type(rec_type):
    return rec_type & REC_ID_MASK

def get_record_type_without_id(rec_type):
    return rec_type & ~REC_ID_MASK