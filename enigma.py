"""
Virtual Enigma Machine — Naval M3 Variant
==========================================
Simulates the German Naval Enigma cipher machine used in World War II,
modeling rotor mechanics, plugboard wiring, and multi-step substitution
encryption.

Historical context:
    The Enigma machine was an electro-mechanical cipher device used by
    Nazi Germany. The Naval variant (M3/M4) added extra rotors, making
    it significantly harder to crack. Alan Turing and the team at
    Bletchley Park famously broke the cipher in 1941.

Author: GitHub Portfolio Project
Year:   2024
"""

from __future__ import annotations
from typing import Optional


# ---------------------------------------------------------------------------
# Historical Rotor Wirings (Wehrmacht / Kriegsmarine)
# ---------------------------------------------------------------------------

ROTOR_WIRINGS: dict[str, str] = {
    "I":   "EKMFLGDQVZNTOWYHXUSPAIBRCJ",   # Turnover at Q → R
    "II":  "AJDKSIRUXBLHWTMCQGZNPYFVOE",   # Turnover at E → F
    "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",   # Turnover at V → W
    "IV":  "ESOVPZJAYQUIRHXLNFTGKDCMWB",   # Turnover at J → K
    "V":   "VZBRGITYUPSDNHLXAWMJQOFECK",   # Turnover at Z → A
    # Naval extras
    "VI":   "JPGVOUMFYQBENHZRDKASXLICTW",
    "VII":  "NZJHGRCXMYSWBOUFAIVLPEKQDT",
    "VIII": "FKQHTLXOCBJSPDZRAMEWNIUYGV",
}

ROTOR_NOTCHES: dict[str, str] = {
    "I": "Q", "II": "E", "III": "V",
    "IV": "J", "V": "Z",
    "VI": "ZM", "VII": "ZM", "VIII": "ZM",
}

