import subprocess
import sys
import time

import yaspin
from colors import green
from colors import red
from humanfriendly import format_timespan


def duration_start():
    return time.time()


def duration_stop(start_time):
    end_time = time.time()
    duration = format_timespan(end_time - start_time)

    return f' ({duration})'


SPINNER = [
    ' ⠋', ' ⠙', ' ⠹', ' ⠸', ' ⠼', ' ⠴', ' ⠦', ' ⠧', ' ⠇', ' ⠏'
]


def format_result_ok(message):
    return green(' ✔ ') + message


def format_result_fail(message):
    return red(' ✘ ') + message


def format_result(ok, message):
    if ok:
        return format_result_ok(message)
    else:
        return format_result_fail(message)


class _Spinner(yaspin.api.Yaspin):

    def __init__(self, text):
        super().__init__(yaspin.Spinner(SPINNER, 80), text=text, color='yellow')
        self._start_time = duration_start()

    def __exit__(self, exc_type, exc_val, traceback):
        duration = duration_stop(self._start_time)
        self.write(format_result(exc_type is None, self.text + duration))

        return super().__exit__(exc_type, exc_val, traceback)


class Spinner:

    def __init__(self, text):
        self._text = text
        self._start_time = duration_start()

        if sys.stdout.isatty():
            self._spinner = _Spinner(text)
        else:
            self._spinner = None

    @property
    def text(self):
        raise NotImplementedError()

    @text.setter
    def text(self, text):
        if self._spinner is not None:
            self._spinner.text = text

    def __enter__(self):
        if self._spinner is None:
            return self
        else:
            return self._spinner.__enter__()

    def __exit__(self, exc_type, exc_val, traceback):
        duration = duration_stop(self._start_time)

        if self._spinner is None:
            print(format_result(exc_type is None, self._text + duration), flush=True)
        else:
            return self._spinner.__exit__(exc_type, exc_val, traceback)


def update_spinner_status(spinner, status_path):
    try:
        messages = []

        with open(status_path) as fin:
            for line in fin:
                line = line.strip()

                if line[0] == '>':
                    messages.append(line[2:])
                else:
                    messages.remove(line[2:])

        if len(messages) == 1:
            spinner.text = messages[-1]
        else:
            spinner.text = f'{messages[-1]} ({len(messages)} ongoing)'
    except Exception:
        pass


def run_with_spinner(command, message, env=None, status_path=None):
    output = ''

    try:
        with Spinner(text=message) as spinner:
            with subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  encoding='utf-8',
                                  close_fds=False,
                                  env=env) as proc:

                while proc.poll() is None:
                    if status_path is not None:
                        update_spinner_status(spinner, status_path)

                    time.sleep(0.1)

                spinner.text = message
                output = proc.stdout.read()

                if proc.returncode != 0:
                    raise Exception(f'command failed with {proc.returncode}')
    except Exception:
        lines = []

        for line in output.splitlines():
            if 'make: *** ' in line:
                continue

            lines.append(line)

        raise Exception('\n'.join(lines).rstrip())

    return output


def run(command, message, verbose, env=None, status_path=None):
    if verbose:
        start_time = duration_start()

        try:
            print('Command:', ' '.join(command))

            with subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  encoding='utf-8',
                                  close_fds=False,
                                  env=env) as proc:
                output = []

                while proc.poll() is None:
                    text = proc.stdout.readline()
                    print(text, end="")
                    output.append(text)

                print(proc.stdout.read(), end="")

                if proc.returncode != 0:
                    raise Exception(f'command failed with {proc.returncode}')

            output = ''.join(output)
            print(format_result_ok(message + duration_stop(start_time)), flush=True)
        except Exception:
            print(format_result_fail(message + duration_stop(start_time)), flush=True)
            raise
    else:
        output = run_with_spinner(command, message, env, status_path)

    return output
