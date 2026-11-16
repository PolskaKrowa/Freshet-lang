# 01 — Lexical structure (normative in fsht-01:01)

## Character set and tokens

Source files are UTF-8. Tokens are identifiers, keywords, integer and
float literals, string literals, operators/punctuators, and preprocessor
directives at line start.

```ebnf
identifier      ::= identifier_start { identifier_continue }
identifier_start::= letter | "_"
identifier_continue ::= identifier_start | digit
letter          ::= "A"…"Z" | "a"…"z"
digit           ::= "0"…"9"
```

Identifiers are C-like (`[A-Za-z_][A-Za-z0-9_]*`); case is significant.
Keywords (contextual ones such as `owned` and `borrowed` may still appear
as identifiers where no parameter mode is expected): `fn let mut struct
enum import module pub export extern return defer if else while for
parfor match break continue unsafe give owned borrowed true false nil as
in by`.

## Comments

```ebnf
comment ::= "//" { any } line_end
         |  "/*" { comment | any } "*/"        (* nests *)
```

Line comments run to end of line. Block comments **nest** — `/* /* */ */`
is one comment.

## Numeric literals

```ebnf
int_literal   ::= [ "-" ] decimal_digits [ int_suffix ]
                 | [ "-" ] "0x" hex_digits [ int_suffix ]
decimal_digits::= digit { ["_"] digit }
float_literal ::= [ "-" ] digits "." digits [ float_suffix ]
int_suffix    ::= ("u8"|"u16"|"u32"|"u64"|"usize"|"i8"|"i16"|"i32"|"i64")
float_suffix  ::= "f32" | "f64"
```

A literal carries an optional type suffix (`42u8`, `1.5f32`, `0x1F`).
Unsuffixed literals adopt their annotation's type (chapter 02); in an
arithmetic operation a bare INT literal adopts the other operand's
integer type — signedness AND width (chapter 14). Hex literals are
unsigned in value but adopt their annotation.

## String literals

```ebnf
string_literal ::= '"' { char_escape | any_char_except_quote_nl } '"'
char_escape    ::= "\" n | "\" t | "\" "\" | "\" '"'
```

String literals are `str` values (chapter 10); they are stored
NUL-terminated in the constant pool for C interoperability. `print`
accepts any `str` value, not just literals.

## Preprocessor

```ebnf
directive ::= "#" "include" ("<" path ">" | '"' path '"')
           |  "#" "define" identifier [ "(" params ")" ] replacement
           |  "#" "link" identifier
           |  "#" "pragma" "once"
           |  ("#" "ifdef" | "#" "ifndef") identifier
           |  "#" "else" | "#" "endif"
```

The preprocessor supports `#include "file"` / `#include <file>` (searched
in `-I` directories), `#define` object and function-like macros,
`#link m` (link a library), `#pragma once`, and
`#ifdef/#ifndef/#else/#endif` conditionals. The preprocessor is
deliberately a *local text* facility: it is not the module system
(chapter 16) and MUST NOT leak into imported modules.

## Conformance requirements

* A conforming compiler MUST lex the productions above and MUST support
  the directives listed.
* Nesting block comments, literal suffixes and negative literals are
  MUST-level lexical features.
* Diagnostics: unexpected character `F0101`; preprocessor errors
  `F0103`/`F0104` (unknown directive).
