import pandas as pd

# take first 25 sub1 numerator for sub 2 data
numerator_ids = [
10025,10047,10150,10266,10299,
10417,10686,11226,11332,11461,
11710,11884,11994,12169,13113,
13225,13686,13847,14630,14690,
15486,16034,18666,19629,19831,
]
numerator_encounters = [
79162,25048,19909,96884,89668,
52059,61052,79239,57658,71774,
34354,35950,56433,72467,49438,
95314,53141,59121,38402,10623,
74311,71646,83442,62699,16418,
]
brief_counselings = pd.DataFrame({
    "patient_id" : numerator_ids,
    "encounter_id" : numerator_encounters
})
brief_counselings.patient_id = brief_counselings.patient_id.astype(str)

data = [brief_counselings]
