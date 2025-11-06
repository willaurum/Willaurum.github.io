# Week 6: Unpacking Operator (`*`)

**Unpacking Operator in Python (`*` and `**`)**  
- The `*` operator in Python is used for **unpacking iterables** (like lists, tuples, or strings) into separate variables.  
- The `**` operator is used for **unpacking dictionaries** into key-value pairs.  
- These are extremely useful in **input parsing**, **function calls**, and **data manipulation**.

---

## Basic Usage of `*`

```python
numbers = [1, 2, 3, 4]
a, *b = numbers

print(a) # 1
print(b) # [2, 3, 4]
```

- `a` gets the **first** element.
- `*b` collects the **remaining** elements into a list.

---

## Unpacking with Inputs

Often used in competitive programming to simplify input handling:

```python
k, *outlets = map(int, input().split())
print("Power strips:", k)
print("Outlets:", outlets)
```

**Example Input:**
```
3 4 5 6
```

**Output:**
```
Power strips: 3
Outlets: [4, 5, 6]
```

---

## Using `*` in Function Calls

You can use `*` to unpack lists or tuples directly into a function’s arguments:

```python
def add(x, y, z):
    return x + y + z

nums = [1, 2, 3]
print(add(*nums)) # Same as add(1, 2, 3)
```

---

## Using `**` for Dictionaries

The double star `**` unpacks a dictionary into keyword arguments:

```python
def greet(name, age):
    print(f"Hello {name}, you are {age} years old!")

person = {"name": "Jane Doe", "age": 23}
greet(**person)
# Output: Hello Jane Doe, you are 23 years old!
```

---

## Multiple Star Unpacks

You can combine multiple unpacking operators in one expression:

```python
a = [1, 2]
b = [3, 4]
c = [*a, *b]
print(c) # [1, 2, 3, 4]
```

- This merges lists (or tuples) cleanly without loops.

---

## Rule of Thumb

- Use `*` when you want to **capture or expand multiple values**.
- Use `**` when you’re working with **dictionaries or keyword arguments**.

---

## Competitive Programming Uses

- Parsing variable-length input lines.
- Capturing “the rest” of a list.
- Expanding argument lists for cleaner function calls.
- Combining multiple lists into one efficiently.

---

## Quick Example

```python
for _ in range(int(input())):
    k, *o = map(int, input().split())
    print(sum(o) - k + 1)
```

- `k` gets the first number (count of power strips).
- `*o` collects the rest (number of outlets).
- Formula computes total usable outlets.

---

> **Note:** The unpacking operator is incredibly useful. It's simple, powerful, and often used in real-world code and contests.
