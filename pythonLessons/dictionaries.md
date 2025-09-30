# Week 2: Dictionaries

This week's easy problem is pretty simple so this week, we'll expand on **Python dictionaries**, a powerful data structure for storing and managing key-value pairs. You'll learn how to create dictionaries, update them, and use them for tasks like categorizing, counting, and looking up values efficiently. We'll also review important operators (`+=`, `-=`, `==`) and how they're used with dictionaries.

## Creating and Accessing Dictionaries

```python
dictionary = {
    'key': 'value'
}

print(dictionary['key'])
# Output: value
```

- Dictionaries store data as **key-value pairs**.
- You can access values by referencing their keys.

## Adding New Key-Value Pairs

```python
dictionary['newKey'] = 'aNewValue'

# Dictionary now looks like this:
dictionary = {
    'key': 'value',
    'newKey': 'aNewValue'
}
```

- Assigning a value to a new key adds it to the dictionary.

## Use Cases for Dictionaries

### Categorizing items

```python
fruits = ['apple', 'banana', 'orange', 'apple', 'banana']
categories = {}
for fruit in fruits:
    if fruit not in categories:
        categories[fruit] = []
    categories[fruit].append(fruit)
print("Categorized:", categories)
# Output: {'apple': ['apple', 'apple'], 'banana': ['banana', 'banana'], 'orange': ['orange']}
```

### Counting items

```python
counts = {}
for fruit in fruits:
    counts[fruit] = counts.get(fruit, 0) + 1
print("Counts:", counts)
# Output: {'apple': 2, 'banana': 2, 'orange': 1}
```

### Fast index lookups

```python
student_grades = {'Alice': 90,
                  'Bob': 85,
                  'Charlie': 92}
print("Alice's grade:", student_grades['Alice'])
# Output: Alice's grade: 90
```

## Important Operators with Dictionaries

### `+=` (increment/accumulate)

- Adds a value to the existing one.
- Commonly used for counters or scores.

```python
score = {'Will': 5}
score['Will'] += 1
print(score['Will'])  
# Output: 6
```

### `-=` (decrement)

- Subtracts a value from the existing one.
- Useful for reducing counts, such as lives or resources.

```python
inventory = {'arrows': 10}
inventory['arrows'] -= 2
print(inventory['arrows'])  
# Output: 8
```

### `==` (equality comparison)

- Checks if two values are the same.
- Useful in conditionals when comparing dictionary values.

```python
grades = {'Alice': 90}
if grades['Alice'] == 90:
    print("Alice scored exactly 90!")
# Output: Alice scored exactly 90!
```

## Club Example From Thursday: Updating Scores

```python
score = {
    'Colter': 5,
    'Will Eves': 8,
    'Will Cook': 2
}

name = input()

if name in score:
    score[name] += 1
else:
    score[name] = 1

print(score[name])
```

- Checks if a name exists in the dictionary.
- If it does, increases the score by 1 (`+= 1`).
- If not, adds the name with a starting score of 1.

## Printing Dictionaries Neatly

```python
for key, value in score.items():
    print(key, value)
```

- Loops through all items in the dictionary.
- Prints each key with its value in an easy-to-read format.