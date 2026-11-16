# Grammar — consolidated EBNF (informative appendix to fsht-01:01)

One page, consolidated from the per-chapter normative productions. In
case of conflict, the per-chapter EBNF and the prose rules win.

```ebnf
(* ---------------- lexical ---------------- *)
program          ::= { toplevel }
toplevel         ::= module_decl | import_decl | struct_decl
                  | enum_decl | function_decl | extern_decl
                  | preproc_directive | ";"

module_decl      ::= "module" identifier ";"
import_decl      ::= "import" identifier ";"
extern_decl      ::= "extern" "fn" identifier "(" [ params ] ")"
                     [ "->" type ] ";"

(* ---------------- declarations ---------------- *)
function_decl    ::= { attribute } [ "export" ] "fn"
                     [ generic_params ] identifier "(" [ params ] ")"
                     [ "->" type ] block
attribute        ::= "@" identifier [ "(" args ")" ]
attribute_names  ::= "pure" | "strictfp" | "fastmath" | "inline"
                  | "noinline" | "hpc_strict" | "unsafe" | "test"
                  | "alias" | "vectorize" | "reproducible"
params           ::= param { "," param }
param            ::= [ "owned" | "borrowed" ] identifier ":" type
generic_params   ::= "<" type_param { "," type_param } ">"
type_param       ::= identifier [ ":" constraint ]
constraint       ::= "Numeric" | "Int" | "Float" | "Signed"
args             ::= expr { "," expr }

struct_decl      ::= "struct" identifier [ "align" "(" int_literal ")" ]
                     "{" field { "," field } "}"
field            ::= identifier ":" type
enum_decl        ::= "enum" [ generic_params ] identifier
                     "{" variant { "," variant } "}"
variant          ::= identifier [ "(" type { "," type } ")" ]

(* ---------------- types ---------------- *)
type             ::= scalar | pointer_type | array_type | span_type
                  | soa_type | "str" | fn_ptr_type
                  | identifier            (* struct/enum *)
                  | "Option" "<" type ">" | "Result" "<" type "," type ">"
                  | "String"
scalar           ::= "u8"|"u16"|"u32"|"u64"|"usize"|"i8"|"i16"|"i32"|"i64"
                  | "f32"|"f64"|"bool"|"void"
pointer_type     ::= "*" type
array_type       ::= "[" type ";" int_literal "]"
span_type        ::= "Span" "<" type ">"
soa_type         ::= "soa" "(" identifier ")"
fn_ptr_type     ::= "fn" "(" [ type { "," type } ] ")" [ "->" type ]

(* ---------------- statements ---------------- *)
block            ::= "{" { stmt } "}"
stmt             ::= binding ";" | assignment ";" | "return" [ expr ] ";"
                  | "defer" call ";" | "give" "(" expr ")" ";"
                  | if_stmt | while_stmt | for_stmt | parfor_stmt
                  | match_stmt | "break" ";" | "continue" ";"
                  | "unsafe" block | block | expr_stmt ";"
binding          ::= "let" [ "mut" ] identifier ":" type "=" expr
assignment       ::= lhs ( "=" | "+=" | "-=" | "*=" | "/=" | "%="
                  | "&=" | "|=" | "^=" | "<<=" | ">>=" ) expr
lhs              ::= identifier | postfix | call

if_stmt          ::= "if" "(" expr ")" block [ "else" ( if_stmt | block ) ]
while_stmt       ::= "while" "(" expr ")" block
for_stmt         ::= "for" "(" for_head ")" block
for_head         ::= identifier "=" expr ";" expr ";" step
                  | identifier "in" expr ".." expr [ "by" [ "-" ] expr ]
step             ::= identifier "+=" expr | identifier "-=" expr
                  | identifier "=" identifier ( "+" | "-" ) expr

parfor_stmt      ::= [ "@reproducible" ] "parfor" "(" identifier "in"
                     expr ".." expr ")" [ "[" clause { "," clause } "]" ] block
clause           ::= "reduction" "(" ("+"|"-"|"*"|"min"|"max") ":"
                     identifier ")"
                  | "threads" ":" int | "chunk" ":" int
                  | "affinity" ":" ( "close" | "spread" )
                  | "collapse" ":" int

match_stmt       ::= "match" "(" expr ")" "{" arm { "," arm } "}"
arm              ::= ( variant [ "(" binder { "," binder } ")" ] | "_" )
                     "=>" block

expr_stmt        ::= expr
call             ::= callee "(" [ expr { "," expr } ] ")"
callee           ::= identifier | module_qualifier | fn_ptr_value
module_qualifier ::= identifier "::" identifier

(* ---------------- expressions ---------------- *)
expr             ::= logic_or
logic_or         ::= logic_and { "||" logic_and }
logic_and        ::= equality { "&&" equality }
equality         ::= comparison { ( "==" | "!=" ) comparison }
comparison       ::= additive { ( "<" | "<=" | ">" | ">=" ) additive }
additive         ::= multiplicative { ( "+" | "-" ) multiplicative }
multiplicative   ::= castable { ( "*" | "/" | "%" ) castable }
shift            ::= castable { ( "<<" | ">>" ) castable }   (* int only *)
castable         ::= unary [ "as" type ]
unary            ::= ( "-" | "!" ) unary | postfix
postfix          ::= primary { "." identifier
                  | "[" expr "]" | "[" expr ".." expr "]" }
primary          ::= literal | identifier | module_qualifier
                  | call | "(" expr ")"
                  | struct_literal | variant_ctor
                  | "give" "(" expr ")" | expr "?"
                  | builtin_call
literal          ::= int_literal | float_literal | string_literal
                  | "true" | "false" | "nil"
struct_literal   ::= identifier "{" identifier ":" expr
                     { "," identifier ":" expr } "}"
variant_ctor     ::= [ identifier "." ] identifier
                     [ "(" expr { "," expr } ")" ]

builtin_call     ::= "malloc" "(" type "," expr ")"
                  | "free" "(" expr ")"
                  | "memcpy" "(" expr "," expr "," expr ")"
                  | "memset" "(" expr "," int "," expr ")"
                  | "span" "(" expr "," expr ")" | "span" "(" identifier ")"
                  | "soa_new" "(" identifier "," expr ")"
                  | "soa_free" "(" expr ")" | "soa_len" "(" expr ")"
                  | "stack_alloc" "(" type "," expr ")"
                  | "sizeof" "(" type ")" | "alignof" "(" type ")"
                  | math_fn | string_fn | io_fn | freshet_intrinsic
math_fn          ::= "sqrt"|"fabs"|"floor"|"ceil"|"round"|"fmin"|"fmax"
                  | "pow"|"exp"|"log"|"sin"|"cos"|"tan"|"log2"|"log10"
                  | "imin" | "imax"
string_fn        ::= "string_new"|"string_from"|"string_append"|"str_cat"
                  | "str_of"|"string_free"|"str_eq"|"str_to_cstr"
                  | "fmt_i64" | "fmt_f64"
io_fn            ::= "print"|"print_i64"|"print_u64"|"print_f64"|"println"
                  | "assert"
freshet_intrinsic ::= "freshet" "." ("time_ns"|"cycles"|"threads"|"pause"
                  | "prefetch_r"|"prefetch_w"|"clflush") "(" [ expr ] ")"

(* ---------------- preprocessor ---------------- *)
preproc_directive ::= "#" "include" ( "<" path ">" | '"' path '"' )
                  |  "#" "define" identifier [ "(" params ")" ] replacement
                  |  "#" "link" identifier | "#" "pragma" "once"
                  |  ( "#" "ifdef" | "#" "ifndef" ) identifier
                  |  "#" "else" | "#" "endif"
```

Notes: `if` is a statement, not an expression; `match` is a statement;
`?` binds to the expression it postfixes; attribute position precedes
`fn` (or the `parfor`/loop it annotates); `owned`/`borrowed` are
contextual keywords in parameter position only.
