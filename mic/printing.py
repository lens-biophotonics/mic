def colored(r, g, b, text):
    return f'\033[38;2;{r};{g};{b}m{text} \033[38;2;255;255;255m'


def print_heading(mode, obj='zeiss25x'):
    """
    Print script heading.

    Parameters
    ----------
    mode: int
        correction mode (see help documentation)

    obj: str
        employed objective

    Returns
    -------
    None
    """
    hdr_str = colored(0, 191, 255, '\nMicroscopy illumination correction')

    if mode == 0:
        hdr_str += '\n\nmode:      zero-light-preserved'
    elif mode == 1:
        hdr_str += '\n\nmode:      dynamic-range-corrected'
    elif mode == 2:
        hdr_str += '\n\nmode:      direct'

    hdr_str += f'\nobjective: {obj.capitalize()}'

    print(hdr_str)
