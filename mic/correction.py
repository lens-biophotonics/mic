import numpy as np
import tempfile
import tifffile as tiff

from joblib import Parallel, delayed
from skimage.transform import resize

from mic.utils import create_memory_map, get_available_cores, delete_tmp_data, print_heading


def load_illumination_models(field_path, wl=(618, 482, -1), obj='tpfm_zeiss25x'):
    """
    Load spatial gain (v) and additive noise (z) terms from .txt data files.

    Parameters
    ----------
    field_path: pathlib Path object
        path to illumination field models

    wl: int or tuple of int
        RGB channel wavelengths [nm]
        
    obj: str
        name of the employed objective

    Returns
    -------
    v: numpy.ndarray (dtype=float)
        spatial gain function

    z: numpy.ndarray (dtype=float)
        spatial offset function
    """
    # load illumination models (gain and additive terms, v and z)
    field_path = field_path / obj.lower()
    ch_name = ('R', 'G', 'B')
    ch_corr = ''
    v_lst = []
    z_lst = []
    for c, w in enumerate(wl):
        if w != -1:
            v_path = field_path / str(w) / 'v.tif'
            z_path = field_path / str(w) / 'z.tif'
            if c > 0:
                ch_corr += '           '
            try:
                v_lst.append(tiff.imread(v_path))
                z_lst.append(tiff.imread(z_path))
            except ValueError:
                ch_corr += f'{ch_name[c]} ({w}nm not available! Skipping channel...)'
            else:
                ch_corr += f'{ch_name[c]} ({w}nm)'
        else:
            v_lst.append(None)
            z_lst.append(None)

    # add "fake" channels to correction models
    is_corr = [isinstance(c, np.ndarray) for c in v_lst]
    is_none = [i for i, x in enumerate(is_corr) if not x]
    is_not_none = [i for i, x in enumerate(is_corr) if x]
    if is_none:
        idx = is_not_none[0]
        for j in is_none:
            z_lst[j] = np.zeros_like(z_lst[idx])
            v_lst[j] = np.ones_like(v_lst[idx])

    # create arrays from channel-wise lists
    print(f'channels:  {ch_corr}')
    v = np.stack(v_lst, axis=-1)
    z = np.stack(z_lst, axis=-1)

    return v, z


def resize_illumination_models(v, z, out_shape):
    """
    Illumination models resizing.

    Parameters
    ----------
    v: numpy.ndarray (dtype=float)
        spatial gain function

    z: numpy.ndarray (dtype=float)
        spatial offset function

    out_shape: tuple
        lateral (in-plane) shape of input image stacks

    Returns
    -------
    v_out: numpy.ndarray (dtype=float)
        resized spatial gain function

    z_out: numpy.ndarray (dtype=float)
        resized spatial offset function
    """
    # if shapes do not match...
    if out_shape != v.shape[:-1]:
        v_rsz = np.zeros(out_shape)
        z_rsz = np.zeros(out_shape)

        # resize models, looping over available wavelengths
        for c in range(v.shape[-1]):
            v_rsz[..., c] = resize(v[..., c], out_shape, anti_aliasing=True, preserve_range=True)
            z_rsz[..., c] = resize(z[..., c], out_shape, anti_aliasing=True, preserve_range=True)

        v_out = np.squeeze(v_rsz)
        z_out = np.squeeze(z_rsz)

    else:
        v_out = np.squeeze(v)
        z_out = np.squeeze(z)

    return v_out, z_out


def correct_zslice(d, img_in, img_out, v, z, v_mean, z_mean, mode=0, ptype=np.float64):
    """
    Apply illumination correction models to z-slice.

    Parameters
    ----------
    d: int
        depth index

    img_in: numpy.ndarray
        original image stack

    img_out: NumPy memory-map object
        corrected stack

    v: numpy.ndarray (dtype=float)
        spatial gain function

    z: numpy.ndarray (dtype=float)
        spatial offset function

    v_mean: float
        mean gain value (computed once for efficiency's sake)

    z_mean: float
        mean offset value (computed once for efficiency's sake)

    mode: int
        correction mode
        (0: zero-light preserved; 1: dynamic range corrected; 2: direct)

    ptype: dtype
        processing data type

    Returns
    -------
    None
    """
    # apply requested correction mode
    # zero-light-preserved
    if mode == 0:
        img_out[d, ...] = z_mean + v_mean * (np.divide(img_in[d, ...].astype(ptype) - z, v))

    # dynamic-range-corrected
    elif mode == 1:
        img_out[d, ...] = v_mean * (np.divide(img_in[d, ...].astype(ptype) - z, v))

    # direct correction
    elif mode == 2:
        img_out[d, ...] = np.divide(img_in[d, ...].astype(ptype) - z, v)


