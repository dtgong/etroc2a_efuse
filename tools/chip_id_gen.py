import csv
import os

from eFuse_encoder import eFuse_encoder


MAX_LOCATION_ID = 116
OUTPUT_CSV = "../data/chips.csv"
BATCH_LIST_CSV = "../data/batch_list.csv"


def bits_to_int(bits):
    value = 0
    for i, bit in enumerate(bits):
        value |= (bit & 1) << i
    return value


def make_chip_id(batch_id, wafer_id, location_id):
    """
    17-bit chip_id layout:
        [16:14] batch_id
        [13: 7] wafer_id
        [ 6: 0] location_id
    """
    if not (0 <= batch_id <= 7):
        raise ValueError("batch_id must be in range 0..7")
    if not (1 <= wafer_id <= 127):
        raise ValueError("wafer_id must be in range 1..127")
    if not (1 <= location_id <= 127):
        raise ValueError("location_id must be in range 1..127")

    return (batch_id << 14) | (wafer_id << 7) | location_id


def read_batch_list(batch_list_csv):
    """
    Read batch wafer ranges from CSV.

    Expected columns:
        batch,min_wafer_id,max_wafer_id
    """
    batch_ranges = []

    with open(batch_list_csv, "r", newline="") as f:
        reader = csv.DictReader(f)

        required_fields = {"batch", "min_wafer_id", "max_wafer_id"}
        if not required_fields.issubset(reader.fieldnames or []):
            raise ValueError(
                "batch_list.csv must contain columns: "
                "batch,min_wafer_id,max_wafer_id"
            )

        for row in reader:
            batch_id = int(row["batch"])
            min_wafer_id = int(row["min_wafer_id"])
            max_wafer_id = int(row["max_wafer_id"])

            if not (0 <= batch_id <= 7):
                raise ValueError(f"invalid batch_id {batch_id} in batch_list.csv")
            if not (1 <= min_wafer_id <= 127):
                raise ValueError(
                    f"invalid min_wafer_id {min_wafer_id} for batch {batch_id}"
                )
            if not (1 <= max_wafer_id <= 127):
                raise ValueError(
                    f"invalid max_wafer_id {max_wafer_id} for batch {batch_id}"
                )
            if min_wafer_id > max_wafer_id:
                raise ValueError(
                    f"min_wafer_id > max_wafer_id for batch {batch_id}"
                )

            batch_ranges.append((batch_id, min_wafer_id, max_wafer_id))

    return batch_ranges


def chip_id_gen(
    output_csv=OUTPUT_CSV,
    batch_list_csv=BATCH_LIST_CSV,
    max_location_id=MAX_LOCATION_ID
):
    if not (1 <= max_location_id <= 127):
        raise ValueError("max_location_id must be in range 1..127")

    batch_ranges = read_batch_list(batch_list_csv)

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "batch_id",
            "wafer_id",
            "location_id",
            "chip_id",
            "parity_code",
            "codeword",
            "used",
        ])

        for batch_id, min_wafer_id, max_wafer_id in batch_ranges:
            for wafer_id in range(min_wafer_id, max_wafer_id + 1):
                for location_id in range(1, max_location_id + 1):
                    chip_id = make_chip_id(batch_id, wafer_id, location_id)

                    _, parity_bits = eFuse_encoder(chip_id)
                    parity_code = bits_to_int(parity_bits)

                    # codeword = [parity(15b) | chip_id(17b)]
                    codeword = (parity_code << 17) | chip_id

                    writer.writerow([
                        batch_id,
                        wafer_id,
                        location_id,
                        f"0x{chip_id:05X}",
                        f"0x{parity_code:04X}",
                        f"0x{codeword:08X}",
                        0,
                    ])


if __name__ == "__main__":
    chip_id_gen()
    print(f"Generated {OUTPUT_CSV}")