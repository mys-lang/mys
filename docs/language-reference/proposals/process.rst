Process
-------

To utilize more than one CPU core.

An example that creates a process and communicates with it using a
queue:

.. code-block:: mys

   from process import Process
   from process import Queue

   class MyProcess(Process):
       x: i64
       y: i64
       queue: Queue[i64]

       def run(self):
           self.queue.put(self.x + self.y)

   def main():
       queue = Queue[i64]()
       proc = MyProcess(1, 2, queue)
       proc.start()
       proc.join()
       print(queue.get())

An example that creates a process function pool and calls "functions"
in it. All "functions" must have the same return type:

.. code-block:: mys

   from process import FunPool
   from process import Fun
   from process import call

   class Add(Fun[i64]):
       a: i64
       b: i64

       def call(self) -> i64:
           return self.a + self.b

   def main():
       pool = FunPool[i64](5)
       assert pool.call(Add(1, 2)) == 3
       assert pool.call([Add(5, 6), Add(7, 8)]) == [11, 15]
       function = pool.call_no_wait(Add(3, 4))
       assert function.result() == 7
       assert call(Add(8, 9)) == 17

An example that creates a process job pool and runs jobs in it:

.. code-block:: mys

   from process import JobPool
   from process import Job
   from process import run

   class Add(Job):
       a: i64
       b: i64

       def run(self) -> bool:
           print(self.a + self.b)

           return True

   def main():
       pool = JobPool(5)
       assert pool.run(Add(1, 2))
       assert pool.run([Add(5, 6), Add(7, 8)]) == [True, True]
       job = pool.run_no_wait(Add(3, 4))
       assert job.wait()
       assert run(Add(10, 11))
