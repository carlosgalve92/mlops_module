from mlops.components.validation.data_validation import DataValiadtion
from mlops.config.configuration import ConfigurationManager
from mlops.logger.logger import logger

STAGE_NAME = "Data Validation stage"


class DataValidationTrainingPipeline:
    def __init__(self):
        config = ConfigurationManager()
        #
        data_validation_config = config.get_data_validation_config()
        self.data_validation = DataValiadtion(config=data_validation_config)

    def initiate_data_validation(self):
        for step in self.data_validation.config.steps:
            name = step.name
            params = step.get("params", {})
            method = getattr(self.data_validation, name)
            print(f"\n==> Executing step: {name}")
            method(**params)


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = DataValidationTrainingPipeline()
        obj.initiate_data_validation()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
