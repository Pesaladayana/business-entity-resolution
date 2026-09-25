from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TRAIN_DIR = PROJECT_ROOT / "dataset" / "train"

SOURCE2_PATH = TRAIN_DIR / "train_source2.tsv"


if __name__ == "__main__":

    print("Testing chunked reading...")
    print("File:", SOURCE2_PATH)

    chunk = pd.read_csv(
        SOURCE2_PATH,
        sep="\t",
        dtype=str,
        nrows=10000
    )

    print("\nSuccessfully loaded 10,000 rows.")

    print("Rows:", len(chunk))
    print("Columns:", list(chunk.columns))

    print("\nFirst 5 rows:")
    print(chunk.head())