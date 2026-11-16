# 17 — FFI & function pointers (normative in fsht-01:01)

## `extern fn`

```ebnf
extern_decl ::= "extern" "fn" identifier "(" [ extern_params ] ")"
                [ "->" type ] ";"
```

`extern fn` declares a C-ABI function resolved at link time; `#link m`
adds a library to the link line. Calling conventions are the C ABI.
Variadic C functions remain out of scope in fsht-01:01 (recorded in the
registry as a deferred feature).

## Function pointers (fsht-01:01-07.02.01)

```ebnf
fn_ptr_type  ::= "fn" "(" [ type_list ] ")" [ "->" type ]
fn_ptr_value ::= identifier | "&" identifier
indirect     ::= fn_ptr_value "(" args ")"
```

* `fn(P1, P2) -> R` is a first-class, pointer-sized **value type**
  (structurally interned; `void` return may be written `-> void`).
* Referencing a function by name (or `&name`) yields its pointer; slots
  are reassignable; `export fn` keeps its exact C symbol so C code can
  call back in.
* Indirect calls type-check arguments against the pointer's signature.
  Their effects are unknown → an indirect call inside `parfor` is
  `F0307`, and `@pure` bodies may not contain them.

```
fn add(a: i64, b: i64) -> i64 { return a + b; }

let f: fn(i64, i64) -> i64 = add;       // fn value coerces to the ptr type
let mut g: fn(i64, i64) -> i64 = add;
g = mul;                                // reassign
print_i64(f(2, 3));                      // INDIRECT call through the slot

fn apply_twice(f: fn(i64, i64) -> i64, x: i64) -> i64 {
    return f(f(x, x), x);               // fn-pointer PARAMETERS
}

extern fn qsort(base: *u8, n: usize, sz: usize,
                cmp: fn(*u8, *u8) -> i32);   // C callback ABI
fn cmp_desc(a: *u8, b: *u8) -> i32 { ... }
qsort(d as *u8, n, sizeof(i64), cmp_desc);   // Freshet fn as callback
```

## Interoperability surface

* String literals are NUL-terminated in the constant pool for C interop
  (chapter 10); `str_to_cstr` produces a malloc'd C string the caller
  frees.
* `Span<T>` exposes `.ptr` for handoff; `sizeof(T)` gives the C size.
* `libfsh` — the runtime's C API (`include/fsh/*.h`, `libfsh.a`) — is
  reachable through `extern fn` + `#link fsh` for everything the `fsh`
  module does not wrap (chapter 18).
* C header *generation* from Freshet declarations is a recorded future
  feature (registry); today bindings are declared, not generated.

## Conformance requirements

The fn-pointer value type, coercion of fn names, indirect-call typing,
the C callback ABI and extern linkage rules are MUST-level. `F0307`
rejection of indirect calls inside `parfor` is MUST-level.
