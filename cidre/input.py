import argparse


class CIDRE:
    """ CIDRE mode flags """
    ZERO_PRESERVED = 0
    RANGE_CORRECTED = 1
    DIRECT = 2


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass


def cli_parser_config():
    """
    Configure CLI argument parser object.

    Parameters
    ----------
    None

    Returns
    -------
    cli_args:
        command line arguments
    """
    cli_parser = argparse.ArgumentParser(
        description='\n' +
                    '\033[96mCIDRE microscopy illumination correction\033[0m\n'
                    'author:     Michele Sorelli (2022)\n'
                    'reference:  Smith et al.    (2014) - '
                    'CIDRE: an illumination-correction method '
                    'for optical microscopy\n\n'
                    'example:    python3 cidre.py '
                    '/mnt/NASone/michele/hbp/tpfm_mosaic_folder '
                    '-o nikon10x -m 1 -w 618 530 390\n\n',
        formatter_class=CustomFormatter)
    cli_parser.add_argument(dest='source_path',
                            help='either path to input image stack or\n'
                                 'path to folder including multiple input '
                                 'stacks (.tif or .tiff)')
    cli_parser.add_argument('-d', '--dest', dest='dest_path',
                            default=None,
                            help='destination path')
    cli_parser.add_argument('-c', '--cidre', dest='cidre_path',
                            default='./models',
                            help='path to CIDRE models')
    cli_parser.add_argument('-o', '--objective', dest='objective',
                            default='zeiss25x',
                            help='objective, ' +
                                 'either \'zeiss25x\' or \'nikon10x\'')
    cli_parser.add_argument('-w', '--wavelength', dest='wavelength',
                            default=[618, 482, -1],
                            nargs='+', type=int,
                            help='RGB channels wavelengths: negative value if not correcting')
    cli_parser.add_argument('-m', '--mode', dest='mode',
                            default=0, type=int,
                            help='correction mode flag\n\n'
                                 u'\u2023v: gain function\n'
                                 u'\u2023z: additive noise term\n\n'
                                 '0 \u2192 zero-light preserved:'
                                 u'\tz\u0304 + '
                                 u'v\u0304\u00B7(I - z)/v\n'
                                 '1 \u2192 dynamic range corrected:'
                                 u'\t    v\u0304\u00B7(I - z)/v\n'
                                 '2 \u2192 direct:'
                                 u'\t\t\t      (I - z)/v\t')

    # parse arguments
    cli_args = cli_parser.parse_args()

    return cli_args


def get_cli_input(cli_args):
    """
    Get CLI input arguments.

    Parameters
    ----------
    cli_args:
        command line arguments

    Returns
    -------
    source:
        source path
        (single stack file or directory including multiple stacks)

    dest:
        output path

    model:
        path to CIDRE model data files
        (default: /mnt/NASone/michele/CIDRE)

    corr_mode: int
        correction mode flag

    objective: string
        microscope objective employed (Zeiss or Nikon)

    wavelength: list
        RGB channels wavelengths [nm]
    """
    source = cli_args.source_path
    dest = cli_args.dest_path
    model = cli_args.cidre_path
    corr_mode = cli_args.mode
    objective = cli_args.objective
    wavelength = cli_args.wavelength

    return source, dest, model, corr_mode, objective, wavelength
