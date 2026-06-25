"""Pandas data loading and cleaning helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def load_and_prepare_dataset(dataset_path: Path) -> pd.DataFrame:
    """Load, clean, sort, and normalize a CSV dataset."""
    frame = pd.read_csv(dataset_path)
    frame = frame.drop_duplicates().copy()
    for column in frame.columns:
        if pd.api.types.is_numeric_dtype(frame[column]):
            frame[column] = frame[column].fillna(frame[column].median())
        else:
            frame[column] = frame[column].fillna("Unknown")
    numeric_columns = frame.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        frame = frame.sort_values(numeric_columns[0]).reset_index(drop=True)
        for column in numeric_columns:
            minimum = frame[column].min()
            maximum = frame[column].max()
            if maximum != minimum:
                frame[f"{column}_normalized"] = (frame[column] - minimum) / (maximum - minimum)
            else:
                frame[f"{column}_normalized"] = 0.5
    return frame
