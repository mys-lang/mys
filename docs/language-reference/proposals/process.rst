Process
-------

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
