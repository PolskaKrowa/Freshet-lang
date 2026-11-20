# Grammar — consolidated EBNF (informative appendix to fsht-03:03)

One page, consolidated from the per-chapter normative productions. In
case of conflict, the per-chapter EBNF and the prose rules win.

```ebnf
(* ---------------- lexical ---------------- *)
program          ::= { toplevel }
toplevel         ::= module_decl | import_decl | struct_decl
                  | enum_decl | function_decl | extern_decl
                  | trait_decl | impl_decl          (* fsht-02:02 *)
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
param            ::= [ "owned" | "borrowed" [ "mut" ] ] identifier ":" type
                                                   (* borrowed mut: fsht-03:02 *)
generic_params   ::= "<" type_param { "," type_param } ">"
type_param       ::= identifier [ ":" constraint ]
                  | "const" identifier ":" "usize"     (* fsht-02:03 *)
constraint       ::= constraint_part { "+" constraint_part }
constraint_part  ::= "Numeric" | "Int" | "Float" | "Signed"
                  | identifier   (* a declared trait, fsht-02:02 *)
args             ::= expr { "," expr }

const_fn_decl    ::= "const" "fn" identifier "(" [ params ] ")"
                     [ "->" type ] block               (* fsht-02:03 *)
trait_decl       ::= [ "pub" ] "trait" identifier "{"
                     { trait_method } "}"             (* fsht-02:02 *)
trait_method     ::= "fn" identifier "(" [ trait_param { "," trait_param } ] ")"
                     [ "->" type ] ";"
trait_param      ::= identifier ":" type
impl_decl        ::= [ "pub" ] "impl" identifier "for" type "{"
                     { impl_method } "}"
impl_method      ::= "fn" identifier "(" [ param { "," param } ] ")"
                     [ "->" type ] block

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
                  | "String" | vec_type | "Reader" | "Writer"
vec_type         ::= "Vec" "<" type ">"                (* fsht-02:01 *)
                    (* Reader/Writer: fsht-03:01, ch. 23 §4 *)
scalar           ::= "u8"|"u16"|"u32"|"u64"|"usize"|"i8"|"i16"|"i32"|"i64"
                  | "f32"|"f64"|"bool"|"void"
pointer_type     ::= "*" type
array_type       ::= "[" type ";" length "]"
length           ::= int_literal | const_expr           (* fsht-02:03 *)
const_expr       ::= const_operand { ( "+" | "-" | "*" | "/" | "%" ) const_operand }
const_operand    ::= int_literal | identifier
                  | identifier "(" const_expr { "," const_expr } ")"
                  | "(" const_expr ")"
span_type        ::= "Span" "<" type ">"
soa_type         ::= "soa" "(" identifier ")"
fn_ptr_type     ::= "fn" "(" [ type { "," type } ] ")" [ "->" type ]

(* ---------------- statements ---------------- *)
block            ::= "{" { stmt } "}"
stmt             ::= binding ";" | assignment ";" | "return" [ expr ] ";"
                  | "defer" call ";" | "give" "(" expr ")" ";"
                  | "const_assert" "(" expr ")" ";"    (* fsht-02:03 *)
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
                  | builtin_call | borrow_expr
borrow_expr      ::= "&" [ "mut" ] place          (* fsht-03:02, ch. 24 §1 *)
place            ::= identifier { "." identifier | "[" expr "]" }
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
                  | vec_fn | parse_fn | checked_fn | saturating_fn
                  | wrapping_fn | cast_fn | bounds_fn
vec_fn           ::= "vec_new" | "vec_from_span" | "vec_from_array"
                  | "vec_clone" | "vec_push" | "vec_pop" | "vec_insert"
                  | "vec_remove" | "vec_reserve" | "vec_truncate"
                  | "vec_resize" | "vec_clear" | "vec_free" | "vec_get"
                  | "vec_slice" | "vec_len" | "vec_capacity"
                  | "vec_is_empty"                       (* fsht-02:01 *)
parse_fn         ::= "parse_i64" | "parse_u64" | "parse_f64"
                                                    (* fsht-03:01 *)
checked_fn       ::= "checked_add" | "checked_sub" | "checked_mul"
                  | "checked_div" | "checked_rem"      (* fsht-03:01 *)
saturating_fn    ::= "saturating_add" | "saturating_sub"
                  | "saturating_mul"                      (* fsht-03:01 *)
wrapping_fn      ::= "wrapping_add" | "wrapping_sub" | "wrapping_mul"
                                                    (* fsht-03:01 *)
cast_fn          ::= "checked_cast" | "saturating_cast" (* fsht-03:01 *)
bounds_fn        ::= "int_min" | "int_max"              (* fsht-03:01 *)
math_fn          ::= "sqrt"|"fabs"|"floor"|"ceil"|"round"|"fmin"|"fmax"
                  | "pow"|"exp"|"log"|"sin"|"cos"|"tan"|"log2"|"log10"
                  | "imin" | "imax"
string_fn        ::= "string_new"|"string_from"|"string_append"|"str_cat"
                  | "str_of"|"string_free"|"string_clone"|"string_clear"
                  | "str_eq"|"str_to_cstr"
                  | "fmt_i64" | "fmt_f64"
                  | parse_fn     (* string module re-export; parse since fsht-03:01 *)
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
`fn` (or the `parfor`/loop it annotates); `owned`/`borrowed` (and
`borrowed mut`, fsht-03:02) are contextual keywords in parameter
position only; `mut` after `&` is a contextual keyword in the borrow
expression (fsht-03:02). `Vec<T>` mutation builtins take the mutable
borrow of a `let mut` binding — `&mut v` explicitly or the legacy
`&v` — and `v[i]` / `v[lo..hi]` behave like other postfix indexing
(ch. 20; the borrow discipline itself is ch. 24). `Trait::method`,
`Type::method` and `Self::method` calls travel through
`module_qualifier` (ch. 21); `const_assert` is compile-time only
(ch. 22); the stdlib module functions (`io::reader_open` and friends)
are ordinary `pub fn`s reached through `module_qualifier` (ch. 23).
`checked_cast`'s target type is inferred from context (ch. 23 §3).
