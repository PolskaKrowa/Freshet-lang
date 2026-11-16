# 11 — Option & Result (normative in fsht-01:01)

## Prelude enums (fsht-01:01-02.07.01)

`Option<T>` and `Result<T, E>` are prelude generic enums, lazily
registered on first use, with the exact shapes:

```
enum Option<T>   { Some(T), None }
enum Result<T,E> { Ok(T), Err(E) }
```

They behave exactly like user enums (chapter 08): values with copy
semantics, contextual/qualified/payload construction, `match`
exhaustiveness, generic instantiation through any position.

## The `?` operator (fsht-01:01-02.07.02)

```ebnf
question ::= expr "?"
```

`expr?` propagates `None`/`Err` out of the enclosing function:

* the enclosing function MUST return the same family (`Option` or
  `Result`) — checked;
* for `Result`, the error payload types MUST match — checked;
* on the ok path, `expr?` yields the payload;
* on the early-exit path, registered `defer`s run, then the function
  returns the propagated value.

`assert` remains the tool for violated invariants.

```
fn safe_div(a: i64, b: i64) -> Result<i64, i64> {
    if (b == 0) { return Err(1001); }
    return Ok(a / b);
}
fn work(a: i64, b: i64) -> Result<i64, i64> {
    let q: i64 = safe_div(a, b)?;    // early-return on Err
    return Ok(q * 2);
}
```

## Conformance requirements

The prelude shapes, `?`'s family/payload checks and its defer-running
early exit are MUST-level. `Option<T>` is the deliberate representation
for absent values; raw nullable pointers remain for C interop only
(chapter 17).
