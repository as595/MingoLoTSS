from astropy.io import fits
import numpy as np
import pandas as pd
import pylab as pl


def get_id_by_class():

    filename = 'Mingo19_LoMorph_Cat.fits'
    hdu = fits.open(filename)
    data = hdu[1].data

    srcname, classes = [], []
    for i in range(len(data)):

        item = data[i]
        
        fri  = item[5]
        frii = item[6]
        ind  = item[7]
        sml  = item[8]
        nat  = item[9]
        wat  = item[10]
        dd   = item[11]
        
        if fri and sml and nat: print("here")
        
        if fri and not (sml or nat or wat or dd):
            obj_class = 0
        elif fri and sml:
            obj_class = 1
        elif fri and nat:
            obj_class = 2
        elif fri and wat:
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
             
        srcname.append(item[0])
        classes.append(obj_class)
        
    class_list = {"Source ID": srcname,
                  "Class": classes}
                  
    df = pd.DataFrame(class_list, columns=['Source ID','Class'])
             
    return df

def get_class_count():

    filename = 'Mingo19_LoMorph_Cat.fits'
    hdu = fits.open(filename)
    data = hdu[1].data
    
    classes = np.zeros(10)

    for i in range(len(data)):

        item = data[i]
        
        fri  = item[5]
        frii = item[6]
        ind  = item[7]
        sml  = item[8]
        nat  = item[9]
        wat  = item[10]
        dd   = item[11]
        
        if fri and sml and nat: print("here")
        
        if fri and not (sml or nat or wat or dd):
            classes[0] +=1
        elif fri and sml:
            classes[1] +=1
        elif fri and nat:
            classes[2] +=1
        elif fri and wat:
            classes[3] +=1
        elif frii and not (sml or nat or wat or dd):
            classes[4] +=1
        elif frii and sml:
            classes[5] +=1
        elif dd:
            classes[6]+=1
        elif ind and not sml:
            classes[7]+=1
        elif ind and sml:
            classes[8]+=1
        elif sml and not (fri or frii or ind or nat or wat or dd):
            classes[9]+=1
      
    print(classes, np.sum(classes))
    print("FRI (total): ", classes[0]+classes[2]+classes[3])
    print("FRII (total): ", classes[4])
    print("Ind (total): ", classes[7]+classes[8])
    
    return classes

def get_las_dist():

    filename = 'Mingo19_LoMorph_Cat.fits'
    hdu = fits.open(filename)
    data = hdu[1].data
    
    las = np.array([data[i][3] for i in range(len(data))])
    
    n, bins, patches = pl.hist(las, 50, density=False, facecolor='green', alpha=0.75)
    pl.plot([2250,2250],[0,5000])
    pl.show()
    
    idx = np.argwhere(las>2000)
    print(idx)
    print(data[np.where(las>2000)])
    
    return

if __name__ == "__main__":

    get_class_count()
    get_las_dist()
