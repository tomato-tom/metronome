import sys

# Euclidean rhythm generator using Bjorklund's algorithm
# Usage: python euclidean.py k n [--raw]
#   k: number of onsets (1s)
#   n: total number of pulses
#   --raw: output only the rhythm pattern without labels

args = sys.argv

# Check if raw output option is requested
raw_output = False
if "--raw" in args:
    raw_output = True
    args = [arg for arg in args if arg != "--raw"]

# Validate arguments
if len(args) < 3:
    print("Usage: python euclidean.py k n [--raw]")
    exit(1)

k, n = int(args[1]), int(args[2])

# Validate input values
if k > n or k < 0:
    print(f"Error: E({k}, {n})")
    exit(1)

# Initialize groups: k groups of [1] and (n-k) groups of [0]
groups = [[1]] * k + [[0]] * (n - k)

# Main Bjorklund algorithm loop
while True:
    left_count, right_count, found = 0, 0, False
    
    # Find the first boundary between different elements
    for i in range(len(groups) - 1):
        if groups[i] != groups[i + 1]:
            left_count = i + 1
            right_count = len(groups) - left_count
            found = True
            break
    
    # Termination condition: no boundary found or right side too small
    if not found or right_count <= 1:
        break
    
    # Create pairs from left and right sides
    pairs = min(left_count, right_count)
    new_groups = []
    
    # Combine left and right elements into pairs
    for i in range(pairs):
        new_groups.append(groups[i] + groups[left_count + i])
    
    # Add remaining left elements
    for i in range(pairs, left_count):
        new_groups.append(groups[i])
    
    # Add remaining right elements
    for i in range(left_count + pairs, len(groups)):
        new_groups.append(groups[i])
    
    groups = new_groups

# Flatten the nested groups into a single list of bits
bits = []
for group in groups:
    for bit in group:
        bits.append(bit)

# Convert bits to string
result = ''.join(str(bit) for bit in bits)

# Output based on option
if raw_output:
    print(result)
else:
    print(f"E({k}, {n}): [{result}]")
