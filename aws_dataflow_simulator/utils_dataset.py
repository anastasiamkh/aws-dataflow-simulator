import pandas as pd
from typing import Optional


def preprocess_dataset(
    dataset_path: str,
    start_datetime: Optional[str],
    apply_delay: bool,
    delay_ms: Optional[int],
    timestamp_column_name: Optional[str],
) -> pd.DataFrame:
    """Adds time_till_next_event_ms column for streaming.

    Args:
        dataset_path (str): Path to the dataset CSV file.
        start_datetime (Optional[str]): The datetime to normalize the timestamps to.
        apply_delay (bool): Whether to apply delay or stream as fast as possible.
        delay_ms (Optional[int]): If apply_delay is True, adds static delay between events.
        timestamp_column_name (Optional[str]): If apply_delay is True,
            uses timestamp_column_name to calculate the difference between row events.

    Returns:
        pd.DataFrame: The preprocessed DataFrame.
    """
    df = pd.read_csv(dataset_path)
    df.columns = [col.lower() for col in df.columns]

    if not apply_delay:
        return df

    assert start_datetime, "You must specify start datetime for first event."

    # If apply_delay is True, either apply a static delay or calculate based on timestamps
    if delay_ms:
        # Apply a static delay in milliseconds
        df["time_till_next_event_ms"] = delay_ms
    elif timestamp_column_name:
        # Ensure the datetime column exists
        if timestamp_column_name not in df.columns:
            raise ValueError(
                f"The column '{timestamp_column_name}' was not found in the dataset."
            )

        # Convert the datetime column to datetime objects
        df[timestamp_column_name] = pd.to_datetime(df[timestamp_column_name])

        # Sort by the datetime column if not already sorted
        df = df.sort_values(by=timestamp_column_name)

        # Calculate the delay based on the difference between consecutive timestamps
        df["time_till_next_event_ms"] = (
            df[timestamp_column_name]
            .diff()
            .shift(-1)
            .fillna(pd.Timedelta(0))
            .dt.total_seconds()
            * 1000
        )
    else:
        raise ValueError("Either delay_ms or timestamp_column_name must be specified.")

    return df
