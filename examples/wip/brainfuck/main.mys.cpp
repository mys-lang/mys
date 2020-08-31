#include "mys.hpp"

class Tape;
class Op;

List<std::shared_ptr<Op>>
parse(std::shared_ptr<StringIO>& source);

void run(List<std::shared_ptr<Op>>& ops, std::shared_ptr<Tape>& tape);

int main();

String SOURCE_B(">++[<+++++++++++++>-]<[[>+>+<<-]>[<+>-]++++++++\n[>++++++++<-]>.[-]<<>++++++++++[>++++++++++[>++\n++++++++[>++++++++++[>++++++++++[>++++++++++[>+\n+++++++++[-]<-]<-]<-]<-]<-]<-]<-]++++++++++.");

class Tape {

public:
    List<int> m_tape;
    int m_pos;

    Tape()
    {
        m_tape = List<int>({0});
        m_pos = 0;
    }

    int get()
    {
        return m_tape[m_pos];
    }

    void inc(int x)
    {
        m_tape[m_pos] += x;
    }

    void move(int x)
    {
        m_pos += x;

        while (m_pos >= len(m_tape)) {
            m_tape.append(0);
        }
    }

};

class Op {

public:

    virtual void execute(std::shared_ptr<Tape>& tape)
    {
        throw NotImplementedError();
    }

};

class Inc : public Op {

public:
    int m_val;

    Inc(int val)
    {
        m_val = val;
    }

    void execute(std::shared_ptr<Tape>& tape)
    {
        tape->inc(m_val);
    }

};

class Move : public Op {

public:
    int m_val;

    Move(int val)
    {
        m_val = val;
    }

    void execute(std::shared_ptr<Tape>& tape)
    {
        tape->move(m_val);
    }

};

class Print : public Op {

public:

    void execute(std::shared_ptr<Tape>& tape)
    {
        std::cout << chr(tape->get()) << std::flush;
    }

};

class Loop : public Op {

public:
    List<std::shared_ptr<Op>> m_ops;

    Loop(List<std::shared_ptr<Op>>& ops)
    {
        m_ops = ops;
    }

    void execute(std::shared_ptr<Tape>& tape)
    {
        while (tape->get() > 0) {
            run(m_ops, tape);
        }
    }

};

List<std::shared_ptr<Op>>
parse(std::shared_ptr<StringIO>& source)
{
    auto ops = List<std::shared_ptr<Op>>({});
    while (true) {
        String c = source->read(1);
        if (c == "+") {
            ops.append(std::make_shared<Inc>(1));
        } else {
            if (c == "-") {
                ops.append(std::make_shared<Inc>(-1));
            } else {
                if (c == ">") {
                    ops.append(std::make_shared<Move>(1));
                } else {
                    if (c == "<") {
                        ops.append(std::make_shared<Move>(-1));
                    } else {
                        if (c == ".") {
                            ops.append(std::make_shared<Print>());
                        } else {
                            if (c == "[") {
                                auto parsed = parse(source);
                                ops.append(std::make_shared<Loop>(parsed));
                            } else {
                                if (contains(c, List<String>({"]", ""}))) {
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return ops;
}

void run(List<std::shared_ptr<Op>>& ops, std::shared_ptr<Tape>& tape)
{
    for (auto op: ops) {
        op->execute(tape);
    }
}

int main()
{
    auto string = std::make_shared<StringIO>(SOURCE_B);
    auto ops = parse(string);
    auto tape = std::make_shared<Tape>();
    run(ops, tape);

    return 0;
}
