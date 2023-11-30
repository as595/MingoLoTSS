from scrape_lotss import *
from astropy.io import fits

def get_fits(filename):
    hdu = fits.open(filename)
    data = hdu[1].data

    # total objects:
    print("Total number of catalog objects: ", len(data))

    # start a driver for a web browser:
    driver = init_driver()

    for i in range(len(data)):
        srcname = data[i][0]
        coords  = str(data[i][1])
        coords += ', '+str(data[i][2])
        
        print("------------------------")
        print(srcname, coords)
        
        # enter source data:
        enter_coords(driver, coords=coords, fieldsize='0.1')
            
        # download files:
        get_mos_files(driver, filename=srcname, path='./fits/', overwrite=False)
            
        # add an extra wait
        time.sleep(2)
     
    # close the driver:
    close_driver(driver)

if __name__ == "__main__":
 
    filename = 'Mingo19_LoMorph_Cat.fits'
    get_fits(filename)
