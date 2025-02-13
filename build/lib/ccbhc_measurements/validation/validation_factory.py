from ccbhc_measurements.validation.validator import Validator
from ccbhc_measurements.validation.schemas import get_schema
from ccbhc_measurements.validation.required_data import get_required_dataframes
    


@staticmethod
def build(submeasure_name: str) -> Validator:
    """
    Builds a Validator for the given submeasure

    Parameters
    ----------
    submeasure_name
        The name of the submeasure to validate

    Returns
    -------
    Validator
        An instance of `Validator` with predefined dataframe schemas

    Raises
    ------
    ValueError
        If the submeasure is invalid
    """
    required_dataframes = get_required_dataframes(submeasure_name)
    validation_schemas = {df_name: get_schema(df_name) for df_name in required_dataframes}
    return Validator(validation_schemas)
