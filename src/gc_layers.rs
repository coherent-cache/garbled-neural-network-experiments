use fancy_garbling::{Fancy, HasModulus};

/// Encode a public 16-bit constant vector into GC wires
pub fn const_vec<F: Fancy>(f: &mut F, v: &[u16]) -> Vec<F::Item> {
    v.iter().map(|&c| f.constant(c, 1 << 15).unwrap()).collect()
}

/// One matrix-vector multiply with public W (shape m×n) and secret x (len n)
pub fn matvec<F: Fancy>(
    f: &mut F,
    w: &[Vec<u16>],    // rows
    x: &[F::Item],
) -> Vec<F::Item> {
    w.iter().map(|row| {
        let mut acc = f.constant(0, 1 << 15).unwrap();
        for (&w_ij, x_j) in row.iter().zip(x) {
            let prod = f.cmul(x_j, w_ij).unwrap();   // 1 HG
            acc = f.add(&acc, &prod).unwrap();
        }
        acc
    }).collect()
}

/// ReLU(x) = max(x,0) using Ball-Rosulek 1-AND comparator
pub fn relu<F: Fancy>(f: &mut F, x: F::Item) -> F::Item {
    let is_pos = gt_const(f, &x, 0);
    f.mul(&is_pos, &x).unwrap()
}

/// Compare `x` against a constant `c`, returning 1 if `x > c` else 0.
pub fn gt_const<F: Fancy>(f: &mut F, x: &F::Item, c: u16) -> F::Item {
    let q = x.modulus();
    let tt: Vec<u16> = (0..q).map(|v| if v > c { 1 } else { 0 }).collect();
    f.proj(x, 2, Some(tt)).unwrap()
}
