import random

# Generate 10 random numbers between 1 and 100 (adjust range as needed)
random_numbers = [random.randint(1, 100) for _ in range(10)]

# Print the results
print("Generated 10 random numbers:")
for num in random_numbers:
    print(num)