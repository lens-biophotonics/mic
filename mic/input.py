import argparse

from pathlib import Path


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
    pass


def cli_parser_config():
    """
    Configure CLI argument parser object.

    Returns
    -------
    cli_args:
        command line arguments
    """
    cli_parser = argparse.ArgumentParser(
        description='\n' +
                    'Microscopy illumination correction\n'
                    'author:     Michele Sorelli (2024)\n'
                    'reference:  Smith et al.    (2014) - '
                    'CIDRE: an illumination-correction method '
                    'for optical microscopy\n\n'
                    'example: /path/to/local/dir$ mic '
                    '/mnt/c/tpfm_stack_dset '
                    '-o tpfm_nikon10x -m 1 -w 618 530 -1\n\n',
        formatter_class=CustomFormatter)
    cli_parser.add_argument(dest='source_path',
                            help='either path to TIFF image stack or\n'
                                 'path to directory including multiple stacks')
    cli_parser.add_argument('-d', '--dest', dest='dest_path',
                            default=None,
                            help='output path')
    cli_parser.add_argument('-f', '--field', dest='field_path',
                            default='models/',
                            help='path to flat- and dark-field models (v.tif and z.tif, respectively): '
                                 'these must be placed inside folders named after the corresponding wavelength, '
                                 'within another parent folder named after the employed objective, e.g.:\n'
                                 '/\n'
                                 '└──models/\n'
                                 '   └── zeiss25x\n'
                                 '          ├── 482/\n'
                                 '          |    ├── v.tif\n'
                                 '          |    └── z.tif\n'
                                 '          └── 618/\n'
                                 '               ├── v.tif\n'
                                 '               └── z.tif\n')
    cli_parser.add_argument('-o', '--objective', dest='objective',
                            default='tpfm_zeiss25x',
                            help='employed objective, either \'tpfm_zeiss25x\', ' +
                                 '\'tpfm_nikon10x\', \'tpfm_nikon20x\', or \'lsfm_lavision12x_dskwd\'')
    cli_parser.add_argument('-w', '--wavelength', dest='wavelength',
                            default=[618, 482, -1],
                            nargs='+',
                            help='corrected colors: scalar value for grayscale image stacks or 3-element list for '
                                 'RGB files (set single elements to -1 to skip the corresponding channel correction) ')
    cli_parser.add_argument('-m', '--mode', dest='mode',
                            default=0, type=int,
                            help='illumination correction mode:\n\n'
                                 u'\u2023v: spatial gain function\n'
                                 u'\u2023z: spatial offset term\n\n'
                                 '0 \u2192 zero-light-preserved:'
                                 u'\tz\u0304 + '
                                 u'v\u0304\u00B7(I - z)/v\n'
                                 '1 \u2192 dynamic-range-corrected:'
                                 u'\t    v\u0304\u00B7(I - z)/v\n'
                                 '2 \u2192 direct:'
                                 u'\t\t\t      (I - z)/v\t')
    cli_parser.add_argument('--fmt', dest='fmt',
                            default=['tif', 'tiff'],
                            nargs='+', type=str,
                            help='input image formats')

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
    source: pathlib Path object
        source path
        (single stack file or directory including multiple stacks)

    fmt: list (dtype=str)
        list of input file formats

    dest: pathlib Path object
        output path

    field: pathlib Path object
        path to illumination models

    mode: int
        correction mode (see help documentation)

    obj: str
        employed objective

    wl: int or list of int
        channel wavelengths [nm]
    """
    source = Path(cli_args.source_path)
    try:
        dest = Path(cli_args.dest_path)
    except TypeError:
        dest = None
    field = Path(cli_args.field_path)
    mode = cli_args.mode
    obj = cli_args.objective
    wl = cli_args.wavelength
    fmt = cli_args.fmt    
    if not isinstance(fmt, list):
        fmt = [fmt]

    return source, fmt, dest, field, mode, obj, wl
