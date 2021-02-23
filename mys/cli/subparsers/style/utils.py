def get_source(source_lines, lineno, col_offset, end_lineno, end_col_offset):
    source = []
    number_of_lines = end_lineno - lineno + 1
    new_lineno = lineno

    if number_of_lines == 1:
        line = source_lines[lineno - 1]
        line = line[col_offset:end_col_offset]

        if line:
            source.append(line)
    else:
        for i in range(number_of_lines):
            line = source_lines[lineno + i - 1]

            if i == 0:
                line = line[col_offset:]

                if not line:
                    new_lineno += 1
                    continue
            elif i == number_of_lines - 1:
                line = line[:end_col_offset]

                if not line:
                    continue

            source.append(line)

    return new_lineno, source


def get_function_or_class_node_start(node):
    if node.decorator_list:
        node = node.decorator_list[0]

    return node.lineno, 0
