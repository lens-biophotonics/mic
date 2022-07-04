import numpy as np
import random
import tifffile
from os import listdir, mkdir, path, walk


# path to TIFF z-stacks
source = 'D:\\Nikon_CIDRE_dataset\\NIKON_source_stacks'
dest_ch = [path.join(path.dirname(source), 'NIKON_source_red_v2'),
           path.join(path.dirname(source), 'NIKON_source_green_v2'),
           path.join(path.dirname(source), 'NIKON_source_blue_v2')]

# relative threshold on black pixels
black_rel_thr = 0.80
mean_rel_thr = 0.005

# max channel dataset size (10GB)
max_dataset_size = 2e9


def main():

    # create destination folder if needed
    num_slices = np.zeros((3,), dtype=int)
    for d in range(3):
        if not(path.isdir(dest_ch[d])):
            mkdir(dest_ch[d])
    else:
        num_slices[d] = len([name for name in listdir(dest_ch[d]) if path.isfile(path.join(dest_ch[d], name))])

    # get all z-stacks file paths in source folder
    listOfFiles = list()
    for (dirpath, _, filenames) in walk(source):
        listOfFiles += [path.join(dirpath, file) for file in filenames]
    random.shuffle(listOfFiles)

    # loop over source z-stacks
    stack_ctr = 1
    slice_ctr = num_slices + 1
    num_stacks = len(listOfFiles)
    dataset_size = np.zeros((3,), dtype=np.int64)
    print()
    for f in listOfFiles:

        # print progress
        prc_progress = 100 * (stack_ctr / num_stacks)
        print('              processing stack {0}/{1}: {2:0.1f}%'.format(stack_ctr, num_stacks, prc_progress), end='\r')

        # read z-stack
        zstack = tifffile.imread(f)
        immax = np.iinfo(zstack.dtype).max

        # loop over z-slices
        for z in range(zstack.shape[0]):

            # loop over channels
            for c in range(3):

                # check exported dataset size (per channel)
                if dataset_size[c] < max_dataset_size:
                    img = zstack[z, :, :, c]
                    if np.count_nonzero(img) / np.size(img) > black_rel_thr \
                       and np.mean(img[img != 0]) > mean_rel_thr * immax:

                        # save tiff
                        tifffile.imwrite(path.join(dest_ch[c], str(slice_ctr[c]) + '.tif'), img)

                        # update channel dataset size
                        dataset_size[c] += img.itemsize * img.size

                        # update slice counter
                        slice_ctr[c] += 1

            # break if all channels reached max size
            if np.all(dataset_size) >= max_dataset_size:
                break

        # update stack counter
        stack_ctr += 1
    print('\n\n              Done.')


if __name__ == '__main__':
    main()
