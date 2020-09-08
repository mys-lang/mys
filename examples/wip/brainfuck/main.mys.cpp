#include "mys.hpp"

class Tape;
class Op;

List<std::shared_ptr<Op>>
parse(std::shared_ptr<StringIO>& source);

void run(List<std::shared_ptr<Op>>& ops, std::shared_ptr<Tape>& tape);

int main();

String SOURCE_B(">++[<+++++++++++++>-]<[[>+>+<<-]>[<+>-]++++++++\n[>++++++++<-]>.[-]<<>++++++++++[>++++++++++[>++\n++++++++[>++++++++++[>++++++++++[>++++++++++[>+\n+++++++++[-]<-]<-]<-]<-]<-]<-]<-]++++++++++.");

class Tape : public Object {

public:
    List<int> tape;
    int pos;

    Tape()
    {
        this->tape = List<int>({0});
        this->pos = 0;
    }

    int get()
    {
        return this->tape[this->pos];
    }

    void inc(int x)
    {
        this->tape[this->pos] += x;
    }

    void move(int x)
    {
        this->pos += x;

        while (this->pos >= len(this->tape)) {
            this->tape.append(0);
        }
    }

    virtual String __str__() const
    {
        std::stringstream ss;

        ss << "Tape(tape=" << this->tape << ", pos=" << this->pos << ")";

        return String(ss.str().c_str());
    }

};

class Op : public Object {

public:

    virtual void execute(std::shared_ptr<Tape>& tape)
    {
        throw NotImplementedError();
    }

    virtual String __str__() const
    {
        return String("Op()");
    }

};

class Inc : public Op {

public:
    int val;

    Inc(int val)
    {
        this->val = val;
    }

    void execute(std::shared_ptr<Tape>& tape)
    {
        tape->inc(this->val);
    }

    virtual String __str__() const
    {
        std::stringstream ss;

        ss << "Inc(val=" << this->val << ")";

        return String(ss.str().c_str());
    }

};

class Move : public Op {

public:
    int val;

    Move(int val)
    {
        this->val = val;
    }

    void execute(std::shared_ptr<Tape>& tape)
    {
        tape->move(this->val);
    }

    virtual String __str__() const
    {
        std::stringstream ss;

        ss << "Move(val=" << this->val << ")";

        return String(ss.str().c_str());
    }

};

class Print : public Op {

public:

    void execute(std::shared_ptr<Tape>& tape)
    {
        std::cout << chr(tape->get()) << std::flush;
    }

    virtual String __str__() const
    {
        return String("Print()");
    }

};

class Loop : public Op {

public:
    List<std::shared_ptr<Op>> ops;

    Loop(List<std::shared_ptr<Op>>& ops)
    {
        this->ops = ops;
    }

    void execute(std::shared_ptr<Tape>& tape)
    {
        while (tape->get() > 0) {
            run(this->ops, tape);
        }
    }

    virtual String __str__() const
    {
        std::stringstream ss;

        ss << "Loop(ops=" << this->ops << ")";

        return String(ss.str().c_str());
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
