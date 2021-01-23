Notable differences to Python
-----------------------------

Mys looks a lot like Python, but there are differences. Below is a
list of the most notable differences that we could think of.

- Traits instead of classic inheritence.

- Statically typed.

- Bytes are mutable.

- Integers are bound (i32, u32, i64, ...).

- Iterators/generators do not (yet?) exist.

- Rust-like generic functions and classes.

- Only packages. No stand alone modules.

- Compiled to machine code. No interpreter.

- Data races and memory corruption possible, but unlikely.

- No async.

- Only ``from ... import ...`` is allowed. ``import ...`` is not.

- Only functions, enums, traits, classes and variables can be
  imported, not modules.

- Ruby-like built in regular expressions.
