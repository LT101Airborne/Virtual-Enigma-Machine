"""
Enigma Machine — Example Usage
================================
Practical demonstrations of the Virtual Enigma Machine.
"""

from enigma import EnigmaMachine


def example_basic():
    print("=" * 55)
    print("EXAMPLE 1: Basic encryption & decryption")
    print("=" * 55)

    machine = EnigmaMachine.from_key_sheet(
        rotors=["I", "II", "III"],
        reflector="UKW-B",
        ring_settings=[1, 1, 1],
        start_positions="AAA",
    )

    plaintext = "HELLO WORLD"
    ciphertext = machine.encrypt(plaintext)
    print(f"Plaintext : {plaintext}")
    print(f"Ciphertext: {ciphertext}")

    # Decrypt — same settings, same operation (self-reciprocal)
    machine.set_positions("AAA")
    decrypted = machine.encrypt(ciphertext.replace(" ", ""))
    print(f"Decrypted : {decrypted}")
    print()


def example_plugboard():
    print("=" * 55)
    print("EXAMPLE 2: With plugboard (Steckerbrett)")
    print("=" * 55)

    settings = dict(
        rotors=["I", "II", "III"],
        reflector="UKW-B",
        ring_settings=[1, 1, 1],
        start_positions="MCK",
        plugboard_pairs=["AV", "BS", "CG", "DL", "FU"],
    )

    m1 = EnigmaMachine.from_key_sheet(**settings)
    msg = "ATTACKATDAWN"
    ct = m1.encrypt(msg, group_output=True)
    print(f"Plaintext : {msg}")
    print(f"Ciphertext: {ct}")

    m2 = EnigmaMachine.from_key_sheet(**settings)
    pt = m2.encrypt(ct.replace(" ", ""))
    print(f"Decrypted : {pt}")
    print()


def example_rotor_positions():
    print("=" * 55)
    print("EXAMPLE 3: Tracking rotor positions")
    print("=" * 55)

    m = EnigmaMachine.from_key_sheet(
        rotors=["I", "II", "III"],
        start_positions="AAU",   # III at U, one step from notch V
    )

    for i, letter in enumerate("ABCDE"):
        before = m.get_positions()
        out = m._encrypt_char(letter)
        after = m.get_positions()
        print(f"  Keypress {i+1}: {letter} → {out}   rotors: {before} → {after}")
    print()


def example_naval_m3():
    print("=" * 55)
    print("EXAMPLE 4: Naval M3 with all rotors")
    print("=" * 55)

    m = EnigmaMachine.from_key_sheet(
        rotors=["VI", "VII", "VIII"],
        reflector="UKW-C",
        ring_settings=[14, 9, 24],
        start_positions="ZAP",
        plugboard_pairs=["AE", "BF", "CM", "DQ", "HU", "JN", "LX", "PR", "SZ", "VW"],
    )

    message = "WETTERBERICHT NORDATLANTIK STURM"
    ciphertext = m.encrypt(message, group_output=True)
    print(f"Plaintext : {message}")
    print(f"Ciphertext: {ciphertext}")
    print()


if __name__ == "__main__":
    example_basic()
    example_plugboard()
    example_rotor_positions()
    example_naval_m3()
