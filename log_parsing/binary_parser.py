import struct
import os
from typing import Dict

import pandas as pd

import embedded_constants as EC
from embedded_constants import REC_TYPE, EVENT_MAP, ERROR_MAP


def read_log(log_path: str) -> str:
    base_name = log_path.split('/')[-1].split('.')[0]

    plot_output_dir = f'output/{base_name}'
    raw_output_dir = f'output/{base_name}/raw'
    processed_output_dir = f'output/{base_name}/processed'

    for out_dir in [plot_output_dir, raw_output_dir, processed_output_dir]:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

    with open(log_path, 'r') as f:
        log_str = f.read()

    return log_str, base_name, plot_output_dir, raw_output_dir, processed_output_dir


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

    
    print('\nErrors:')
    for error in log_dict['error_info']:
        if error['error'] in ERROR_MAP:
            error['error'] = ERROR_MAP[error['error']]
        print(f"{error['ts']} -- {error['error']}")
    return ev_liftoff_ts


def extract_data(log_path: str, state_map: Dict[int, str]):
    log_str, base_name, plot_output_dir, raw_output_dir, processed_output_dir = read_log(
        log_path)

    log_str_formatted = prepare_log(log_str)

    log_b = bytes.fromhex(log_str_formatted)

    print(f"start of log: {log_b[:23]}")

    log_dict = parse_log(log_b)

    ev_liftoff_ts = report_non_periodic_recordings(log_dict, state_map)

    imu = log_dict['imu']
    baro = log_dict['baro']
    accelerometer = log_dict['accelerometer']
    flight_info = log_dict['flight_info']
    orientation_info = log_dict['orientation_info']
    filtered_data_info = log_dict['filtered_data_info']
    flight_states = log_dict['flight_states']
    covariance_info = log_dict['covariance_info']
    sensor_info = log_dict['sensor_info']
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
    covariance_df = pd.DataFrame(covariance_info)
    flight_info_df['lower_bound'] = flight_info_df['height'] + \
        3 * (covariance_df['height_cov']) ** 0.5
    flight_info_df['upper_bound'] = flight_info_df['height'] - \
        3 * (covariance_df['height_cov']) ** 0.5
    sensor_info_df = pd.DataFrame(sensor_info)
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
    covariance_df.to_csv(
        f'{raw_output_dir}/{base_name} - covariance_df_raw.csv')
    sensor_info_df.to_csv(
        f'{raw_output_dir}/{base_name} - sensor_info_raw.csv')
    event_info_df.to_csv(f'{raw_output_dir}/{base_name} - event_info_raw.csv')
    error_info_df.to_csv(f'{raw_output_dir}/{base_name} - error_info_raw.csv')
    magneto_df.to_csv(f'{raw_output_dir}/{base_name} - magneto_info_raw.csv')
    flight_states_df.to_csv(
        f'{raw_output_dir}/{base_name} - flight_states_raw.csv')
    orientation_info_df

    # process logs
    def offset_col(df, col, offset):
        df[col] -= offset

    def scale_col(df, col, scale_factor):
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
    offset_col(covariance_df, 'ts', zero_ts)
    #offset_col(sensor_info_df, 'ts', zero_ts)

    scale_col(imu_df, 'ts', 1000)
    scale_col(baro_df, 'ts', 1000)
    scale_col(magneto_df, 'ts', 1000)
    scale_col(accelerometer_df, 'ts', 1000)
    scale_col(orientation_info_df, 'ts', 1000)
    scale_col(flight_info_df, 'ts', 1000)
    scale_col(filtered_data_info_df, 'ts', 1000)
    scale_col(covariance_df, 'ts', 1000)
    #scale_col(sensor_info_df, 'ts', 1000)

    if len(event_info_df) > 0:
        offset_col(event_info_df, 'ts', zero_ts)
        scale_col(event_info_df, 'ts', 1000)
    if len(flight_states_df) > 0:
        offset_col(flight_states_df, 'ts', zero_ts)
        scale_col(flight_states_df, 'ts', 1000)
    if len(error_info_df) > 0:
        offset_col(error_info_df, 'ts', zero_ts)
        scale_col(error_info_df, 'ts', 1000)

    scale_col(imu_df, 'Gx', 16.4)
    scale_col(imu_df, 'Gy', 16.4)
    scale_col(imu_df, 'Gz', 16.4)
    scale_col(imu_df, 'Ax', 1024)
    scale_col(imu_df, 'Ay', 1024)
    scale_col(imu_df, 'Az', 1024)

    scale_col(orientation_info_df, 'q0_estimated', 1000)
    scale_col(orientation_info_df, 'q1_estimated', 1000)
    scale_col(orientation_info_df, 'q2_estimated', 1000)
    scale_col(orientation_info_df, 'q3_estimated', 1000)
    scale_col(orientation_info_df, 'q0_raw', 1000)
    scale_col(orientation_info_df, 'q1_raw', 1000)
    scale_col(orientation_info_df, 'q2_raw', 1000)
    scale_col(orientation_info_df, 'q3_raw', 1000)

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
    covariance_df.to_csv(
        f'{processed_output_dir}/{base_name} - covariance_df_processed.csv')
    sensor_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - sensor_info_processed.csv')
    event_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - event_info_processed.csv')
    error_info_df.to_csv(
        f'{processed_output_dir}/{base_name} - error_info_processed.csv')
    magneto_df.to_csv(
        f'{processed_output_dir}/{base_name} - magneto_processed.csv')
    flight_states_df.to_csv(
        f'{processed_output_dir}/{base_name} - flight_states_processed.csv')

    return {'imu_df': imu_df, 'baro_df': baro_df, 'accelerometer_df': accelerometer_df, 'flight_info_df': flight_info_df,
            'orientation_info_df': orientation_info_df, 'filtered_data_info_df': filtered_data_info_df, 'covariance_df': covariance_df,
            'sensor_info_df': sensor_info_df, 'event_info_df': event_info_df, 'error_info_df': error_info_df, 'magneto_df': magneto_df, 'flight_states_df': flight_states_df}, plot_output_dir, base_name


