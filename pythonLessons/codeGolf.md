# Bonus Lesson: Code Golf Techniques

**Code Golf** is writing code that solves a problem using **as few characters as possible**.  
It’s a fun way to master Python’s syntax and learn shortcuts.

---

## What Is Code Golf?

- The goal: **Shortest working solution**, not really readability.  
- Common in **competitive programming** and **online challenges**.  
- It helps improve efficiency and creativity by looking at less-known Python features.
- You probably even use some of these already!

---

## Common Code Golf Tricks

### 1. Use Short Variable Names

```python
for i in range(3):print(i)
```
Instead of:
```python
for index in range(3):
    print(index)
```
Shorter variables save characters and time.

---

### 2. Skip Unnecessary Whitespace

Python doesn’t need spaces after `,` or `=` unless it affects readability.

```python
a,b=map(int,input().split())
```

---

### 3. Use List Comprehensions or Generators

Replace loops with one-liners:

```python
print(sum(int(x)for x in input().split()))
```

Instead of:
```python
s=0
for x in input().split():s+=int(x)
print(s)
```

---

### 4. Inline Logic with Ternary Operators

```python
print("Yes"if x>0 else"No")
```

---

### 5. Exploit Built-ins

Python’s built-in functions often replace longer logic:

| Task | Long Version | Golfed Version |
|------|---------------|----------------|
| Sum | `s=0;for i in g:s+=i` | `sum(g)` |
| Sort | `l.sort();print(l)` | `print(sorted(l))` |
| Find Max | `m=max(l)` | `max(l)` |

---


### 6. Use String Tricks

```python
print("".join(sorted(input())))
```

- `"".join()` concatenates efficiently.
- `sorted()` returns a sorted list of characters.

---

### 7. Use `*` for Unpacking

```python
a,*b=map(int,input().split())
print(sum(b)-a+1)
```

Saves extra indexing and loops.

---

### 8. Avoid Temporary Variables

```python
print((lambda a,b:a+b)(*map(int,input().split())))
```

Anonymous functions can pack logic into one call.

---

## Code Golf Mindset

- Think in **patterns**: “Can I do this in one expression?”  
- Master **built-ins**: `map`, `sum`, `max`, `min`, `any`, `all`, etc.  

---

## When *Not* to Use Code Golf

- Never in **production code** because it sacrifices readability.  
- Best used for **contests**, **fun**, or **personal challenges**.

---
