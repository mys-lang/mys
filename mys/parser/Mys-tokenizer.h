#ifndef Mys_Py_TOKENIZER_H
#define Mys_Py_TOKENIZER_H
#ifdef __cplusplus
extern "C" {
#endif

#include "object.h"

/* Tokenizer interface */

#include "Mys-token.h"      /* For token types */

#define MAXINDENT 100   /* Max indentation level */
#define MAXLEVEL 200    /* Max parentheses level */

enum decoding_state {
    STATE_INIT,
    STATE_RAW,
    STATE_NORMAL        /* have a codec associated with input */
};

/* Tokenizer state */
struct tok_state {
    /* Input state; buf <= cur <= inp <= end */
    /* NB an entire line is held in the buffer */
    char *buf;          /* Input buffer, or NULL; malloc'ed if fp != NULL */
    char *cur;          /* Next character in buffer */
    char *inp;          /* End of data in buffer */
    const char *end;    /* End of input buffer if buf != NULL */
    const char *start;  /* Start of current token if not NULL */
    int done;           /* E_OK normally, E_EOF at EOF, otherwise error code */
    /* NB If done != E_OK, cur must be == inp!!! */
    FILE *fp;           /* Rest of input; NULL if tokenizing a string */
    int tabsize;        /* Tab spacing */
    int indent;         /* Current indentation index */
    int indstack[MAXINDENT];            /* Stack of indents */
    int atbol;          /* Nonzero if at begin of new line */
    int pendin;         /* Pending indents (if > 0) or dedents (if < 0) */
    const char *prompt, *nextprompt;          /* For interactive prompting */
    int lineno;         /* Current line number */
    int first_lineno;   /* First line of a single line or multi line string
                           expression (cf. issue 16806) */
    int level;          /* () [] {} Parentheses nesting level */
            /* Used to allow free continuations inside them */
    char parenstack[MAXLEVEL];
    int parenlinenostack[MAXLEVEL];
    PyObject *filename;
    /* Stuff for checking on different tab sizes */
    int altindstack[MAXINDENT];         /* Stack of alternate indents */
    /* Stuff for PEP 0263 */
    enum decoding_state decoding_state;
    int decoding_erred;         /* whether erred in decoding  */
    int read_coding_spec;       /* whether 'coding:...' has been read  */
    char *encoding;         /* Source encoding. */
    int cont_line;          /* whether we are in a continuation line. */
    const char* line_start;     /* pointer to start of current line */
    const char* multi_line_start; /* pointer to start of first line of
                                     a single line or multi line string
                                     expression (cf. issue 16806) */
    PyObject *decoding_readline; /* open(...).readline */
    PyObject *decoding_buffer;
    const char* enc;        /* Encoding for the current str. */
    char* str;
    char* input;       /* Tokenizer's newline translated copy of the string. */

    int type_comments;      /* Whether to look for type comments */
};

extern struct tok_state *Mys_PyTokenizer_FromString(const char *, int);
extern struct tok_state *Mys_PyTokenizer_FromUTF8(const char *, int);
extern struct tok_state *Mys_PyTokenizer_FromFile(FILE *, const char*,
                                              const char *, const char *);
extern void Mys_PyTokenizer_Free(struct tok_state *);
extern int Mys_PyTokenizer_Get(struct tok_state *, const char **, const char **);

#define tok_dump _Py_tok_dump

#ifdef __cplusplus
}
#endif
#endif /* !Py_TOKENIZER_H */
