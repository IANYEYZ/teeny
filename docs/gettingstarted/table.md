# **Table**

Tables are one of the most flexible and powerful types in Teeny.
They act as arrays, dictionaries (maps), objects, or any combination of these — all in one structure.

## **Constructing Tables**

Use square brackets `[]` to create a table:

```teeny
t := [1, 2, 3, key: "value"]
```

* Elements without keys are stored sequentially (like a list).
* Elements with `key: value` are stored by key (like a dictionary).
* Only numbers, strings or regex can be key.

## **Structural Assignment**

Sometimes you might want to unpack a table into variables.
Instead of assigning each element manually:

```teeny
a := [1, 2]
b := a[0]
c := a[1]
```

You can use structural assignment:

```teeny
a := [1, 2]
[b, c] := a
```

This assigns:

* `b = 1`
* `c = 2`

Structural assignment can match nested tables:

```teeny
a := [1, [2, 3]]
[b, [c, d]] := a
```

Here:

* `b = 1`
* `c = 2`
* `d = 3`

Structural assignment also works in `for` loops to destructure table elements, this will be covered later.

It can also be more complex

```teeny
[data: a, config, c] := [
    "Some other stuff",
    config: "Some super cool config",
    data: [
        "Some super important data"
    ]
]
```

Here:

- `a = [ "Some super important data" ]`
- `config = "Some super cool config"`
- `c = "Some other stuff"`

Basically:

- If the left part has a key-value pair: find the same key in the right part, if doesn't exist, raise an Error
- If the left part only has a name, first try find the exact same name as key in the right part, if doesn't exist, pull out the next available numeric-key value(i.e. the one created without any key before it), if also doesn't exist, raise an Error

## **Table Methods**

Tables come with many useful builtin methods. These methods can be called using the dot syntax:

```teeny
t.push(4)     # append a value
t.keys()      # return a list of keys
t.values()    # return a list of values
```

Below is a summary of available table methods:

### Basic Operations

| Method        | Description                                                    |
| ------------- | -----------------------------------                            |
| `push!(value)` | Append `value` to the table                                    |
| `pop!(index)` | Pop the value at `index`                                   |
| `keys()`      | Get a table of all keys                                         |
| `values()`    | Get a table of all values                                       |
| `enumerate()` | Get a table, each key is [index, value], only numeric index     |
| `pairs()`     | Get a table, each key is [index, value], only non-numeric index            |
| `has?(key)`    | Check if `key` exists in table                                 |

### Aggregation & Statistics

These return new tables with results:

| Method       | Description                          |
| ------------ | ------------------------------------ |
| `sum()`      | Return the sum of all values         |
| `mean()`     | Return the average of all values     |
| `median()`   | Return the median                    |
| `stdev()`    | Return the standard deviation        |
| `describe()` | Return a summary of statistics       |

Examples:

```teeny
nums := [1, 2, 3, 4]
println(nums.sum())      # 10
println(nums.mean())     # 2.5
```

### Transformations

| Method       | Description                                                  |
| ------------ | ------------------------------------------------------------ |
| `map(fn)`    | Return a new table by applying `fn` to each element          |
| `filter(fn)` | Return a new table of elements where `fn(element)` is truthy |
| `reduce(fn, initial)` | for every value in table, let initial be fn(initial, value), return the final value |
| `sort()`     | Sort table values in place                                   |
| `shuffle()`     | Shuffle table values in place                                   |

Examples:

```teeny
nums := [3, 1, 2]
sorted := nums.sort()
println(sorted)    # [1, 2, 3]

# doubling all values
doubled := nums.map(x => x * 2)
println(doubled)   # [2, 4, 6]
```

### Size & Slicing

| Method      | Description                                                                         |
| ----------- | ----------------------------------------------------------------------------------- |
| `len()`     | Return the number of elements                                                       |
| `sub(i, j)` | Return a slice from index `i` to `j`, inclusive on both side                        |

Examples:

```teeny
data := [10, 20, 30, 40]
println(data.len())      # 4
println(data.sub(1, 3))   # [20, 30, 40]
```