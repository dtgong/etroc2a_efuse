from itertools import combinations

def eFuse_decoder(message_int, parity_int):
    # The 17x15 parity matrix P
    P = [
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0],
        [1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0],
        [1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0],
        [1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1],
        [0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1],
        [0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1],
        [0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
        [0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
    ]

    # Decoder input may be corrupted, so message_int is allowed to be 0.
    if message_int < 0 or message_int >= (1 << 17):
        raise ValueError("message_int must be a 17-bit unsigned integer")

    if parity_int < 0 or parity_int >= (1 << 15):
        raise ValueError("parity_int must be a 15-bit unsigned integer")

    # ------------------------------------------------------------
    # Bit conversion helpers
    # Internal convention:
    #   bits[16] = MSB for 17-bit message
    #   bits[14] = MSB for 15-bit parity
    #   bits[0]  = LSB
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Compute parity from message using the same convention as encoder
    # P row 0 corresponds to message_bits[16] (MSB)
    # P row 16 corresponds to message_bits[0]  (LSB)
    # parity_bits[14] is MSB, parity_bits[0] is LSB
    # ------------------------------------------------------------
    def compute_parity_bits(msg_bits):
        parity_bits = [0] * 15
        for col in range(15):
            bit_sum = 0
            for row in range(17):
                bit_sum ^= msg_bits[16 - row] & P[row][col]
            parity_bits[14 - col] = bit_sum
        return parity_bits

    # ------------------------------------------------------------
    # Build received bits
    # ------------------------------------------------------------
    message_bits = int_to_bits(message_int, 17)
    parity_bits = int_to_bits(parity_int, 15)

    # ------------------------------------------------------------
    # Syndrome = received parity XOR recomputed parity(message)
    # ------------------------------------------------------------
    calc_parity_bits = compute_parity_bits(message_bits)
    syndrome_bits = [parity_bits[i] ^ calc_parity_bits[i] for i in range(15)]

    if syndrome_bits == [0] * 15:
        return {
            "error_status": "no_error",
            "corrected_message_int": message_int,
            "corrected_parity_int": parity_int,
        }

    # ------------------------------------------------------------
    # Full codeword layout for correction search:
    #   codeword_bits[16:0]   = message bits
    #   codeword_bits[31:17]  = parity bits
    # Internally stored as:
    #   codeword_bits[0]   = message LSB
    #   codeword_bits[16]  = message MSB
    #   codeword_bits[17]  = parity LSB
    #   codeword_bits[31]  = parity MSB
    # ------------------------------------------------------------
    codeword_bits = message_bits + parity_bits

    def split_codeword(bits32):
        msg_bits = bits32[:17]
        par_bits = bits32[17:]
        return msg_bits, par_bits

    def compute_syndrome(bits32):
        msg_bits, par_bits = split_codeword(bits32)
        par_calc = compute_parity_bits(msg_bits)
        return [par_bits[i] ^ par_calc[i] for i in range(15)]

    # ------------------------------------------------------------
    # Try all 1-bit, 2-bit, and 3-bit error patterns
    # ------------------------------------------------------------
    for weight in (1, 2, 3):
        for positions in combinations(range(32), weight):
            trial_bits = codeword_bits[:]
            for pos in positions:
                trial_bits[pos] ^= 1

            if compute_syndrome(trial_bits) == [0] * 15:
                corrected_message_bits, corrected_parity_bits = split_codeword(trial_bits)

                return {
                    "error_status": f"corrected_{weight}_bit_error",
                    "corrected_message_int": bits_to_int(corrected_message_bits),
                    "corrected_parity_int": bits_to_int(corrected_parity_bits),
                }

    # ------------------------------------------------------------
    # If no 1/2/3-bit correction is found, treat as uncorrectable
    # ------------------------------------------------------------
    return {
        "error_status": "uncorrectable_error",
        "corrected_message_int": message_int,
        "corrected_parity_int": parity_int,
    }


# --- Example Usage ---
# if __name__ == "__main__":
#     # Example received values
#     rx_message = 0x12345
#     rx_parity = 0x1234

#     result = eFuse_decoder(rx_message, rx_parity)

#     print(f"Error Status:          {result['error_status']}")
#     print(f"Corrected Message Int: {result['corrected_message_int']}")
#     print(f"Corrected Parity Int:  {result['corrected_parity_int']}")