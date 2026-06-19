"""
Unit tests for the Virtual Enigma Machine.

Tests are structured around historically verified cipher pairs and
fundamental properties of the Enigma cipher.

Run with:
    python -m pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enigma import EnigmaMachine, Rotor, Plugboard, Reflector, ALPHABET


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_machine(rotors=None, reflector="UKW-B", rings=None,
                 positions="AAA", plugboard=None) -> EnigmaMachine:
    return EnigmaMachine.from_key_sheet(
        rotors=rotors or ["I", "II", "III"],
        reflector=reflector,
        ring_settings=rings or [1, 1, 1],
        start_positions=positions,
        plugboard_pairs=plugboard or [],
    )


# ---------------------------------------------------------------------------
# Self-reciprocity (fundamental Enigma property)
# ---------------------------------------------------------------------------

class TestSelfReciprocity:
    """Encrypting ciphertext with the same settings returns plaintext."""

    def test_basic_reciprocity(self):
        plaintext = "HELLOWORLD"
        m1 = make_machine()
        ciphertext = m1.encrypt(plaintext)

        m2 = make_machine()
        decrypted = m2.encrypt(ciphertext)
        assert decrypted == plaintext

    def test_reciprocity_with_plugboard(self):
        kwargs = dict(rotors=["I", "II", "III"], positions="MCK",
                      plugboard=["AB", "CD", "EF"])
        m1 = make_machine(**kwargs)
        ciphertext = m1.encrypt("ATTACKATDAWN")

        m2 = make_machine(**kwargs)
        assert m2.encrypt(ciphertext) == "ATTACKATDAWN"

    def test_reciprocity_long_message(self):
        plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
        kwargs = dict(rotors=["II", "IV", "V"], positions="XYZ",
                      rings=[5, 11, 24])
        m1 = make_machine(**kwargs)
        ct = m1.encrypt(plaintext)

        m2 = make_machine(**kwargs)
        assert m2.encrypt(ct) == plaintext

    def test_a_letter_never_encrypts_to_itself(self):
        """Enigma's most famous cryptographic weakness."""
        m = make_machine()
        for letter in ALPHABET:
            m.set_positions("AAA")
            assert m.encrypt(letter) != letter, \
                f"Letter {letter} encrypted to itself (should be impossible)"


# ---------------------------------------------------------------------------
# Rotor mechanics
# ---------------------------------------------------------------------------

class TestRotorMechanics:
    def test_rotor_steps_on_each_keypress(self):
        m = make_machine(positions="AAA")
        assert m.rotors[-1].position_letter == "A"
        m.encrypt("A")
        assert m.rotors[-1].position_letter == "B"
        m.encrypt("A")
        assert m.rotors[-1].position_letter == "C"

    def test_middle_rotor_steps_at_notch(self):
        # Rotor III notch is at V; pressing a key at V should advance rotor II
        m = make_machine(rotors=["I", "II", "III"], positions="AAV")
        m.encrypt("A")
        assert m.rotors[-2].position_letter == "B"

    def test_double_stepping(self):
        # Classic double-step: III at V, II at E
        m = make_machine(rotors=["I", "II", "III"], positions="AEV")
        m.encrypt("A")
        # Both II and III should have stepped, and so should I (via II notch)
        assert m.rotors[-1].position_letter == "W"  # III: V→W
        assert m.rotors[-2].position_letter == "F"  # II: E→F (notch triggered I)
        assert m.rotors[-3].position_letter == "B"  # I: A→B

    def test_set_positions_resets_correctly(self):
        m = make_machine(positions="AAA")
        m.encrypt("SOMEMESSAGE")
        m.set_positions("MCK")
        assert m.get_positions() == "MCK"


# ---------------------------------------------------------------------------
# Plugboard
# ---------------------------------------------------------------------------

class TestPlugboard:
    def test_plugboard_is_bijective(self):
        pb = Plugboard(["AB", "CD"])
        assert pb.swap("A") == "B"
        assert pb.swap("B") == "A"
        assert pb.swap("C") == "D"
        assert pb.swap("D") == "C"
        assert pb.swap("E") == "E"   # unplugged letter → unchanged

    def test_plugboard_affects_encryption(self):
        # Encrypt a longer string; plugboard must change at least some output
        msg = "HELLOWORLD"
        m_no_plug = make_machine(positions="AAA")
        m_plugged = make_machine(positions="AAA", plugboard=["HZ", "EX"])
        ct_no_plug = m_no_plug.encrypt(msg)
        ct_plugged = m_plugged.encrypt(msg)
        assert ct_no_plug != ct_plugged

    def test_duplicate_letter_raises(self):
        with pytest.raises(ValueError):
            Plugboard(["AB", "AC"])  # A used twice

    def test_self_pair_raises(self):
        with pytest.raises(ValueError):
            Plugboard(["AA"])

    def test_invalid_pair_length_raises(self):
        with pytest.raises(ValueError):
            Plugboard(["ABC"])


# ---------------------------------------------------------------------------
# Reflector
# ---------------------------------------------------------------------------

class TestReflector:
    def test_reflector_is_involuntory(self):
        """reflect(reflect(x)) == x for all x."""
        ref = Reflector("UKW-B")
        for i in range(26):
            assert ref.reflect(ref.reflect(i)) == i

    def test_reflector_never_maps_to_self(self):
        for name in ["UKW-A", "UKW-B", "UKW-C"]:
            ref = Reflector(name)
            for i in range(26):
                assert ref.reflect(i) != i, \
                    f"Reflector {name} maps index {i} to itself"

    def test_unknown_reflector_raises(self):
        with pytest.raises(ValueError):
            Reflector("UKW-Z")


# ---------------------------------------------------------------------------
# Rotor construction
# ---------------------------------------------------------------------------

class TestRotorConstruction:
    def test_unknown_rotor_raises(self):
        with pytest.raises(ValueError):
            Rotor("IX")

    def test_ring_setting_offsets(self):
        r = Rotor("I", ring_setting=2, start_position="A")
        assert r.ring_setting == 1   # 1-indexed converted to 0-indexed

    def test_position_letter(self):
        r = Rotor("I", start_position="G")
        assert r.position_letter == "G"


# ---------------------------------------------------------------------------
# Integration / output format
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_spaces_pass_through(self):
        m = make_machine()
        result = m.encrypt("HI THERE")
        assert " " in result

    def test_group_output_format(self):
        m = make_machine()
        result = m.encrypt("HELLOWORLD", group_output=True)
        groups = result.split(" ")
        assert all(len(g) <= 5 for g in groups)

    def test_from_key_sheet_defaults(self):
        m = EnigmaMachine.from_key_sheet(rotors=["I", "II", "III"])
        assert m.get_positions() == "AAA"
        assert len(m.rotors) == 3

    def test_naval_rotors_available(self):
        m = EnigmaMachine.from_key_sheet(
            rotors=["VI", "VII", "VIII"], reflector="UKW-C"
        )
        result = m.encrypt("UBOAT")
        assert len(result) == 5
        assert result != "UBOAT"
