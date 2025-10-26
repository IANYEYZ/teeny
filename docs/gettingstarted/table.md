# Table

Table is very flexible and strong in teeny.

## Basic Usage

Use `[]` to construct a table, for example:
`[1, 2, 3, key: "value"]`
The `key: "value"` part creates a `key-value pair`, it's basically how dictionary in python works, but it supports ALL data types in teeny to be the key, code such as: `[1, 2, 3, [1, 2]: [1, 2, 3]]` totally works!

## Structural assignment

It's technically not a table feature, rather a syntactic sugar. Sometimes you might want to unpack a table to different variables, like this:
```teeny
a := [1, 2];
b := a[0];
c := a[1];
```
But it's tedious to do, so structural assignment is born:
```teeny
a := [1, 2];
[b, c] := a;
```
It's also possible to do more complex structural assignment:
```teeny
a := [1, [2, 3]];
[b, [c, d]] := a;
```
This is also possible to be used in for loops, more on that later