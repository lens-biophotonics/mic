import numpy as np

from cidre.correction import correct_TPFM_illumination
from cidre.input import cli_parser_config, get_cli_input
from cidre.utils import create_save_dir, create_stack_list


def cidre(cli_args):

    # retrieve command line input
    source_path, dest_path, model_path, corr_mode, objective, wavelength = get_cli_input(cli_args)

    # create save directory
    dest_path = create_save_dir(source_path, dest_path, objective, corr_mode)

    # generate list of stack filenames
    stacks = create_stack_list(source_path)

    # correct illumination using CIDRE
    correct_TPFM_illumination(stacks, model_path, dest_path, mode=corr_mode, wave=wavelength, obj=objective,
                              pro_dtype=np.float64)


if __name__ == '__main__':
    cidre(cli_args=cli_parser_config())
