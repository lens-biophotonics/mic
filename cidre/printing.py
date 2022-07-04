from time import perf_counter

import numpy as np

from cidre.input import CIDRE


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def print_heading(mode=CIDRE.ZERO_PRESERVED, obj='zeiss25x'):
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
    hdr_str = colored(0, 191, 255,
                      "\n  CIDRE microscopy illumination correction\n\n")
    if mode == CIDRE.ZERO_PRESERVED:
        hdr_str += ' mode:      zero-light preserved\n'
    elif mode == CIDRE.RANGE_CORRECTED:
        hdr_str += ' mode:      dynamic range corrected\n'
    elif mode == CIDRE.DIRECT:
        hdr_str += ' mode:      direct\n'
    hdr_str += '  objective: ' + obj.capitalize()
    print(hdr_str)


def print_progress(count, num_stacks):
    """
    Print script progress.

    Parameters
    ----------
    count: int
        loop counter

    num_stacks: int
        total number of processed stacks

    Returns
    -------
    None
    """
    prc_progress = 100 * (count / num_stacks)
    print('  correcting stack {0}/{1}: {2:0.1f}%'.format(count, num_stacks, prc_progress), end='\r')


def print_elapsed_time(start_time, num_stacks):
    """
    Print total processing time.

    Parameters
    ----------
    start_time: float
        analysis start time

    num_stacks: int
        total number of processed stacks

    Returns
    -------
    None
    """
    stop_time = perf_counter()
    total_time = stop_time - start_time
    mins = np.floor(total_time / 60)
    secs = total_time % 60
    mins_per_stack = np.floor((total_time / num_stacks) / 60)
    secs_per_stack = (total_time / num_stacks) % 60
    print("\n\n  process completed in: {0} min {1:3.1f} s ({2} min {3:3.1f} s per stack)\n"
          .format(mins, secs, mins_per_stack, secs_per_stack))
