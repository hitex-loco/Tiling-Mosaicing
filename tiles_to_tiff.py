import math
import urllib.request
import requests
import os
import glob
import subprocess
import shutil
from tile_convert import bbox_to_xyz, tile_edges
from osgeo import gdal

#---------- CONFIGURATION -----------#
# Option 1: Online source
tile_source = "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"

# Option 2: Local file system source
#tile_source = "C:\offlinemaps\d-area-at-12\{z}\{x}\{y}.jpg"

temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
output_dir = os.path.join(os.path.dirname(__file__), 'output')
zoom = 12
lon_min = 77.132104
lon_max = 77.186159
lat_min = 10.985789
lat_max = 11.039844
#-----------------------------------#


def fetch_tile(x, y, z, tile_source):
    url = tile_source.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z))
    path = f'{temp_dir}\{x}_{y}_{z}.jpg'
    r = requests.get(url)
    with open(path,'wb') as f:
        f.write(r.content)
    # urllib.request.urlretrieve(url, path)
    print(url, path)
    #shutil.copyfile(url, path)
    #print(url, path)
    return(path)


def merge_tiles(input_pattern, output_path):
    
    i=0
    for name in range(len(glob.glob(input_pattern))):
        
        if i==(len(glob.glob(input_pattern))-1):
            break
        if i==0:
            merge_command = 'python gdal_merge.py -o ' + output_path + str(i+1) + '.tif'
            merge_command = merge_command + ' ' + glob.glob(input_pattern)[i] + ' ' + glob.glob(input_pattern)[i+1]
            # merge_command.append(glob.glob(input_pattern)[i])
            # merge_command.append(glob.glob(input_pattern)[i+1])
            os.system(merge_command)
        else:
            merge_command = 'python gdal_merge.py -o ' + output_path + str(i+1) + '.tif'
            merge_command = merge_command + ' ' + output_path + str(i) + '.tif' + ' ' + glob.glob(input_pattern)[i+1]
            #merge_command.append(output_path)
            #merge_command.append(glob.glob(input_pattern)[i+1])
            os.system(merge_command)
            os.remove(output_path + str(i) + '.tif')
        print(merge_command)
        #subprocess.call(merge_command)
        
        
        i=i+1
        print(i+1, 'done')


def georeference_raster_tile(x, y, z, path):
    bounds = tile_edges(x, y, z)
    filename, extension = os.path.splitext(path)
    gdal.Translate(filename + '.tif',
                   path,
                   outputSRS='EPSG:4326',
                   outputBounds=bounds)


x_min, x_max, y_min, y_max = bbox_to_xyz(
    lon_min, lon_max, lat_min, lat_max, zoom)

print(f"Fetching {(x_max - x_min + 1) * (y_max - y_min + 1)} tiles")

for x in range(x_min, x_max + 1):
    for y in range(y_min, y_max + 1):
        try:
            print("i am trying")
            jpg_path = fetch_tile(x, y, zoom, tile_source)
            print(f"{x},{y} fetched")
            georeference_raster_tile(x, y, zoom, jpg_path)
        except OSError:
            print(f"{x},{y} missing")
            pass

print("Fetching of tiles complete")

print("Merging tiles")
merge_tiles(temp_dir + '/*.tif', output_dir + '\\merged')
print("Merge complete")

#shutil.rmtree(temp_dir)
#os.makedirs(temp_dir)
