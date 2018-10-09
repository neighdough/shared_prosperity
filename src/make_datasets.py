import pandas as pd
import geopandas as gpd
import os


def clean_boundaries(f):
    for d in os.listdir(f):
        path = f + d
        shp = [i for i in os.listdir(path) if i.endswith(".shp")][0]
        df = gpd.read_file(path+"/"+shp)
        df = df[df.GISJOIN.str[:7] == "G470157"]
        df.columns = [col.lower() for col in df.columns]
        df.to_file("../../processed/"+shp)

if __name__=="__main__":
    os.chdir(__file__)
    clean_boundaries("../data/raw/nhgis0021_shape/")
