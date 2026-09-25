from pathlib import Path
import pandas as pd

from blocking import (
    create_name_block_key,
    create_address_block_key
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "dataset"

TRAIN_DIR = DATASET_DIR / "train"

SOURCE1_PATH = TRAIN_DIR / "train_source1.tsv"

SOURCE2_PATH = TRAIN_DIR / "train_source2.tsv"

GROUND_TRUTH_PATH = TRAIN_DIR / "train_ground_truth.tsv"

SAMPLE_SIZE = 10000


def load_training_sample():

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

    return source1, ground_truth


def get_s2_ids_from_ground_truth(ground_truth):

    true_s2_ids = set()

    for value in ground_truth[
        "matched_entity_ids"
    ].fillna(""):

        if not value:
            continue

        for entity_id in value.split(","):

            entity_id = entity_id.strip()

            if entity_id.startswith("S2-"):

                true_s2_ids.add(entity_id)

    return true_s2_ids


def test_blocking():

    print("Loading training sample...")

    source1, ground_truth = load_training_sample()

    print(
        f"S1 records tested: "
        f"{len(source1):,}"
    )

    # -----------------------------
    # Create S1 name blocking keys
    # -----------------------------

    source1["name_block_key"] = source1.apply(
        lambda row: create_name_block_key(
            row["business_name"],
            row["country"]
        ),
        axis=1
    )

    # -----------------------------
    # Create S1 address blocking keys
    # -----------------------------

    source1["address_block_key"] = source1.apply(
        lambda row: create_address_block_key(
            row["business_address"],
            row["country"]
        ),
        axis=1
    )

    # Store unique S1 keys

    s1_name_block_keys = set(
        source1["name_block_key"]
    )

    s1_address_block_keys = set(
        source1["address_block_key"]
    )

    print(
        f"Unique name blocking keys: "
        f"{len(s1_name_block_keys):,}"
    )

    print(
        f"Unique address blocking keys: "
        f"{len(s1_address_block_keys):,}"
    )

    # -----------------------------
    # Get true S2 matches
    # -----------------------------

    true_s2_ids = get_s2_ids_from_ground_truth(
        ground_truth
    )

    print(
        f"True S2 matches in sample: "
        f"{len(true_s2_ids):,}"
    )

    candidate_s2_ids = set()

    processed = 0

    print("\nScanning Source 2 in chunks...")

    # -----------------------------
    # Scan Source 2
    # -----------------------------

    for chunk in pd.read_csv(
        SOURCE2_PATH,
        sep="\t",
        dtype=str,
        chunksize=100000
    ):

        # Create S2 name keys

        chunk["name_block_key"] = chunk.apply(
            lambda row: create_name_block_key(
                row["business_name"],
                row["country"]
            ),
            axis=1
        )

        # Create S2 address keys

        chunk["address_block_key"] = chunk.apply(
            lambda row: create_address_block_key(
                row["business_address"],
                row["country"]
            ),
            axis=1
        )

        # -----------------------------
        # Candidate if either key matches
        # -----------------------------

        matching_rows = chunk[
            chunk["name_block_key"].isin(
                s1_name_block_keys
            )
            |
            chunk["address_block_key"].isin(
                s1_address_block_keys
            )
        ]

        candidate_s2_ids.update(
            matching_rows["entity_id"].tolist()
        )

        processed += len(chunk)

        print(
            f"Processed "
            f"{processed:,} S2 rows"
        )

    # -----------------------------
    # Calculate blocking recall
    # -----------------------------

    found_true_matches = (
        true_s2_ids.intersection(
            candidate_s2_ids
        )
    )

    if true_s2_ids:

        recall = (
            len(found_true_matches)
            /
            len(true_s2_ids)
        )

    else:

        recall = 1.0

    # -----------------------------
    # Results
    # -----------------------------

    print("\n========== RESULTS ==========")

    print(
        f"True S2 matches:       "
        f"{len(true_s2_ids):,}"
    )

    print(
        f"Candidate S2 records:  "
        f"{len(candidate_s2_ids):,}"
    )

    print(
        f"True matches found:    "
        f"{len(found_true_matches):,}"
    )

    print(
        f"\nBlocking recall: "
        f"{recall:.4f}"
    )

    print(
        f"Blocking recall: "
        f"{recall * 100:.2f}%"
    )

    print("=============================")


if __name__ == "__main__":

    test_blocking()