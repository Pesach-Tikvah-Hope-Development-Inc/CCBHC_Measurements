from ccbhc_measurements.demos.dep_rem_demo import data as dr_data
from ccbhc_measurements.measurements.dep_rem import Dep_Rem

measurements = [Dep_Rem(dr_data)]

for measure in measurements:
    results = measure.get_all_submeasures()
    for key,val in results.items():
        print(key)
        print(val)
        val.to_excel(key+".xlsx", index=False)
