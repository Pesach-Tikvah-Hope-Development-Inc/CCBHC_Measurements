ASC_sub_1 = [
    "Alcohol_Encounters",
    "Diagnostic_History",
    "ASC_Demographic_Data",
    "Insurance_History"
]
ASC_sub_2 = [
    None
]
CDF_AD_sub_1 = [
    "CDF_Populace",
    "Diagnostic_History",
    "Demographic_Data",
    "Insurance_History"
]
CDF_CH_sub_1 = [
    "CDF_Populace",
    "Diagnostic_History",
    "Demographic_Data",
    "Insurance_History"
]
DEP_REM_sub_1 = [
    "PHQ9",
    "Dep_Rem_Diagnostic_History",
    "Demographic_Data",
    "Insurance_History"
]
SDOH_sub_1 = [
    "Populace",
    "Demographic_Data",
    "Insurance_History"
]

def get_required_dataframes(submeasure_name:str) -> list[str]:
    """
    Gets the required Dataframes for a given submeasure

    Parameters
    ----------
    submeasure_name
        Name of the submeasure

    Returns
    -------
    list[str]
        Names of required Dataframes

    Raises
    ------
    ValueError
        If the submeasure is unknown
    """
    match submeasure_name:
        case "ASC_sub_1":
            return ASC_sub_1
        case "ASC_sub_2":
            return ASC_sub_2
        case "CDF_AD_sub_1":
            return CDF_AD_sub_1
        case "CDF_CH_sub_1":
            return CDF_CH_sub_1
        case "DEP_REM_sub_1":
            return DEP_REM_sub_1
        case "SDOH_sub_1":
            return SDOH_sub_1
    raise ValueError(f"Unknown submeasure: {submeasure_name}")
    