import gc
import tempfile
from multiprocessing import cpu_count
from os import environ
from pathlib import Path
from shutil import rmtree

import numpy as np

from joblib import dump, load


def create_memory_map(dtype, shape=None, name='tmp', tmp=None, arr=None, mmap_mode='w+'):
    """
    Create a memory-map to an array stored in a binary file on disk.

    Parameters
    ----------
    dtype:
        data-type used to interpret the file contents

    shape: tuple
        shape of the stored array

    name: str
        optional temporary filename

    tmp: str
        temporary file directory

    arr: numpy.ndarray
        array to be mapped

    mmap_mode: str
        file opening mode

    Returns
    -------
    mmap: NumPy memory map
        memory-mapped array
    """
    if tmp is None:
        tmp = tempfile.mkdtemp()
    mmap_path = Path(tmp) / f'{name}.mmap'

    if arr is None:
        _ = open(mmap_path, mode='w+', encoding='utf-8')
        mmap = np.memmap(mmap_path, dtype=dtype, mode=mmap_mode, shape=shape)
        mmap[:] = 0
    else:
        _ = dump(arr, mmap_path)
        mmap = load(mmap_path, mmap_mode=mmap_mode)
        del arr
        _ = gc.collect()

    return mmap


def create_save_dir(source, dest, obj, mode):
    """
    Create output directory.

    Parameters
    ----------
    source: pathlib Path object
        source path
        (single TIFF stack or directory including multiple stacks)

    dest: pathlib Path object
        output path

    obj: str
        employed objective

    mode: int
        correction mode
        (0: zero-light-preserved; 1: dynamic-range-corrected; 2: direct)

    Returns
    -------
    dest:
        output path (adapted)
    """
    if dest is None:
        if Path.is_file(source) is True:
            dest = source.parents[0]
        else:
            dest = source

    dest = dest / f'flat-field-corrected_{obj}_mode{mode}'

    if not Path.is_dir(dest):
        dest.mkdir(parents=True, exist_ok=True)

    return dest


def create_stack_list(source, format=['tif', 'tiff']):
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
    
    fmt: list (dtype=str)
        list of input file formats
    """
    # single-stack
    if Path.is_file(source):
        stacks = [source]

    # multiple stacks
    else:
        stacks = []
        for path in Path(source).glob('*'):
            if path.is_file() and any(str(path).lower().endswith(fmt) for fmt in format):
                stacks.append(source / path.name)

    return stacks


def delete_tmp_data(tmp_dir, tmp_data):
    """
    Delete temporary folder.

    Parameters
    ----------
    tmp_dir: str
        path to temporary folder to be removed

    tmp_data: tuple
        temporary data objects within tmp_dir

    Returns
    -------
    None
    """
    if not isinstance(tmp_data, list):
        tmp_data = [tmp_data]
    try:
        for d in tmp_data:
            del d

        rmtree(tmp_dir)

    except OSError:
        pass


def get_available_cores():
    """
    Return the number of available logical cores.

    Returns
    -------
    num_cpu: int
        number of available cores
    """
    num_cpu = environ.pop('OMP_NUM_THREADS', default=None)
    if num_cpu is None:
        num_cpu = cpu_count()
    else:
        num_cpu = int(num_cpu)

    return num_cpu


def ensure_three_axes(array):
    if array.ndim == 3:
        return array
    else:
        return np.expand_dims(array, axis=-1)


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
