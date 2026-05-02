# **String & Regex**

## **String**

Strings in Teeny are quite flexible and come with a wide range of built-in methods to make manipulation easy. Strings can be defined using single or double quotes:

```teeny
str1 := "Hello, World!"
str2 := 'Teeny'
```

### **Indexing a String**

Indexing in Teeny is much more powerful then indexing in other programming languages

1. Indexing with Number:
   This is the most common index:
   ```teeny
   "abcde"[0] # a
   ```
2. Indexing with Table:
   This takes every value in it, indexing with them, and concat the return value together
   ```teeny
   "abcde"[1..3] # "ab"
   ```
3. Indexing with another String:
   If the given string is founded as a substring, the result is the original string, otherwise Nil
4. Indexing with Regex
   Return the first match if exist, otherwise Nil

### **String Methods**

Teeny provides several built-in methods for strings:

* **Length**: Get the length of a string:
  ```teeny
  "Hello".len()  # 5
  ```

* **Uppercase & Lowercase**: Convert the string to upper or lowercase:
  ```teeny
  "hello".upper()  # "HELLO"
  "WORLD".lower()  # "world"
  ```

* **Trim**: Remove whitespace from the start and end of a string:
  ```teeny
  "  hello  ".trim()  # "hello"
  ```

* **Replace**: Replace part of the string with another string, the first argument can be a Regex:
  ```teeny
  "hello world".replace("world", "Teeny")  # "hello Teeny"
  ```

* **Substring**: Extract a substring from a string:
  ```teeny
  "hello world".sub(0, 5)  # "hello"
  ```

* **Split**: Split a string into a table based on a delimiter:
  ```teeny
  "apple,banana,orange".split(",")  # ["apple", "banana", "orange"]
  ```

* **Join**: Join a table of strings into a single string with a delimiter:
  ```teeny
  ["apple", "banana", "orange"].join(",")  # "apple,banana,orange"
  ```

* **Find**: Find the index of a substring within a string:
  ```teeny
  "hello world".find("world")  # 6
  ```

### **String Interpolation**

Teeny also supports **string interpolation** (embed variables inside strings):

```teeny
name := "Alice"
greeting := "Hello, {name}!"  # "Hello, Alice!"
```

The `{}` syntax allows you to insert any expression inside the string, just like in any other programming language.

---

## **Regex**

Teeny’s support for regular expressions uses **backtick** syntax for regex patterns:

```teeny
pattern := `\d+`  # matches one or more digits
```

Teeny uses `=~` for matching string and regex:

```teeny
"123" =~ `\d+` # truthy
"abc" =~ `\d+` # falsy
```

Some of string methods allow passing in Regex, like so:

```teeny
"abc123xyz".find(`\d+`)  # 3 (index of first match)
"abc123xyz".replace(`\d+`, "456")  # "abc456xyz"
```