use crate::gc_layers::*;
use fancy_garbling::{Fancy, HasModulus};

/// Transformer model parameters
#[derive(Clone, Debug)]
pub struct Params {
    pub d_model: usize,    // Model dimension (e.g., 32)
    pub d_ff: usize,       // Feed-forward dimension (e.g., 128)
    pub seq_len: usize,    // Sequence length (e.g., 16)
    pub vocab_size: usize, // Vocabulary size (e.g., 256)

    // Weights (quantized to 16-bit fixed point with 8 fractional bits)
    pub w_q: Vec<Vec<u16>>,   // Query weights: d_model × d_model
    pub w_k: Vec<Vec<u16>>,   // Key weights: d_model × d_model
    pub w_v: Vec<Vec<u16>>,   // Value weights: d_model × d_model
    pub w_o: Vec<Vec<u16>>,   // Output weights: d_model × d_model
    pub w_ff1: Vec<Vec<u16>>, // First FF layer: d_model × d_ff
    pub w_ff2: Vec<Vec<u16>>, // Second FF layer: d_ff × d_model
    pub embed: Vec<Vec<u16>>, // Embedding: vocab_size × d_model
}

impl Params {
    /// Load parameters (currently returns dummy parameters)
    /// TODO: Load from PyTorch checkpoint
    pub fn load() -> Self {
        let d_model = 32;
        let d_ff = 128;
        let seq_len = 16;
        let vocab_size = 256;

        // Initialize with small random values (scaled by 2^8 for fixed point)
        let init_weight = || (rand::random::<u16>() % 512) + 128; // Range: 0.5-2.5 in fixed point

        Self {
            d_model,
            d_ff,
            seq_len,
            vocab_size,
            w_q: (0..d_model)
                .map(|_| (0..d_model).map(|_| init_weight()).collect())
                .collect(),
            w_k: (0..d_model)
                .map(|_| (0..d_model).map(|_| init_weight()).collect())
                .collect(),
            w_v: (0..d_model)
                .map(|_| (0..d_model).map(|_| init_weight()).collect())
                .collect(),
            w_o: (0..d_model)
                .map(|_| (0..d_model).map(|_| init_weight()).collect())
                .collect(),
            w_ff1: (0..d_ff)
                .map(|_| (0..d_model).map(|_| init_weight()).collect())
                .collect(),
            w_ff2: (0..d_model)
                .map(|_| (0..d_ff).map(|_| init_weight()).collect())
                .collect(),
            embed: (0..vocab_size)
                .map(|_| (0..d_model).map(|_| init_weight()).collect())
                .collect(),
        }
    }
}

/// Embedding layer: token IDs -> dense vectors
pub fn embedding<F: Fancy>(
    f: &mut F,
    token_ids: &[F::Item],      // Input token IDs (seq_len)
    embed_weights: &[Vec<u16>], // Embedding matrix (vocab_size × d_model)
) -> Vec<Vec<F::Item>> {
    token_ids
        .iter()
        .map(|token_id| {
            // For each token, lookup its embedding vector
            // This requires a more sophisticated lookup mechanism in GC
            // For now, we'll use a simplified approach with projection
            embed_weights[0]
                .iter()
                .map(|&weight| f.cmul(token_id, weight).unwrap())
                .collect()
        })
        .collect()
}

