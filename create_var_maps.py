import pandas as pd
import argparse
import json
import os


if __name__ == "__main__":

    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("country", help = "Country.")
    parser.add_argument("places_dir", help = "Path to places files.", default = "places", nargs='?')
    parser.add_argument("varmaps_dir", help = "Path to Flow output directory.", default = "var_maps", nargs='?')
    args = parser.parse_args()
    
    df = pd.read_csv(os.path.join(args.places_dir, "Appendix B - Places - " + args.country + ".csv"))
    df = df.fillna("-99")
    df['var'] = df["id"] + " " + df["name"]
    df = df[df["var"] != "-99 -99"]
    df['var'] = df.replace("-99", "")
    df = df[['var']]
    df.tail()

    state_keys, state_vals = [], []
    place_to_state_keys, place_to_state_vals = [], []
    place_keys, place_vals = [], []
    state_to_place_keys, state_to_place_vals = [], []


    cur_state, cur_state_name = '', ''
    for col, row in df.iterrows():
        if row['var'][0].isdigit(): # This means the row is a place
            
            print(row['var'])
            
            place_to_state_vals.append(int(cur_state))

            if row['var'].split(" ")[0] == "2Acuña":
                place_to_state_keys.append(2)
            else:
                place_to_state_keys.append(int(row['var'].split(" ")[0]))


            if row['var'].split(" ")[0] == "2Acuña":
                place_vals.append(2)
                place_keys.append("Acuña")
            else:
                place_vals.append(int(row['var'].split(" ")[0]))
                place_keys.append(" ".join(row['var'].split(" ")[1:]))


            state_name = cur_state_name.split("(")[0].strip()
            place_name = " ".join(row['var'].split(" ")[1:])

            stp_name = place_name + ", " + state_name
            stp_num = str(cur_state) + "-" + row['var'].split(" ")[0].replace("2Acuña", "2")

            state_to_place_keys.append(stp_num)
            state_to_place_vals.append(stp_name)

        else:                                      # This means the row is a state
            
            cur_state_name = row['var']

            if cur_state_name.startswith("("):
                state_keys.append(int(cur_state_name.split(" ")[0].strip("(").strip(")")))
                state_vals.append(" ".join(cur_state_name.split(" ")[1:]).strip())
                cur_state = int(cur_state_name.split(" ")[0].strip("(").strip(")"))
            else:
                state_keys.append(int(cur_state_name.split(" ")[-1].strip("(").strip(")")))
                state_vals.append(cur_state_name.split("(")[0].strip())
                cur_state = int(cur_state_name.split(" ")[-1].strip("(").strip(")"))
                
                print(cur_state_name)
                
            state_to_place_keys.append(str(cur_state) + "-" + "0")
            state_to_place_vals.append(cur_state_name.split("(")[0].strip())


            state_to_place_keys.append(str(cur_state) + "-" + "9999")
            state_to_place_vals.append(cur_state_name.split("(")[0].strip())


    state_to_place_map = dict(zip(state_to_place_keys, state_to_place_vals))
    with open(os.path.join(args.varmaps_dir, args.country + "_state_to_place_map.json"), "w") as f:
        f.write(json.dumps(state_to_place_map))


    state_map = dict(zip(state_keys, state_vals))
    with open(os.path.join(args.varmaps_dir, args.country + "_state_map.json"), "w") as f:
        f.write(json.dumps(state_map))


    place_to_state_map = dict(zip(place_to_state_keys, place_to_state_vals))
    with open(os.path.join(args.varmaps_dir, args.country + "_place_to_state_map.json"), "w") as f:
        f.write(json.dumps(place_to_state_map))


    place_map = dict(zip(place_keys, place_vals))
    with open(os.path.join(args.varmaps_dir, args.country + "_place_map.json"), "w") as f:
        f.write(json.dumps(place_map))


#     us = pd.read_csv(os.path.join(args.places_dir, "Appendix B - US - " + args.country + ".csv"))
#     print(us.head())
#     with open(os.path.join(args.varmaps_dir, args.country + "_us_places.json"), "w") as f:
#         f.write(json.dumps(dict(zip(us['id'], us['place']))))