REFLECTOR_WIRINGS: dict[str, str] = {
    "UKW-A": "EJMZALYXVBWFCRQUONTSPIKHGD",
    "UKW-B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",   # Most common
    "UKW-C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ---------------------------------------------------------------------------
# Rotor
# ---------------------------------------------------------------------------

class Rotor:
    """
    Models a single Enigma rotor with forward/backward substitution,
    ring setting offset, and notch-based turnover mechanics.
    """

    def __init__(self, name: str, ring_setting: int = 1, start_position: str = "A") -> None:
        if name not in ROTOR_WIRINGS:
            raise ValueError(f"Unknown rotor '{name}'. Choose from: {list(ROTOR_WIRINGS)}")

        self.name = name
        self.wiring = ROTOR_WIRINGS[name]
        self.notches = ROTOR_NOTCHES.get(name, "")
        self.ring_setting = ring_setting - 1          # Convert 1-indexed → 0-indexed
        self.position = ALPHABET.index(start_position.upper())

    # ------------------------------------------------------------------
    # Position helpers
    # ------------------------------------------------------------------

    @property
    def position_letter(self) -> str:
        return ALPHABET[self.position]

    def at_notch(self) -> bool:
        """Return True if this rotor's notch is engaged (triggers next rotor)."""
        return self.position_letter in self.notches

    def step(self) -> None:
        """Advance the rotor by one position."""
        self.position = (self.position + 1) % 26

    # ------------------------------------------------------------------
    # Signal path
    # ------------------------------------------------------------------

    def _offset(self, index: int) -> int:
        return (index + self.position - self.ring_setting) % 26

    def _reverse_offset(self, index: int) -> int:
        return (index - self.position + self.ring_setting) % 26

    def forward(self, signal: int) -> int:
        """Pass a signal through the rotor right-to-left (entry side)."""
        shifted = self._offset(signal)
        mapped = ALPHABET.index(self.wiring[shifted])
        return self._reverse_offset(mapped)

    def backward(self, signal: int) -> int:
        """Pass a signal through the rotor left-to-right (return path)."""
        shifted = self._offset(signal)
        mapped = self.wiring.index(ALPHABET[shifted])
        return self._reverse_offset(mapped)

    def __repr__(self) -> str:
        return f"Rotor({self.name}, pos={self.position_letter}, ring={self.ring_setting + 1})"


# ---------------------------------------------------------------------------
# Plugboard (Steckerbrett)
# ---------------------------------------------------------------------------

class Plugboard:
    """
    Models the Enigma plugboard — a set of letter-pair swaps applied
    before and after the rotor stack.

    Pairs are bidirectional: 'AB' means A↔B.
    A real Enigma allowed 0–13 pairs (10 was standard in the field).
    """

    def __init__(self, pairs: Optional[list[str]] = None) -> None:
        self.mapping: dict[str, str] = {}
        if pairs:
            self.configure(pairs)

    def configure(self, pairs: list[str]) -> None:
        """
        Configure plugboard with a list of letter pairs.
        Example: ['AB', 'CD', 'EF']
        """
        self.mapping = {}
        for pair in pairs:
            pair = pair.upper().strip()
            if len(pair) != 2:
                raise ValueError(f"Each plugboard pair must be exactly 2 letters, got '{pair}'")
            a, b = pair[0], pair[1]
            if a == b:
                raise ValueError(f"Plugboard pair cannot connect a letter to itself: '{pair}'")
            if a in self.mapping or b in self.mapping:
                raise ValueError(f"Letter already used in plugboard: '{pair}'")
            self.mapping[a] = b
            self.mapping[b] = a

    def swap(self, letter: str) -> str:
        """Return the plugboard-swapped letter (or the original if unplugged)."""
        return self.mapping.get(letter, letter)

    def __repr__(self) -> str:
        pairs = [f"{a}{b}" for a, b in self.mapping.items() if a < b]
        return f"Plugboard(pairs={pairs})"


# ---------------------------------------------------------------------------
# Reflector (Umkehrwalze)
# ---------------------------------------------------------------------------

class Reflector:
    """
    The Enigma reflector routes the signal back through the rotors.
    It has no moving parts and ensures the cipher is self-reciprocal
    (encrypt and decrypt use the same operation).
    """

    def __init__(self, name: str = "UKW-B") -> None:
        if name not in REFLECTOR_WIRINGS:
            raise ValueError(f"Unknown reflector '{name}'. Choose from: {list(REFLECTOR_WIRINGS)}")
        self.name = name
        self.wiring = REFLECTOR_WIRINGS[name]

    def reflect(self, signal: int) -> int:
        return ALPHABET.index(self.wiring[signal])

    def __repr__(self) -> str:
        return f"Reflector({self.name})"


# ---------------------------------------------------------------------------
# Enigma Machine
# ---------------------------------------------------------------------------

class EnigmaMachine:
    """
    Full simulation of the German Naval Enigma (M3 variant).

    Signal path for each keypress:
        Plugboard → Rotor III → Rotor II → Rotor I → Reflector
                  → Rotor I  → Rotor II → Rotor III → Plugboard → Lamp

    The machine is self-reciprocal: the same settings decrypt ciphertext.

    Example usage:
        machine = EnigmaMachine.from_key_sheet(
            rotors=["I", "II", "III"],
            reflector="UKW-B",
            ring_settings=[1, 1, 1],
            start_positions="AAA",
            plugboard_pairs=["AB", "CD"]
        )
        cipher = machine.encrypt("HELLO WORLD")
        # Reset to same settings, then decrypt:
        machine.set_positions("AAA")
        plain  = machine.encrypt(cipher)
    """

    def __init__(
        self,
        rotors: list[Rotor],
        reflector: Reflector,
        plugboard: Plugboard,
    ) -> None:
        if len(rotors) < 3:
            raise ValueError("Enigma requires at least 3 rotors.")
        # rotors[0] = leftmost (slow), rotors[-1] = rightmost (fast)
        self.rotors = rotors
        self.reflector = reflector
        self.plugboard = plugboard

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_key_sheet(
        cls,
        rotors: list[str],
        reflector: str = "UKW-B",
        ring_settings: Optional[list[int]] = None,
        start_positions: str = "AAA",
        plugboard_pairs: Optional[list[str]] = None,
    ) -> "EnigmaMachine":
        """
        Construct an Enigma machine from human-readable key-sheet values.

        Args:
            rotors:           Rotor names left-to-right, e.g. ['I', 'II', 'III']
            reflector:        Reflector name, e.g. 'UKW-B'
            ring_settings:    Ring (Ringstellung) settings 1–26 per rotor
            start_positions:  Starting window letters, e.g. 'AAA' or 'MCK'
            plugboard_pairs:  Stecker pairs, e.g. ['AB', 'CD', 'EF']
        """
        ring_settings = ring_settings or [1] * len(rotors)
        positions = start_positions.upper().ljust(len(rotors), "A")

        rotor_objects = [
            Rotor(name, ring, pos)
            for name, ring, pos in zip(rotors, ring_settings, positions)
        ]
        return cls(
            rotors=rotor_objects,
            reflector=Reflector(reflector),
            plugboard=Plugboard(plugboard_pairs or []),
        )

    # ------------------------------------------------------------------
    # Rotor stepping (double-stepping anomaly included)
    # ------------------------------------------------------------------

    def _step_rotors(self) -> None:
        """
        Advance rotors according to Enigma's double-stepping mechanism.
        The middle rotor steps again if it is at its own notch position.
        """
        r = self.rotors  # left … right
        # Double-step: middle rotor at notch causes itself AND left to step
        if len(r) >= 3 and r[-2].at_notch():
            r[-2].step()
            r[-3].step()
        elif r[-1].at_notch():
            r[-2].step()
        # Rightmost always steps
        r[-1].step()

    # ------------------------------------------------------------------
    # Single-character encryption
    # ------------------------------------------------------------------

    def _encrypt_char(self, letter: str) -> str:
        if letter not in ALPHABET:
            return letter   # Pass spaces/punctuation through unchanged

        self._step_rotors()

        # 1. Plugboard (entry)
        signal = ALPHABET.index(self.plugboard.swap(letter))

        # 2. Forward through rotors (right → left)
        for rotor in reversed(self.rotors):
            signal = rotor.forward(signal)

        # 3. Reflector
        signal = self.reflector.reflect(signal)

        # 4. Backward through rotors (left → right)
        for rotor in self.rotors:
            signal = rotor.backward(signal)

        # 5. Plugboard (exit)
        return self.plugboard.swap(ALPHABET[signal])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encrypt(self, text: str, group_output: bool = False) -> str:
        """
        Encrypt (or decrypt) a message.

        Args:
            text:         Plaintext or ciphertext string.
            group_output: If True, format output in 5-letter groups like
                          authentic Enigma operators did.

        Returns:
            Encrypted/decrypted string (uppercase).
        """
        text = text.upper()
        result = "".join(self._encrypt_char(c) for c in text)

        if group_output:
            letters_only = result.replace(" ", "")
            result = " ".join(
                letters_only[i : i + 5] for i in range(0, len(letters_only), 5)
            )

        return result

    def set_positions(self, positions: str) -> None:
        """Reset rotor start positions without changing any other setting."""
        positions = positions.upper().ljust(len(self.rotors), "A")
        for rotor, pos in zip(self.rotors, positions):
            rotor.position = ALPHABET.index(pos)

    def get_positions(self) -> str:
        """Return current rotor window positions as a string."""
        return "".join(r.position_letter for r in self.rotors)

    def __repr__(self) -> str:
        return (
            f"EnigmaMachine(\n"
            f"  rotors={self.rotors},\n"
            f"  reflector={self.reflector},\n"
            f"  plugboard={self.plugboard}\n"
            f")"
        )
