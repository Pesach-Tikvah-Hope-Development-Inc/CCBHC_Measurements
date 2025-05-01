from ccbhc_measurements.measurements.dep_rem import Dep_Rem
from ccbhc_measurements.measurements.asc import ASC
from ccbhc_measurements.measurements.sdoh import SDOH
from ccbhc_measurements.demos.dep_rem_demo import data as dr_sub_1_data
from ccbhc_measurements.demos.asc_sub_1_demo import data as asc_sub_1_data
from ccbhc_measurements.demos.sdoh_demo import data as sdoh_sub_1_data

measurements = [
    Dep_Rem(dr_sub_1_data),
    ASC(asc_sub_1_data),
    SDOH(sdoh_sub_1_data)
]

output_path = r'../dashboard/excel files/'

for measure in measurements:
    results = measure.get_all_submeasures()
    for key,val in results.items():
        print(key)
        print(val)
        val.to_excel(output_path+key+".xlsx",sheet_name=key, index=False)
