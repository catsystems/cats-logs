import struct
import os
from typing import Dict

import pandas as pd

import embedded_constants as EC
from embedded_constants import REC_TYPE, EVENT_MAP, ERROR_MAP


def read_log(log_path: str, plot_output_dir: str, raw_output_dir: str, processed_output_dir: str) -> str:

    for out_dir in [plot_output_dir, raw_output_dir, processed_output_dir]:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    is_binary = log_path.split('/')[-1].split('.')[-1] == 'cfl'

    with open(log_path, 'rb' if is_binary else 'r') as f:
        log_str = f.read()

    return log_str, is_binary


def prepare_log(log_str: str) -> str:
    log_str_formatted = log_str.replace('\r\n', ' ')
    log_str_formatted = log_str_formatted.replace('\n', ' ')
    log_str_formatted = log_str_formatted.replace('  ', ' ')
    log_str_formatted = log_str_formatted.strip()
    return log_str_formatted


def report_non_periodic_recordings(log_dict: Dict[str, list], state_map: Dict[int, str]) -> int:
    ev_liftoff_ts = 0
    print('\nEvents:')
    for event in log_dict['event_info']:
        event['event'] = EVENT_MAP[event['event']]
        print(
            f"{event['ts']} -- {event['event']} -- out_idx: {event['out_idx']}")
        if event['event'] == 'EV_LIFTOFF':
            ev_liftoff_ts = event['ts']

    print('\nFlight States:')
    for state in log_dict['flight_states']:
        state['state'] = state_map[state['state']]
        print(f"{state['ts']} -- {state['state']}")

    
    # print('\nErrors:')
    # for error in log_dict['error_info']:
    #     # if error['error'] in ERROR_MAP:
    #     #     error['error'] = ERROR_MAP[error['error']]
    #     print(f"{error['ts']} -- {error['error']}")
    return ev_liftoff_ts


