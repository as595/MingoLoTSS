from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u
import glob
import pylab as pl
import numpy as np
import pandas as pd
import os, sys
from PIL import Image

from mpl_toolkits.axes_grid1 import ImageGrid
from reproject import reproject_interp

def get_sky_pos(object, catalog):

    src_id = object['Source ID']
    
    hdu  = fits.open(catalog)
    data = hdu[1].data
    
    ids_cat = np.array([data[i][0] for i in range(len(data))])
    ra_cat  = np.array([data[i][1] for i in range(len(data))])
    dec_cat = np.array([data[i][2] for i in range(len(data))])
    
    idx = np.argwhere(ids_cat==src_id)

    return ra_cat[idx], dec_cat[idx]
    
    
def get_pix_pos(ra, dec, fitsfile):

    img_hdu = fits.open(fitsfile)
    img_hdr = img_hdu[0].header
    w = WCS(img_hdr)
                
    sky = SkyCoord(ra*u.deg, dec*u.deg, frame='icrs')
    x, y = w.world_to_pixel(sky)

    return x,y
    
    
def pad_and_recentre(img, rms, x, y):

    """
    y_np = x_fits
    x_np = y_fits
    """
    
    xdim = img.shape[0]
    ydim = img.shape[1]

    padx1, padx2, pady1, pady2 = 0, 0, 0, 0
    
    x1 = x
    x2 = xdim - x
    
    y1 = y
    y2 = ydim - y

    if x2>x1:
        padx1 = int(x2 - x1)
    else:
        padx2 = int(x1 - x2)

    if y2>y1:
        pady1 = int(y2 - y1)
    else:
        pady2 = int(y1 - y2)

    img = np.pad(img, ((padx1,padx2), (pady1,pady2)), 'constant', constant_values=((np.nan, np.nan),(np.nan,np.nan)))
    rms = np.pad(rms, ((padx1,padx2), (pady1,pady2)), 'constant', constant_values=((np.nan, np.nan),(np.nan,np.nan)))

    return img, rms
    

def get_maps(src_map, rms_map):

    src_hdu = fits.open(src_map)
    rms_hdu = fits.open(rms_map)
    
    src_data = np.squeeze(src_hdu[0].data)
    rms_data = np.squeeze(rms_hdu[0].data)

    # set NaN to zero:
    #src_data[np.where(np.isnan(src_data))]=0.0
    #rms_data[np.where(np.isnan(rms_data))]=0.0

    return src_data, rms_data
    
    
def crop_centre(img, crop=150):
    
    xsize = np.shape(img)[0] # image width
    ysize = np.shape(img)[1] # image height
    startx = xsize//2-(crop//2)
    starty = ysize//2-(crop//2)
    sub_img = img[startx:startx+crop,starty:starty+crop]
    
    return sub_img
    
    
def apply_circular_mask(img):

    centre = (np.rint(img.shape[0]/2), np.rint(img.shape[1]/2))
    radius = min(centre[0], centre[1], img.shape[0]-centre[0], img.shape[1]-centre[1])

    Y, X = np.ogrid[:img.shape[1], :img.shape[1]]
    dist_from_centre = np.sqrt((X - centre[0])**2 + (Y-centre[1])**2)

    mask = dist_from_centre <= radius
    
    img *= mask.astype(int)
    
    return img
    
    
def subtract_3sigma(src_data, rms_data):
        
    img_sub = src_data
    img_sub[np.where(src_data<=3.*rms_data)] = 0.0

#    fig = pl.figure()
#    grid = ImageGrid(fig, 111,  # similar to subplot(111)
#                 nrows_ncols=(1, 3),  # creates 2x2 grid of axes
#                 axes_pad=0.1,  # pad between axes in inch.
#                 )
#    grid[0].imshow(src_data)
#    grid[1].imshow(rms_data)
#    grid[2].imshow(img_sub)
#    grid[0].axis('off');grid[1].axis('off');grid[2].axis('off')
#    pl.show()
        
    return img_sub


def rescale_image(img):

    img_max = np.max(img)
    img /= img_max
    img *= 255.

    return img
    
    
