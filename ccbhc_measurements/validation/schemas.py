Alcohol_Encounters = {
    "patient_id": (str, 'object'),
    "patient_DOB": ("datetime64[ns]",),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "cpt_code": (str, 'object'),
    "screening": (str, 'object'),
    "score": (int, float),
}
ASC_Demographic_Data = {
    "patient_id": (str, 'object'),
    "sex": (str, 'object'),
    "race": (str, 'object'),
    "ethnicity": (str, 'object')
}
CDF_Populace = {
    "patient_id": (str, 'object'),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "patient_DOB": ("datetime64[ns]",),
    "follow_up": (bool,),
    "total_score": (float,), 
    "screening_type": (str, 'object')
}
Demographic_Data = {
    "patient_id": (str, 'object'),
    "race": (str, 'object'),
    "ethnicity": (str, 'object')
}
Diagnostic_History = {
    "patient_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "diagnosis": (str, 'object')
}
Insurance_History = {
    "patient_id": (str, 'object'),
    "insurance": (str, 'object'),
    "start_datetime": ("datetime64[ns]",),
    "end_datetime": ("datetime64[ns]",)
}
PHQ9 = {
    "patient_id": (str, 'object'),
    "patient_DOB": ("datetime64[ns]",),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "total_score": (int, float)
}
Populace = {
    "patient_id": (str, 'object'),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),  
    "patient_DOB": ("datetime64[ns]",)         
}
SDOH_Screenings = {
    "patient_id": (str, 'object'),
    "screening_id": (str, 'object'),
    "screening_date": ("datetime64[ns]",)
}

def get_schema(df_name:str) -> dict[str:type]:
    """
    Gets the required schema for a given dataframe

    Parameters
    ----------
    df_name
        Name of the Dataframe

    Returns
    -------
    dict[str:type]
        str
            Column name
        type
            Data type
    """
    match df_name:
        case "Alcohol_Encounters":
            return Alcohol_Encounters
        case "ASC_Demographic_Data":
            return ASC_Demographic_Data
        case "CDF_Populace":
            return CDF_Populace
        case "Demographic_Data":
            return Demographic_Data
        case "Diagnostic_History":
            return Diagnostic_History
        case "Insurance_History":
            return Insurance_History
        case "SDOH_Screenings":
            return SDOH_Screenings
        case "Populace":
            return Populace
        case "PHQ9":
            return PHQ9
        case None:
            return None
