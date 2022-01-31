Stackless fibers
----------------

Or possibly calculate maximum stack usage at compile time.

- Callbacks. Their memory usage can be calculated.

- Recursive calls. New alloc per call.

``Fiber.run()`` and ``main()`` are task entry points. They have one
state each. Each state contains all data needed from entry point to
all suspend points.

.. code-block:: mys

   def bar(v: i64) -> i64:
       for _ in range(10):
           v += random()

       return v

   def fum():
       v = 0
       # Call fiber function.
       sleep(2.0)
       v += 1

   def foo(x: i64, y: string) -> string:
       a = x + y
       b = 0

       for ch in y:
           b += bar(a + i64(i32(ch)))

       # Call fiber function.
       sleep(1.0)
       fum()

       return str(b)

   def main():
       res = foo()

       raise Exception(res)

   @enum
   class TaskState:
       Init
       FooSleep
       FooFumSleep
       Finished

   class Task:
       state: TaskState
       b: i64
       v: i64

       def __init__(self):
           self.state = TaskState.Init

   def part_1(task: Task):
       a = x + y
       task.b = 0

       for ch in y:
           task.b += bar(a + i64(i32(ch)))

       do_sleep(1.0)
       task.state = TaskState.PartSleep

   def part_2(task: Task):
       task.v = 0
       do_sleep(2.0)
       task.state = TaskState.PartFumSleep

   def part_3(task: Task):
       task.v += 1
       task.state = TaskState.Finished

       return str(task.b)

   def main():
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
