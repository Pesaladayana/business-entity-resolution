from pathlib import Path
import pandas as pd

from blocking import (
    create_name_block_key,
    create_address_block_key
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_DIR = PROJECT_ROOT / "dataset" / "train"

SOURCE1_PATH = TRAIN_DIR / "train_source1.tsv"
SOURCE2_PATH = TRAIN_DIR / "train_source2.tsv"
GROUND_TRUTH_PATH = TRAIN_DIR / "train_ground_truth.tsv"

SAMPLE_SIZE = 10000


def get_true_s2_ids(ground_truth):
    true_s2_ids = set()

    for value in ground_truth["matched_entity_ids"].fillna(""):
        if not value:
            continue

        for entity_id in value.split(","):
            entity_id = entity_id.strip()

            if entity_id.startswith("S2-"):
                true_s2_ids.add(entity_id)

    return true_s2_ids


def main():

    print("Loading S1 sample and ground truth...")

    source1 = pd.read_csv(
        SOURCE1_PATH,
        sep="\t",
        dtype=str,
        nrows=SAMPLE_SIZE
    )

    ground_truth = pd.read_csv(
        GROUND_TRUTH_PATH,
        sep="\t",
        dtype=str,
        nrows=SAMPLE_SIZE
    )

    # Create S1 blocking keys
    source1["name_block_key"] = source1.apply(
        lambda row: create_name_block_key(
            row["business_name"],
            row["country"]
        ),
        axis=1
    )

    source1["address_block_key"] = source1.apply(
        lambda row: create_address_block_key(
            row["business_address"],
            row["country"]
        ),
        axis=1
    )

    s1_name_keys = set(source1["name_block_key"])
    s1_address_keys = set(source1["address_block_key"])

    # True S2 matches
    true_s2_ids = get_true_s2_ids(ground_truth)

    # Find S2 candidates
    candidate_s2_ids = set()

    print("Scanning Source 2...")

    for chunk in pd.read_csv(
        SOURCE2_PATH,
        sep="\t",
        dtype=str,
        chunksize=100000
    ):

        chunk["name_block_key"] = chunk.apply(
            lambda row: create_name_block_key(
                row["business_name"],
                row["country"]
            ),
            axis=1
        )

        chunk["address_block_key"] = chunk.apply(
            lambda row: create_address_block_key(
                row["business_address"],
                row["country"]
            ),
            axis=1
        )

        matching_rows = chunk[
            chunk["name_block_key"].isin(s1_name_keys)
            |
            chunk["address_block_key"].isin(s1_address_keys)
        ]

        candidate_s2_ids.update(
            matching_rows["entity_id"].tolist()
        )

    # True matches that the blocker missed
    missed_s2_ids = true_s2_ids - candidate_s2_ids

    print("\n========== MISSED MATCHES ==========")
    print(f"True S2 matches:  {len(true_s2_ids):,}")
    print(f"Found by blocker: {len(true_s2_ids & candidate_s2_ids):,}")
    print(f"Missed matches:   {len(missed_s2_ids):,}")
    print("====================================")

    if not missed_s2_ids:
        print("\nNo missed matches!")
        return

    # Load only the missed S2 records
    print("\nLoading missed S2 records...")

    missed_records = []

    for chunk in pd.read_csv(
        SOURCE2_PATH,
        sep="\t",
        dtype=str,
        chunksize=100000
    ):

        matches = chunk[
            chunk["entity_id"].isin(missed_s2_ids)
        ]

        if not matches.empty:
            missed_records.append(matches)

    missed_s2 = pd.concat(
        missed_records,
        ignore_index=True
    )

    # Map each S2 ID to its S1 IDs from ground truth
    examples = []

    for index, row in ground_truth.iterrows():

        matched_ids = str(
            row["matched_entity_ids"]
        )

        if not matched_ids or matched_ids == "nan":
            continue

        s2_ids = [
            x.strip()
            for x in matched_ids.split(",")
            if x.strip().startswith("S2-")
        ]

        missed_for_s1 = [
            x
            for x in s2_ids
            if x in missed_s2_ids
        ]

        if not missed_for_s1:
            continue

        s1_row = source1.iloc[index]

        for s2_id in missed_for_s1:

            s2_rows = missed_s2[
                missed_s2["entity_id"] == s2_id
            ]

            for _, s2_row in s2_rows.iterrows():

                examples.append({
                    "S1_ID": s1_row["entity_id"],
                    "S1_Name": s1_row["business_name"],
                    "S1_Address": s1_row["business_address"],
                    "S2_ID": s2_row["entity_id"],
                    "S2_Name": s2_row["business_name"],
                    "S2_Address": s2_row["business_address"]
                })

    result = pd.DataFrame(examples)

    print("\n========== MISSED MATCH EXAMPLES ==========")

    if result.empty:
        print("Could not construct examples.")
    else:
        print(result.head(20).to_string(index=False))

    print("\n===========================================")


if __name__ == "__main__":
    main()