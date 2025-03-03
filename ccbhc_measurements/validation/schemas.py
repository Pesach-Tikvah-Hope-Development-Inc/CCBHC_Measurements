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
Regular_Visits = {
    "patient_id": (str, 'object'),
    "patient_DOB": ("datetime64[ns]",),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",)
}
Preventive_Visits = {
    "patient_id": (str, 'object'),
    "patient_DOB": ("datetime64[ns]",),
    "encounter_id": (str, 'object'),
    "encounter_datetime": ("datetime64[ns]",),
    "cpt_code": (str, 'object')
}
Alcohol_Screenings = {
    "patient_id": (str, 'object'),
    "screening_datetime": ("datetime64[ns]",)
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
        case "Regular_Visits":
            return Regular_Visits
        case "Preventive_Visits":
            return Preventive_Visits
        case "Alcohol_Screenings":
            return Alcohol_Screenings
        case "Brief_Counselings":
            return Brief_Counselings