def correct_microscopy_dset(stacks, fields, dest, mode=0, wl=(618, 482, -1), obj='tpfm_zeiss25x', ptype=np.float64):
    """
    Apply illumination correction to microscopy image dataset (using parallel processes).

    Parameters
    ----------
    stacks: list of pathlib Path objects
        list of image stacks to be processed

    fields: pathlib Path object
        path to illumination models

    dest: pathlib Path object
        output path

    mode: int
        correction mode
        (0: zero-light-preserved; 1: dynamic-range-corrected; 2: direct)

    wl: int or list of int
        channel wavelengths [nm]

    obj: str
        employed objective

    ptype: dtype
        processing data type

    Returns
    -------
    None
    """
    # get illumination models
    print_heading(mode, obj)
    v, z = load_illumination_models(fields, wl=wl, obj=obj)

    # compute mean models once
    v_mean = np.mean(v, axis=(0, 1))
    z_mean = np.mean(z, axis=(0, 1))

    # iteratively process input z-stacks
    n_cpu = get_available_cores()
    n_stk = len(stacks)
    for i in range(n_stk):
        print(f"\n•Correcting z-stack {i+1}/{n_stk}...")
        correct_zstack(stacks[i], v, z, v_mean, z_mean, mode, ptype, dest, jobs=n_cpu)


def correct_zstack(stack, v, z, v_mean, z_mean, mode, ptype, dest, jobs=1):
    """
    Apply adaptive illumination correction to microscopy image stack.

    Parameters
    ----------
    stack: pathlib Path object
        path to stack to be corrected

    v: numpy.ndarray (dtype=float)
        spatial gain function

    z: numpy.ndarray (dtype=float)
        additive noise term

    v_mean: float
        mean spatial gain

    z_mean: float
        mean spatial offset

    mode: int
        correction mode flag
        (0: zero-light preserved; 1: dynamic range corrected; 2: direct)

    ptype: dtype
        processing data type

    dest: str
        output path

    jobs: int
        number of parallel threads

    Returns
    -------
    None
    """
    # load z-stack
    img_in = tiff.imread(stack)

    """
    TODO:
    - add support for both channel-first and channel-last RGB z-stacks
    - only channel-last z-stacks are supported now...
    """

    # resize illumination model arrays, if required
    v, z = resize_illumination_models(v, z, out_shape=img_in.shape[1:3])

    # create memory-mapped objects
    tmp_path = tempfile.mkdtemp(dir=dest)
    img_out = create_memory_map(dtype=ptype, shape=img_in.shape, tmp=tmp_path, name='corr')

    # process z-slices using parallel processes
    n_frms = img_in.shape[0]
    with Parallel(n_jobs=min(jobs, n_frms), prefer='threads', verbose=10, require='sharedmem') as parallel:
        parallel(
            delayed(correct_zslice)
            (d, img_in, img_out, v, z, v_mean=v_mean, z_mean=z_mean, mode=mode, ptype=ptype)
            for d in range(n_frms))

    # clip values
    max_out = np.iinfo(img_in.dtype).max
    img_out = np.where(img_out >= 0, img_out, 0)
    img_out = np.where(img_out <= max_out, img_out, max_out)
    img_out = img_out.astype(img_in.dtype)
    metadata = {'axes': 'ZYX'} if img_out.ndim == 3 else {'axes': 'ZYXC'}

    # save corrected z-stack (with compression) and erase temporary files
    print(' Saving compressed z-stack...')
    tiff.imwrite(dest / stack.name, img_out, metadata=metadata, compression='zlib', compressionargs={'level': 9})
    delete_tmp_data(tmp_path, img_out)
