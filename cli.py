"""
Enigma Machine — Command-Line Interface
=======================================
Interact with the Virtual Enigma Machine from the terminal.

Usage examples:
    # Encrypt a message
    python cli.py encrypt "HELLO WORLD" --rotors I II III --positions AAA

    # Decrypt (same settings = same operation)
    python cli.py encrypt "MFNCU OQNLN" --rotors I II III --positions AAA

    # Full configuration
    python cli.py encrypt "ATTACK AT DAWN" \\
        --rotors I II III \\
        --reflector UKW-B \\
        --rings 1 1 1 \\
        --positions MCK \\
        --plugboard AB CD EF \\
        --group

    # Run interactive demo
    python cli.py demo

    # List available rotors and reflectors
    python cli.py list-parts
"""

import argparse
import sys
from enigma import EnigmaMachine, ROTOR_WIRINGS, REFLECTOR_WIRINGS, ALPHABET


BANNER = r"""
  ███████╗███╗   ██╗██╗ ██████╗ ███╗   ███╗ █████╗
  ██╔════╝████╗  ██║██║██╔════╝ ████╗ ████║██╔══██╗
  █████╗  ██╔██╗ ██║██║██║  ███╗██╔████╔██║███████║
  ██╔══╝  ██║╚██╗██║██║██║   ██║██║╚██╔╝██║██╔══██║
  ███████╗██║ ╚████║██║╚██████╔╝██║ ╚═╝ ██║██║  ██║
  ╚══════╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝
         Virtual Naval Enigma Machine  (M3)
"""


def build_machine(args) -> EnigmaMachine:
    """Construct machine from parsed CLI arguments."""
    return EnigmaMachine.from_key_sheet(
        rotors=args.rotors,
        reflector=args.reflector,
        ring_settings=args.rings,
        start_positions="".join(args.positions),
        plugboard_pairs=args.plugboard or [],
    )


def cmd_encrypt(args) -> None:
    """Encrypt or decrypt a message."""
    machine = build_machine(args)
    text = " ".join(args.text)

    print(f"\n  Input   : {text.upper()}")
    print(f"  Rotors  : {' '.join(args.rotors)}  |  Positions: {''.join(args.positions)}")
    print(f"  Rings   : {' '.join(str(r) for r in args.rings)}  |  Reflector: {args.reflector}")
    if args.plugboard:
        print(f"  Plugboard: {' '.join(args.plugboard)}")

    result = machine.encrypt(text, group_output=args.group)
    print(f"\n  Output  : {result}")
    print(f"  Final rotor positions: {machine.get_positions()}\n")


def cmd_demo(args) -> None:
    """Run an interactive demonstration."""
    print(BANNER)
    print("  DEMO MODE — Encrypting a historical-style naval message\n")

    settings = {
        "rotors": ["I", "II", "III"],
        "reflector": "UKW-B",
        "ring_settings": [1, 1, 1],
        "start_positions": "MCK",
        "plugboard_pairs": ["AV", "BS", "CG", "DL", "FU", "HZ", "IN", "KM", "OW", "RX"],
    }

    plaintext = "WETTERBERICHT NORDATLANTIK"

    print(f"  Settings:")
    print(f"    Rotors     : {' '.join(settings['rotors'])}")
    print(f"    Reflector  : {settings['reflector']}")
    print(f"    Rings      : {' '.join(str(r) for r in settings['ring_settings'])}")
    print(f"    Positions  : {settings['start_positions']}")
    print(f"    Plugboard  : {' '.join(settings['plugboard_pairs'])}")
    print(f"\n  Plaintext  : {plaintext}")

    machine = EnigmaMachine.from_key_sheet(**settings)
    ciphertext = machine.encrypt(plaintext, group_output=True)
    print(f"  Ciphertext : {ciphertext}")

    # Decrypt using same settings
    machine2 = EnigmaMachine.from_key_sheet(**settings)
    decrypted = machine2.encrypt(ciphertext.replace(" ", ""))
    print(f"  Decrypted  : {decrypted}")
    print(f"\n  Self-reciprocal verified: {plaintext.replace(' ', '') == decrypted.replace(' ', '')}\n")


def cmd_interactive(args) -> None:
    """Live interactive encryption session."""
    print(BANNER)
    machine = build_machine(args)
    print(f"  Machine ready. Type letters to encrypt (Ctrl+C to exit).\n")
    print(f"  Settings: rotors={args.rotors}, positions={''.join(args.positions)}\n")

    try:
        while True:
            user_input = input("  > ").strip()
            if not user_input:
                continue
            result = machine.encrypt(user_input)
            print(f"    {result}")
            print(f"    [positions: {machine.get_positions()}]\n")
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Session ended.\n")


def cmd_list_parts(args) -> None:
    """List available rotors and reflectors."""
    print(BANNER)
    print("  Available Rotors:")
    for name, wiring in ROTOR_WIRINGS.items():
        print(f"    {name:6s}  {wiring}")
    print("\n  Available Reflectors:")
    for name, wiring in REFLECTOR_WIRINGS.items():
        print(f"    {name:8s}  {wiring}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Virtual Naval Enigma Machine (M3)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command")

    # Shared rotor arguments
    rotor_args = argparse.ArgumentParser(add_help=False)
    rotor_args.add_argument(
        "--rotors", nargs="+", default=["I", "II", "III"],
        metavar="ROTOR",
        help="Rotor names left-to-right (e.g. I II III)"
    )
    rotor_args.add_argument(
        "--reflector", default="UKW-B",
        help="Reflector name (default: UKW-B)"
    )
    rotor_args.add_argument(
        "--rings", nargs="+", type=int, default=[1, 1, 1],
        metavar="N",
        help="Ring settings 1–26 per rotor (default: 1 1 1)"
    )
    rotor_args.add_argument(
        "--positions", nargs="+", default=["A", "A", "A"],
        metavar="LETTER",
        help="Start positions per rotor (default: A A A)"
    )
    rotor_args.add_argument(
        "--plugboard", nargs="*", metavar="PAIR",
        help="Plugboard pairs e.g. AB CD EF"
    )

    # encrypt sub-command
    enc = subparsers.add_parser("encrypt", parents=[rotor_args], help="Encrypt or decrypt text")
    enc.add_argument("text", nargs="+", help="Text to encrypt/decrypt")
    enc.add_argument("--group", action="store_true", help="Format output in 5-letter groups")
    enc.set_defaults(func=cmd_encrypt)

    # interactive sub-command
    live = subparsers.add_parser("interactive", parents=[rotor_args], help="Live interactive mode")
    live.set_defaults(func=cmd_interactive)

    # demo sub-command
    demo = subparsers.add_parser("demo", help="Run a built-in demonstration")
    demo.set_defaults(func=cmd_demo)

    # list-parts sub-command
    lp = subparsers.add_parser("list-parts", help="List available rotors and reflectors")
    lp.set_defaults(func=cmd_list_parts)

    args = parser.parse_args()
    if not args.command:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
