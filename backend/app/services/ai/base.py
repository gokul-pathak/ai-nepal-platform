from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, user_input: str = "") -> str:
        raise NotImplementedError
