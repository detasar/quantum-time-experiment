# O1 — Chain Characterization Proof Obligation

Let `B:T -> {0,1}^E` and define `t <=_B t'` iff `B(t) <= B(t')` coordinate-wise.

A sequence `(t_0,...,t_k)` is persistent iff every coordinate is nondecreasing along the sequence.

## Claim
The persistent sequences are exactly the chains of the preorder induced by `<=_B`, after quotienting duplicate signatures.

## Proof
If the sequence is persistent, then for every `i<j`, each coordinate satisfies `b_e(t_i)<=b_e(t_j)`, hence `t_i<=_B t_j`; the sequence is a chain. Conversely, a chain can be indexed in dominance order, and every coordinate is nondecreasing, hence the sequence is persistent.

## Corollary
A single scalar trajectory containing every distinct signature exists iff the quotient poset is a chain.

## Important non-result
An arbitrary linear extension of a branching poset is not necessarily persistent as an adjacent physical sequence.

## G1 verification

`results/processed/T101_chain_verification.json` checks 272 small distinct
record codes and 188,158 candidate sequences with zero mismatches. The diamond
fixture has two maximal persistent chains, two scheduler linear extensions and
zero full persistent scalar orders.
