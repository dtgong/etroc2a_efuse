def eFuse_encoder(message_int):
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

    if message_int <= 0 or message_int >= (1 << 17):
        raise ValueError("message_int must be a nonzero 17-bit unsigned integer")
    # Bit order:
    #   m_bits[16] = MSB m_bits[0]  = LSB
    m_bits = [0] * 17
    for i in range(17):
        m_bits[i] = (message_int >> i) & 1

    parity_bits = [0] * 15

    # parity = message * P over GF(2)
    # P row 16 corresponds to m_bits[16] (MSB)
    # P row  0 corresponds to m_bits[0]  (LSB)
    for col in range(15):
        bit_sum = 0
        for row in range(17):
            bit_sum ^= m_bits[16 - row] & P[row][col]
        parity_bits[14 - col] = bit_sum

    return m_bits, parity_bits

# --- Example Usage ---
# test_val = 0x12345 
# msg, parity = eFuse_encoder(test_val)

# msg_str = ''.join(str(msg[i]) for i in range(16, -1, -1))
# parity_str = ''.join(str(parity[i]) for i in range(14, -1, -1))

# print(f"Input Message (Int): {test_val}")
# print(f"Message Bits:        {msg_str}")
# print(f"Parity Bits (15-bit):{parity_str}")
# print(f"Full Codeword:       {parity_str}{msg_str}")

