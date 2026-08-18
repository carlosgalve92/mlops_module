from mlops.models.registry import ModelRegistry


class ModelFactory:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def get_model(self, model_name: str, model_version: str = "latest"):
        """Obtiene un modelo desde el registry"""
        return self.registry.load_model(model_name, model_version)
