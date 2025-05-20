PHQ9 = {
    "patient_id": (str, 'object'),
    "patient_DOB": ("datetime64[ns]",),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "total_score": (int, float)
}
Diagnostic_History = {
    "patient_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "diagnosis": (str, 'object')
}
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
Brief_Counselings = {
    "patient_id": (str, 'object'),
    "encounter_id": (str, 'object')
}
Demographic_Data = {
    "patient_id": (str, 'object'),
    "race": (str, 'object'),
    "ethnicity": (str, 'object')
}
Insurance_History = {
    "patient_id": (str, 'object'),
    "insurance": (str, 'object'),
    "start_datetime": ("datetime64[ns]",),
    "end_datetime": ("datetime64[ns]",)
}
SDOH_Screenings = {
    "patient_id": (str, 'object'),
    "screening_id": (str, 'object'),
    "screening_date": ("datetime64[ns]",)
}
Populace = {
    "patient_id": (str, 'object'),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),  
    "patient_DOB": ("datetime64[ns]",)         
}
CDF_Screenings = {
    "patient_id": (str, 'object'),
    "encounter_id": (str, 'object'),
    "screening_date": ("datetime64[ns]",),
    "total_score": (int, float),
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
        case "PHQ9":
            return PHQ9
        case "Demographic_Data":
            return Demographic_Data
        case "Diagnostic_History":
            return Diagnostic_History
        case "Insurance_History":
            return Insurance_History
        case "Alcohol_Encounters":
            return Alcohol_Encounters
        case "ASC_Demographic_Data":
            return ASC_Demographic_Data
        case "SDOH_Screenings":
            return SDOH_Screenings
        case "Populace":
            return Populace
        case "CDF_Screenings":
            return CDF_Screenings
        case None:
            return None