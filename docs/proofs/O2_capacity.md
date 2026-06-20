# O2/O3 — Persistent Record Capacity

## Binary case
A strict chain in the Boolean lattice `{0,1}^E` increases Hamming weight by at least one at every strict step. Hamming weight ranges from 0 to E, so a strict chain has at most E+1 elements. The thermometer code attains E+1.

Therefore N distinct clock states in one persistent scalar trajectory require E >= N-1 binary record coordinates.

## Multi-level case
For coordinate e with L_e ordered levels, the rank function is the sum of coordinate levels. A strict step increases rank by at least one. The rank range has length `sum_e(L_e-1)`, so the maximum chain length is `1+sum_e(L_e-1)`.
