from pathlib import Path
import pandas as pd


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Dataset folders
DATASET_DIR = PROJECT_ROOT / "dataset"

TRAIN_DIR = DATASET_DIR / "train"
TEST_DIR = DATASET_DIR / "test"


def load_source1(train=True):
    """Load Source 1."""

    if train:
        file_path = TRAIN_DIR / "train_source1.tsv"
    else:
        file_path = TEST_DIR / "test_source1.tsv"

    return pd.read_csv(
        file_path,
        sep="\t",
        dtype=str
    )


if __name__ == "__main__":

    print("Testing data loader...")

    source1 = load_source1(train=True)

    print("\nSource 1 loaded successfully!")
    print("Rows:", len(source1))
    print("Columns:", list(source1.columns))

    print("\nFirst 5 rows:")
    print(source1.head())