def parse_log(log_b: bytes):
    imu = []
    baro = []
    accelerometer = []
    flight_info = []
    orientation_info = []
    filtered_data_info = []
    flight_states = []
    covariance_info = []
    sensor_info = []
    event_info = []
    error_info = []
    magneto = []
    i = 0
    first_ts = -1
    last_ts = -1
    try:
        while i < len(log_b):
            t = struct.unpack('<L', log_b[i:i + 4])[0]
            sensor_id = EC.get_id_from_record_type(t)
            t_without_id = EC.get_record_type_without_id(t)
            i += 4
            if t_without_id == REC_TYPE.IMU:
                ts, gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z = struct.unpack(
                    '<Lhhhhhh', log_b[i: i + 16])
                if first_ts == -1:
                    first_ts = ts
                #print(f"{ts} IMU {t-1}: Gx: {gyro_x}, Gy: {gyro_y}, Gz: {gyro_z}, Ax: {acc_x}, Ay: {acc_y}, Az: {acc_z}")
                imu.append({'ts': ts,
                            'id': f'IMU{sensor_id}',
                            'Gx': gyro_x,
                            'Gy': gyro_y,
                            'Gz': gyro_z,
                            'Ax': acc_x,
                            'Ay': acc_y,
                            'Az': acc_z})
                # print(imu_data)
                i += 4 + 6 + 6  # ts + 6 x int16
            elif t_without_id == REC_TYPE.BARO:
                ts, pressure, temperature = struct.unpack(
                    '<LLL', log_b[i: i + 12])
                if first_ts == -1:
                    first_ts = ts
                #print(f"{ts} BARO {t-4}: P: {pressure}, T: {temperature}")
                baro.append({'ts': ts,
                            'id': f'BARO{sensor_id}',
                             'T': temperature,
                             'P': pressure})
                # print(baro_data)
                i += 4 + 4 + 4
            elif t_without_id == REC_TYPE.MAGNETO:
                ts, mag_x, mag_y, mag_z = struct.unpack(
                    '<Lfff', log_b[i: i + 16])
                if first_ts == -1:
                    first_ts = ts
                magneto.append({'ts': ts,
                                'mx': mag_x,
                                'my': mag_y,
                                'mz': mag_z, })
                i += 4 + 4 + 4 + 4
            elif t_without_id == REC_TYPE.ACCELEROMETER:
                ts, acc_x, acc_y, acc_z = struct.unpack(
                    '<Lbbb', log_b[i: i + 7])
                if first_ts == -1:
                    first_ts = ts
                accelerometer.append({'ts': ts,
                                      'acc_x': acc_x,
                                      'acc_y': acc_y,
                                      'acc_z': acc_z, })
                i += 4 + 1 + 1 + 1 + 1
            elif t_without_id == REC_TYPE.FLIGHT_INFO:
                ts, height, velocity, acceleration = struct.unpack(
                    '<Lfff', log_b[i: i + 16])
                if first_ts == -1:
                    first_ts = ts
                #print(f"{ts} FLIGHT_INFO: Height: {height}, Velocity: {velocity}, Acc: {acceleration}")
                flight_info.append({'ts': ts,
                                    'height': height,
                                    'velocity': velocity,
                                    'acceleration': acceleration})
                # print(flight_info_data)
                i += 4 + 4 + 4 + 4
            elif t_without_id == REC_TYPE.ORIENTATION_INFO:
                ts, est_0, est_1, est_2, est_3, raw_0, raw_1, raw_2, raw_3 = struct.unpack(
                    '<Lhhhhhhhh', log_b[i: i + 20])
                if first_ts == -1:
                    first_ts = ts
                orientation_info.append({'ts': ts,
                                        'q0_estimated': est_0,
                                         'q1_estimated': est_1,
                                         'q2_estimated': est_2,
                                         'q3_estimated': est_3,
                                         'q0_raw': raw_0,
                                         'q1_raw': raw_1,
                                         'q2_raw': raw_2,
                                         'q3_raw': raw_3})
                # print(orientation_info)
                i += 4 + 4 + 4 + 4 + 4
            elif t_without_id == REC_TYPE.FILTERED_DATA_INFO:
                ts, altitude_agl, raw_acceleration, filtered_altitude_AGL, filtered_acceleration = struct.unpack(
                    '<Lffff', log_b[i: i + 20])
                if first_ts == -1:
                    first_ts = ts
                #print(f"{ts} FLIGHT_INFO: Height: {height}, Velocity: {velocity}, Acc: {acceleration}")
                filtered_data_info.append({'ts': ts,
                                           'altitude_agl': altitude_agl,
                                           'raw_acceleration': raw_acceleration,
                                           'filtered_altitude_AGL': filtered_altitude_AGL,
                                           'filtered_acceleration': filtered_acceleration})
                # print(flight_info_data)
                i += 4 + 4 + 4 + 4 + 4
            elif t_without_id == REC_TYPE.FLIGHT_STATE:
                # print("FLIGHT_STATE")
                ts, state = struct.unpack('<LL', log_b[i: i + 8])
                if first_ts == -1:
                    first_ts = ts
                flight_states.append({'ts': ts, 'state': state})
                #print(f"{ts} FLIGHT STATE: State: {state}")
                i += 4 + 4
            elif t_without_id == REC_TYPE.COVARIANCE_INFO:
                ts, height_cov, velocity_cov = struct.unpack(
                    '<Lff', log_b[i: i + 12])
                if first_ts == -1:
                    first_ts = ts
                #print(f"{ts} COVARIANCE_INFO: Height cov: {height_cov}, Velocity cov: {velocity_cov}")
                covariance_info.append({'ts': ts,
                                        'height_cov': height_cov,
                                        'velocity_cov': velocity_cov})
                # print(flight_info_data)
                i += 4 + 4 + 4
            elif t_without_id == REC_TYPE.SENSOR_INFO:
                #print(f"Sensor info found at {i}")
                ts, imu_0, imu_1, imu_2, baro_0, baro_1, baro_2 = struct.unpack(
                    '<LBBBBBB', log_b[i: i + 10])
                if first_ts == -1:
                    first_ts = ts
                sensor_info.append({'ts': ts,
                                    'imu_0': imu_0,
                                    'imu_1': imu_1,
                                    'imu_2': imu_2,
                                    'baro_0': baro_0, 'baro_1': baro_1, 'baro_2': baro_2})
                i += 4 + 6 + 2  # +2 is because of the padding
            elif t_without_id == REC_TYPE.EVENT_INFO:
                #print(f"Event info found at {i}")
                ts, event, out_idx = struct.unpack('<LLB', log_b[i: i + 9])
                if first_ts == -1:
                    first_ts = ts
                event_info.append({'ts': ts,
                                   'event': event,
                                   'out_idx': out_idx})
                i += 4 + 4 + 1 + 3  # +3 is because of the padding
            elif t_without_id == REC_TYPE.ERROR_INFO:
                #print(f"Error info found at {i}")
                ts, error = struct.unpack('<LL', log_b[i: i + 8])
                if first_ts == -1:
                    first_ts = ts
                error_info.append({'ts': ts,
                                   'error': error})
                i += 4 + 4
            else:
                print(t)
                print(f"ERROR at {i}")
                break
            last_ts = ts
    except Exception as e:
        print(f'Parsing ended with error: {e}')
    finally:
        print(
            f'Parsing ended at position: {i}/{len(log_b)}\nFirst timestamp: {first_ts / 1000}s; Last timestamp: {last_ts / 1000}s\n')

    return {'imu': imu, 'baro': baro, 'accelerometer': accelerometer, 'flight_info': flight_info,
            'orientation_info': orientation_info, 'filtered_data_info': filtered_data_info,
            'flight_states': flight_states, 'covariance_info': covariance_info, 'sensor_info': sensor_info,
            'event_info': event_info, 'error_info': error_info, 'magneto': magneto, 'first_ts': first_ts}
