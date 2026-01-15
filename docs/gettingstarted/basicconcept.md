# **Basic Concept**

## Before Anything

Teeny takes inspiration from **Lua, Python, and other expressive languages**. You’ll see familiar ideas if you know them, but Teeny has its own rules and expectations — so it’s recommended to read this tutorial carefully, even if some parts look familiar.

## Expressions Everywhere

In Teeny, **everything is an expression**.
That means constructs you may think of as “statements” in other languages — such as `if`, `for`, and code blocks — are all expressions with values.

Teeny always tries to parse the **longest valid expression** from the current position.

For example:

```teeny
a = 1
[1]
```

At first glance this seems like two separate lines — but without a semicolon, Teeny reads it like:

```teeny
a = 1[1]  # tries to index literal 1 — error!
```

To break expressions cleanly, use a semicolon (`;`):

```teeny
a = 1;   # now the expression ends
[1]      # this is a separate expression
```

## Data Types

Teeny currently has **five core data types**:

* **Number** — numeric values (floating-point; integers are just special cases)
* **String** — sequences of text
* **Table** — flexible collections (like Lua’s tables; can act as lists, dictionaries, objects, etc.)
* **Nil** — absence of value
* **Closure** — functions

Some notes on these:

1. **Number** covers both integers and floating point — there is no separate integer type.
2. **Boolean** is *not* a separate type — instead, truthiness is derived from values (see below).
3. **Table** is a powerful, mutable structure — more than just a list or dictionary. We’ll cover more on tables later.
4. **Closure** represents functions; a callable table can behave like a function too.

### Truthiness

Teeny doesn’t have a built-in Boolean type. Instead:

* **Falsy values:** `0`, `""` (empty string), ``` `` ``` (empty regex) , `[]` (empty table), and `nil`
* **Truthy values:** everything else

This means you can write:

```teeny
if x {
    println("x is truthy")
}
```

with the same intuitive meaning as in languages with booleans.

## Operators

Most operators in Teeny will feel familiar:

```
+  -  *  /  %   &&  ||  ==  !=  <=  >=  <  >
```

But there are some special ones you’ll see later:

* `??` — nil coalescing

  ```teeny
  a ?? b  # if a isn’t nil then a, else b
  ```
* `?:` — truthy coalescing

  ```teeny
  a ?: b  # if a is truthy then a, else b
  ```
* `=~` — regex match

  ```teeny
  "123" =~ `\d+`  # returns 1 if match, else 0
  ```
* `|>` — pipeline operator. It's worth its own part, more on it later

  ```teeny
  x |> f |> g
  ```

## Assignment & Definition

Teeny makes a no distinction between **defining** a new variable and **assigning** to an existing variable:

**Define a or Assign to a variable:**

  ```teeny
  name = "Bob"
  ```

  If `name` already exists in some outer scope(possibly current scope), this changes its value. Otherwise, it creates a new variable called `name`. It's also possible(at least up till now) but really not suggested to use `:=`:

  ```teeny
  name := "Bob"
  ```

  This is for the reason of backward compatibility, and could be removed in any version onward. It's also suggested to change all `:=` to `=` in exisiting projects

That covers the core ideas you’ll need to start writing basic Teeny code.
Next up: **Tables**
