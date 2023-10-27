// benches/benchmark.rs
#[cfg(test)]
mod benches {
    use test::Bencher;

    use super::*;

    #[bench]
    fn benchmark_hello_world(b: &mut Bencher) {
        b.iter(|| {
            main();
        });
    }
}
