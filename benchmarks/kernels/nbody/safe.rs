// safe.rs — Kernel 05 "nbody": O(B^2) N-body gravitational sweep. Serial.
// Idiomatic Rust shape: Vec<Body> (array of structs) + three scratch planes.
// Normative spec: ../KERNELS.md (fsht-01:01). CS type: i64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const B: usize = 2048;
const S: usize = 10;
const DT: f64 = 0.00001;
const EPS2: f64 = 0.0625;

struct Body {
    x: f64,
    y: f64,
    z: f64,
    vx: f64,
    vy: f64,
    vz: f64,
    m: f64,
}

#[inline(never)]
fn hot() -> i64 {
    let mut bodies: Vec<Body> = (0..B)
        .map(|i| Body {
            x: (i & 63) as f64 * 0.25,
            y: (i & 31) as f64 * 0.5,
            z: (i & 15) as f64 * 0.125,
            vx: 0.0,
            vy: 0.0,
            vz: 0.0,
            m: 1.0 + (i & 7) as f64 * 0.125,
        })
        .collect();
    let mut axv: Vec<f64> = vec![0.0; B];
    let mut ayv: Vec<f64> = vec![0.0; B];
    let mut azv: Vec<f64> = vec![0.0; B];
    for _s in 0..S {
        // phase 1: forces (self-interaction j == i included; r2 >= eps2)
        for i in 0..B {
            let mut ax: f64 = 0.0;
            let mut ay: f64 = 0.0;
            let mut az: f64 = 0.0;
            for j in 0..B {
                let dx: f64 = bodies[j].x - bodies[i].x;
                let dy: f64 = bodies[j].y - bodies[i].y;
                let dz: f64 = bodies[j].z - bodies[i].z;
                let r2: f64 = dx * dx + dy * dy + dz * dz + EPS2;
                let inv: f64 = 1.0 / f64::sqrt(r2);
                let inv3: f64 = inv * inv * inv;
                let mm: f64 = bodies[j].m * inv3;
                ax = ax + dx * mm;
                ay = ay + dy * mm;
                az = az + dz * mm;
            }
            axv[i] = ax;
            ayv[i] = ay;
            azv[i] = az;
        }
        // phase 2: integrate (x uses the freshly updated v)
        for i in 0..B {
            let b = &mut bodies[i];
            b.vx = b.vx + axv[i] * DT;
            b.vy = b.vy + ayv[i] * DT;
            b.vz = b.vz + azv[i] * DT;
            b.x = b.x + b.vx * DT;
            b.y = b.y + b.vy * DT;
            b.z = b.z + b.vz * DT;
        }
    }
    let mut s: f64 = 0.0;
    for i in 0..B {
        s += bodies[i].x
            + bodies[i].y
            + bodies[i].z
            + bodies[i].vx
            + bodies[i].vy
            + bodies[i].vz
            + bodies[i].m;
    }
    (s * 65536.0) as i64
}

fn main() {
    let t0 = std::time::Instant::now();
    let cs = hot();
    let ns = t0.elapsed().as_nanos() as u64;
    println!("TIME {}", ns);
    println!("CS {}", cs);
}
