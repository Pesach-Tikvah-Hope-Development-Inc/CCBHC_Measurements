import pandas as pd
from datetime import datetime
from ccbhc_measurements.compat.typing_compat import override
from ccbhc_measurements.abstractions.measurement import Measurement
from ccbhc_measurements.abstractions.submeasure import Submeasure
from ccbhc_measurements.measurements.cdf_base import _CDF_Sub_1

class _Sub_1(_CDF_Sub_1):
    """
    Percentage of minors screened for depression during the measurement year
    using an age-appropriate standardized depression screening tool,
    and if positive, a follow-up plan is documented on the date of the eligible encounter
    """

    # the child measure is bounded on both ends
    MINIMUM_AGE = 12
    MAXIMUM_AGE = 17

class CDF_CH(Measurement):
    """
    Percentage of beneficiaries [clients] ages 12 to 17 screened for depression on the date of the
    encounter or 14 days prior to the date of the encounter using an age-appropriate standardized
    depression screening tool, and if positive, a follow-up plan is documented on the date of the eligible encounter
    
    Parameters
    ----------
    sub1_data
        List of dataframes containing all needed data to calculate submeasure 1

    Notes
    -----
    sub1_data must follow the its `Schema` as defined by the `Validation_Factory` in order to ensure the `submeasure` can run properly

    Example
    -------
    >>> CDF_CH_sub_1 = [
    >>>     "Populace",
    >>>     "Diagnostic_History",
    >>>     "Demographic_Data",
    >>>     "Insurance_History"
    >>> ]

    >>> Populace = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "patient_DOB": ("datetime64[ns]",)
    >>> }

    >>> Diagnostic_History = {
    >>>     "patient_id": (str, 'object'),
    >>>     "encounter_datetime": ("datetime64[ns]",),
    >>>     "diagnosis": (str, 'object')
    >>> }

    >>> Demographic_Data = {
    >>>     "patient_id": (str, 'object'),
    >>>     "race": (str, 'object'),
    >>>     "ethnicity": (str, 'object')
    >>> }

    >>> Insurance_History = {
    >>>     "patient_id": (str, 'object'),
    >>>     "insurance": (str, 'object'),
    >>>     "start_datetime": ("datetime64[ns]",),
    >>>     "end_datetime": ("datetime64[ns]",)
    >>> }
    """ 

    def __init__(self, sub1_data:list[pd.DataFrame]):
        super().__init__("CDF_CH")
        self.__sub1__: Submeasure = _Sub_1(self.name + "_sub_1", sub1_data)

    @override
    def get_all_submeasures(self) -> dict[str,pd.DataFrame]:
        """
        Calculates all the data for the CDF_CH Measurement and its Submeasures

        Returns
        -------
        dict[str:pd.DataFrame]
            str
                Submeasure name
            pd.DataFrame
                Submeasure Data

        Raises
        ------
        ValueError
            When the submeasure data isn't properly formatted
        """ 
        try:
            return self.__sub1__.get_submeasure_data()
        except Exception:
            raise
