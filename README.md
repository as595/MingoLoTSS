# MingoLoTSS
Repo for MingoLoTSS batched dataset of classified radio galaxies from the LOFAR LoTSS survey.

---

This repo contains the code for *building* the MingoLoTSS deep learning dataset. To *use* the dataset all you need is the dataset class file, which will automatically load the pre-made dataset:

* `MingoLoTSS.py`

If you do use the dataset in a publication, please cite the originating catalogue paper and the DOI for the batched dataset:

* Mingo et al. [link]
* Zenodo link [link]

---

## Dataset description

#### Images

Each sample in the MingoLoTSS dataset contains a single channel 150 x 150 pixel image. 150 pixels is equivalent to 37.5 arcmin (0.625 degrees), which is larger than the LAS for all objects in the catalog with the exception of ILTJ142930.70+544406.2, which has an LAS of 53.7 arcmin. This source is not currently excluded from the data set. The next largest source has an LAS of ~34 arcmin.

#### Labels

The classifications for each source are mapped to class labels: {0, 1, 2, ... 9} as described in the table below, where the relative numbers of each class are also listed.

<p align="center" width="100%">
    <img width="70%" src="https://github.com/as595/MingoLoTSS/blob/main/images/labels.png">
</p>

## Re-making the dataset

To remake the MingoLoTSS dataset simply run the `main.py` script:

```python
python3 main.py
```

This will execute a number of steps including: 

 - automatically downloading the FITS images for each source from the LoTSS image server;
 - applying the image pre-processing steps (specified below) and creating PNG files for each source;
 - creating a batched dataset (MNIST-style) for use with standard deep learning libraries such as PyTorch and Keras.

### Data Extraction

FITS files are scraped individually from the LoTSS postage stamp server with a field-of-view of 0.1 degree and a pixel size of 15 arcseconds (`scrape_lotss.py`). The full catalogue is scraped using the `get_fits.py` script.

If a specified FITS file already exists then the default is not to overwrite it with a new file. This can be changed by setting `overwrite=True` when `get_fits()` is called.


### Image Pre-processing

#### Field down-select

For many catalogued objects, FITS files from multiple LoTSS fields are recovered. In a number of cases FITS files were found to contain only NaN values, where the object was just outside the field of view for a particular LoTSS field. These files were removed (`validation.py`). 

For objects that still had multiple FITS maps associated with them the preferred file was selected based on two criteria: (i) the angular separation between the catalogued position of the source and the centre of the FITS image, and (ii) the percentage of NaN-valued pixels in the image. Four cases were identified:

1. Where the percentage of NaN-valued pixels was uniformly zero for all matched FITS files, the file with the smallest separation was selected.

2. Where Case 1 did not apply, and the file with the minimum percentage of NaN-valued pixels was also the same as the file with the smallest separation, this file was selected.

3. Where neither Case 1 or Case 2 applied, and all of the separations were smaller than one pixel, the file with the lowest percentage of NaN-valued pixels was selected.

4. Two objects, ILTJ122754.23+530332.7 & ILTJ133946.84+512633.5, were found not to meet the criteria for any of the previous cases and these objects had their file match selected manually.

#### Field edges

FITS files extracted from the LoTSS postage stamp server are not guaranteed to be equal in size, with images near field edges often being truncated. For these edge cases the field centre and the catalogued object position are not necessarily coincident. Fifteen matched FITS images were found to have an offset between the catalogued source position and the FITS field centre greater than 15 arcseconds (i.e. one pixel). These images were visually inspected to confirm that the source was present in the image and then both the image and rms maps were recentred on the catalogued source position, using NaN padding where resizing was required to keep the full image size above 150 x 150 pixels.


**ILTJ111725.92+563648.6** Left: original image. Right: recentred and padded image.
<p align="center" width="100%">
    <img width="70%" src="https://github.com/as595/MingoLoTSS/blob/main/images/recentre.png">
</p>


#### Image pre-processing

For each object in the catalogue there is now one source image and one rms noise image. These are used to perform the following pre-processing steps:

1. Set all NaN-valued pixels in the image file to zero.

2. Use the rms image to set all pixels in the source image with pixel values less than 3 times the rms at the same position to zero.

Left: original image. Centre: rms image. Right: subtracted image.
<p align="center" width="100%">
    <img width="70%" src="https://github.com/as595/MingoLoTSS/blob/main/images/subtracted.png"> 
</p>

3. Crop the central 150 x 150 pixels.

4. Set all pixels outside a radial distance of 75 pixels to zero.

5. Normalise the image using:

$$
Output = 255 \frac{Input - Min}{Max - Min}
$$

Left: centrally cropped image. Centre: radially cropped image. Right: normalised image.
<p align="center" width="100%">
    <img width="70%" src="https://github.com/as595/MingoLoTSS/blob/main/images/masked.png"> 
</p>

These steps are specified in `process_fits.py`.

### Dependencies

Most of the dependencies are very standard; however the code uses the [`selenium`](https://selenium-python.readthedocs.io) library for scraping the FITS files from the postage stamp server. Here this is set up to use the [Chrome](https://www.google.com/chrome/) driver for `selenium`, which may require you to download the appropriate version of chrome and its associated *chromedriver* [from google](https://googlechromelabs.github.io/chrome-for-testing/). The chromedriver should be findable somewhere in your PATH, e.g. `/usr/local/bin`.
