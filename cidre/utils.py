from os import makedirs, path, scandir
import gc


def create_save_dir(source, dest, objective, corr_mode):
    """
    Create output directory.

    Parameters
    ----------
    source:
        source path
        (single stack file or directory including multiple stacks)

    dest:
        output path

    corr_mode: int
        correction mode flag

    Returns
    -------
    dest:
        output path (adapted)
    """
    if dest is None:
        if path.isfile(source) is True:
            dest = path.join(path.dirname(source), 'cidre_corrected_'
                             + objective + '_mode' + str(corr_mode))
        else:
            dest = path.join(source, 'cidre_corrected_'
                             + objective + '_mode' + str(corr_mode))
    else:
        dest = path.join(dest, 'cidre_corrected_'
                         + objective + '_mode' + str(corr_mode))

    if not path.isdir(dest):
        makedirs(dest)

    return dest


def create_stack_list(source):
    """
    Create list of input stack paths.

    Parameters
    ----------
    source:
        source path (single stack file or directory including multiple stacks)

    Returns
    -------
    stacks: list
        list of input stacks to be processed
    """
    # single-stack case
    if path.isfile(source) is True:
        stacks = [source]

    # multiple stacks
    # (mosaic folder)
    else:
        obj = scandir(source)
        stacks = list()
        for entry in obj:
            if entry.is_file() and \
               (entry.name.endswith('tif') or entry.name.endswith('tiff')):
                stacks.append(path.join(source, entry.name))

    return stacks


def clear_from_memory(data):
    del data
    gc.collect()
