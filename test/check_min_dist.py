def check_weight_distribution():
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

    # Initialize a list to store counts for weights 0 through 32
    # weight_counts[8] will hold the number of codewords with weight 8
    weight_counts = [0] * 33

    print("Analyzing all nonzero codewords...")

    # Loop through ALL messages (1 to 2^17 - 1)
    for i in range(1, 2**17):
        message = [int(bit) for bit in format(i, '017b')]
        
        # Calculate parity bits
        parity_bits = []
        for j in range(15):
            column_sum = 0
            for row_idx in range(17):
                column_sum ^= (message[row_idx] & P[row_idx][j])
            parity_bits.append(column_sum)
            
        current_weight = sum(message) + sum(parity_bits)
        
        # Increment the counter for this specific weight
        weight_counts[current_weight] += 1

    # Print the Statistics Table
    print("\nWeight Distribution (Statistics):")
    print("-" * 30)
    print("Weight | Number of Codewords")
    print("-" * 30)
    for w, count in enumerate(weight_counts):
        if count > 0: # Only print weights that actually occur
            print(f"{w:6} | {count:19,}")
    print("-" * 30)
    print(f"Total  | {sum(weight_counts):19,}")

check_weight_distribution()