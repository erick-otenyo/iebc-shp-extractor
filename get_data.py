import telegram_send
import zipfile
import glob
import os
import requests
import subprocess
import geojson

BASE_URL = "http://api.iebc.or.ke/geojson/"


def fetch_data(level, id):
    data_name = level + "_" + str(id) + ".geojson"
    print("Fetching " + data_name)
    r = requests.get(BASE_URL + data_name)
    if r.status_code == 200:
        return r.json()
    else:
        pass


def get_data(level, r):
    message = "Boundary data for each {} as obtained from IEBC :".format(level)
    print(message)
    # telegram_send.send(messages=[message])
    for i in range(222, r):
        r_geojson = fetch_data(level, i)
        if r_geojson:
            if level == "county":
                file_name = strip_string(r_geojson['features'][0]['properties']['COUNTY_NAM']).lower() + " " + level
            elif level == "ward":
                file_name = strip_string(r_geojson['features'][0]['properties']['COUNTY_A_1']).lower() + " " + level
            elif level == "constituency":
                file_name = strip_string(r_geojson['features'][0]['properties']['CONSTITUEN']).lower() + " " + level

            file_name_geojson = file_name + ".geojson"  #
            with open(file_name_geojson, 'w') as f:
                geojson.dump(r_geojson, f)
            shp_name = file_name + '.shp'
            args = ['ogr2ogr', '-f', 'ESRI Shapefile', shp_name, file_name_geojson]
            subprocess.call(args)
            zip_shapefile(shp_name)
            with open(shp_name.replace(".shp",".zip"), "rb") as f:
                telegram_send.send(files=[f])


def zip_shapefile(file_name):
    zip_name = file_name.replace(".shp", ".zip")
    zip_obj = zipfile.ZipFile(zip_name, 'w')
    for infile in glob.glob(file_name.replace(".shp", ".*")):
        print('zipping ' + infile + ' into ' + zip_name)
        if infile != zip_name:
            zip_obj.write(infile, os.path.basename(infile), zipfile.ZIP_DEFLATED)
    print("Shapefile zipped")


def strip_string(sentence):
    punctuation_marks = r', .;:?!−_()[]∖’∖”‘/<>{}#='
    for punctuation in punctuation_marks:
        sentence = sentence.replace(punctuation, " ")
    return sentence


get_data("constituency", 291)
