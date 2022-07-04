import argparse


def cli_parser_config():
    """
    Configure CLI argument parser object.

    Parameters
    ----------
    None

    Returns
    -------
    cli_parser:
        configured command line argument parser
    """
    cli_parser = argparse.ArgumentParser(
        description='\n' +
                    '\033[96mCIDRE microscopy illumination correction\033[0m\n'
                    + 'author:     Michele Sorelli (2022)\n'
                    + 'reference:  Smith et al.    (2014) - '
                    + 'CIDRE: an illumination-correction method '
                    + 'for optical microscopy\n\n'
                    + 'example:    python3 cidre_illumination_correction.py '
                    + '/mnt/NASone/michele/hbp/tpfm_mosaic_folder '
                    + '-o nikon -m 1\n\n',
        formatter_class=argparse.RawTextHelpFormatter)
    cli_parser.add_argument(dest='source_path',
                            help='either path to input image stack or\n'
                                 + 'path to folder including multiple input '
                                 + 'stacks\n(.tif or .tiff)')
    cli_parser.add_argument('-d', '--dest', dest='dest_path',
                            default=None,
                            help='destination path '
                                 + '(default: new folder at source path)\n\n')
    cli_parser.add_argument('-c', '--cidre', dest='cidre_path',
                            default='./models',
                            help='path to CIDRE models (default: '
                                 + './models)'
                                 + '\n\n')
    cli_parser.add_argument('-o', '--objective', dest='objective',
                            default='zeiss25x',
                            help='objective, ' +
                                 'either \'zeiss25x\' or \'nikon10x\'' +
                                 ' (case-insensitive; ' +
                                 'default: \'zeiss25x\')\n\n')
    cli_parser.add_argument('-w', '--wavelength', dest='wavelength',
                            default=[618, 482, -1],
                            nargs='+', type=int,
                            help='RGB channels wavelengths ' +
                                 'default: [618, 482, None] nm)\n\n')
    cli_parser.add_argument('-m', '--mode', dest='mode',
                            default=0, type=int,
                            help='correction mode flag\n'
                                 + '0 \u2192 zero-light preserved:'
                                 + u'\tz\u0304 + '
                                 + u'v\u0304\u00B7(I - z)/v\t'
                                 + '(default)\n'
                                 + '1 \u2192 dynamic range corrected:'
                                 + u'\t    v\u0304\u00B7(I - z)/v\n'
                                 + '2 \u2192 direct:'
                                 + u'\t\t\t      (I - z)/v\n\n'
                                 + u'\u2023v: gain function\n'
                                 + u'\u2023z: additive noise term\n\n')

    return cli_parser


def get_cli_input(parser):
    """
    Get CLI input arguments.

    Parameters
    ----------
    parser: ArgumentParser object

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
    args = parser.parse_args()
    source = args.source_path
    dest = args.dest_path
    model = args.cidre_path
    corr_mode = args.mode
    objective = args.objective
    wavelength = args.wavelength

    return source, dest, model, corr_mode, objective, wavelength
