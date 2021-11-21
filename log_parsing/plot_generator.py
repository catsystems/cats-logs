import plotly.graph_objs as go
import numpy as np

from embedded_constants import ERROR_MAP


layout_font = dict(family="Courier New, monospace", size=12)

legend = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)

layout_args = dict(
    xaxis_title="Timestamp [s]",
    template="plotly_dark",
    legend=legend,
    font=layout_font,
    width=1500,
    height=800,
)

def show(plot_arr: list[go.Figure]):
    for plot in plot_arr:
        plot.show()


def add_flight_states_and_events(
    fig: go.Figure, flight_states_df, event_info_df, error_info_df
):
    y_mins = []
    y_maxs = []
    for trace_data in fig.data:
        y_mins.append(np.nanmin(trace_data.y[trace_data.y != -np.inf]))
        y_maxs.append(np.nanmax(trace_data.y[trace_data.y != np.inf]))
    y_min = min(y_mins)
    y_max = max(y_maxs)
    # print(y_min, y_max)

    for idx, state in flight_states_df.iterrows():
        fig.add_scatter(
            x=[state["ts"], state["ts"]],
            y=[y_min * 0.95, y_max],
            name="State",
            legendgroup="State",
            line_color="green",
            text=[state["state"], None],
            textposition="bottom center",
            mode="lines+text",
            showlegend=True if idx == 1 else False,
            line_width=1,
            line_dash="dash",
        )

    for idx, event in event_info_df.iterrows():
        fig.add_scatter(
            x=[event["ts"], event["ts"]],
            y=[y_min * 0.85, y_max],
            name="Event",
            legendgroup="Event",
            line_color="orange",
            text=[event["event"], None],
            mode="lines+text",
            showlegend=True if idx == 1 else False,
            line_width=1,
            line_dash="dash",
        )

    for idx, error in error_info_df.iterrows():
        err = int(error_info_df.iloc[idx]["error"])
        txt = f"{err}:<br />"
        for key, val in ERROR_MAP.items():
            if key & err:
                txt += f"{val}<br />"

        fig.add_scatter(
            x=[error["ts"], error["ts"]],
            y=[y_min * 0.70, y_max],
            name="Error",
            legendgroup="Error",
            line_color="red",
            hovertext=txt,
            mode="lines",
            showlegend=True if idx == 1 else False,
            line_width=1,
            line_dash="dot",
        )


def plot_imu_data(imu_df, flight_states_df, event_info_df, error_info_df):
    fig_ax = go.Figure()
    fig_ay = go.Figure()
    fig_az = go.Figure()
    fig_gx = go.Figure()
    fig_gy = go.Figure()
    fig_gz = go.Figure()
    for imu_id, one_imu in imu_df.groupby("id"):
        fig_ax.add_scatter(x=one_imu.ts, y=one_imu.Ax, name=imu_id, mode="lines")
        fig_ay.add_scatter(x=one_imu.ts, y=one_imu.Ay, name=imu_id, mode="lines")
        fig_az.add_scatter(x=one_imu.ts, y=one_imu.Az, name=imu_id, mode="lines")
        fig_gx.add_scatter(x=one_imu.ts, y=one_imu.Gx, name=imu_id, mode="lines")
        fig_gy.add_scatter(x=one_imu.ts, y=one_imu.Gy, name=imu_id, mode="lines")
        fig_gz.add_scatter(x=one_imu.ts, y=one_imu.Gz, name=imu_id, mode="lines")

    add_flight_states_and_events(fig_ax, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_ay, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_az, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_gx, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_gy, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_gz, flight_states_df, event_info_df, error_info_df)

    # for measurement in [('Acc', 'g'), ('Gyro', 'dps')]:
    #     for axis in ['x', 'y', 'z']:
    #         print(f"{measurement[0]}_{axis} [{measurement[1]}]")
    #         fig_ax.update_layout(
    #             title=f"IMU {measurement[0]}_{axis}",
    #             yaxis_title="Acc_x [g]",
    #             legend_title="IMU ID",
    #             **layout_args
    #         )

    fig_ax.update_layout(
        title="IMU Acc_x", yaxis_title="Acc_x [g]", legend_title="IMU ID", **layout_args
    )

    fig_ay.update_layout(
        title="IMU Acc_y", yaxis_title="Acc_y [g]", legend_title="IMU ID", **layout_args
    )

    fig_az.update_layout(
        title="IMU Acc_z", yaxis_title="Acc_z [g]", legend_title="IMU ID", **layout_args
    )

    fig_gx.update_layout(
        title="IMU Gyro_x",
        yaxis_title="Gyro_x [dps]",
        legend_title="IMU ID",
        **layout_args,
    )

    fig_gy.update_layout(
        title="IMU Gyro_y",
        yaxis_title="Gyro_y [dps]",
        legend_title="IMU ID",
        **layout_args,
    )

    fig_gz.update_layout(
        title="IMU Gyro_z",
        yaxis_title="Gyro_z [dps]",
        legend_title="IMU ID",
        **layout_args,
    )

    return [fig_ax, fig_ay, fig_az, fig_gx, fig_gy, fig_gz]


