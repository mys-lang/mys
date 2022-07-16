Stackless fibers
----------------

Likely limitations/issues:

- Traits. Their memory usage can be calculated based on all classes
  that implements them.

- Recursive calls. New alloc per call, or possibly do not allow
  suspend in recursive calls.

``Fiber.run()`` and ``main()`` are task entry points. They have one
state each. Each state contains all data needed from entry point to
all suspend calls.

Stackful fibers are probably faster than multi level state machine
stackless fibers, and probably similar speed to single level state
machine stackless fibers.

Stackless fibers often use less memory than stackful fibers. It's
certainly true for fibers that use very little stack (much less than a
memory page).

Another option is to calculate the maximum stack usage of each fiber
at compile time and spawn them with stacks of that size. This requires
a user space fiber scheduler.

.. code-block:: mys

   func bar(v: i64) -> i64:
       for _ in range(10):
           v += random()

       return v

   func fum():
       v = 0
       # Call fiber function.
       sleep(2.0)
       v += 1

   func foo(x: i64, y: string) -> string:
       a = x + y
       b = 0

       for ch in y:
           b += bar(a + i64(ch))

       # Call fiber function.
       sleep(1.0)
       fum()

       return str(b)

   func main():
       res = foo()

       raise Exception(res)

Multi level state machine:

.. code-block:: mys

   func bar(v: i64) -> i64:
       for _ in range(10):
           v += random()

       return v

   class Fum:
       _state: i64
       v: i64
       sleep: Sleep

       func next(self) -> bool:
           while True:
               match self._state:
                   case 0:
                       self.v = 0
                       self.sleep = Sleep(2.0)
                       self._state = 1
                   case 1:
                       if self.sleep.next():
                           self._state = 2
                       else:
                           return False
                   case 2:
                       self.v += 1
                   case 3:
                       return True

   class Foo:
       _state: i64
       b: i64
       sleep: Sleep
       fum: Fum

       func next(self) -> bool:
           while True:
               match self._state:
                   case 0:
                       a = x + y
                       self.b = 0

                       for ch in y:
                           self.b += bar(a + i64(ch))

                       self.sleep = Sleep(1.0)
                       self._state = 1
                   case 1:
                       if self.sleep.next():
                           self.sleep = None
                           self.fum = Fum()
                           self._state = 2
                       else:
                           return False
                   case 2:
                       if self.fum.next():
                           self.fum = None
                           self._state = 3
                       else:
                           return False
                   case 3:
                       self.result = str(self.b)
                       self._state = 4
                   case 4:
                       return True

   func main():
       foo = Foo()

       while True:
           if foo.next():
               res = foo.result
               break

       raise Exception(res)

Single level state machine:

.. code-block:: mys

   enum TaskState:
       Init
       FooSleep
       FooFumSleep
       Finished

   class Task:
       state: TaskState
       b: i64
       v: i64

       func __init__(self):
           self.state = TaskState.Init

   func part_1(task: Task):
       a = x + y
       task.b = 0

       for ch in y:
           task.b += bar(a + i64(ch))

       do_sleep(1.0)
       task.state = TaskState.PartSleep

   func part_2(task: Task):
       task.v = 0
       do_sleep(2.0)
       task.state = TaskState.PartFumSleep

   func part_3(task: Task):
       task.v += 1
       task.state = TaskState.Finished

       return str(task.b)

   func main():
       task = Task()
       res = None

       while True:
           match task.state:
               case TaskState.Init:
                   part_1()
               case TaskState.PartSleep:
                   part_2()
               case TaskState.PartFumSleep:
                   res = part_3()
               case TaskState.Finished:
                   break

           reschedule()

       raise Exception(res)
