# Closure

Closure is essentially function in other programming languages

## Constructing a closure

It's easy to construct a closure:
```teeny
fn (a, b) a + b

fn (a, b, c) {
    [a, b, c]
}

(x, y) => x + y
```
Since a closure doesn't have name, Teeny uses `this` to refer to the closure itself(for recursion), like this:
```teeny
fib = fn (a) match a {
    1: 1,
    2: 1,
    _: this(a - 1) + this(a - 2)
}
```