import random
import sys
import os

sys.path.insert(0, os.path.abspath("../tools"))

from eFuse_encoder import eFuse_encoder
from eFuse_decoder import eFuse_decoder


def int_to_bits(value, width):
    bits = [0] * width
    for i in range(width):
        bits[i] = (value >> i) & 1
    return bits


def bits_to_int(bits):
    value = 0
    for i, bit in enumerate(bits):
        value |= (bit & 1) << i
    return value


def inject_errors(message_int, parity_int, n_errors):
    """
    Inject n_errors random bit flips into the 32-bit codeword.

    Internal codeword layout:
        codeword_bits[0:17]   -> message bits [0]..[16]
        codeword_bits[17:32]  -> parity bits  [0]..[14]

    Returns:
        corrupted_message_int
        corrupted_parity_int
        error_positions
    """
    if n_errors < 0 or n_errors > 32:
        raise ValueError("n_errors must be between 0 and 32")

    message_bits = int_to_bits(message_int, 17)
    parity_bits = int_to_bits(parity_int, 15)

    codeword_bits = message_bits + parity_bits

    error_positions = random.sample(range(32), n_errors)
    for pos in error_positions:
        codeword_bits[pos] ^= 1

    corrupted_message_bits = codeword_bits[:17]
    corrupted_parity_bits = codeword_bits[17:]

    corrupted_message_int = bits_to_int(corrupted_message_bits)
    corrupted_parity_int = bits_to_int(corrupted_parity_bits)

    return corrupted_message_int, corrupted_parity_int, error_positions


def test_error_injection(n_tests=1000, n_errors=3, verbose=False):
    """
    Generate random nonzero 17-bit messages, encode, inject errors,
    decode, and check whether the corrected message matches the original.

    Args:
        n_tests:   number of random test messages
        n_errors:  number of random bit errors injected into each codeword
        verbose:   print details for failures or all cases

    Returns:
        summary dictionary
    """
    if n_errors < 0 or n_errors > 32:
        raise ValueError("n_errors must be between 0 and 32")

    total = 0
    success = 0
    fail = 0
    status_count = {}

    for _ in range(n_tests):
        original_message_int = random.randint(1, (1 << 17) - 1)

        original_message_bits, original_parity_bits = eFuse_encoder(original_message_int)
        original_parity_int = bits_to_int(original_parity_bits)

        rx_message_int, rx_parity_int, error_positions = inject_errors(
            original_message_int,
            original_parity_int,
            n_errors,
        )

        result = eFuse_decoder(rx_message_int, rx_parity_int)
        status = result["error_status"]

        total += 1
        status_count[status] = status_count.get(status, 0) + 1

        corrected_message_int = result["corrected_message_int"]
        corrected_parity_int = result["corrected_parity_int"]

        # Re-encode corrected message and compare parity too
        _, expected_parity_bits = eFuse_encoder(corrected_message_int)
        expected_parity_int = bits_to_int(expected_parity_bits)

        passed = (
            corrected_message_int == original_message_int
            and corrected_parity_int == expected_parity_int
        )

        if passed:
            success += 1
        else:
            fail += 1
            if verbose:
                print("FAIL")
                print(f"  original_message_int   = 0x{original_message_int:05X}")
                print(f"  original_parity_int    = 0x{original_parity_int:04X}")
                print(f"  rx_message_int         = 0x{rx_message_int:05X}")
                print(f"  rx_parity_int          = 0x{rx_parity_int:04X}")
                print(f"  corrected_message_int  = 0x{corrected_message_int:05X}")
                print(f"  corrected_parity_int   = 0x{corrected_parity_int:04X}")
                print(f"  expected_parity_int    = 0x{expected_parity_int:04X}")
                print(f"  status                 = {status}")
                print(f"  error_positions        = {sorted(error_positions)}")
                print()

        if verbose and passed:
            print("PASS")
            print(f"  original_message_int   = 0x{original_message_int:05X}")
            print(f"  original_parity_int    = 0x{original_parity_int:04X}")
            print(f"  rx_message_int         = 0x{rx_message_int:05X}")
            print(f"  rx_parity_int          = 0x{rx_parity_int:04X}")
            print(f"  corrected_message_int  = 0x{corrected_message_int:05X}")
            print(f"  corrected_parity_int   = 0x{corrected_parity_int:04X}")
            print(f"  status                 = {status}")
            print(f"  error_positions        = {sorted(error_positions)}")
            print()

    summary = {
        "n_tests": total,
        "n_errors": n_errors,
        "success": success,
        "fail": fail,
        "status_count": status_count,
    }

    return summary


if __name__ == "__main__":
    N_TESTS = 100
    N_ERRORS = 3
    VERBOSE = True

    summary = test_error_injection(
        n_tests=N_TESTS,
        n_errors=N_ERRORS,
        verbose=VERBOSE,
    )

    print("Test Summary")
    print(f"  Number of tests   : {summary['n_tests']}")
    print(f"  Errors injected   : {summary['n_errors']}")
    print(f"  Success           : {summary['success']}")
    print(f"  Fail              : {summary['fail']}")
    print("  Status count      :")
    for status, count in summary["status_count"].items():
        print(f"    {status}: {count}")