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

def clean_table(f):
    df = pd.read_csv(f+"/nhgis0019_ts_nominal_tract.csv", encoding="windows-1252")
    df.rename(str.lower, axis="columns", inplace=True)
    df = df[df.nhgiscode.str[:7] == "G470157"]
    def rename_columns(columns):
        new_columns = {"b18aa": "r_wh_", "b18ab": "r_bl_", "b18ac": "r_ai_", 
                                "b18ad": "r_as_", "b18ae": "r_2m_", #race
                       "b84aa": "emp_tot_", "b84ad": "emp_", "b84ae": "emp_un_", #employment status
                       "cl6aa": "pov_" #poverty
                       }
        columns_to_rename = [col for col in columns if col[:5] in new_columns.keys()
                                and col[-1] != "m"]
        return {x: new_columns[x[:5]] + x[-4:] 
                    if "125" not in x
                    else new_columns[x[:5]] + "2012"
                    for x in columns_to_rename}

    new_col_dict = rename_columns(df.columns)
    df.rename(new_col_dict, inplace=True, axis="columns")

    cols_to_keep= ['nhgiscode', 'gjoin1970', 'gjoin1980', 'gjoin1990', 'gjoin2000',
                   'gjoin2010', 'gjoin2012', 'state', 'statefp', 'statenh', 'county',
                   'countyfp', 'countynh', 'tracta', 'name1970', 'name1980', 'name1990',
                   'name2000', 'name2010', 'name2012'
                   ]
    df.drop([col for col in df.columns if col not in list(new_col_dict.values())+cols_to_keep],
            axis="columns", inplace=True)
    years = set([v.split("_")[-1] for v in new_col_dict.values()])
    for year in years:
        df["pop_"+year] = (df[[c for c in df.columns if
                                c.split("_")[-1] == year
                                and c[:2] == "r_"]].sum(axis=1)
                                )
    value_map = []
    for col in df.columns:
        if col in cols_to_keep:
            value_map.append('"string"')
        else:
            value_map.append('"integer"')
    with open("../data/processed/nhgis_estimates.csvt", "w") as f:
        f.writelines(",".join(value_map))
    df.to_csv("../data/processed/nhgis_estimates.csv", index=False)

def prepare_dot_density_data(f):
    csv = pd.read_csv(f+"nhgis_estimates.csv")
    for year in set([col[-4:] for col in csv.columns if col[-4].isnumeric() and col[-4:]!= "2012"]):
        shp_name = [f for f in os.listdir(f) if f.endswith(".shp") and year in f][0]
        shp = gpd.read_file(f+shp_name)
        yr_csv = csv[[col for col in csv.columns if col[-4:] == year]]
        yr_csv = yr_csv[yr_csv["gjoin"+year].isna() == False]
        yr_csv.replace(0, 1, inplace=True)
        shp = shp.merge(yr_csv, how="left", left_on="gisjoin", right_on="gjoin"+year)
        shp = shp[shp["r_wh_"+year].isnull() == False]
        for col in shp.columns:
            if col[:2] == "r_" or col[:3] == "pop":
                shp[col] = shp[col].astype(int)
        shp.to_file(f+"race_"+year)



if __name__=="__main__":
    os.chdir(__file__)
    clean_boundaries("../data/raw/nhgis0021_shape/")
    clean_table("../data/raw/nhgis0019_csv")
    prepare_dot_density_data("../data/processed")