def extract_data(input_log_path: str, output_log_path: str, state_map: Dict[int, str], from_notebook: bool = False):
    base_name = input_log_path.split('/')[-1].split('.')[0]
    if from_notebook:
        plot_output_dir = f'output/{base_name}'
        raw_output_dir = f'output/{base_name}/raw'
        processed_output_dir = f'output/{base_name}/processed'
    else:
        if output_log_path is None:
            output_log_path = os.getcwd()

        plot_output_dir = f'{output_log_path}'
        raw_output_dir = f'{output_log_path}/raw'
        processed_output_dir = f'{output_log_path}/processed'

    log_str, is_binary = read_log(
        input_log_path, plot_output_dir, raw_output_dir, processed_output_dir)

    if not is_binary:
        log_str_formatted = prepare_log(log_str)
        log_b = bytes.fromhex(log_str_formatted)
    else:
        log_b = log_str
        print(type(log_str))

    # print(f"start of log: {log_b[:23]}")

    log_dict = parse_log(log_b)

    ev_liftoff_ts = report_non_periodic_recordings(log_dict, state_map)
    #ev_liftoff_ts = 1000

    imu = log_dict['imu']
    baro = log_dict['baro']
    accelerometer = log_dict['accelerometer']
    flight_info = log_dict['flight_info']
    orientation_info = log_dict['orientation_info']
    filtered_data_info = log_dict['filtered_data_info']
    flight_states = log_dict['flight_states']
    event_info = log_dict['event_info']
    error_info = log_dict['error_info']
    magneto = log_dict['magneto']
    first_ts = log_dict['first_ts']

    imu_df = pd.DataFrame(imu)
    baro_df = pd.DataFrame(baro)
    accelerometer_df = pd.DataFrame(accelerometer)
    flight_info_df = pd.DataFrame(flight_info)
    orientation_info_df = pd.DataFrame(orientation_info)
    filtered_data_info_df = pd.DataFrame(filtered_data_info)
    event_info_df = pd.DataFrame(event_info)
    error_info_df = pd.DataFrame(error_info)
    magneto_df = pd.DataFrame(magneto)
    flight_states_df = pd.DataFrame(flight_states)


    # save raw logs
    imu_df.to_csv(f'{raw_output_dir}/{base_name} - imu_raw.csv')
    baro_df.to_csv(f'{raw_output_dir}/{base_name} - baro_raw.csv')
    accelerometer_df.to_csv(
        f'{raw_output_dir}/{base_name} - accelerometer_raw.csv')
    orientation_info_df.to_csv(
        f'{raw_output_dir}/{base_name} - orientation_info_raw.csv')
    flight_info_df.to_csv(
        f'{raw_output_dir}/{base_name} - flight_info_raw.csv')
    filtered_data_info_df.to_csv(
        f'{raw_output_dir}/{base_name} - filtered_data_info_raw.csv')
    event_info_df.to_csv(f'{raw_output_dir}/{base_name} - event_info_raw.csv')
    error_info_df.to_csv(f'{raw_output_dir}/{base_name} - error_info_raw.csv')
    magneto_df.to_csv(f'{raw_output_dir}/{base_name} - magneto_info_raw.csv')
    flight_states_df.to_csv(
        f'{raw_output_dir}/{base_name} - flight_states_raw.csv')
    orientation_info_df

    # process logs
    def offset_col(df, col, offset):
        if col in df.columns:
            df[col] -= offset

    def scale_col(df, col, scale_factor):
        if col in df.columns:
            df[col] /= scale_factor

    zero_ts = first_ts
    if ev_liftoff_ts > 0:
        zero_ts = ev_liftoff_ts

    offset_col(imu_df, 'ts', zero_ts)
    offset_col(baro_df, 'ts', zero_ts)
    offset_col(magneto_df, 'ts', zero_ts)
    offset_col(accelerometer_df, 'ts', zero_ts)
    offset_col(orientation_info_df, 'ts', zero_ts)
    offset_col(flight_info_df, 'ts', zero_ts)
    offset_col(filtered_data_info_df, 'ts', zero_ts)

    scale_col(imu_df, 'ts', 1000)
    scale_col(baro_df, 'ts', 1000)
    scale_col(magneto_df, 'ts', 1000)
    scale_col(accelerometer_df, 'ts', 1000)
    scale_col(orientation_info_df, 'ts', 1000)
    scale_col(flight_info_df, 'ts', 1000)
    scale_col(filtered_data_info_df, 'ts', 1000)

    if len(event_info_df) > 0:
        offset_col(event_info_df, 'ts', zero_ts)
        scale_col(event_info_df, 'ts', 1000)
    if len(flight_states_df) > 0:
        offset_col(flight_states_df, 'ts', zero_ts)
        scale_col(flight_states_df, 'ts', 1000)
    if len(error_info_df) > 0:
        offset_col(error_info_df, 'ts', zero_ts)
        scale_col(error_info_df, 'ts', 1000)

    #new VEGA scalng
    scale_col(imu_df, 'Gx', 14.28)
    scale_col(imu_df, 'Gy', 14.28)
    scale_col(imu_df, 'Gz', 14.28)
    scale_col(imu_df, 'Ax', 2048)
    scale_col(imu_df, 'Ay', 2048)
    scale_col(imu_df, 'Az', 2048)

    #old VEGA scaling
    # scale_col(imu_df, 'Gx', 16.4)
    # scale_col(imu_df, 'Gy', 16.4)
    # scale_col(imu_df, 'Gz', 16.4)
    # scale_col(imu_df, 'Ax', 1024)
    # scale_col(imu_df, 'Ay', 1024)
    # scale_col(imu_df, 'Az', 1024)
    
    scale_col(accelerometer_df, 'Ax', 1.28)
    scale_col(accelerometer_df, 'Ay', 1.28)
    scale_col(accelerometer_df, 'Az', 1.28)

    scale_col(orientation_info_df, 'q0_estimated', 1000)
    scale_col(orientation_info_df, 'q1_estimated', 1000)
    scale_col(orientation_info_df, 'q2_estimated', 1000)
    scale_col(orientation_info_df, 'q3_estimated', 1000)

    scale_col(baro_df, 'T', 100)

    imu_df.to_csv(f'{processed_output_dir}/{base_name} - imu_processed.csv')
    baro_df.to_csv(f'{processed_output_dir}/{base_name} - baro_processed.csv')
    accelerometer_df.to_csv(
        f'{processed_output_dir}/{base_name} - accelerometer_processed.csv')
    flight_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - flight_info_processed.csv')
    orientation_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - orientation_info_processed.csv')
    filtered_data_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - filtered_data_info_processed.csv')
    event_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - event_info_processed.csv')
    error_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - error_info_processed.csv')
    magneto_df.to_csv(
        f'{processed_output_dir}/{base_name} - magneto_processed.csv')
    flight_states_df.to_csv(
        f'{processed_output_dir}/{base_name} - flight_states_processed.csv')

    return {'imu_df': imu_df, 'baro_df': baro_df, 'accelerometer_df': accelerometer_df, 'flight_info_df': flight_info_df,
            'orientation_info_df': orientation_info_df, 'filtered_data_info_df': filtered_data_info_df, 'event_info_df': event_info_df,
            'error_info_df': error_info_df, 'magneto_df': magneto_df, 'flight_states_df': flight_states_df}, plot_output_dir, base_name


