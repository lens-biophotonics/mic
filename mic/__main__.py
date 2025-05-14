from mic.correction import correct_microscopy_dset
from mic.input import cli_parser_config, get_cli_input
from mic.utils import create_save_dir, create_stack_list


def mic(cli_args):

    # retrieve command line arguments
    source, fmt, dest, fields, mode, obj, wl = get_cli_input(cli_args)

    # create output directory
    dest_dir = create_save_dir(source, dest, obj, mode)

    # generate list of stack filenames
    stacks = create_stack_list(source, fmt=fmt)

    # correct illumination using available flat/dark-field models
    correct_microscopy_dset(stacks, fields, dest_dir, mode=mode, wl=wl, obj=obj, ptype=float)


def main():
    mic(cli_args=cli_parser_config())


if __name__ == '__main__':
    main()
