from os import path

import numpy as np
import tifffile
from alive_progress import alive_bar
from numba import njit
from skimage.transform import resize

from cidre.printing import print_heading
from cidre.utils import clear_from_memory


def load_cidre_models(cidre_path, wave=[618, 482, -1], obj='zeiss25x',
                      mshape=(512, 512, 3), ch_name=['R', 'G', 'B']):
    """
    Load CIDRE-based gain (v) and additive noise (z) terms from .txt data files
    (red and green channel components).

    Parameters
    ----------
    cidre_path: str
        path to CIDRE model data files

    wave: list
        RGB channels wavelengths [nm]

    ch_name: list
        channels name

    Returns
    -------
    v: numpy.ndarray (shape=(512,512), dtype=float64)
        spatial gain function

    z: numpy.ndarray (shape=(512,512), dtype=float64)
        spatial offset function
    """
    # objective selection
    cidre_path = path.join(cidre_path, obj.lower())

    # initialize empty model arrays
    v = np.empty(mshape)
    v[:] = np.nan
    z = v.copy()
    print('channels:  ', end='')

    # load CIDRE models (gain and additive terms, v and z)
    ch_corr = ''
    for c in range(len(ch_name)):
        if wave[c] > 0:
            v_path = path.join(cidre_path, str(wave[c]), 'v.txt')
            z_path = path.join(cidre_path, str(wave[c]), 'z.txt')
            if c > 0:
                ch_corr += '           '
            try:
                v[..., c] = np.loadtxt(v_path, delimiter='\t')
                z[..., c] = np.loadtxt(z_path, delimiter='\t')
            except Exception:
                ch_corr += '{} ({}nm not available! Skipping channel...)\n'.format(ch_name[c], str(wave[c]))
            else:
                ch_corr += ch_name[c] + ' (' + str(wave[c]) + 'nm)\n'
    print(ch_corr)

    return v, z


def resize_cidre_models(v, z, slice_shape):
    """
    Resize CIDRE models if needed.

    Parameters
    ----------
    v: numpy.ndarray (shape=(512,512), dtype=float)
        spatial gain function

    z: numpy.ndarray (shape=(512,512), dtype=float)
        spatial offset function

    slice_shape: tuple
        lateral (in-plane) shape of input image stacks

    Returns
    -------
    v_res: numpy.ndarray (dtype=float)
        resized spatial gain function

    z_res: numpy.ndarray (dtype=float)
        resized spatial offset function
    """
    # if shapes do not match...
    model_shape = v.shape
    if slice_shape != model_shape:
        v_res = np.zeros(slice_shape)
        z_res = v_res.copy()

        # resize models, looping over channels
        for c in range(slice_shape[-1]):
            v_res[..., c] = resize(v[..., c], slice_shape[:-1], anti_aliasing=True, preserve_range=True)
            z_res[..., c] = resize(z[..., c], slice_shape[:-1], anti_aliasing=True, preserve_range=True)

        return v_res, z_res

    else:
        return v, z


@njit(cache=True)
def apply_cidre_to_slice(slice_rgb, v, z, v_mean, z_mean, mode=0, ptype=np.float64):
    """
    Apply CIDRE correction models to 2D RGB slice.

    Parameters
    ----------
    slice_rgb: numpy.ndarray (y, x, c)
        RGB slice

    v: numpy.ndarray
        spatial gain model

    z: numpy.ndarray
        spatial offset model

    v_mean: float
        mean gain value (computed once for efficiency's sake)

    z_mean: float
        mean offset value (computed once for efficiency's sake)

    mode: int
        correction mode flag
        (0: zero-light preserved; 1: dynamic range corrected; 2: direct)

    ptype: dtype
        processing data type

    Returns
    -------
    corr_slice: numpy.ndarray
        corrected RGB slice
    """
    # original conversion
    slice_rgb = slice_rgb.astype(ptype)

    # initialize zero slice
    corr_slice = np.zeros_like(slice_rgb)

    # zero-light preserved
    if mode == 0:
        for c in range(3):
            if v_mean[c] != np.nan:
                corr_slice[..., c] = z_mean[c] + v_mean[c] * (np.divide(slice_rgb[..., c] - z[..., c], v[..., c]))

    # dynamic range corrected
    elif mode == 1:
        for c in range(3):
            if v_mean[c] != np.nan:
                corr_slice[..., c] = v_mean[c] * (np.divide(slice_rgb[..., c] - z[..., c], v[..., c]))

    # direct correction
    elif mode == 2:
        for c in range(3):
            if v_mean[c] != np.nan:
                corr_slice[..., c] = np.divide(slice_rgb[..., c] - z[..., c], v[..., c])

    return corr_slice


def correct_tpfm_illumination(stacks, model_path, dest_path, mode=0,
                              wave=[618, 482, -1], obj='zeiss25x', ptype=np.float64):
    """
    CIDRE-based illumination correction function.

    Parameters
    ----------
    stacks: list
        list of input stacks to be processed

    model_path: str
        path to CIDRE model data files

    dest: str
        output path

    mode: int
        correction mode flag
        (0: zero-light preserved; 1: dynamic range corrected; 2: direct)

    wave: list
        RGB channel wavelengths [nm]

    obj: str
        microscope objective employed (Zeiss or Nikon)

    ptype: dtype
        processing data type

    Returns
    -------
    None
    """
    # print heading
    print_heading(mode, obj)

    # load CIDRE models
    v, z = load_cidre_models(model_path, wave=wave, obj=obj)

    # compute mean values once
    v_mean = np.mean(v, axis=(0, 1))
    z_mean = np.mean(z, axis=(0, 1))

    # loop over input z-stacks
    n_stack = len(stacks)
    with alive_bar(n_stack, title='z-stack', length=31) as bar:
        for s in stacks:

            # load z-stack
            vol_in = tifffile.imread(s)
            vshape = vol_in.shape

            # check if actually a stack
            if len(vshape) == 4:

                # check if model resize is needed (once)
                v, z = resize_cidre_models(v, z, slice_shape=vshape[1:])

                # loop over z-slices, apply CIDRE correction
                vol_out = np.zeros_like(vol_in, dtype=ptype)
                for d in range(vshape[0]):
                    vol_out[d, ...] = \
                        apply_cidre_to_slice(vol_in[d, ...], v, z, v_mean=v_mean, z_mean=z_mean, mode=mode, ptype=ptype)

                # truncate values
                vdtype = vol_in.dtype
                max_out = np.iinfo(vdtype).max
                vol_out = np.where(vol_out >= 0, vol_out, 0)
                vol_out = np.where(vol_out <= max_out, vol_out, max_out)

                # convert back to input data type
                vol_out = vol_out.astype(vdtype)

                # save corrected volume
                tifffile.imwrite(path.join(dest_path, path.basename(s)), vol_out)

            # clear input stack from memory
            clear_from_memory(vol_in)

            # advance progress bar
            bar()

    # skip line and exit
    print('\n')
