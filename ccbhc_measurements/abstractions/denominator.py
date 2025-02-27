from abc import ABC, abstractmethod

class Denominator(ABC):
    """
    Abstract base class for denominator calculations

    This class defines the core methods that must be implemented 
    by any concrete denominator class
    """

    @abstractmethod
    def _set_populace(self) -> None:
        """
        Sets the initial population for the denominator

        This method must be implemented by the concrete class 
        to define how the initial population is obtained.
        """
        pass

    @abstractmethod
    def _remove_exclusions(self) -> None:
        """
        Removes any exclusions from the population

        This method must be implemented by the concrete class 
        to define how exclusions are identified and removed
        """
        pass
