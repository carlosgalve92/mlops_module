from pathlib import Path

from mlops.components.transformation.data_transformation import (
    DataTransformation,
)
from mlops.config.configuration import ConfigurationManager
from mlops.logger.logger import logger

STAGE_NAME = "Data Transformation Stage"


class DataTransformationTrainingPipeline:
    def __init__(self):
        config = ConfigurationManager()
        data_transformation_config = config.get_data_transformation_config()
        self.data_transformation = DataTransformation(config=data_transformation_config)

    def initiate_data_transformation(self):
        try:
            with open(Path("artifacts/data_validation/status.txt"), "r") as f:
                status = f.read().split(" ")[-1]
            if status == "True":
                for step in self.data_transformation.config.steps:
                    name = step.name
                    params = step.get("params", {})
                    method = getattr(self.data_transformation, name)
                    print(f"\n==> Executing step: {name}")
                    method(**params)
            else:
                raise Exception("Your data scheme is not valid")

        except Exception as e:
            print(e)


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = DataTransformationTrainingPipeline()
        obj.initiate_data_transformation()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
