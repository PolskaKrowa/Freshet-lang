# 05 — Statements (normative in fsht-01:01)

## Statement grammar

```ebnf
stmt ::= binding ";"
       | lhs "=" expr ";" | lhs "+=" expr ";" | lhs "-=" expr ";"
       | lhs "*=" expr ";" | lhs "/=" expr ";" | lhs "%=" expr ";"
       | lhs "&=" expr ";" | lhs "|=" expr ";" | lhs "^=" expr ";"
       | lhs "<<=" expr ";" | lhs ">>=" expr ";"
       | "return" [ expr ] ";"
       | "defer" call ";"
       | "give" "(" expr ")" ";"
       | if_stmt | while_stmt | for_stmt | parfor_stmt
       | match_stmt | "break" ";" | "continue" ";"
       | "unsafe" block | block | expr_stmt ";"
if_stmt    ::= "if" "(" expr ")" block [ "else" ( if_stmt | block ) ]
while_stmt ::= "while" "(" expr ")" block
match_stmt ::= "match" "(" expr ")" "{" match_arm { "," match_arm } "}"
match_arm  ::= pattern "=>" block
pattern    ::= variant_pattern | "_"
```

## Control flow

* `if`/`else`, `while` and blocks behave as in C-family languages;
  `if` is a **statement**, not an expression.
* `break;` / `continue;` bind to the innermost enclosing `for`/`while`
  loop (`F0213` outside a loop). Inside `parfor` they carry **lane-local
  semantics** (chapter 12).
* Every non-void function MUST return on every path (`F0209`).

## Loops

```ebnf
for_stmt ::= "for" "(" for_head ")" block
for_head ::= c_style | range_style
c_style   ::= identifier "=" expr ";" expr ";" step
step      ::= identifier "+=" expr | identifier "-=" expr
            | identifier "=" identifier ( "+" | "-" ) expr
range_style ::= identifier "in" expr ".." expr [ "by" [ "-" ] int_expr ]
```

* The C-style step may be `i += E`, `i -= E`, or `i = i ± E`; the
  condition is any expression re-evaluated per iteration.
* Range loops accept `for (i in a..b by E)`; `by -1` iterates descending.
* Non-unit strides compile correctly but are an `F0405` performance
  warning (an error under strict mode, chapter 15); modifying the
  induction variable inside the body is `F0406`.
* Constant-trip loops with small bounds are legitimate full-unroll
  candidates (an optimisation remark, not a semantic rule).

## `defer`

```ebnf
defer_stmt ::= "defer" call ";"
```

`defer <call>` runs at scope exit — on every `return` AND before every
`break`/`continue` that leaves the scope. The ownership analysis
(chapter 06) requires every `malloc` to be matched by a visible `free`,
a `defer free`, or a `give` transfer; `defer` is the idiomatic tool.

## `match`

`match (e) { Variant => { ... }, Variant(a, b) => { ... }, _ => {...} }`
dispatches on an enum's tag (chapter 08):

* payload bindings are **positional** and immutable copies;
* exhaustiveness is checked: every variant covered or `_` present
  (`F0204`);
* arms are blocks; `match` is a statement.

## Conformance requirements

All productions above are MUST-level, including the compound-assignment
family (`<<=`/`>>=` included), `by` ranges (with `by -1` descending), and
`defer`'s exit-path semantics. Statements after a terminator in the same
block are unreachable and SHOULD be diagnosed.
