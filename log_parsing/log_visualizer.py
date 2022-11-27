#!/bin/python3

import argparse

from embedded_constants import FLIGHT_MAP
from plot_generator import *
from html_generator import *
import binary_parser


def main(args):
    df_dict, plot_output_dir, base_name = binary_parser.extract_data(args.input_path, args.output_path, FLIGHT_MAP)

    imu_df = df_dict['imu_df']
    baro_df = df_dict['baro_df']
    accelerometer_df = df_dict['accelerometer_df']
    magneto_df = df_dict['magneto_df']

    flight_info_df = df_dict['flight_info_df']

    orientation_info_df = df_dict['orientation_info_df']
    filtered_data_info_df = df_dict['filtered_data_info_df']

    event_info_df = df_dict['event_info_df']
    error_info_df = df_dict['error_info_df']
    flight_states_df = df_dict['flight_states_df']
    
    print('\nGenerating plots, this might take a while...')
    
    imu_plots = plot_imu_data(imu_df, flight_states_df, event_info_df, error_info_df)
    magneto_plots = plot_magneto_data(magneto_df, flight_states_df, event_info_df, error_info_df)
    accelerometer_plots = plot_acc_data(accelerometer_df, flight_states_df, event_info_df, error_info_df)
    baro_plots = plot_baro_data(baro_df, flight_states_df, event_info_df, error_info_df)
    state_plots = plot_flight_info(flight_info_df, filtered_data_info_df, flight_states_df, event_info_df, error_info_df, False)
    figures_to_html(imu_plots, baro_plots, accelerometer_plots, magneto_plots, state_plots, f'{plot_output_dir}/{base_name} - plots.html')
    
    print(f'Plots generated in {plot_output_dir}!')
    
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input',
                    dest = 'input_path',
                    help = 'Input log location',
                    type=str,
                    required=True)

    parser.add_argument('-o', '--output',
                        dest = 'output_path',
                        help='Desired output location',
                        type=str)
    
    args = parser.parse_args()

    main(args)

