Regular Expressions
-------------------

Regular expressions are part of the language. The string type has
methods that takes regular expressions, for example ``match()``,
``split()`` and ``replace()``.

An example
^^^^^^^^^^

.. code-block:: mys

   def main():
       # Match.
       mo = "I am 6 years old.".match(re"(\d+) years")
       print("mo:         ", mo)
       print("mo.group(1):", mo.group(1))

       # Split.
       print("split():    ", "I have 15 apples and 3 bananas.".split(re"\d+"))

       # Case-insensitive replace.
       print("replace():  ", "I want more AppLEs.".replace(re"apples"i, "bananas"))

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   mo:          RegexMatch(span=(5, 12), match="6 years")
   mo.group(1): 6
   split():     ["I have ", " apples and ", " bananas."]
   replace():   I want more bananas.
