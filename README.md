# cats-logs

This repository contains the code for parsing and plotting binary flight logs
from CATS records.

## Installation

To install the package in a `python` environment, run

```bash
pip install git+https://github.com/catsystems/cats-logs/catslogs.git
```

For local development, **clone the repository** and run:

```bash
pip install -e .
```

This will install the package in editable mode.

## Usage

To parse a binary log, you will need:

```python
from catslogs.embedded_constants import FLIGHT_MAP
from catslogs import binary_parser, html_generator, plot_generator


log_path = "path_to_your_log_file.cfl"

df_dict, plot_output_dir, base_name = binary_parser.extract_data(
    input_log_path=log_path,
    output_log_path=None,
    state_map=FLIGHT_MAP,
    from_notebook=True,
)
df_dict
```

It is an option to rename the dictionary values for easier access:


```python 
imu_df = df_dict["imu_df"]
baro_df = df_dict["baro_df"]

event_info_df = df_dict["event_info_df"]
error_info_df = df_dict["error_info_df"]
flight_states_df = df_dict["flight_states_df"]
```

To generate plots, you will need:

```python
imu_plots = plot_imu_data(
    imu_df, flight_states_df, event_info_df, error_info_df
)
baro_plots = plot_baro_data(
    baro_df, flight_states_df, event_info_df, error_info_df
)
```

To get a complete usage example and further information, please refer to the
`log_parsing/log_visualizer.ipynb` notebook.

## License

This work is licensed under the GNU GENERAL PUBLIC LICENSE Version 3. See
[LICENSE](https://github.com/catsystems/cats-logs/blob/main/LICENSE.md) for details.
