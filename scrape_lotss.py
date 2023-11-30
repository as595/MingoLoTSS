import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import requests
import time
import os, sys

file_exts = ['-low-mosaic','-low-residual-mosaic','-residual-mosaic']

def init_driver():
 
     # initiate the driver:
     driver = webdriver.Chrome()
 
     # set a default wait time for the browser [5 seconds here]:
     driver.wait = WebDriverWait(driver, 5)
 
     return driver
     
def close_driver(driver):
 
    driver.close()
 
    return
    
def enter_coords(driver, coords, fieldsize='0.1'):
 
    # open the web page in the browser:
    driver.get("https://vo.astron.nl/hetdex/lotss-dr1-img/cutout/form")
 
    # find the coordinates field:
    coords_field = driver.find_element(By.NAME, "hPOS")
    coords_field.send_keys(coords)
    driver.implicitly_wait(1)
    
    # find the fieldsize field:
    fieldsize_field = driver.find_element(By.NAME, "hSIZE")
    fieldsize_field.send_keys(Keys.BACK_SPACE)
    fieldsize_field.send_keys(Keys.BACK_SPACE)
    fieldsize_field.send_keys(Keys.BACK_SPACE)
    fieldsize_field.send_keys(fieldsize)
    driver.implicitly_wait(1)
    
    # find the intersection type field:
    fieldsize_field = driver.find_element(By.ID, "genForm-hINTERSECT-3").click()
    driver.implicitly_wait(1)
    
    # find the "go" button:
    fieldsize_field = driver.find_element(By.NAME, "submit").click()
    driver.implicitly_wait(1)
 
    return
    
def get_all_files(driver, path=''):

    # downloads all returned files
    
    file_list = driver.find_elements(By.CLASS_NAME, "productlink")
    for file in file_list:
        url = file.get_attribute("href")
        name = file.text
        file = requests.get(url, allow_redirects=True)
        open(path+name, 'wb').write(file.content)
        
    return
    
    
def get_mos_files(driver, filename='', path='', overwrite=False):

    # only downloads '*-mosaic.fits' and '*-mosaic-rms.fits'
    
    file_list = driver.find_elements(By.CLASS_NAME, "productlink")
    for file in file_list:
        
        name = file.text
        field = name.split('-')[0]
        ext = name.replace('.fits','').replace(field,'')
        
        if ext not in file_exts:
            fname = filename+'_'+name
            fexist = os.path.exists(path+fname)
            if overwrite or not fexist:
                url = file.get_attribute("href")
                file = requests.get(url, allow_redirects=True)
                open(path+fname, 'wb').write(file.content)
                print("Downloaded: "+path+fname)
            else:
                print("File exists: "+path+fname)
        
    return
    
    
    
if __name__ == "__main__":
 
    # start a driver for a web browser:
    driver = init_driver()
 
    # enter source data:
    enter_coords(driver, coords='161.0675996198537, 52.67702739650525', fieldsize='0.1')
    
    # download files:
    get_mos_files(driver, filename='test', overwrite=False)
    
    # add an extra wait
    time.sleep(2)
 
    # close the driver:
    close_driver(driver)