def plot_acc_data(acc_df, flight_states_df, event_info_df, error_info_df):
    fig_ax = go.Figure()
    fig_ay = go.Figure()
    fig_az = go.Figure()
    fig_ax.add_scatter(x=acc_df.ts, y=acc_df["acc_x"], name="Acc x", mode="lines")
    fig_ay.add_scatter(x=acc_df.ts, y=acc_df["acc_y"], name="Acc y", mode="lines")
    fig_az.add_scatter(x=acc_df.ts, y=acc_df["acc_z"], name="Acc z", mode="lines")

    add_flight_states_and_events(fig_ax, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_ay, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_az, flight_states_df, event_info_df, error_info_df)

    fig_ax.update_layout(
        title="Accelerometer X",
        yaxis_title="Acc_x [g]",
        legend_title="Acc ID",
        **layout_args,
    )

    fig_ay.update_layout(
        title="Accelerometer Y",
        yaxis_title="Acc_y [g]",
        legend_title="Acc ID",
        **layout_args,
    )

    fig_az.update_layout(
        title="Accelerometer Z",
        yaxis_title="Acc_z [g]",
        legend_title="Acc ID",
        **layout_args,
    )

    return [fig_ax, fig_ay, fig_az]


def plot_magneto_data(magneto_df, flight_states_df, event_info_df, error_info_df):
    fig_mx = go.Figure()
    fig_my = go.Figure()
    fig_mz = go.Figure()
    fig_mx.add_scatter(
        x=magneto_df.ts, y=magneto_df["mx"], name="magneto x", mode="lines"
    )
    fig_my.add_scatter(
        x=magneto_df.ts, y=magneto_df["my"], name="magneto y", mode="lines"
    )
    fig_mz.add_scatter(
        x=magneto_df.ts, y=magneto_df["mz"], name="magneto z", mode="lines"
    )

    add_flight_states_and_events(fig_mx, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_my, flight_states_df, event_info_df, error_info_df)
    add_flight_states_and_events(fig_mz, flight_states_df, event_info_df, error_info_df)

    fig_mx.update_layout(
        title="Magneto X",
        yaxis_title="Mag_x [mG]",
        legend_title="MAG ID",
        **layout_args,
    )

    fig_my.update_layout(
        title="Magneto Y",
        yaxis_title="Mag_y [mG]",
        legend_title="MAG ID",
        **layout_args,
    )

    fig_mz.update_layout(
        title="Magneto Z",
        yaxis_title="Mag_z [mG]",
        legend_title="MAG ID",
        **layout_args,
    )

    return [fig_mx, fig_my, fig_mz]


def plot_baro_data(baro_df, flight_states_df, event_info_df, error_info_df):
    fig_temp = go.Figure()
    fig_press = go.Figure()
    for baro_id, one_baro in baro_df.groupby("id"):
        fig_temp.add_scatter(x=one_baro.ts, y=one_baro["T"], name=baro_id, mode="lines")
        fig_press.add_scatter(
            x=one_baro.ts, y=one_baro["P"], name=baro_id, mode="lines"
        )

    add_flight_states_and_events(
        fig_temp, flight_states_df, event_info_df, error_info_df
    )
    add_flight_states_and_events(
        fig_press, flight_states_df, event_info_df, error_info_df
    )

    deg = "\N{DEGREE SIGN}"
    fig_temp.update_layout(
        title="BARO Temperature",
        yaxis_title=f"T [{deg}C]",
        legend_title="BARO ID",
        **layout_args,
    )

    fig_press.update_layout(
        title="BARO Pressure",
        yaxis_title="P [hPa]",
        legend_title="BARO ID",
        **layout_args,
    )

    return [fig_temp, fig_press]


def plot_flight_info(
    flight_info_df,
    filtered_data_info_df,
    flight_states_df,
    event_info_df,
    error_info_df,
    include_bounds=True,
):
    fig_height = go.Figure()
    fig_vel = go.Figure()
    fig_acc = go.Figure()

    fig_height.add_scatter(
        x=flight_info_df.ts, y=flight_info_df["height"], name="height", mode="lines"
    )
    fig_height.add_scatter(
        x=filtered_data_info_df.ts,
        y=filtered_data_info_df["altitude_agl"],
        name="altitude_agl",
        mode="lines",
    )
    fig_height.add_scatter(
        x=filtered_data_info_df.ts,
        y=filtered_data_info_df["filtered_altitude_AGL"],
        name="filtered_altitude_agl",
        mode="lines",
    )

    if include_bounds:
        fig_height.add_scatter(
            x=flight_info_df.ts,
            y=flight_info_df["lower_bound"],
            name="lower_bound",
            mode="lines",
        )
        fig_height.add_scatter(
            x=flight_info_df.ts,
            y=flight_info_df["upper_bound"],
            name="upper_bound",
            mode="lines",
        )

    fig_vel.add_scatter(
        x=flight_info_df.ts, y=flight_info_df["velocity"], name="velocity", mode="lines"
    )

    fig_acc.add_scatter(
        x=flight_info_df.ts,
        y=flight_info_df["acceleration"],
        name="acceleration",
        mode="lines",
    )
    fig_acc.add_scatter(
        x=filtered_data_info_df.ts,
        y=filtered_data_info_df["raw_acceleration"],
        name="raw_acceleration",
        mode="lines",
    )
    fig_acc.add_scatter(
        x=filtered_data_info_df.ts,
        y=filtered_data_info_df["filtered_acceleration"],
        name="filtered_acceleration",
        mode="lines",
    )

    add_flight_states_and_events(
        fig_height, flight_states_df, event_info_df, error_info_df
    )
    add_flight_states_and_events(
        fig_vel, flight_states_df, event_info_df, error_info_df
    )
    add_flight_states_and_events(
        fig_acc, flight_states_df, event_info_df, error_info_df
    )

    fig_height.update_layout(title="Height", yaxis_title="Height [m]", **layout_args)

    fig_vel.update_layout(title="Velocity", yaxis_title="Velocity [m/s]", **layout_args)

    squared = "\N{SUPERSCRIPT TWO}"
    fig_acc.update_layout(
        title="Acceleration", yaxis_title=f"Acceleration [m/s{squared}]", **layout_args
    )

    return [fig_height, fig_vel, fig_acc]
