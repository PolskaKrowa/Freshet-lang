#!/usr/bin/env python3
"""Freshet differential fuzz generator (fsht-03:03).

Generates random, deterministic-output Freshet programs from shapes that
are valid per the fsht-03:03 standard (each shape mirrors a construct
exercised by the curated corpus — including the fsht-02 additions:
`Vec<T>` containers with scope-exit drops, user traits with static
dispatch, and const-generic instantiation with `const fn` evaluation;
and the fsht-03 additions: numeric text parsing round-trips,
checked/saturating/wrapping variant arithmetic, and mutable-borrow
fill patterns).
The programs print only computed values, so their stdout is a differential
oracle: any two builds of the same program (any optimisation level, any
pass configuration, any thread count) must produce byte-identical output.

Integer reductions inside parfor are grouping-independent (exact
arithmetic), and float accumulation uses exact dyadic constants, so even
fast-math-shaped reassociations cannot change the printed values.

usage: fuzz/gen.py --seed 123 [--budget 12]     (prints one program)
"""
import argparse
import random
import sys

HELPERS = [
    "fn work(x: i64) -> i64 { return x * 3 - 1; }",
    "fn pick2(a: i64, b: i64) -> i64 { if (a < b) { return a; } return b; }",
    "fn scale(x: f64) -> f64 { return x * 0.25 + 0.5; }",
]


