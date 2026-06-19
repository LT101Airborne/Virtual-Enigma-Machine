# Virtual Enigma Machine

A faithful simulation of the **German Naval Enigma M3** cipher machine, implemented in Python. Models the complete signal path — plugboard wiring, rotor substitution with stepping mechanics, and reflector — that made Enigma one of history's most complex cipher systems.

```
  ███████╗███╗   ██╗██╗ ██████╗ ███╗   ███╗ █████╗
  ██╔════╝████╗  ██║██║██╔════╝ ████╗ ████║██╔══██╗
  █████╗  ██╔██╗ ██║██║██║  ███╗██╔████╔██║███████║
  ██╔══╝  ██║╚██╗██║██║██║   ██║██║╚██╔╝██║██╔══██║
  ███████╗██║ ╚████║██║╚██████╔╝██║ ╚═╝ ██║██║  ██║
  ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝
```

---

## Features

- **Full rotor simulation** — all 8 Wehrmacht/Kriegsmarine rotors (I–VIII) with historically accurate wirings and notch positions
- **Plugboard (Steckerbrett)** — up to 13 configurable letter-swap pairs
- **Three reflectors** — UKW-A, UKW-B, UKW-C
- **Double-stepping anomaly** — the famous mechanical quirk that weakened Enigma's periodicity
- **Ring settings (Ringstellung)** — per-rotor offset configuration
- **Self-reciprocal cipher** — the same settings encrypt and decrypt
- **CLI** — interactive terminal interface with grouped output
- **100% test coverage** of core cryptographic mechanics

---

## How It Works

Each keypress on the Enigma routed an electrical signal through up to five components:

```
Keypress
   │
   ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
│Plugboard │────▶│  Rotor   │────▶│  Rotor   │────▶│  Rotor   │────▶│ Reflector  │
│(Stecker) │     │  III     │     │  II      │     │  I       │     │  (UKW-B)   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └────────────┘
   ▲                  │                 │                 │                 │
   │                  ◀─────────────────◀─────────────────◀─────────────────┘
   │
   ▼
 Lamp (output letter)
```

The rotor stack steps before each character is encrypted, ensuring no two consecutive keypresses follow the same substitution path — producing a **polyalphabetic cipher** with a period of over 16,000 characters.

### Signal Path

1. **Plugboard (entry)** — swaps the input letter if wired
2. **Rotors right → left** — each rotor performs a Caesar-like substitution adjusted for its current position and ring setting
3. **Reflector** — routes the signal back through the rotors on a different path
4. **Rotors left → right** — reverse substitution path
5. **Plugboard (exit)** — final swap before the output lamp lights

---

## Project Structure

```
enigma-machine/
├── enigma.py          # Core simulation: Rotor, Plugboard, Reflector, EnigmaMachine
├── cli.py             # Command-line interface
├── examples/
│   └── example_usage.py   # Annotated usage examples
├── tests/
│   └── test_enigma.py     # Pytest unit tests
├── docs/
│   └── cryptography_notes.md  # Deep-dive on Enigma's mathematics
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/enigma-machine.git
cd enigma-machine

# No external dependencies for core simulation
python enigma.py    # Import and use as a module

# Run the built-in demo
python cli.py demo

# Encrypt a message
python cli.py encrypt "HELLO WORLD" --rotors I II III --positions AAA

# Decrypt (same settings)
python cli.py encrypt "MFNCUOQNLN" --rotors I II III --positions AAA

# Run tests
pip install pytest
python -m pytest tests/ -v
```

---

## API Reference

### `EnigmaMachine.from_key_sheet()`

```python
from enigma import EnigmaMachine

machine = EnigmaMachine.from_key_sheet(
    rotors=["I", "II", "III"],       # Rotor names, left to right
    reflector="UKW-B",               # UKW-A, UKW-B, or UKW-C
    ring_settings=[1, 1, 1],         # Ringstellung 1–26 per rotor
    start_positions="MCK",           # Window letters
    plugboard_pairs=["AB", "CD"],    # Stecker pairs (up to 13)
)

ciphertext = machine.encrypt("ATTACK AT DAWN")
print(ciphertext)  # → e.g. "PKWIQ ZV HBYJ"

# Decrypt: reset positions and encrypt again
machine.set_positions("MCK")
plaintext = machine.encrypt(ciphertext.replace(" ", ""))
print(plaintext)   # → "ATTACKATDAWN"
```

### Rotor Options

| Rotor  | Turnover | Notes                    |
|--------|----------|--------------------------|
| I      | Q        | Wehrmacht standard        |
| II     | E        | Wehrmacht standard        |
| III    | V        | Wehrmacht standard        |
| IV     | J        | Wehrmacht extended        |
| V      | Z        | Wehrmacht extended        |
| VI     | Z, M     | Kriegsmarine (Naval)      |
| VII    | Z, M     | Kriegsmarine (Naval)      |
| VIII   | Z, M     | Kriegsmarine (Naval)      |

### Reflector Options

| Reflector | Notes                         |
|-----------|-------------------------------|
| UKW-A     | Early variant                 |
| UKW-B     | Most widely used              |
| UKW-C     | Late-war Naval variant        |

---

## CLI Reference

```bash
# List all available rotors and reflectors
python cli.py list-parts

# Encrypt with full configuration
python cli.py encrypt "WEATHER REPORT" \
    --rotors I II III \
    --reflector UKW-B \
    --rings 1 1 1 \
    --positions MCK \
    --plugboard AV BS CG DL FU \
    --group   # format output as 5-letter groups

# Interactive live encryption session
python cli.py interactive --rotors I II III --positions AAA

# Built-in historical demo
python cli.py demo
```

---

## Cryptographic Notes

### Why Enigma Was Hard to Break

- **Polyalphabetic substitution** — the cipher alphabet changed with every keypress
- **Key space** — rotor order × ring settings × start positions × plugboard ≈ **10¹¹⁴** combinations
- **Self-reciprocity** — the same configuration encrypts and decrypts, simplifying operator workflow but creating the constraint that *no letter can ever encrypt to itself*

### How Bletchley Park Broke It

Alan Turing and Gordon Welchman exploited that no letter maps to itself (eliminating huge portions of the key space) along with known plaintext ("cribs") to build electro-mechanical bombe machines that tested configurations at speed. By 1941 they could reliably read Kriegsmarine traffic within hours of interception.

### Modern Relevance

Enigma's weaknesses directly informed modern symmetric cipher design:
- **AES** uses an S-Box that is explicitly non-identity (no fixed points), a lesson learned from Enigma
- **IV (initialization vectors)** in stream ciphers address the key-reuse vulnerability that daily Enigma settings created
- **Known-plaintext attacks** against Enigma pioneered the methodology still used in modern differential cryptanalysis

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

Tests verify:
- Self-reciprocity across multiple rotor/plugboard configurations
- The double-stepping anomaly
- Rotor turnover at correct notch positions
- Plugboard bijection and error handling
- Reflector involution (`reflect(reflect(x)) == x`)
- No letter ever encrypts to itself

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## References

- [Crypto Museum — Enigma](https://www.cryptomuseum.com/crypto/enigma/)
- Singh, S. (1999). *The Code Book*. Doubleday.
- Welchman, G. (1982). *The Hut Six Story*. McGraw-Hill.
- [Wikipedia — Enigma machine](https://en.wikipedia.org/wiki/Enigma_machine)
