# Week 5: Math

This week, we'll focus on **math operations in Python**, covering built-in math functions and useful tools from the `math` library. You'll learn how to perform calculations, work with powers and roots, and use constants like π and e. We'll also explore how math integrates into problem-solving scenarios like calculating distances, averages, and probabilities.

## Basic Arithmetic
### Just for some review, here some some basic math operations

```python
a = 10
b = 3

print(a + b)  # Addition
print(a - b)  # Subtraction
print(a * b)  # Multiplication
print(a / b)  # Division (float)
print(a // b) # Floor division
print(a % b)  # Modulus (remainder)
print(a ** b) # Exponentiation
```

- Python supports all standard arithmetic operations.
- `//` gives the integer result, `%` gives the remainder.

## Built-in Math Functions

```python
print(abs(-7))    # Absolute value → 7
print(round(3.14159, 2))  # Round to 2 decimals → 3.14
print(pow(2, 5))  # Power (same as 2**5) → 32
```

- `abs()` handles negatives.
- `round()` controls decimal precision.
- `pow()` is another way to do exponentiation.

## Using the `math` Module
```python
import math
```

### The following are tons of different use cases for `math` in Competitve Programming

In competitive programming, the `math` module provides many useful helpers that save implementation time. Below are the most common ones with short explanations.

## Basic Operations
```python
import math

math.ceil(x)   # Smallest integer >= x
math.floor(x)  # Largest integer <= x
math.trunc(x)  # Truncate towards zero
```

## GCD and LCM
```python
math.gcd(a, b)  # Greatest common divisor
math.lcm(a, b)  # Least common multiple (Python 3.9+)
```

## Factorials, Combinations, and Permutations
```python
math.factorial(n)   # n!
math.comb(n, k)     # Binomial coefficient C(n, k) (Python 3.8+)
math.perm(n, k)     # Permutations (Python 3.8+)
```

## Roots, Powers, and Logs
```python
math.sqrt(x)     # Square root
math.isqrt(x)    # Integer square root (avoids float issues)
math.pow(x, y)   # Floating-point exponentiation (use ** for ints)
math.log(x, base)  # Logarithm with optional base
math.log2(x)     # Base-2 logarithm
math.log10(x)    # Base-10 logarithm
```

## Trigonometry (used in geometry problems)
```python
math.sin(x)      # Sine (x in radians)
math.cos(x)      # Cosine (x in radians)
math.tan(x)      # Tangent (x in radians)
math.asin(x)     # Arc sine
math.acos(x)     # Arc cosine
math.atan(x)     # Arc tangent
math.atan2(y, x) # Angle from x-axis, safer than atan(y/x)
math.radians(x)  # Degrees → Radians
math.degrees(x)  # Radians → Degrees
```

## Constants
```python
math.pi  # π (3.14159...)
math.e   # Euler's number (2.718...)
```

## Miscellaneous
```python
math.hypot(x, y)          # sqrt(x^2 + y^2), useful for distances
math.isclose(a, b)        # Floating-point comparison
```


- `math` provides advanced functions and constants.
- Always `import math` before using it.

## Common Use Cases

### Distance Formula

```python
import math

x1, y1 = (0, 0)
x2, y2 = (3, 4)

distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
print("Distance:", distance)
# Output: Distance: 5.0
```

- Uses Pythagoras’ theorem to find the distance between two points.

### Average Calculation

```python
numbers = [2, 4, 6, 8]
average = sum(numbers) / len(numbers)
print("Average:", average)
# Output: Average: 5.0
```

- Combines `sum()` and `len()` for efficiency.

### Probability Example

```python
favorable = 3
total = 10
probability = favorable / total
print("Probability:", probability)
# Output: Probability: 0.3
```

- Simple probability = favorable outcomes ÷ total outcomes.

