class CommentsReader:

    def __init__(self, comments):
        self.comments = []

        for lineno, lines in comments:
            for i, line in enumerate(lines):
                self.comments.append((lineno + i, line))

        self.pos = 0

    def get_at(self, wanted_lineno):
        if self.pos == len(self.comments):
            return ''

        # ToDo: Remove the loop once we know that all comments prior
        #       to this line has been read.
        while self.pos < len(self.comments):
            lineno, line = self.comments[self.pos]

            if lineno < wanted_lineno:
                self.pos += 1
            else:
                if lineno == wanted_lineno:
                    self.pos += 1
                else:
                    line = ''

                break

        return line

    def get_before(self, wanted_lineno, prev_line):
        """Get any lines found directly before given line number.

        """

        if self.pos == len(self.comments):
            return []

        lineno, line = self.comments[self.pos]
        lines = []
        blank_lines_count = 0

        while lineno < wanted_lineno:
            if line == '':
                blank_lines_count += 1
            else:
                if not lines:
                    if prev_line == '':
                        blank_lines_count = 0
                    else:
                        blank_lines_count = min(blank_lines_count, 1)

                lines += [''] * blank_lines_count
                blank_lines_count = 0
                lines.append(line)

            self.pos += 1

            if self.pos == len(self.comments):
                break

            lineno, line = self.comments[self.pos]

        if blank_lines_count > 0 and (lines or prev_line != ''):
            lines.append('')

        return lines

    def get_remaining(self, prev_line):
        if self.pos == len(self.comments):
            return []

        return self.get_before(self.comments[-1][0] + 1, prev_line)
