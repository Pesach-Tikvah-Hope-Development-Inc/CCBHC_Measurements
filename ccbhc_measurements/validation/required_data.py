DEP_REM_sub_1 = [
    "PHQ9",
    "Diagnostic_History",
    "Demographic_Data",
    "Insurance_History"
]
ASC_sub_1 = [
    "Regular_Visits",
    "Preventive_Visits",
    "Screenings",
    "Diagnostic_History",
    "Demographic_Data",
    "Insurance_History"
]


def get_required_dataframes(submeasure_name: str) -> list[str]:
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
        case "DEP_REM_sub_1":
            return DEP_REM_sub_1
        case "ASC_sub_1":
            return ASC_sub_1
    raise ValueError(f"Unknown submeasure: {submeasure_name}")
    