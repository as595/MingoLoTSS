

# specify source catalog:
filename = 'Mingo19_LoMorph_Cat.fits'

# scrape fits files from LoTSS image server:
fitspath = './fits/'
get_fits(filename)

# FITS validation:
csvfile = "MingoML.csv"
fits_validation(filename, csvfile)

# do data pre-processing and create PNG files
preprocess(filename, fitspath, csvfile)

# IMG validation:
catalog_check(filename, img_path='./img/')

# make batched dataset:
do_batch(csvfile)
