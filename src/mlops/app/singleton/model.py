from functools import lru_cache

import mlflow
from dotenv import load_dotenv

from mlops.constants import CONFIG_FILE_PATH
from mlops.models.factory import ModelFactory
from mlops.models.registry import ModelRegistry
from mlops.utils.common import read_yaml


@lru_cache(maxsize=1)
def get_model_factory() -> ModelFactory:
    registry = ModelRegistry()
    return ModelFactory(registry)


load_dotenv()

config_production = read_yaml(CONFIG_FILE_PATH).production


@lru_cache(maxsize=1)
def load_model(
    model_name=config_production.model_name, model_alias=config_production.model_alias
):
    model_uri = rf"models:/{model_name}@{model_alias}"

    return mlflow.sklearn.load_model(model_uri)


if __name__ == "__main__":
    model = load_model()
    print(model)
