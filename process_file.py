import pandas as pd
import numpy as np
import argparse
import json
import os


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("pers_path", help = "Path to PERS file.")
    parser.add_argument("mig_path", help = "Path to MIG file.")
    parser.add_argument("country", help = "Country.")
    parser.add_argument("data_dir", help = "Path to PERS file.", default = "LAMP_data", nargs='?')
    parser.add_argument("indiv_flow_dir", help = "Path to Flow output directory.", default = "indiv_flows", nargs='?')
    parser.add_argument("all_flow_dir", help = "Path to Flow output directory.", default = "flows", nargs='?')
    parser.add_argument("var_map_dir", help = "Path to Flow output directory.", default = "var_maps", nargs='?')
    args = parser.parse_args()
    
    for crs in range(1, 31):
    
        if args.pers_path.split(".")[1] == "csv":
            pers = pd.read_csv(os.path.join(args.data_dir, args.pers_path), low_memory=False)
        else:
            pers = pd.read_stata(os.path.join(args.data_dir, args.pers_path))
        pers = pers[pers['relhead'] == 1]
        pers_vars = ["COMMUN", "HHNUM", "DOSTATEL", "DOPLACEL", "USYR1", "USDUR1", "USDOC1", "USSTATE1", "USPLACE1", "USMAR1", "USOCC1", "USWAGE1"]
        pers = pers[[i.lower() for i in pers_vars]]
        
        try:

            if args.mig_path.split(".")[1] == "csv":
                mig = pd.read_csv(os.path.join(args.data_dir, args.mig_path), low_memory=False)
            else:
                mig = pd.read_stata(os.path.join(args.data_dir, args.mig_path))    

            mig_vars = ["COMMUN", "HHNUM","PLACEBRN", "STATEBRN", "CRSYR" + str(crs), "CRSST" + str(crs), "CRSPL" + str(crs)]

            if args.country == "SLV":
                mig = mig.rename(columns ={"crsmxst" + str(crs): "crsst" + str(crs), "crsmxpl" + str(crs): "crspl" + str(crs)})

            mig = mig[[i.lower() for i in mig_vars]]
            mig = mig[~mig['crsst' + str(crs)].isin([8888, 9999, 1111])] # Filter for crossings with a known state of crossing
            mig = mig[~mig['crspl' + str(crs)].isin([8888, 9999, 1111])] # Filter for crossings with a known place of crossing
            mig = mig[mig["statebrn"] != 8888]
            mig = mig[mig["statebrn"] != 9999]
            mig["placebrn"] = mig["placebrn"].astype(str).str.replace("8888", "0").astype(str)
            mig["placebrn"] = mig["placebrn"].astype(str).str.replace("9999", "0").astype(str)

            with open(os.path.join(args.var_map_dir, 'MEX' + "_state_to_place_map.json"), "r") as f:
                mex_state_to_place_map = json.load(f)

            with open(os.path.join(args.var_map_dir, args.country + "_state_to_place_map.json"), "r") as f:
                state_to_place_map = json.load(f)

            with open(os.path.join(args.var_map_dir, "MEX" + "_us_places.json"), "r") as f:
                us_places = json.load(f)

#             print(mig.columns)

            pers['ID'] = pers['commun'].astype(str) + "-" + pers['hhnum'].astype(str)
            mig['ID'] = mig['commun'].astype(str) + "-" + mig['hhnum'].astype(str)


            pers = pers.drop(["commun", "hhnum"], axis = 1)
            mig = mig.drop(["commun", "hhnum"], axis = 1)

            pers_mig = pd.merge(pers, mig, on = "ID")

            pers_mig['cross_loc'] = pers_mig['crsst' + str(crs)].astype(int).astype(str) + "-" + pers_mig['crspl' + str(crs)].astype(int).astype(str)
            pers_mig['cross_loc'] = pers_mig['cross_loc'].astype(str).map(mex_state_to_place_map)
            pers_mig['born_loc'] = pers_mig['statebrn'].astype(float).astype(int).astype(str) + "-" + pers_mig['placebrn'].astype(float).astype(int).astype(str)
            pers_mig['born_loc'] = pers_mig['born_loc'].astype(str).map(state_to_place_map)
            pers_mig['last_mx_loc'] = pers_mig['dostatel'].astype(float).astype(int).astype(str) + "-" + pers_mig['doplacel'].astype(float).astype(int).astype(str)
            pers_mig['last_mx_loc'] = pers_mig['last_mx_loc'].astype(str).map(state_to_place_map)
            pers_mig['last_mx_loc'] = pers_mig['last_mx_loc'].fillna("-99")

            # If the person never migrated from their place of birth, use that as the origin location, otherwise place of origin is last known place living in MX
            pers_mig['origin_loc'] = np.where(pers_mig['last_mx_loc'] == "-99", pers_mig['born_loc'], pers_mig['last_mx_loc'])

            try:
                pers_mig['us_loc'] = pers_mig['usplace1'].astype(float).astype(int).astype(str).map(us_places)
            except:
                pers_mig['us_loc'] = pers_mig['usplace1'].astype(str).map(us_places)
            pers_mig['us_loc'] = pers_mig['us_loc'].str.replace("PMSA", "")
            pers_mig['us_loc'] = pers_mig['us_loc'].str.replace("MSA", "")

            flows = pers_mig[["crsyr" + str(crs), "origin_loc", "cross_loc", "us_loc"]]

            print(crs, flows.shape[0], " total flows created.")
            
            if flows.shape[0] == 0:
                
                break

            if "other" in args.mig_path:
                flows.to_csv(args.indiv_flow_dir + "/" + args.country + "_other_flows" + str(crs) + ".csv", index = False)
            else:
                flows.to_csv(args.indiv_flow_dir + "/" + args.country + "_hhead_flows" + str(crs) + ".csv", index = False)
                
        
        except Exception as e:
            
            print(e)
            
            break
        

country_cross_files = [i for i in os.listdir(args.indiv_flow_dir) if args.country in i]


for file in range(0, len(country_cross_files)):
    
    cross = pd.read_csv(os.path.join(args.indiv_flow_dir, country_cross_files[file]))
    cross.columns = ["crsyr", "origin_loc","cross_loc", "us_loc"]
    
    if file == 0:
        all_crosses = cross
        print(cross.shape, all_crosses.shape)
    else:
        all_crosses = all_crosses.append(cross)
        print(cross.shape, all_crosses.shape)
        
all_crosses.to_csv(args.all_flow_dir + "/" + args.country + "_flows.csv", index = False)
