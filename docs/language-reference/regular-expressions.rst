Regular Expressions
-------------------

Regular expressions are part of the langauge. The string type has has
methods that takes regular expressions, for example ``match()`` and
``split()``.

An example
^^^^^^^^^^

.. code-block:: mys

   def main():
       mo = "I am 6 years old.".match(re"(\d+) years")
       print("mo:         ", mo)
       print("mo.group(1):", mo.group(1))
       print("split():    ", "I have 15 apples and 3 bananas.".split(re"\d+"))
       value = "I want more AppLEs."
       value.replace(re"apples"i, "bananas")
       print("replace():  ", value)

.. code-block:: myscon

   ❯ mys run
    ✔ Reading package configuration (0 seconds)
    ✔ Building (0.01 seconds)
   mo:          RegexMatch(span=(5, 12), match="6 years")
   mo.group(1): 6
   split():     ["I have ", " apples and ", " bananas."]
   replace():   I want more AppLEs.