class Gen:
    def __init__(self, rng):
        self.rng = rng
        self.decls = []
        self.n = 0

    def fresh(self):
        self.n += 1
        return self.n

    # ---------------- statement blocks (all deterministic) ----------------

    def b_plain(self):
        i = self.fresh()
        lo = self.rng.choice([0, 0, 1, -3])
        trip = self.rng.choice([0, 1, 2, 9, 17, 20, 25, 33])
        hi = lo + trip
        c = self.rng.randint(1, 9)
        return ["    for (k%d in %d..%d) { acc += k%d * %d + %d; }"
                % (i, lo, hi, i, c, self.rng.randint(0, 9))]

    def b_peel(self):
        i = self.fresh()
        lo = self.rng.choice([0, 1])
        trip = self.rng.choice([1, 2, 5, 17, 20])
        return [
            "    for (k%d in %d..%d) {" % (i, lo, lo + trip),
            "        if (k%d == %d) { acc += 100; } else { acc += 1; }" % (i, lo),
            "    }",
        ]

    def b_call(self):
        i = self.fresh()
        lo = self.rng.choice([0, 1])
        trip = self.rng.choice([1, 2, 17, 20, 25])
        return ["    for (k%d in %d..%d) { acc += work(k%d as i64); }"
                % (i, lo, lo + trip, i)]

    def b_cast(self):
        i = self.fresh()
        trip = self.rng.choice([2, 9, 17, 25])
        return [
            "    for (k%d in 0..%d) {" % (i, trip),
            "        let t: u8 = (k%d as u8);" % i,
            "        accu += t as u64;",
            "        acc += (t as i64) + 1;",
            "    }",
        ]

    def b_nested(self):
        i = self.fresh()
        j = self.fresh()
        inner = self.rng.randint(2, 6)
        trip = self.rng.choice([2, 3, 5])
        return [
            "    for (k%d in 0..%d) {" % (i, trip),
            "        for (j%d in 0..%d) { acc += k%d * %d + j%d; }" % (
                j, inner, i, inner, j),
            "    }",
        ]

    def b_while(self):
        i = self.fresh()
        lim = self.rng.choice([6, 10, 20])
        skip = self.rng.randint(2, 4)
        stop = self.rng.randint(5, 9)
        return [
            "    let mut w%d: i64 = 0;" % i,
            "    while (w%d < %d) {" % (i, lim),
            "        w%d = w%d + 1;" % (i, i),
            "        if (w%d == %d) { continue; }" % (i, skip),
            "        if (w%d == %d) { break; }" % (i, stop),
            "        acc = acc + w%d * 2;" % i,
            "    }",
        ]

    def b_array(self):
        i = self.fresh()
        c = self.rng.randint(2, 7)
        return [
            "    let a%d: [i64; 6] = [1, 2, 3, 4, 5, 6];" % i,
            "    let mut s%d: i64 = 0;" % i,
            "    for (i%d in 0..a%d.len) { s%d = s%d + a%d[i%d] * %d; }" % (
                i, i, i, i, i, i, c),
            "    acc = acc + s%d;" % i,
        ]

    def b_span(self):
        i = self.fresh()
        lo = self.rng.randint(0, 3)
        hi = lo + self.rng.randint(2, 5)
        c = self.rng.randint(1, 9)
        return [
            "    let arr%d: [i64; 8] = [1, 2, 3, 4, 5, 6, 7, 8];" % i,
            "    let v%d: Span<i64> = span(arr%d);" % (i, i),
            "    let sub%d: Span<i64> = v%d[%d..%d];" % (i, i, lo, hi),
            "    acc = acc + sub%d.len * %d + sub%d[0];" % (i, c, i),
        ]

    def b_enum(self):
        i = self.fresh()
        self.decls.append("enum E%d { A, B, C(i64), D }" % i)
        which = self.rng.choice(["A", "B", "C(7)", "D"])
        c = self.rng.randint(1, 9)
        return [
            "    let e%d: E%d = %s;" % (i, i, which),
            "    match (e%d) {" % i,
            "        A => { acc = acc + 1; }",
            "        B => { acc = acc + 2; }",
            "        C(v) => { acc = acc + v * %d; }" % c,
            "        D => { acc = acc - 1; }",
            "    }",
        ]

    def b_struct(self):
        i = self.fresh()
        self.decls.append("struct S%d { x: i64, y: i64 }" % i)
        a = self.rng.randint(1, 9)
        b = self.rng.randint(1, 9)
        return [
            "    let s%d: S%d = S%d { x: %d, y: %d };" % (i, i, i, a, b),
            "    acc = acc + s%d.x * s%d.y;" % (i, i),
        ]

    def b_malloc(self):
        i = self.fresh()
        c = self.rng.randint(1, 9)
        return [
            "    let p%d: *i64 = malloc(i64, 4);" % i,
            "    defer free(p%d);" % i,
            "    for (q%d in 0..4) { p%d[q%d] = q%d as i64 * %d; }" % (
                i, i, i, i, c),
            "    acc = acc + p%d[0] + p%d[3];" % (i, i),
        ]

    def b_parfor(self):
        i = self.fresh()
        n = self.rng.choice([64, 128, 1024])
        c = self.rng.randint(1, 9)
        flagged = self.rng.random() < 0.5
        red = "@reproducible " if flagged else ""
        return [
            "    let pn%d: usize = %d;" % (i, n),
            "    let d%d: *i64 = malloc(i64, pn%d);" % (i, i),
            "    defer free(d%d);" % i,
            "    parfor (i%d in 0..pn%d) { d%d[i%d] = i%d as i64 + %d; }" % (
                i, i, i, i, i, c),
            "    let mut r%d: i64 = 0;" % i,
            "    %sparfor (i%d in 0..pn%d) [reduction(+: r%d)] {"
            % (red, i, i, i),
            "        r%d = r%d + d%d[i%d];" % (i, i, i, i),
            "    }",
            "    acc = acc + r%d;" % i,
        ]

    def b_fchain(self):
        i = self.fresh()
        lim = self.rng.choice([10, 50, 100])
        return [
            "    for (f%d in 0..%d) { facc = facc + (f%d as f64) * 0.25; }"
            % (i, lim, i),
        ]

    def b_fcall(self):
        i = self.fresh()
        lim = self.rng.choice([4, 10, 20])
        return [
            "    for (g%d in 0..%d) { facc = facc + scale(g%d as f64); }" % (
                i, lim, i),
        ]

    def b_str(self):
        i = self.fresh()
        c = self.rng.randint(1, 9)
        return [
            "    let t%d: str = \"freshet\";" % i,
            "    acc = acc + t%d.len * %d + t%d[0] as i64;" % (i, c, i),
        ]

    def b_pick2(self):
        i = self.fresh()
        a = self.rng.randint(-5, 9)
        b = self.rng.randint(-5, 9)
        return ["    acc = acc + pick2(%d, %d);" % (a, b)]

    # ------------- fsht-02 shapes -------------

    def b_vec(self):
        # Vec<T>: growth, borrowed Span view, scope-exit drop (ch. 20)
        i = self.fresh()
        c = self.rng.randint(1, 9)
        trip = self.rng.choice([2, 3, 5, 9])
        return [
            "    let mut v%d: Vec<i64> = vec_new(i64, 2);" % i,
            "    for (u%d in 0..%d) { vec_push(&v%d, u%d as i64 * %d); }" % (
                i, trip, i, i, c),
            "    let view%d: Span<i64> = v%d[0..v%d.len];" % (i, i, i),
            "    for (j%d in 0..view%d.len) { acc = acc + view%d[j%d]; }" % (
                i, i, i, i),
        ]

    def b_traits(self):
        # trait + impl + generic caller: static dispatch per
        # instantiation (ch. 21)
        i = self.fresh()
        a = self.rng.randint(1, 9)
        k = self.rng.randint(1, 9)
        self.decls.append(
            "trait Bump%d {\n"
            "    fn bump(x: Self) -> Self;\n"
            "}\n"
            "impl Bump%d for i64 {\n"
            "    fn bump(x: Self) -> Self { return x * %d + %d; }\n"
            "}\n"
            "fn bump2<T: Bump%d>(x: T) -> T {\n"
            "    return Bump%d::bump(Bump%d::bump(x));\n"
            "}" % (i, i, k, a, i, i, i))
        return ["    acc = acc + bump2(%d as i64);" % a]

    def b_constgen(self):
        # const generic struct instantiated through a const fn call in a
        # const position; const_assert over the same evaluation (ch. 22)
        i = self.fresh()
        c = self.rng.randint(1, 4)
        d = self.rng.randint(0, 5)
        n = 4
        length = n * c + d
        elems = ", ".join(str((x % 9) + 1) for x in range(length))
        self.decls.append("struct CG%d<T, const N: usize> { data: [T; N] }" % i)
        self.decls.append(
            "const fn cf%d(x: usize) -> usize { return x * %d + %d; }" % (
                i, c, d))
        return [
            "    let g%d: CG%d<i64, cf%d(%d)> = CG%d { data: [%s] };" % (
                i, i, i, n, i, elems),
            "    acc = acc + g%d.data[0] + g%d.data[%d];" % (i, i, length - 1),
            "    acc = acc + cf%d(%d) as i64;" % (i, n),
            "    const_assert(cf%d(%d) == %d);" % (i, n, length),
        ]

    # ------------- fsht-03 shapes -------------

    def b_parse(self):
        # parse is fmt's inverse: the round trip is always Ok, and the
        # payload feeds exact integer arithmetic (ch. 23 §1)
        i = self.fresh()
        v = self.rng.randint(-999, 999)
        return [
            "    let ps%d: String = fmt_i64(%d);" % (i, v),
            "    match (parse_i64(str_of(&ps%d))) {" % i,
            "        Ok(pv%d) => { acc = acc + pv%d; }" % (i, i),
            "        Err(pe%d) => { acc = acc + 1; }" % i,
            "    }",
        ]

    def b_checked(self):
        # checked/saturating/wrapping variants over i8: every path is
        # deterministic two's-complement arithmetic (ch. 23 §2)
        i = self.fresh()
        a = self.rng.randint(-120, 120)
        b = self.rng.randint(-120, 120)
        return [
            "    let ca%d: i8 = %d as i8;" % (i, a),
            "    let cb%d: i8 = %d as i8;" % (i, b),
            "    match (checked_add(ca%d, cb%d)) {" % (i, i),
            "        Some(x%d) => { acc = acc + (x%d as i64); }" % (i, i),
            "        None => { acc = acc + (int_max(ca%d) as i64); }" % i,
            "    }",
            "    acc = acc + (saturating_add(ca%d, cb%d) as i64);" % (i, i),
            "    acc = acc + (wrapping_mul(ca%d, cb%d) as i64);" % (i, i),
        ]

    def b_borrow(self):
        # mutable borrow of array storage, written through indexing and
        # read back through the owner (ch. 24 §1/§2)
        i = self.fresh()
        c = self.rng.randint(1, 9)
        k = self.rng.randint(1, 9)
        return [
            "    let mut bx%d: [i64; 2] = [0, 0];" % i,
            "    let bp%d: *i64 = &mut bx%d[0];" % (i, i),
            "    bp%d[0] = %d;" % (i, c),
            "    bp%d[1] = bp%d[0] * %d;" % (i, i, k),
            "    acc = acc + bx%d[1];" % i,
        ]


