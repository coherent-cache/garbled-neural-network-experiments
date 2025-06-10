use crate::gc_layers::{matvec, relu, gt_const};
use fancy_garbling::Fancy;

/// Holder for quantized Transformer weights.
#[derive(Clone)]
pub struct Params {
    pub w_q: Vec<Vec<u16>>, // (d_model x d_model)
    pub w_k: Vec<Vec<u16>>, // (d_model x d_model)
    pub w_v: Vec<Vec<u16>>, // (d_model x d_model)
    pub w_ff1: Vec<Vec<u16>>,
    pub w_ff2: Vec<Vec<u16>>,
    pub scale: u16,
    pub thresh: u16,
    pub d_model: usize,
}

impl Params {
    /// Load parameters from disk. Here we simply generate dummy values
    /// to keep the example self contained.
    pub fn load() -> Self {
        // small demo with d_model=4
        let d = 4;
        let dummy = vec![vec![1u16; d]; d];
        Self {
            w_q: dummy.clone(),
            w_k: dummy.clone(),
            w_v: dummy.clone(),
            w_ff1: dummy.clone(),
            w_ff2: dummy.clone(),
            scale: 1,
            thresh: 0,
            d_model: d,
        }
    }
}

/// A single-layer encoder block.
pub fn mini_transformer<F: Fancy>(
    f: &mut F,
    x: &[F::Item],
    params: &Params,
) -> Vec<F::Item> {
    // 1) Q = W_Q x ;  K = W_K x ; V = W_V x
    let q = matvec(f, &params.w_q, x);
    let k = matvec(f, &params.w_k, x);
    let v = matvec(f, &params.w_v, x);

    // 2) score = (Q·K) * scale
    let mut score = f.constant(0, 1 << 15).unwrap();
    for (q_i, k_i) in q.iter().zip(&k) {
        let prod = f.mul(q_i, k_i).unwrap();
        score = f.add(&score, &prod).unwrap();
    }
    score = f.cmul(&score, params.scale).unwrap();
    // Demo shortcut: treat score as gate
    let gate = gt_const(f, &score, params.thresh);
    // 3) context = gate * V
    let context: Vec<_> = v
        .iter()
        .map(|v_i| f.mul(&gate, v_i).unwrap())
        .collect();

    // 4) FFN: y = W2 · ReLU(W1·context)
    let z1 = matvec(f, &params.w_ff1, &context)
        .into_iter()
        .map(|w| relu(f, w))
        .collect::<Vec<_>>();
    matvec(f, &params.w_ff2, &z1)
}
