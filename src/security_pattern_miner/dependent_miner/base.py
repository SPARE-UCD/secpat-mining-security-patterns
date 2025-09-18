from abc import ABC, abstractmethod


class DependentMiner(ABC):
    @abstractmethod
    def get_dependents(self, package_name: str):
        pass

class LibrariesIODependentMiner(ABC):
    @abstractmethod
    def get_dependents(self, package_manager: str, package_name: str):
        pass
    
    