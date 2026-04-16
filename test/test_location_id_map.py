# test_location_id_tool.py
import sys
import os

sys.path.insert(0, os.path.abspath("../tools"))

from location_id_map import (
    COL_ROW_TO_LOCATION_ID,
    LOCATION_ID_TO_COL_ROW,
    location_id,
    col_row,
)

def test_unique_mapping():
    # Check: every (col, row) maps to exactly one location_id
    seen_positions = set()
    for pos, loc_id in COL_ROW_TO_LOCATION_ID.items():
        if pos in seen_positions:
            raise AssertionError(f"duplicate (col, row) found: {pos}")
        seen_positions.add(pos)

    # Check: every location_id maps to exactly one (col, row)
    seen_location_ids = set()
    for loc_id, pos in LOCATION_ID_TO_COL_ROW.items():
        if loc_id in seen_location_ids:
            raise AssertionError(f"duplicate location_id found: {loc_id}")
        seen_location_ids.add(loc_id)

    # Cross-check the two dictionaries are exact inverses
    for pos, loc_id in COL_ROW_TO_LOCATION_ID.items():
        if loc_id not in LOCATION_ID_TO_COL_ROW:
            raise AssertionError(f"location_id {loc_id} missing in reverse map")
        if LOCATION_ID_TO_COL_ROW[loc_id] != pos:
            raise AssertionError(
                f"mismatch: forward {pos} -> {loc_id}, "
                f"but reverse {loc_id} -> {LOCATION_ID_TO_COL_ROW[loc_id]}"
            )

    for loc_id, pos in LOCATION_ID_TO_COL_ROW.items():
        if pos not in COL_ROW_TO_LOCATION_ID:
            raise AssertionError(f"(col,row) {pos} missing in forward map")
        if COL_ROW_TO_LOCATION_ID[pos] != loc_id:
            raise AssertionError(
                f"mismatch: reverse {loc_id} -> {pos}, "
                f"but forward {pos} -> {COL_ROW_TO_LOCATION_ID[pos]}"
            )


def test_round_trip():
    for pos, loc_id in COL_ROW_TO_LOCATION_ID.items():
        if location_id(*pos) != loc_id:
            raise AssertionError(f"round-trip failed for position {pos}")
        if col_row(loc_id) != pos:
            raise AssertionError(f"round-trip failed for location_id {loc_id}")


def print_all_location_mappings():
    print("location_id,col,row")
    for loc_id in sorted(LOCATION_ID_TO_COL_ROW):
        col, row = LOCATION_ID_TO_COL_ROW[loc_id]
        print(f"{loc_id},{col},{row}")


if __name__ == "__main__":
    test_unique_mapping()
    test_round_trip()
    print_all_location_mappings()
    print("All tests passed.")