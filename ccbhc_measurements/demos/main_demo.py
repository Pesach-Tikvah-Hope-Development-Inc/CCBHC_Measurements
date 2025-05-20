from typing import List
from ccbhc_measurements.abstractions.measurement import Measurement
from ccbhc_measurements.measurements.asc import ASC
from ccbhc_measurements.measurements.cdf_ad import CDF_AD
from ccbhc_measurements.measurements.cdf_ch import CDF_CH
from ccbhc_measurements.measurements.dep_rem import Dep_Rem
from ccbhc_measurements.measurements.sdoh import SDOH
from ccbhc_measurements.demos.asc_sub_1_demo import data as asc_sub_1_data
from ccbhc_measurements.demos.cdf_ad_demo import data as cdf_ad_sub_1_data
from ccbhc_measurements.demos.cdf_ch_demo import data as cdf_ch_sub_1_data
from ccbhc_measurements.demos.dep_rem_demo import data as dr_sub_1_data
from ccbhc_measurements.demos.sdoh_demo import data as sdoh_sub_1_data

measurements : List[Measurement]
measurements = [
    ASC(asc_sub_1_data),
    CDF_AD(cdf_ad_sub_1_data),
    CDF_CH(cdf_ch_sub_1_data),
    Dep_Rem(dr_sub_1_data),
    SDOH(sdoh_sub_1_data)
]

output_path = r'../dashboard/excel files/'

for measure in measurements:
    results = measure.get_all_submeasures()
    for key,val in results.items():
        # print(key)
        # print(val)
        val.to_excel(output_path+key+".xlsx",sheet_name=key, index=False)
