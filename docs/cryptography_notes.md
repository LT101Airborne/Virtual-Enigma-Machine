# Enigma Machine — Cryptography Notes

Technical deep-dive into the mathematics and mechanics behind the Enigma cipher.

---

## 1. Signal Path Mathematics

Each component of the Enigma can be modeled as a permutation of the 26-letter alphabet (Z₂₆).

Let:
- **P** = plugboard permutation
- **Rᵢ** = rotor i permutation (position-dependent)
- **U** = reflector permutation

The encryption function for a single keypress is:

```
E(x) = P ∘ R₁ ∘ R₂ ∘ R₃ ∘ U ∘ R₃⁻¹ ∘ R₂⁻¹ ∘ R₁⁻¹ ∘ P(x)
```

Because U is an involution (U = U⁻¹) and P = P⁻¹, the full function satisfies:

```
E(E(x)) = x   for all x
```

This is the **self-reciprocal property** — the mathematical foundation of Enigma's encrypt-equals-decrypt behavior.

---

## 2. The No-Self-Encryption Property

A critical consequence of U being a fixed-point-free involution (U(x) ≠ x for all x) is that the complete Enigma permutation E is also fixed-point-free:

```
E(x) ≠ x   for all x ∈ Z₂₆
```

This was an operational convenience (operators could verify settings by checking that input ≠ output) but became a cryptographic catastrophe: it gave Bletchley Park a known constraint to exploit in their bombe attacks.

---

## 3. Rotor Position Mathematics

A rotor with position `p` and ring setting `r` transforms signal `s` as:

```python
# Forward pass (right to left)
shifted  = (s + p - r) % 26
mapped   = ALPHABET.index(WIRING[shifted])
output   = (mapped - p + r) % 26
```

The ring setting introduces an additional static offset to the wiring, separate from the dynamic position offset. Combined, they give each rotor 26 × 26 = 676 possible states — but only the position changes during operation.

---

## 4. Rotor Stepping & The Double-Step

Rotors step in an odometer-like fashion, but with a critical anomaly: the **double-stepping** of the middle rotor.

Normal carry-propagation (like a car odometer):
```
Right rotor steps every keypress
Middle rotor steps when right rotor passes its notch
Left rotor steps when middle rotor passes its notch
```

The anomaly: when the middle rotor is at its own notch, it steps **again** on the next keypress — advancing two positions in two consecutive presses:

```
Positions AEV → BFW   (not AFW)
          ↑↑
          Both left and middle stepped
```

This was a mechanical artifact of the Enigma's pawl-and-ratchet mechanism. It shortened the effective period from 26³ = 17,576 to a slightly irregular sequence, but the irregularity itself made some attacks harder.

---

## 5. Key Space Calculation

For the Naval M3 (3 rotors chosen from 8):

```
Rotor selection order:   8 × 7 × 6          =      336
Ring settings:           26³                 =   17,576
Start positions:         26³                 =   17,576
Plugboard (10 pairs):    C(26,2)×C(24,2)×…  ≈ 1.5 × 10¹⁴
─────────────────────────────────────────────────────────
Total key space:                             ≈ 1.1 × 10²³
```

At 1 million keys/second, exhaustive search would take ~3.4 × 10⁹ years — infeasible without mathematical shortcuts.

---

## 6. Known Attacks

### Crib-Based Attack (Turing's Bombe)
Operators often sent stereotyped messages ("WETTERBERICHT" = weather report, "KEINE BESONDEREN EREIGNISSE" = nothing to report). These **cribs** gave Bletchley known plaintext to work with.

Given a crib, analysts searched for a position in the ciphertext where the crib could align without any letter mapping to itself. This pruned the search space dramatically, and the bombe mechanically tested remaining candidates.

### Index of Coincidence
The index of coincidence (IC) measures how much a ciphertext resembles a natural language:
```
IC = Σ nᵢ(nᵢ-1) / N(N-1)
```
- English plaintext: IC ≈ 0.065
- Random ciphertext: IC ≈ 0.038
- Enigma output: IC ≈ 0.038–0.040

Enigma's IC was close to random — a sign of strong polyalphabetic encryption.

---

## 7. Modern Cryptographic Lessons

| Enigma Weakness | Modern Mitigation |
|-----------------|-------------------|
| No letter encrypts to itself (fixed-point-free) | AES S-Box has no fixed points by design |
| Key reused daily; operator laziness (AAA starts) | Cryptographic key rotation policies; IV randomness requirements |
| Known-plaintext cribs exploited | Authenticated encryption (AEAD) prevents plaintext inference |
| Short period (< 17,576 characters) | AES-CTR has period 2¹²⁸ |
| Operator stereotypes (greeting conventions) | Padded / randomized message formats |

---

## 8. Implementing Correctness Checks

The three canonical self-tests for any Enigma implementation:

```python
# 1. Self-reciprocity
assert machine.encrypt(machine.encrypt(msg, reset=True)) == msg

# 2. No self-encryption
for c in ALPHABET:
    assert machine.encrypt(c) != c

# 3. Reflector involution
for i in range(26):
    assert reflector.reflect(reflector.reflect(i)) == i
```

All three are verified in `tests/test_enigma.py`.
