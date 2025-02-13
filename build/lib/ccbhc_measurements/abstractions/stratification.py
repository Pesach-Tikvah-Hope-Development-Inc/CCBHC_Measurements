from abc import ABC, abstractmethod

class Stratification(ABC):
    """
    Abstract base class for stratifying Submeasures

    This class defines the core methods that must be implemented 
    by any concrete stratification class
    """

    @abstractmethod
    def _set_stratification(self) -> None:
        """
        Sets initial population for the stratification

        This method must be implemented by the concrete class 
        to define how the initial stratification is set
        """
        pass

    @abstractmethod
    def _set_patient_stratification(self) -> None:
        """
        Sets stratification data that is patient dependant

        This method must be implemented by the concrete class 
        to define how the patient stratification is obtained
        """
        pass

    @abstractmethod
    def _set_encounter_stratification(self) -> None:
        """
        Sets stratification data that is encounter dependant

        This method must be implemented by the concrete class 
        to define how the encounter stratification is obtained
        """
        pass

    @abstractmethod
    def _fill_blank_stratification(self) -> None:
        """
        Fills all blank values in the stratification

        This method must be implemented by the concrete class 
        to define how the blank values are filled
        """
        pass