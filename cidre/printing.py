def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def print_heading(mode, obj='zeiss25x'):
    """
    Print script heading.

    Parameters
    ----------
    mode: int
        selected CIDRE correction mode

    Returns
    -------
    None
    """
    hdr_str = colored(0, 191, 255, "\nCIDRE microscopy illumination correction")

    if mode == 0:
        hdr_str += '\n\nmode:      zero-light preserved'
    elif mode == 1:
        hdr_str += '\n\nmode:      dynamic range corrected'
    elif mode == 2:
        hdr_str += '\n\nmode:      direct'

    hdr_str += '\nobjective: ' + obj.capitalize()

    print(hdr_str)
