import subprocess
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


class Spinner(yaspin.api.Yaspin):

    def __init__(self, text):
        super().__init__(yaspin.Spinner(SPINNER, 80), text=text, color='yellow')
        self._start_time = duration_start()

    def __exit__(self, exc_type, exc_val, traceback):
        duration = duration_stop(self._start_time)

        if exc_type is None:
            self.write(green(' ✔ ') + self.text + duration)
        else:
            self.write(red(' ✘ ') + self.text + duration)

        return super().__exit__(exc_type, exc_val, traceback)


def run_with_spinner(command, message, env=None):
    output = ''

    try:
        with Spinner(text=message):
            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding='utf-8',
                                    close_fds=False,
                                    env=env)
            output = result.stdout
            result.check_returncode()
    except Exception:
        lines = []

        for line in output.splitlines():
            if 'make: *** ' in line:
                continue

            lines.append(line)

        raise Exception('\n'.join(lines).rstrip())

    return output


def run(command, message, verbose, env=None):
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
            print(green(' ✔ ') + message + duration_stop(start_time))
        except Exception:
            print(red(' ✘ ') + message + duration_stop(start_time))
            raise
    else:
        output = run_with_spinner(command, message, env)

    return output
