from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units as u
import glob
import pylab as pl
import numpy as np
import os, sys
from PIL import Image
import pandas as pd
              
              
def get_maps(src_map, rms_map):

    src_hdu = fits.open(src_map)
    rms_hdu = fits.open(rms_map)
    
    src_data = np.squeeze(src_hdu[0].data)
    rms_data = np.squeeze(rms_hdu[0].data)

    # set NaN to zero:
    src_data[np.where(np.isnan(src_data))]=0.0
    rms_data[np.where(np.isnan(rms_data))]=0.0

    return src_data, rms_data
    
def get_rms_map(src_map, rms_files):

    srcname = src_map.split('-')[0]
    for file in rms_files:
        if srcname in file:
            rms_map = file
            
    return rms_map
    
def get_class(srcid, cat_data):

    obj_class = -1
    
    for i in range(len(cat_data)):
        item = cat_data[i]
        if item[0]==srcid:
            fri  = item[5]
            frii = item[6]
            ind  = item[7]
            sml  = item[8]
            nat  = item[9]
            wat  = item[10]
            dd   = item[11]
            
            if fri and not (sml or nat or wat or dd):
                obj_class = 0
            elif fri and nat:
                obj_class = 1
            elif fri and wat:
                obj_class = 2
            elif fri and sml:
                obj_class = 3
            elif frii and not (sml or nat or wat or dd):
                 obj_class = 4
            elif frii and sml:
                 obj_class = 5
            elif dd:
                 obj_class = 6
            elif ind and not sml:
                 obj_class = 7
            elif ind and sml:
                 obj_class = 8
            elif sml and not (fri or frii or ind or nat or wat or dd):
                 obj_class = 9
        
    return obj_class
    
    
def get_separation(ra_cat, dec_cat, fitsfile):

    img_hdu = fits.open(fitsfile)
    img_hdr = img_hdu[0].header
    w = WCS(img_hdr)
                
    ax1 = img_hdr['NAXIS1']
    ax2 = img_hdr['NAXIS2']

    sky = w.pixel_to_world(int(ax1/2), int(ax2/2))
    cat = SkyCoord(ra_cat*u.deg, dec_cat*u.deg, frame='icrs')
    sep = cat.separation(sky)

    return sep.arcsecond
    
    
def get_pnans(fitsfile):

    src_hdu = fits.open(fitsfile)
    src_data = np.squeeze(src_hdu[0].data)
    
    npix = src_data.shape[0]*src_data.shape[1]
    
    nans = np.count_nonzero(np.isnan(src_data))
    pnans = float(nans/npix)*100.

    return pnans


def remove_nan_files(fits_path='./fits/'):

    rms_files = glob.glob(fits_path+'*rms.fits')
    mos_files = glob.glob(fits_path+'*mosaic.fits')

    for src_map in mos_files:
        rms_map = get_rms_map(src_map, rms_files)
        src_data, rms_data = get_maps(src_map, rms_map)
        nans = np.count_nonzero(src_data)
        if nans==0:
            print("Removing: "+src_map)
            os.system("rm -rf "+src_map+" \n")
            os.system("rm -rf "+rms_map+" \n")
            
    return
    

def make_match(catalog, fits_path='./fits/'):

    fitslist, fieldlist, classlist, separations, perc_nans = [], [], [], [], []
    
    hdu  = fits.open(catalog)
    data = hdu[1].data
    hdr  = hdu[1].header
    
    ids_cat = [data[i][0] for i in range(len(data))]
    ra_cat  = np.array([data[i][1] for i in range(len(data))])
    dec_cat = np.array([data[i][2] for i in range(len(data))])
    
    fits_list = glob.glob(fits_path+'*mosaic.fits')

    m=0
    for i in range(len(ids_cat)):
        n=0; files=[]; fields=[]; sepns=[]; pnans=[]
        for file in fits_list:
            if ids_cat[i] in file:
                files.append(file.split('/')[-1])
                if len(file.split('_'))==2:
                    fields.append(file.split('_')[1].split('-')[0])
                elif len(file.split('_'))==3:
                    fields.append('+'.join(file.split('_')[1:]).split('-')[0])
                sepns.append(get_separation(ra_cat[i], dec_cat[i], file))
                pnans.append(get_pnans(file))
                n+=1
        if n>1:
            m+=1
            idx = np.argmin(sepns)
            if (np.sum(pnans)==0.) or (pnans[idx]==np.min(pnans)):
                fitsfile = files[idx]
                separation = sepns[idx]
                perc_nan = pnans[idx]
                field = fields[idx]
            elif np.sum(np.array(sepns)>=15.)==0:
                idx = np.argmin(pnans)
                fitsfile = files[idx]
                separation = sepns[idx]
                perc_nan = pnans[idx]
                field = fields[idx]
            else:
                if ids_cat[i]=='ILTJ122754.23+530332.7': idx = 0
                if ids_cat[i]=='ILTJ133946.84+512633.5': idx = 0
                fitsfile = files[idx]
                separation = sepns[idx]
                perc_nan = pnans[idx]
                field = fields[idx]
                
        else:
            fitsfile = files[0]
            separation = sepns[0]
            perc_nan = pnans[0]
            field = fields[0]
            
        
        obj_class = get_class(ids_cat[i], data)
        if obj_class==-1:
            print("Source "+ids_cat[i]+" not found")
        else:
            classlist.append(obj_class)
    
        fieldlist.append(field)
        fitslist.append(fitsfile)
        separations.append(separation)
        perc_nans.append(perc_nan)
        
    df_data = {"Source ID": ids_cat,
               "Field": fieldlist,
               "Class": classlist,
               "Map File": fitslist,
               "Separation": separations,
               "Percentage NaN": perc_nans,
              }

    df = pd.DataFrame(df_data, columns=['Source ID','Field','Class','Map File','Separation','Percentage NaN'])
        
    return df

def fits_validation(filename, csvfile):

    # match catalog with fits files:
    df = make_match(catalogue, fits_path='./fits/')
    
    # remove fits files full of NaNs:
    remove_nan_files(fits_path='./fits/')
    
    # write out csv file:
    df.to_csv(csvfile)

    return


if __name__ == "__main__":

    filename = 'Mingo19_LoMorph_Cat.fits'
    csvfile = "MingoML.csv"
        
    fits_validation(filename, csvfile)
