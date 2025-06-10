use garbled_neural_net_experiments::transformer::*;
use fancy_garbling::twopac::semihonest::{Garbler, Evaluator};
use fancy_garbling::Fancy;
use fancy_garbling::FancyInput;
use ocelot::ot::{AlszReceiver as OtReceiver, AlszSender as OtSender};
use scuttlebutt::{unix_channel_pair, AesRng, UnixChannel};
use std::io::{self, Read};

fn main() {
    // Create a Unix channel pair
    let (sender, receiver) = unix_channel_pair();

    // Spawn evaluator thread
    std::thread::spawn(move || {
        let rng = AesRng::new();
        let mut ev = Evaluator::<UnixChannel, AesRng, OtReceiver>::new(receiver, rng).unwrap();
        // Read evaluator input from stdin as whitespace-separated numbers
        let mut input_str = String::new();
        io::stdin().read_to_string(&mut input_str).unwrap();
        let x_plain: Vec<u16> = input_str
            .split_whitespace()
            .filter_map(|s| s.parse().ok())
            .collect();
        let moduli = vec![1 << 15; x_plain.len()];
        let x_wires = ev.encode_many(&x_plain, &moduli).unwrap();
        let params = Params::load();
        let out = mini_transformer(&mut ev, &x_wires, &params);
        let res: Vec<u16> = out.iter().map(|w| ev.output(w).unwrap().unwrap()).collect();
        println!("{:?}", res);
    });

    // Garbler side
    let rng = AesRng::new();
    let mut gb = Garbler::<UnixChannel, AesRng, OtSender>::new(sender, rng).unwrap();
    let params = Params::load();
    let dummy_x = vec![gb.constant(0, 1 << 15).unwrap(); params.d_model];
    mini_transformer(&mut gb, &dummy_x, &params);
}