def parse_log(log_b: bytes):
    imu = []
    baro = []
    accelerometer = []
    flight_info = []
    orientation_info = []
    filtered_data_info = []
    flight_states = []
    event_info = []
    error_info = []
    magneto = []
    i = 0
    first_ts = -1
    last_ts = -1
    try:
        while i < len(log_b):
            ts, t = struct.unpack('<LL', log_b[i:i + 8])
            sensor_id = EC.get_id_from_record_type(t)
            t_without_id = EC.get_record_type_without_id(t)
            i += 8
            if first_ts == -1:
                first_ts = ts
            if t_without_id == REC_TYPE.IMU:
                acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = struct.unpack(
                    '<hhhhhh', log_b[i: i + 12])
                # print(f"{ts} IMU {sensor_id}: Gx: {gyro_x}, Gy: {gyro_y}, Gz: {gyro_z}, Ax: {acc_x}, Ay: {acc_y}, Az: {acc_z}")
                imu.append({'ts': ts,
                            'id': f'IMU{sensor_id}',
                            'Ax': acc_x,
                            'Ay': acc_y,
                            'Az': acc_z,
                            'Gx': gyro_x,
                            'Gy': gyro_y,
                            'Gz': gyro_z})
                # print(imu_data)
                i += 6 * 2  # 6 x int16
            elif t_without_id == REC_TYPE.BARO:
                pressure, temperature = struct.unpack(
                    '<LL', log_b[i: i + 8])
                # print(f"{ts} BARO {sensor_id}: P: {pressure}, T: {temperature}")
                baro.append({'ts': ts,
                             'id': f'BARO{sensor_id}',
                             'T': temperature,
                             'P': pressure})
                # print(baro_data)
                i += 4 + 4
            elif t_without_id == REC_TYPE.MAGNETO:
                mag_x, mag_y, mag_z = struct.unpack(
                    '<fff', log_b[i: i + 12])
                magneto.append({'ts': ts,
                                'Mx': mag_x,
                                'My': mag_y,
                                'Mz': mag_z, })
                i += 4 + 4 + 4
            elif t_without_id == REC_TYPE.ACCELEROMETER:
                acc_x, acc_y, acc_z = struct.unpack(
                    '<bbb', log_b[i: i + 3])
                accelerometer.append({'ts': ts,
                                      'Ax': acc_x,
                                      'Ay': acc_y,
                                      'Az': acc_z, })
                i += 1 + 1 + 1
            elif t_without_id == REC_TYPE.FLIGHT_INFO:
                height, velocity, acceleration = struct.unpack(
                    '<fff', log_b[i: i + 12])
                # print(f"{ts} FLIGHT_INFO: Height: {height}, Velocity: {velocity}, Acc: {acceleration}")
                flight_info.append({'ts': ts,
                                    'height': height,
                                    'velocity': velocity,
                                    'acceleration': acceleration})
                # print(flight_info_data)
                i += 4 + 4 + 4
            elif t_without_id == REC_TYPE.ORIENTATION_INFO:
                est_0, est_1, est_2, est_3 = struct.unpack(
                    '<hhhh', log_b[i: i + 8])
                orientation_info.append({'ts': ts,
                                         'q0_estimated': est_0,
                                         'q1_estimated': est_1,
                                         'q2_estimated': est_2,
                                         'q3_estimated': est_3,})
                # print(orientation_info)
                i += 4 + 4
            elif t_without_id == REC_TYPE.FILTERED_DATA_INFO:
                filtered_altitude_AGL, filtered_acceleration = struct.unpack(
                    '<ff', log_b[i: i + 8])
                # print(f"{ts} FILTERED_DATA_INFO: Filtered ALT: {filtered_altitude_AGL}, Filtered_acc: {filtered_acceleration}")
                filtered_data_info.append({'ts': ts,
                                           'filtered_altitude_AGL': filtered_altitude_AGL,
                                           'filtered_acceleration': filtered_acceleration})
                # print(flight_info_data)
                i += 4 + 4
            elif t_without_id == REC_TYPE.FLIGHT_STATE:
                # print("FLIGHT_STATE")
                state = struct.unpack('<L', log_b[i: i + 4])[0]
                flight_states.append({'ts': ts, 'state': state})
                # print(f"{ts} FLIGHT STATE: State: {state}")
                i += 4
            elif t_without_id == REC_TYPE.EVENT_INFO:
                # print(f"Event info found at {i}")
                event, out_idx = struct.unpack('<LB', log_b[i: i + 5])
                event_info.append({'ts': ts,
                                   'event': event,
                                   'out_idx': out_idx})
                i += 4 + 1 + 3  # +3 is because of the padding
            elif t_without_id == REC_TYPE.ERROR_INFO:
                # print(f"Error info found at {i}")
                error = struct.unpack('<L', log_b[i: i + 4])[0]
                error_info.append({'ts': ts,
                                   'error': error})
                i += 4
            else:
                print(t)
                print(f"ERROR at {i}")
                break
            last_ts = ts
    except struct.error as e:
        if 'unpack requires a buffer of' in repr(e):
            print('Parsing successful!')
            pass
        else:
            print(f'Parsing ended with error: {e}')
    except Exception as e:
        print(f'Parsing ended with error: {e}')
    finally:
        print(
            f'Parsing ended at position: {i}/{len(log_b)}\nFirst timestamp: {first_ts / 1000}s; Last timestamp: {last_ts / 1000}s\n')

    return {'imu': imu, 'baro': baro, 'accelerometer': accelerometer, 'flight_info': flight_info,
            'orientation_info': orientation_info, 'filtered_data_info': filtered_data_info,
            'flight_states': flight_states, 'event_info': event_info, 'error_info': error_info,
            'magneto': magneto, 'first_ts': first_ts}
