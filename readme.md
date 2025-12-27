<p align="center">
  <img src="teenyBanner.png" width="100%" alt="Teeny - A tiny fast prototyping language">
</p>

# Teeny Programming Language

Teeny is a small, expression-first programming language designed for quick scripting and rapid prototyping. Its syntax stays tiny and predictable, but it still includes useful features like structural binding, pattern matching, modules, pipeline operators, and backtick-style regex. Everything in Teeny is an expression — blocks, functions, conditionals, loops — so code stays compact and consistent. The interpreter is simple, hackable, and built to grow slowly as needed, without unnecessary complexity.

## **A tiny example**

```teeny
greet := (name) => "Hello, {name}!"

for [i, who] in [[1, "Alice"], [2, "Bob"], [3, "Cat"]] {
    print("{i}: " + greet(who))
}
```
