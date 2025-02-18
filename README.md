## Installation
To install the MIC tool for 3D microscopy illumination correction, follow the instructions below.

1. Clone the MIC code repository inside a local folder by executing:
    ```console
    /path/to/local/dir$ git clone git@github.com:lens-biophotonics/mic.git
    ```

2. Create a virtual Python environment using the venv module:
    ```console
    /path/to/local/dir$ python -m venv .mic_venv
    ```

3. Activate the environment:
    ```console
    /path/to/local/dir$ source .mic_venv/bin/activate   (Linux)
    /path/to/local/dir$ .mic_venv\Scripts\activate      (Windows)
    ```

4. Install the wheel command line tool using pip:
    ```console
    /path/to/local/dir$ pip install wheel
    ```

5. Build a Python wheel file by executing:
    ```console
    /path/to/local/dir$ python setup.py bdist_wheel
    ```

6. Install the wheel file by executing:
    ```console
    /path/to/local/dir$ pip install dist/mic-0.1.0-py3-none-any.whl
    ```

## Usage examples
* Apply a dynamic-range-adjusted correction to multiple RGB image stacks, using the flat and dark field models obtained for the listed wavelengths (do not correct the blue channel):
    ```console
    /path/to/local/dir$ mic /path/to/stacks_dir --field /path/to/illumination/models --objective zeiss25x --wavelength 618 482 -1 --mode 1
    ```

* Apply a zero-light-preserved correction to a single grayscale image stack:
    ```console
    /path/to/local/dir$ mic /path/to/stack --field /path/to/illumination/models --objective nikon10x --wavelength 488 --mode 0
    ```

* *NOTE* the tool's help documentation outlines the required structure of the folder including the flat and dark field models identified for particular objectives at different wavelengths; this can be accessed by running:

    ```console
    /path/to/local/dir$ mic --help
    ```

## Documentation
Please read the full documentation at this page:
https://lens-biophotonics.github.io/mic/

## References

Smith, K., Li, Y., Piccinini, F. et al. (2015), CIDRE: an illumination-correction method for optical microscopy. Nat Methods 12, 404–406. 
doi: [10.1038/nmeth.3323](https://doi.org/10.1038/nmeth.3323)

Sorelli, M., Costantini, I., Bocchi, L., Axer, M., Pavone, F. S., Mazzamuto, G.
(2023), Fiber enhancement and 3D orientation analysis in label-free
two-photon fluorescence microscopy, Scientific Reports, 13:4160.
doi: [10.1038/s41598-023-30953-w](https://doi.org/10.1038/s41598-023-30953-w)
