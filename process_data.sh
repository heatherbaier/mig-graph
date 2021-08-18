# Create place variable JSON maps
python3 create_var_maps.py MEX
python3 create_var_maps.py NIC
python3 create_var_maps.py GTM
python3 create_var_maps.py SLV


# Process data
python3 process_file.py pers_MEX.csv mig_MEX.csv MEX
python3 process_file.py pers_MEX.csv migother_MEX.csv MEX
python3 process_file.py pers_NIC.dta mig_NIC.dta NIC
python3 process_file.py pers_NIC.dta migother_NIC.dta NIC
python3 process_file.py pers_GTM.dta mig_GTM.dta GTM
python3 process_file.py pers_SLV.dta mig_SLV.dta SLV


# Geocode
python3 geocode.py


