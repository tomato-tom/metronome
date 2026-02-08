import sys

args = sys.argv
k, n = int(args[1]), int(args[2])
if k > n or k < 0:
    print(f"Error: E({k}, {n})")
    exit(1)

groups = [[1]] * k + [[0]] * (n - k)

while True:
    left_count, right_count, found = 0, 0, False
    
    for i in range(len(groups) - 1):
        if groups[i] != groups[i + 1]:
            left_count = i + 1
            right_count = len(groups) - left_count
            found = True
            break
    
    if not found or right_count <= 1:
        break
    
    pairs = min(left_count, right_count)
    new_groups = []
    
    for i in range(pairs):
        new_groups.append(groups[i] + groups[left_count + i])
    for i in range(pairs, left_count):
        new_groups.append(groups[i])
    for i in range(left_count + pairs, len(groups)):
        new_groups.append(groups[i])
    
    groups = new_groups

result = ''.join(str(bit) for group in groups for bit in group)
print(f"E({k}, {n}): [{result}]")

