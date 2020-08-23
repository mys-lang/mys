import threading
from queue import Queue
import mys


class EchoThread(threading.Thread):

    def __init__(self, queue: mys.Queue[(int, str)]):
        super().__init__()
        self._qin: mys.Queue[(int, str)] = Queue()
        self._qout = queue

    def put(self, message: (int, str)):
        self._qin.put(message)

    def run(self):
        while True:
            message = self._qin.get()

            if message[0] == -1:
                print(message[1])
                break
            else:
                print('Echo thread got:', message)
                self._qout.put(message)


def main():
    queue: mys.Queue[(int, str)] = Queue()
    echo_thread = EchoThread(queue)
    echo_thread.start()

    echo_thread.put((1, 'The first message!'))
    print('Got:', queue.get())

    echo_thread.put((2, 'Another message!'))
    print('Got:', queue.get())

    echo_thread.put((-1, 'Program done!'))
