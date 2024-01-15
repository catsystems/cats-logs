from enum import IntEnum

FLIGHT_MAP = {
    0: 'INVALID',
    1: 'CALIBRATING',
    2: 'READY',
    3: 'THRUSTING',
    4: 'COASTING',
    5: 'DROGUE',
    6: 'MAIN',
    7: 'TOUCHDOWN',
    #0x7FFFFFFF: 'HEHE2'
}

EVENT_MAP = {
    0: 'EV_MOVING',
    1: 'EV_READY',
    2: 'EV_LIFTOFF',
    3: 'EV_MAX_V',
    4: 'EV_APOGEE',
    5: 'EV_MAIN_DEPLOYMENT',
    6: 'EV_TOUCHDOWN',
    7: 'EV_CUSTOM_1',
    8: 'EV_CUSTOM_2',
    #0xFFFFFFFF: 'EV_HEHE'
}

ERROR_MAP = {
    0x01 : 'ERR_NO_CONFIG',
    0x02 : 'ERR_NO_PYRO',
    0x04 : 'ERR_LOG_FULL',
    0x08 : 'ERR_BAT_LOW',
    0x10 : 'ERR_BAT_CRITICAL',
    0x20 : 'ERR_IMU_0',
    0x40 : 'ERR_IMU_1',
    0x80 : 'ERR_IMU_2',
    0x100 : 'ERR_BARO_0',
    0x200 : 'ERR_BARO_1',
    0x400 : 'ERR_BARO_2',
    0x800 : 'ERR_MAGNETO',
    0x1000 : 'ERR_ACC',
    0x2000 : 'ERR_FILTER_ACC',
    0x4000 : 'ERR_FILTER_HEIGHT',
    0x8000 : 'ERR_HARD_FAULT',
    0x10000 : 'ERR_NON_USER_CFG',
    #0xFFFFFFFF: 'ERR_HEHE'
}


class REC_TYPE(IntEnum):
  IMU                = 1 << 4   # 0x20
  BARO               = 1 << 5   # 0x40
  FLIGHT_INFO        = 1 << 6   # 0x80
  ORIENTATION_INFO   = 1 << 7   # 0x100
  FILTERED_DATA_INFO = 1 << 8   # 0x200
  FLIGHT_STATE       = 1 << 9   # 0x400
  EVENT_INFO         = 1 << 10  # 0x800
  ERROR_INFO         = 1 << 11  # 0x1000
  GNSS_INFO          = 1 << 12  # 0x2000
  VOLTAGE_INFO       = 1 << 13  # 0x4000

REC_ID_MASK = 0x0000000F

def get_id_from_record_type(rec_type):
    return rec_type & REC_ID_MASK

def get_record_type_without_id(rec_type):
    return rec_type & ~REC_ID_MASK