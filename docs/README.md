# **Teeny Programming Language**

Teeny is a small, expression-first programming language designed for quick scripting and rapid prototyping. Its syntax stays tiny and predictable, but it still includes useful features like structural binding, pattern matching, modules, pipeline operators, and backtick-style regex. Everything in Teeny is an expression — blocks, functions, conditionals, and loops all produce values, so code stays compact and consistent.

```teeny
greet := (name) => "Hello, {name}!"

for [i, who] in [[1, "Alice"], [2, "Bob"], [3, "Cat"]] {
    println("{i}: " + greet(who))
}
```

Teeny scripts can be run directly, while compiling to JavaScript and Python is in development. It also interoperates with existing Python code through a simple wrapper.

## **Overview**

Teeny provides multiple ways to achieve common tasks, this is to maximize development speed.

```teeny
People := (name) => {
    self := []
    printName := () => println(name)
    self = [
        greet: () => println("Hello, I'm {name}")
    ]
}

john := People("John")
john.greet()
```

Teeny has a complete builtin library and builtin methods, here’s a small part of it in action — iterating, filtering, and transforming:

```teeny
data := [1, 2, 3, 4, 5]
evenSquares :=
    data
    .filter(x => x % 2 == 0)
    .map(x => x * x)

println(evenSquares)  # [4, 16]
```

## **Teeny's Philosiphy**

Teeny is designed for development speed. In short, if you are worry about if you can still read your code after a year or after a long break - then change a language for this project, Teeny is not suitable.

Teeny is for prototyping - 

## **Features Highlights**

Teeny’s syntax is small and regular. Some key points:

* **Everything is an expression**
  Loops, conditionals, and functions all return values.

* **Structural binding**
  You can unpack tables directly:

  ```teeny
  [a, [b, c]] := [1, [2, 3]]
  ```

* **Pipelines (`|>`)**
  Pass values through chains of transformations:

  ```teeny
  f := x => x * 2; g := x => x * x;
  ```

* **Pattern matching**

  ```teeny
  match x {
      0: "zero",
      [_, _]: "pair",
      _: "other"
  }
  ```

* **Backtick regex**

  ```teeny
  if "123" =~ `\d+` {
      println("digits only")
  }
  ```

## **Installation**

With Python installed, the simplest way to install Teeny is:

```
pip install teeny
```

After installation:

* `teeny` — starts the REPL
* `teeny {file_name}` — runs a Teeny script