# Week 4: Eval

**`eval()` in Python**
- **`eval()`** = *evaluate expression* → executes a string as a Python expression.
- Returns the **result** of the evaluated expression.
- Useful for **dynamic expressions**, **user input evaluation**, or **on-the-fly calculations**.

## Basic Usage

```python
x = 5
expression = "x * 10 + 3"
result = eval(expression)   # evaluates to 53
print(result)               # 53
```

## Examples

```python
eval("2 + 3 * 4")          # 14
eval("min(10, 3, 7)")      # 3
eval("'hello'.upper()")    # 'HELLO'
```

## Competitive Programming / Practical Uses

- Quick evaluation of **math expressions** in strings.
- Debugging or **testing small snippets** dynamically.
- Transforming **input-based formulas** into results.

## Rule of Thumb

Only use `eval()` if:
- Input is **controlled** or **sanitized**.
- You specifically need to evaluate expressions at runtime.  
Otherwise, prefer alternatives (`int()`, `float()`, `ast.literal_eval()`).

## Tips

- Combine `eval()` with **dictionaries** for controlled variables:

```python
variables = {"a": 2, "b": 3}
eval("a**b + b", {"__builtins__": None}, variables)  # 11
```

- Avoid using `eval()` with **raw user input** from the internet or untrusted sources.
- Use `eval()` for **quick scripting** during contests or experiments, but sanitize for production code.
