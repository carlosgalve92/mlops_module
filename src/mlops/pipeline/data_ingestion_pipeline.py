from mlops.components.ingestion.data_ingestion import DataIngestion
from mlops.config.configuration import ConfigurationManager
from mlops.logger.logger import logger

STAGE_NAME = "Data Ingestion Stage"


class DataIngestionTrainingPipeline:
    def __init__(self):
        config = ConfigurationManager()
        #
        data_ingestion_config = config.get_data_ingestion_config()
        self.data_ingestion = DataIngestion(config=data_ingestion_config)

    def initiate_data_ingestion(self):
        for step in self.data_ingestion.config.steps:
            name = step.name
            params = step.get("params", {})
            method = getattr(self.data_ingestion, name)
            print(f"\n==> Executing step: {name} con params: {params}")
            method(**params)


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = DataIngestionTrainingPipeline()
        obj.initiate_data_ingestion()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
