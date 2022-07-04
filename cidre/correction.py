from os import path
from time import perf_counter

import numpy as np
import tifffile
from skimage.transform import resize

from cidre.input import CIDRE
from cidre.printing import print_elapsed_time, print_heading, print_progress
from cidre.utils import clear_from_memory


class CIDRE:
    """ CIDRE mode flags """
    ZERO_PRESERVED = 0
    RANGE_CORRECTED = 1
    DIRECT = 2


def load_cidre_models(cidre_path, wave=[618, 482, -1], obj='zeiss25x',
                      mshape=(512, 512, 3), ch_name=['red', 'green', 'blue']):
    """
    Load CIDRE-based gain (v) and additive noise (z) terms from .txt data files
    (red and green channel components).

    Parameters
    ----------
    cidre_path:
        path to CIDRE model data files

    wave: list
        RGB channels wavelengths [nm]

    ch_name: list
        channels name

    Returns
    -------
    v: ndarray (shape=(512,512), dtype=float64)
        spatial gain function

    z: ndarray (shape=(512,512), dtype=float64)
        spatial additive noise
    """

    # objective selection
    cidre_path = path.join(cidre_path, obj.lower())

    # initialize empty model arrays
    v = np.empty(mshape)
    v[:] = np.nan
    z = v.copy()
    print('  channels:  ', end='')

    # load CIDRE models (gain and additive terms, v and z)
    ch_corr = ''
    for c in range(len(ch_name)):
        if wave[c] > 0:
            v_path = path.join(cidre_path, str(wave[c]), 'v.txt')
            z_path = path.join(cidre_path, str(wave[c]), 'z.txt')
            if c > 0:
                ch_corr += '             '
            try:
                v[..., c] = np.loadtxt(v_path, delimiter='\t')
                z[..., c] = np.loadtxt(z_path, delimiter='\t')
            except Exception:
                ch_corr += '{}\t({}nm not available! Skipping channel...)\n'.format(ch_name[c], str(wave[c]))
            else:
                ch_corr += ch_name[c] + '\t(' + str(wave[c]) + 'nm)\n'
    print(ch_corr + '\n')

    return v, z


def resize_cidre_models(v, z, slice_shape):
    """
    Resize CIDRE models if needed.

    Parameters
    ----------
    v: ndarray (shape=(512,512), dtype=float)
        spatial gain function

    z: ndarray (shape=(512,512), dtype=float)
        spatial additive noise

    slice_shape: tuple
        lateral (in-plane) shape of input image stacks

    Returns
    -------
    v_res: ndarray (dtype=float)
        resized spatial gain function

    z_res: ndarray (dtype=float)
        resized spatial additive noise
    """
    # if shapes do not match...
    model_shape = v.shape
    if slice_shape != model_shape:
        v_res = np.zeros(slice_shape)
        z_res = v_res.copy()

        # resize models, looping over channels
        for c in range(slice_shape[-1]):
            v_res[..., c] = resize(v[..., c], slice_shape[:-1],
                                   anti_aliasing=True, preserve_range=True)
            z_res[..., c] = resize(z[..., c], slice_shape[:-1],
                                   anti_aliasing=True, preserve_range=True)
        return v_res, z_res

    else:
        return v, z


def apply_cidre_models(slice_rgb, v, z, v_mean, z_mean,
                       mode=CIDRE.ZERO_PRESERVED, ptype=np.float64):
    """
    Apply CIDRE correction models to 2D RGB slice.

    Parameters
    ----------
    slice_rgb: ndarray (y, x, c)
        RGB slice

    v: ndarray
        gain model

    z: ndarray
        offset model

    v_mean: float
        mean gain value (computed once for efficiency's sake)

    z_mean: float
        mean offset value (computed once for efficiency's sake)

    mode: int
        correction mode flag

    Returns
    -------
        corrected RGB slice
    """
    # original conversion
    slice_rgb = slice_rgb.astype(ptype)

    # initialize zero slice
    corr_slice = np.zeros_like(slice_rgb)

    # zero-light preserved
    if mode == CIDRE.ZERO_PRESERVED:
        for c in range(3):
            if v_mean[c] != np.nan:
                corr_slice[..., c] = z_mean[c] + v_mean[c] * (np.divide(slice_rgb[..., c] - z[..., c], v[..., c]))

    # dynamic range corrected
    elif mode == CIDRE.RANGE_CORRECTED:
        for c in range(3):
            if v_mean[c] != np.nan:
                corr_slice[..., c] = v_mean[c] * (np.divide(slice_rgb[..., c] - z[..., c], v[..., c]))

    # direct correction
    elif mode == CIDRE.DIRECT:
        for c in range(3):
            if v_mean[c] != np.nan:
                corr_slice[..., c] = np.divide(slice_rgb[..., c] - z[..., c], v[..., c])

    return corr_slice


def correct_TPFM_illumination(stacks, model_path, dest_path,
                              mode=CIDRE.ZERO_PRESERVED, wave=[618, 482, -1],
                              obj='zeiss25x', pro_dtype=np.float64):
    """
    CIDRE-based illumination correction function.

    Parameters
    ----------
    stacks: list
        list of input stacks to be processed

    model_path:
        path to CIDRE model data files
        (default: /mnt/NASone/michele/CIDRE)

    dest:
        output path

    mode: int
        correction mode flag

    wave: list
        RGB channels wavelengths [nm]

    obj: string
        microscope objective employed (Zeiss or Nikon)

    pro_dtype: dtype
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
    Nstack = len(stacks)
    loop_counter = 1
    tic = perf_counter()
    for s in stacks:

        # print progress
        print_progress(loop_counter, Nstack)

        # load z-stack
        vol_in = tifffile.imread(s)
        vshape = vol_in.shape
        vdtype = vol_in.dtype
        max_out = np.iinfo(vdtype).max

        # check if actually a stack
        if len(vshape) == 4:

            # check if model resize is needed (once)
            v, z = resize_cidre_models(v, z, slice_shape=vshape[1:])

            # loop over z-slices
            vol_out = np.zeros_like(vol_in, dtype=pro_dtype)
            for d in range(vshape[0]):

                # apply CIDRE correction
                vol_out[d, ...] = apply_cidre_models(vol_in[d, ...], v, z,
                                                     v_mean=v_mean, z_mean=z_mean, mode=mode, ptype=pro_dtype)

            # truncate values
            vol_out = np.where(vol_out >= 0, vol_out, 0)
            vol_out = np.where(vol_out <= max_out, vol_out, max_out)

            # convert back to input data type
            vol_out = vol_out.astype(vdtype)

            # save corrected volume
            tifffile.imwrite(path.join(dest_path, path.basename(s)), vol_out)

        # clear input stack from memory
        clear_from_memory(vol_in)

        # increase counter
        loop_counter += 1

    # print total time
    print_elapsed_time(tic, Nstack)
