# Week 1: Getting Used to Inputs and Variable Types

Hey guys! This week has some information you will definitely need to know for the future. Starting on the next problem set (which you can find on lucpc.org). I am going to start including some important tips to help you solve the easy problem and sometimes the medium problem too!

## Assigning Multiple Integers in One Line

Sometimes you might want to take multiple numbers as input and assign them to variables in **one line**.  
For example, if the input is: `110 45 23`

You can assign these numbers to variables like this:  
```python
var1, var2, var3 = map(int, input().split())
```

### How it works:
- `input().split()` → Splits the input string into separate pieces using spaces as separators.
- `map(int, …)` → Converts each piece from a string to an integer.
- The numbers are then assigned **in order** to `var1`, `var2`, and `var3`.

## 5 Common Variable Types in Python

1. **int (Integer)** – Whole numbers, positive or negative. Example: `x = 42`
2. **float (Floating Point)** – Numbers with decimals. Example: `pi = 3.14159`
3. **str (String)** – Text inside quotes. Example: `name = "CPC is awesome"`
4. **bool (Boolean)** – True/False values. Example: `is_student = True`
5. **list (List)** – Ordered collection, can store multiple types. Example: `numbers = [1, 2, 3, 4]`

## Practice Tips

- Always remember to convert input to the correct type using `int()`, `float()`, etc.
- Use meaningful variable names to make your code readable
- Test your input parsing with different examples before submitting