def run_preprocessing(src_data, rms_data, make_images=False):

    if make_images:
        fig = pl.figure()
        grid = ImageGrid(fig, 111,  # similar to subplot(111)
                nrows_ncols=(1, 3),  # creates 2x2 grid of axes
                axes_pad=0.1,  # pad between axes in inch.
                )
        grid[0].imshow(src_data)
        grid[1].imshow(rms_data)
        
    
    # set nans to zero:
    npix = src_data.shape[0]*src_data.shape[1]
    nans = np.count_nonzero(np.isnan(src_data))
    pnans = float(nans/npix)*100.
    
    src_data[np.where(np.isnan(src_data))]=0.0
    rms_data[np.where(np.isnan(rms_data))]=0.0
        
    # subtract background:
    img = subtract_3sigma(src_data, rms_data)
        
    if make_images:
        grid[2].imshow(img)
        pl.show()
        
    # crop centre:
    img = crop_centre(img)
    
    if make_images:
        fig = pl.figure()
        grid = ImageGrid(fig, 111,  # similar to subplot(111)
                nrows_ncols=(1, 3),  # creates 2x2 grid of axes
                axes_pad=0.1,  # pad between axes in inch.
                )
        grid[0].imshow(img)
        
    # apply circular mask:
    img = apply_circular_mask(img)
        
    if make_images:
        grid[1].imshow(img)
        
    # rescale image:
    img = rescale_image(img)

    if make_images:
        grid[2].imshow(img)
        pl.show()
    
    return img, pnans
    
    
def get_rms_map(src_map, rmspath='./fits/'):

    rms_files = glob.glob(rmspath+'*rms.fits')
    
    srcname = src_map.split('-')[0]
    for file in rms_files:
        if srcname in file:
            rms_map = file
            
    return rms_map
    
    
def create_png(image_data, name='', path=''):
    
    im = Image.fromarray(image_data)
    im = im.convert('L')
    im.save(path+name+".png")
    
    return
    
    
def catalog_check(catalog, img_path):

    hdu = fits.open(catalog)
    data = hdu[1].data
    ids_cat = [data[i][0] for i in range(len(data))]
    ids_cat = set(ids_cat)
    
    img_list = glob.glob(img_path+'*.png')
    id_list = [img.split('/')[2].split('_')[0] for img in img_list]
    id_list = set(id_list)

    if not ids_cat.issubset(id_list):
        diff = list(ids_cat - id_list)
        print(diff)
    
    return
    
def preprocess(filename, fitspath, csvfile):

    df = pd.read_csv(csvfile)

    imagelist = []
    for i in range(len(df)):

        fitsfile = df['Map File'].iloc[i]
        src_map = fitspath+fitsfile
        
        # find matching rms file:
        rms_map = get_rms_map(src_map, rmspath=fitspath)
        
        # extract data:
        src_data, rms_data = get_maps(src_map, rms_map)
        
        # resize and centre edge cases:
        if src_data.shape[0]<150 or src_data.shape[1]<150 or df['Separation'].iloc[i]>15.:
            ra, dec = get_sky_pos(df.iloc[i], catalogue)
            x, y = get_pix_pos(ra, dec, src_map)
            src_data, rms_data = pad_and_recentre(src_data, rms_data, y, x)  # note: (x,y) transposed to (y,x) for fits to numpy
            
        # pre-process image:
        max_nan = 0.
        img, pnans = run_preprocessing(src_data, rms_data, make_images=False)
        if pnans>max_nan: max_nan = pnans
        
        # output png image:
        imgname = src_map.split('/')[2].split('-')[0]
        create_png(img, name=imgname, path='./img/')
        
        imagelist.append(imgname+".png")
        
    print(max_nan)
    
    print(len(df), len(imagelist))
    
    # update csv file
    df.reset_index(drop=True)
    df["Image File"] = imagelist
    df.to_csv("MingoML.csv")

    return
    
    
if __name__ == "__main__":

    catalogue = "Mingo19_LoMorph_Cat.fits"
    csvfile = "MingoML.csv"
    fitspath = "./fits/"
    
    preprocess(filename, fitspath, csvfile)
    catalog_check(catalogue, img_path='./img/')
    
    
