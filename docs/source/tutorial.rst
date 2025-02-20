.. _installation:

Installation
============
To use the *MiC* tool for 3D microscopy illumination correction, follow the instructions below.

#. Download and install the latest Python 3 version: `https://www.python.org/downloads/ <https://www.python.org/downloads/>`_

#. Download and install git: `https://git-scm.com/downloads/ <https://git-scm.com/downloads>`_

#. Clone the *MiC* code repository inside a local folder:
   
   .. code-block:: console

        /path/to/local/dir$ git clone git@github.com:lens-biophotonics/mic.git

#. Create a virtual Python environment using the venv module:
   
   .. code-block:: console

        /path/to/local/dir$ python -m venv .mic_venv

#. Activate the environment:
   
   .. code-block:: console

        /path/to/local/dir$ source .mic_venv/bin/activate   (Linux)
        /path/to/local/dir> .mic_venv\Scripts\activate      (Windows)

#. Install the wheel command line tool using pip:

   .. code-block:: console

        (.mic_venv) /path/to/local/dir$ pip install wheel

#. Build a Python wheel file:

   .. code-block:: console

        (.mic_venv) /path/to/local/dir$ python setup.py bdist_wheel

#. Install the wheel file by executing:

   .. code-block:: console

        (.mic_venv) /path/to/local/dir$ pip install dist/mic-0.1.0-py3-none-any.whl


Complete workflow description
=============================
*MiC* is an intuitive tool designed to efficiently correct uneven illumination in image stacks acquired through 3D fluorescence microscopy,
i.e., two-photon fluorescence microscopy (TPFM) or light sheet fluorescence microscopy (LSFM).
It achieves this by leveraging flat- and dark-field models estimated using retrospective illumination-correction methods.
This tutorial focuses on the CIDRE technique (*Corrected Intensity Distributions using Regularized Energy minimization*; `Smith et al., 2015 <https://www.nature.com/articles/nmeth.3323>`_).
However, while the key assumptions discussed pertain specifically to CIDRE, this workflow may consider other retrospective correction approaches, such as BaSiC (`Peng et al., 2017 <https://www.nature.com/articles/ncomms14836>`_).
The workflow consists of three main steps: (1) generating a dataset of uncorrelated 2D images for various wavelengths of interest from z-stacks previously acquired using different objectives;
(2) identifying optimal flat- and dark-field models with CIDRE (or BaSiC); and (3) applying the *MiC* tool to perform illumination correction based on the newly estimated models.
Each step is described in detail below.

#. **2D image dataset generation**
    The Python notebook included in *mic/notebooks* (*create_cidre_dset.ipynb*) can be used to generate or expand the reference dataset of 2D images used to identify and/or update the illumination models
    related to a specific objective at a particular emission wavelength. This notebook can be run within the same virtual environment created upon installation.
    Users must adapt the source and output directories (i.e., ``source`` and ``outdir``) within the second cell of the notebook and, if necessary, modify the default inclusion criteria specified in the third cell:

        * ``bg_lvl``: (approximate) dark background intensity
        * ``bg_rel_thr``: relative number of sub-threshold background pixels (below ``bg_lvl``)
        * ``mean_rel_thr``: mean intensity relative to the data type maximum

    When applying CIDRE, the following assumptions should be considered and met:

        * images should not be highly correlated, as this can cause significant artifacts in the identified illumination models and, consequently, in the final corrected image stacks (e.g., when using time-lapse images and/or adjacent z-slices of the same tissue ROI). Combining images from different sites can help mitigate this issue;
        * CIDRE performs best with a large number of images containing ample (i.e., not sparse) intensity information that covers the entire field of view for each corrected color;
        * CIDRE requires 1,000 or more uncorrelated images to match or surpass the performance achieved by gold-standard prospective methods (which depend on ad hoc calibration images). 

#. **CIDRE-based flat-field and dark-field estimation**
    The source code of CIDRE (available as a MATLAB script and a Java Fiji plugin) is freely provided as Supplementary Software in Smith's publication.

    You can download it using the following link: `CIDRE source code <https://static-content.springer.com/esm/art%3A10.1038%2Fnmeth.3323/MediaObjects/41592_2015_BFnmeth3323_MOESM177_ESM.zip>`_.

    CIDRE must be run separately on each folder containing a reference image dataset collected for a specific objective and emission wavelength of interest.
    A detailed explanation of its usage can be found in the *cidre.m* file, which includes the definition of the MATLAB function to be executed in the command window.

    The flat-field and dark-field images can be extracted from the ``v`` and ``z`` fields of the ``MODEL`` dictionary returned by this function.
    These fields should be exported as ``.mat`` MATLAB files and then converted to ``.tif`` images. This conversion can be easily performed in Python using *SciPy* and *tifffile*:

    .. code-block:: python

        import scipy.io
        import tifffile as tiff


        v = scipy.io.loadmat('v.mat')['v']
        z = scipy.io.loadmat('z.mat')['z']

        tiff.imwrite('v.tif', v)
        tiff.imwrite('z.tif', z)

    The CIDRE illumination-correction tool requires input images of consistent shape for each color corresponding to a specific objective.
    For instance, when attempting to estimate the flat- and dark-field models of the LaVision 12X objective in Lab 31A, all images must have a size of 2048×2048 pixels.
    Naturally, this will dictate how the final illumination models are shaped.
    However, since MiC appropriately resizes them upon correction, they can be used to process z-stacks of different sizes.
    For instance, 1024×1024 images taken with the same LaVision objective (using pixel binning) can be corrected with the same 2048×2048 pixel flat-field.

    Sample flat-field models, identified for three different objectives at separate emission wavelengths are shown below,
    along with an example of illumination correction applied to a TPFM image stack acquired using a Zeiss 25X objective (adapted from `Sorelli et al., 2023 <https://www.nature.com/articles/s41598-023-30953-w>`_).

    .. image:: _static/ff_ex.png
        :width: 800
        :align: center

#. **Illumination correction with identified flat- and dark-field models: usage examples**

    * Apply a *dynamic-range-adjusted* correction to multiple RGB image stacks, using the illumination models obtained for the TPFM setup in Lab 43 when using a Zeiss 25X objective with the listed emission wavelengths (do not correct the blue channel):

        .. code-block:: console

            (.mic_venv) /path/to/local/dir$ mic /path/to/stacks_dir --field /path/to/illumination/models --objective tpfm_zeiss25x --wavelength 618 482 -1 --mode 1

    * Apply a *zero-light-preserved* correction to a single grayscale image stack acquired using the TPFM setup with a Nikon 10X objective:

        .. code-block:: console

            (.mic_venv) /path/to/local/dir$ mic /path/to/stack.tif --field /path/to/illumination/models --objective tpfm_nikon10x --wavelength 488 --mode 0

    * *NOTE*: the tool's help documentation outlines the mandatory structure required for the folder including the flat- and dark-field models identified for particular objectives at different wavelengths; this can be accessed by running:

        .. code-block:: console

            (.mic_venv) /path/to/local/dir$ mic --help