/// Simplified attention mechanism (no softmax, scaled dot-product)
pub fn attention<F: Fancy>(
    f: &mut F,
    x: &[Vec<F::Item>], // Input: seq_len × d_model
    w_q: &[Vec<u16>],   // Query weights
    w_k: &[Vec<u16>],   // Key weights
    w_v: &[Vec<u16>],   // Value weights
    w_o: &[Vec<u16>],   // Output weights
) -> Vec<Vec<F::Item>> {
    let seq_len = x.len();
    let d_model = x[0].len();

    // Compute Q, K, V for each position
    let mut queries = Vec::new();
    let mut keys = Vec::new();
    let mut values = Vec::new();

    for pos in 0..seq_len {
        queries.push(matvec(f, w_q, &x[pos]));
        keys.push(matvec(f, w_k, &x[pos]));
        values.push(matvec(f, w_v, &x[pos]));
    }

    // Simplified attention: direct weighted combination (no softmax)
    let mut attended = Vec::new();
    for i in 0..seq_len {
        let mut context = vec![f.constant(0, 1 << 15).unwrap(); d_model];

        for j in 0..seq_len {
            // Compute attention weight as dot product of queries and keys
            let mut attention_weight = f.constant(0, 1 << 15).unwrap();
            for k in 0..d_model {
                let prod = f.mul(&queries[i][k], &keys[j][k]).unwrap();
                attention_weight = f.add(&attention_weight, &prod).unwrap();
            }

            // Scale down attention weight (divide by d_model for stability)
            let scale_factor = 256 / d_model as u16; // Fixed point scaling
            attention_weight = f.cmul(&attention_weight, scale_factor).unwrap();

            // Apply attention weight to values
            for k in 0..d_model {
                let weighted_value = f.mul(&attention_weight, &values[j][k]).unwrap();
                context[k] = f.add(&context[k], &weighted_value).unwrap();
            }
        }

        attended.push(context);
    }

    // Apply output projection
    attended
        .iter()
        .map(|context| matvec(f, w_o, context))
        .collect()
}

/// Feed-forward network with ReLU activation
pub fn feed_forward<F: Fancy>(
    f: &mut F,
    x: &[Vec<F::Item>], // Input: seq_len × d_model
    w_ff1: &[Vec<u16>], // First layer weights: d_model → d_ff
    w_ff2: &[Vec<u16>], // Second layer weights: d_ff → d_model
) -> Vec<Vec<F::Item>> {
    x.iter()
        .map(|pos_embedding| {
            // First layer: d_model → d_ff with ReLU
            let hidden = matvec(f, w_ff1, pos_embedding);
            let hidden_relu: Vec<F::Item> = hidden.into_iter().map(|h| relu(f, h)).collect();

            // Second layer: d_ff → d_model
            matvec(f, w_ff2, &hidden_relu)
        })
        .collect()
}

/// Single transformer layer: attention + feed-forward with residual connections
pub fn transformer_layer<F: Fancy>(
    f: &mut F,
    x: &[Vec<F::Item>], // Input: seq_len × d_model
    w_q: &[Vec<u16>],
    w_k: &[Vec<u16>],
    w_v: &[Vec<u16>],
    w_o: &[Vec<u16>],
    w_ff1: &[Vec<u16>],
    w_ff2: &[Vec<u16>],
) -> Vec<Vec<F::Item>> {
    // Self-attention
    let attn_out = attention(f, x, w_q, w_k, w_v, w_o);

    // Residual connection: x + attention(x)
    let mut after_attn = Vec::new();
    for i in 0..x.len() {
        let mut residual = Vec::new();
        for j in 0..x[i].len() {
            residual.push(f.add(&x[i][j], &attn_out[i][j]).unwrap());
        }
        after_attn.push(residual);
    }

    // Feed-forward
    let ff_out = feed_forward(f, &after_attn, w_ff1, w_ff2);

    // Residual connection: x + ff(x)
    let mut output = Vec::new();
    for i in 0..after_attn.len() {
        let mut residual = Vec::new();
        for j in 0..after_attn[i].len() {
            residual.push(f.add(&after_attn[i][j], &ff_out[i][j]).unwrap());
        }
        output.push(residual);
    }

    output
}

/// Mini transformer model: embedding + single transformer layer
pub fn mini_transformer<F: Fancy>(
    f: &mut F,
    token_ids: &[F::Item], // Input token IDs
    params: &Params,
) -> Vec<F::Item> {
    // Embedding layer
    let embedded = embedding(f, token_ids, &params.embed);

    // Single transformer layer
    let transformed = transformer_layer(
        f,
        &embedded,
        &params.w_q,
        &params.w_k,
        &params.w_v,
        &params.w_o,
        &params.w_ff1,
        &params.w_ff2,
    );

    // Return the last position's output
    transformed.last().unwrap().clone()
}
