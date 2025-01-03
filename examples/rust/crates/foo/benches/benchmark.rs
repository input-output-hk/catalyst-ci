//! Simple benchmark example
use criterion::{black_box, criterion_group, criterion_main, Criterion};

/// fibonacci calculates the nth fibonacci number
fn fibonacci(n: u64) -> u64 {
    match n {
        0 | 1 => 1,
        n => fibonacci(n.saturating_sub(1)).saturating_add(fibonacci(n.saturating_sub(2))),
    }
}

/// run a criterion benchmark
fn criterion_benchmark(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

#[allow(missing_docs)]
pub mod foo_bench {
    use super::{criterion_benchmark, criterion_group};
    criterion_group!(benches, criterion_benchmark);
}

use foo_bench::benches;
criterion_main!(benches);
