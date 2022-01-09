import os
import subprocess
import sys
import time

import yaspin
from colors import green
from colors import red
from humanfriendly import format_timespan


class Duration:

    def __init__(self):
        self.start_time = time.time()

    def stop(self):
        end_time = time.time()
        duration = format_timespan(end_time - self.start_time)

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
        self._duration = Duration()

    def __exit__(self, exc_type, exc_val, traceback):
        duration = self._duration.stop()
        self.write(format_result(exc_type is None, self.text + duration))

        return super().__exit__(exc_type, exc_val, traceback)


class Spinner:

    def __init__(self, text):
        self._text = text
        self._duration = Duration()

        if sys.stdout.isatty():
            self._spinner = _Spinner(text)
        else:
            self._spinner = None

    @property
    def text(self):
        if self._spinner is None:
            return self._text
        else:
            return self._spinner.text

    @text.setter
    def text(self, text):
        if self._spinner is None:
            self._text = text
        else:
            self._spinner.text = text

    def __enter__(self):
        if self._spinner is None:
            return self
        else:
            return self._spinner.__enter__()

    def __exit__(self, exc_type, exc_val, traceback):
        if self._spinner is None:
            duration = self._duration.stop()
            print(format_result(exc_type is None, self._text + duration), flush=True)
        else:
            return self._spinner.__exit__(exc_type, exc_val, traceback)


def get_status(status_path, default):
    status = default

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
            status = messages[-1]
        else:
            status = f'{messages[-1]} ({len(messages)} ongoing)'
    except Exception:
        pass

    return status


def run_verbose(command, message, env, status_path, message_as_final):
    duration = Duration()

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

        if not message_as_final:
            message = get_status(status_path, message)

        print(format_result_ok(message + duration.stop()), flush=True)

        return ''.join(output)
    except Exception:
        print(format_result_fail(message + duration.stop()), flush=True)
        raise


def run_with_spinner(command, message, env, status_path, message_as_final):
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
                    spinner.text = get_status(status_path, spinner.text)
                    time.sleep(0.1)

                output = proc.stdout.read()

                if message_as_final:
                    spinner.text = message
                else:
                    spinner.text = get_status(status_path, spinner.text)

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


def run(command, message, verbose, env=None, status_path=None, message_as_final=True):
    if status_path is not None:
        if os.path.exists(status_path):
            os.remove(status_path)

    if verbose:
        return run_verbose(command, message, env, status_path, message_as_final)
    else:
        return run_with_spinner(command, message, env, status_path, message_as_final)
