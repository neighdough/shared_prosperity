import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
%matplotlib


def poverty():
    df = pd.read_csv("../data/processed/nhgis_estimates.csv")
    years = set([col[-4:] for col in df.columns if col[-4].isnumeric() and col[-4:]!= "2012"])
    for year in sorted(years):
        pov = "pov_" + year if year != "2010" else "pov_2012"
        pop_wh = "r_wh_" + year
        pop_total = "pop_" + year
        cur_df = df[(df["gjoin"+year].isnull() == False) & 
                    (df[pov] < df[pop_total])
                    ]
        cur_df["pct_wh"] = cur_df[pop_wh] / cur_df[pop_total]
        y = cur_df[pov] / cur_df["pop_"+year]
        x = [year for i in range(y.shape[0])]
        plt.scatter(cur_df.pct_wh, y, label=year, s=8)
        tck = list(np.arange(0, 110, 10))
        tck_label = ["{}%".format(i) for i in tck]
        plt.yticks(tck,tck_label)
        plt.xticks(tck, tck_label)
        plt.xlabel("Percent Caucasian")
        plt.ylabel("Percent at or Below Poverty")
        plt.title(year)
        plt.savefig("../output/pov_scatter_"+year+".png", dpi=300)
        plt.close()
        

if __name__=="__main__":
    os.chdir(__file__)
    csv = pd.read_csv("../data/processesd/nhgis_estimates.csv")
