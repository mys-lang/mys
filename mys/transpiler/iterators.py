from ..parser import ast


class HasYieldVisitor(ast.NodeVisitor):

    def __init__(self):
        self.has_yield = False

    def visit_Yield(self, _node):
        self.has_yield = True


def has_yield(node):
    visitor = HasYieldVisitor()
    visitor.visit(node)

    return visitor.has_yield


def create_assign_state_node(state):
    return ast.Assign(
        targets=[ast.Attribute(value=ast.Name(id='self'), attr='_state')],
        value=ast.Constant(value=state))


class IteratorVisitor(ast.NodeVisitor):

    def __init__(self):
        self._next_state = 0
        self._resume_states_stack = []
        self._current_states_stack = []
        self._state_bodies = {}
        self._loop_states_stack = []

    def new_state(self):
        state = self._next_state
        self._next_state += 1

        return state

    def push_resume_state(self, state):
        self._resume_states_stack.append(state)

    def pop_resume_state(self):
        return self._resume_states_stack.pop()

    def get_resume_state(self):
        return self._resume_states_stack[-1]

    def push_current_state(self, state):
        self._current_states_stack.append(state)

    def pop_current_state(self):
        return self._current_states_stack.pop()

    def get_current_state(self):
        return self._current_states_stack[-1]

    def push_loop_states(self, states):
        self._loop_states_stack.append(states)

    def pop_loop_states(self):
        return self._loop_states_stack.pop()

    def get_loop_begin_state(self):
        return self._loop_states_stack[-1][0]

    def get_loop_end_state(self):
        return self._loop_states_stack[-1][1]

    def append_to_current_state(self, nodes):
        current_state = self.get_current_state()
        body = self._state_bodies.get(current_state)

        if body is None:
            self._state_bodies[current_state] = nodes
        else:
            body += nodes

    def members(self):
        return []

    def init_args(self):
        return []

    def init_body(self):
        return []

    def match_cases(self):
        cases = []

        for state, body in self._state_bodies.items():
            cases.append(ast.match_case(pattern=ast.Constant(value=state),
                                        body=body))

        return cases

    def visit_body(self, body_nodes):
        body_before_yield = []
        body_iter = iter(body_nodes)
        yield_found = False

        for body_node in body_iter:
            if has_yield(body_node):
                self.push_resume_state(self.new_state())
                body_before_yield += self.visit(body_node)
                self.push_current_state(self.get_resume_state())
                self.pop_resume_state()

                for body_node in body_iter:
                    if has_yield(body_node):
                        self.push_resume_state(self.new_state())
                        self.append_to_current_state(self.visit(body_node))
                        self.pop_current_state()
                        self.push_current_state(self.pop_resume_state())
                    else:
                        self.append_to_current_state([body_node])

                self.append_to_current_state([
                    create_assign_state_node(self.get_resume_state())
                ])
                self.pop_current_state()
                yield_found = True
            else:
                body_before_yield.append(body_node)

        if not yield_found:
            body_before_yield.append(
                create_assign_state_node(self.get_resume_state()))

        return body_before_yield

    def visit_If(self, node):
        return [ast.If(test=node.test,
                       body=self.visit_body(node.body),
                       orelse=self.visit_body(node.orelse))]

    def visit_FunctionDef(self, node):
        self.push_current_state(self.new_state())

        for body_node in node.body:
            if has_yield(body_node):
                self.push_resume_state(self.new_state())
                self.append_to_current_state(self.visit(body_node))
                self.pop_current_state()
                self.push_current_state(self.pop_resume_state())
            else:
                self.append_to_current_state([body_node])

        self.append_to_current_state([
            ast.Raise(
                exc=ast.Call(
                    func=ast.Name(id='RuntimeError'),
                    args=[],
                    keywords=[]))
        ])

    def visit_Yield(self, node):
        return [
            create_assign_state_node(self.get_resume_state()),
            ast.Return(value=node.value)
        ]

    def visit_While(self, node):
        while_state = self.new_state()
        self.push_current_state(while_state)
        self.push_loop_states((while_state, self.get_resume_state()))
        self.push_resume_state(while_state)
        body = self.visit_body(node.body)
        self.pop_resume_state()
        self.pop_loop_states()
        self.append_to_current_state([
            ast.If(test=node.test,
                   body=body,
                   orelse=[
                       create_assign_state_node(self.get_resume_state())
                   ])
        ])
        self.pop_current_state()

        return [create_assign_state_node(while_state)]

    def visit_For(self, node):
        raise NotImplementedError("'for' is not yet implemented in iterators")

    def visit_Try(self, node):
        raise NotImplementedError("'try' is not yet implemented in iterators")

    def visit_Expr(self, node):
        return [ast.Expr(value=node) for node in self.visit(node.value)]

    def visit_Return(self, node):
        raise Exception("'return' is not allowed in iterators")


def transform(tree):
    """Transform given iterator function AST tree to an iterator
    class. The class is returned.

    """

    visitor = IteratorVisitor()
    visitor.visit(tree)

    return ast.ClassDef(
        name=tree.name.title(),
        bases=[],
        keywords=[],
        body=[
            ast.AnnAssign(
                target=ast.Name(id='_state'),
                annotation=ast.Name(id='i64'),
                simple=1)
        ] + visitor.members() + [
            ast.FunctionDef(
                name='__init__',
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg='self')] + tree.args.args,
                    kwonlyargs=tree.args.kwonlyargs,
                    kw_defaults=tree.args.kw_defaults,
                    defaults=tree.args.defaults),
                body=[create_assign_state_node(0)] + visitor.init_body(),
                decorator_list=[]),
            ast.FunctionDef(
                name='next',
                args=ast.arguments(posonlyargs=[],
                                   args=[ast.arg(arg='self')],
                                   kwonlyargs=[],
                                   kw_defaults=[],
                                   defaults=[]),
                body=[
                    ast.While(
                        test=ast.Constant(value=True),
                        body=ast.Match(
                            subject=ast.Attribute(
                                value=ast.Name(id='self'), attr='_state'),
                            cases=visitor.match_cases()),
                        orelse=[])
                ],
                decorator_list=[],
                returns=ast.Name(id='i64'))
        ],
        decorator_list=[])
