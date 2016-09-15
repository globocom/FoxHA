import argparse
from os import getenv
from .utils import Utils
from .print_format import print_warning


def arguments():

    parser = argparse.ArgumentParser(
        add_help=True,
        description="Description: MySQL FoxHA Crypt Passwords")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-g",
        "--generate_new_keyfile",
        help="generate new keyfile",
        action="store_true")
    group.add_argument(
        "-c",
        "--crypt",
        help="crypt password",
        action="store_true")
    group.add_argument(
        "-d",
        "--decrypt",
        help="decrypt password",
        action="store_true")
    parser.add_argument(
        "-p",
        "--password",
        help="specify password",
        action="store")
    parser.add_argument(
        "--keyfile",
        help="different path to key file - Default: ./config/.key",
        action="store")
    args = parser.parse_args()
    argument_vars = vars(args)

    # If None option is specified display help:
    argsvars = vars(parser.parse_args())
    if not any(argsvars.values()):
        parser.print_help()
        exit(0)

    # Parsing Env. Variable FOXHA_HOME
    FOXHA_HOME = getenv('FOXHA_HOME')

    if args.generate_new_keyfile:
        if not args.password:
            Utils.generate_new_keyfile(args.keyfile)
        else:
            print_warning("You should specify option [-g/--generate-new-keyfile] alone.")
        exit(1)

    # Key file argument
    if args.keyfile:
        cipher_suite = Utils.parse_key_file(args.keyfile)
    elif FOXHA_HOME:
        keyfile = FOXHA_HOME + '/config/.key'
        cipher_suite = Utils.parse_key_file(keyfile)
    else:
        cipher_suite = Utils.parse_key_file()

    if (args.crypt or args.decrypt) and args.password is None:
        print_warning("Please specify [-p/--password] parameter in conjunction with "\
            "[-c/--crypt] or [-d/--decrypt] options.")
        exit(1)

    if args.crypt:
        Utils.crypt_pass(cipher_suite, args.password)
        exit(1)
    if args.decrypt:
        Utils.decrypt_pass(cipher_suite, args.password)
        exit(1)

def main(args=None):
    arguments()

if __name__ == '__main__':
    main()
