# O4 — Redundant Noisy Record Bound

For q independent copies of a bit with flip probability p<1/2, majority decoding fails when at least q/2 copies flip. Hoeffding gives

`P(error) <= exp(-2 q (1/2-p)^2)`.

For N clock states and E record coordinates, a union bound over N*E entries gives

`P(full table correct) >= 1 - N E exp(-2 q (1/2-p)^2)`.

The implementation must also calculate the exact binomial tail; Hoeffding is reported as a conservative sufficient bound.

## G1 verification

`results/processed/T104_noise_bound_grid.json` evaluates odd `q` values in
`{1,3,5,7,9,11,15}` and `p` values below `1/2`. No exact-binomial error exceeds
the Hoeffding upper bound in this grid.
