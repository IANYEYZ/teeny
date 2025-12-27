# Basic Concept

## Before anything

Teeny takes great inspiration from Lua, Python and some other languages, so it's common to see similar concepts you might already know, but it's still greatly suggested that you should read the whole tutorial carefully, since Teeny might treat some specific cases different then you might expect.

## Expressions

Teeny treat everything as expressions, and that includes `if`, `for`, etc., basically everything that might be a statement in other programming languages is an expression here.

Teeny always try to find the longest expression possible, for example:
```teeny
a = 1
[1]
```
This looks like two expressions, but actually it's interpreted as:
```teeny
a = 1[1] // Wrong!
```
Which raises an error. Fortuanately, a semicolon marks an end for an expression, that means the following code works:
```teeny
a = 1; // Correct!
[1]
```

## Data types

There're 5 data types in Teeny: Number, String, Table, Nil and Closure

They probably work as you expect, but here're some reminders:
1. Number is used for both integer and floating number, teeny doesn't make a difference between them
2. Boolean technically isn't supported, but you always can rely on 1 for true and 0 for false
3. Table, just like how lua's table work, is much stronger than typical list or dictionary, more on them later
4. Closure is just function, and for the most part, a Closure and a callable Table isn't differenced

The operators in Teeny is fairly normal, beside some strange ones:

1. The assignment and definition operator: Teeny makes a difference between assign a value to a variable and define a variable. The former is done through `=`, and the latter through `:=`