BLOCKS = [Gen.b_plain, Gen.b_peel, Gen.b_call, Gen.b_cast, Gen.b_nested,
          Gen.b_while, Gen.b_array, Gen.b_span, Gen.b_enum, Gen.b_struct,
          Gen.b_malloc, Gen.b_parfor, Gen.b_fchain, Gen.b_fcall, Gen.b_str,
          Gen.b_pick2, Gen.b_vec, Gen.b_traits, Gen.b_constgen,
          Gen.b_parse, Gen.b_checked, Gen.b_borrow]


def gen_program(rng, budget=12, seed_label=""):
    g = Gen(rng)
    # all helpers are always emitted: block generators may reference any
    # of them, and an unsampled helper must not leave a call undefined
    helpers = list(HELPERS)
    body = ["    let mut acc: i64 = 0;",
            "    let mut accu: u64 = 0;",
            "    let mut facc: f64 = 0.0;"]
    for _ in range(rng.randint(2, budget)):
        block = rng.choice(BLOCKS)(g)
        body.extend(block)
    body += ["    print_i64(acc); println();",
             "    print_u64(accu); println();",
             "    print_f64(facc, 6); println();"]
    out = []
    if seed_label:
        out.append("// fuzz seed %s (fsht-03:03 shapes; deterministic output)"
                   % seed_label)
    out.extend(helpers)
    out.extend(g.decls)
    out.append("fn main() {")
    out.extend(body)
    out.append("}")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--budget", type=int, default=12)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    sys.stdout.write(gen_program(rng, args.budget, str(args.seed)))


if __name__ == "__main__":
    main()
