# Control Flow

## `if` and `match`

`if` and `match` are two constructs for control flow in teeny

### `if`

`if` in teeny is very similar to `if` in other programming languages
```teeny
a := 2
if a == 1 {
    print("a equals to 1!")
} elif a == 2 {
    print("a equals to 2!")
} else {
    print("a is not either 1 or 2!")
}
```

### `match`

`match` in teeny is very similar to `switch` in other languages, but it's a bit stronger, here's a typical fizzbuzz program:
```teeny
a := 3
match [a % 3, a % 5] {
    [0, 0]: "fizzbuzz",
    [0, _]: "fizz",
    [_, 0]: "buzz",
    _: a
}
```
In a nutshell, `_` matches for anything, and table will compare one item by one item

## `for` and `while`

`for` and `while` are two constructs of loops in teeny. Another way to do loops is through recursion

### `for`

`for` loop through tables, it only 

### `while`