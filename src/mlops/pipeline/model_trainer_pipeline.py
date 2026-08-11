from mlops.components.train.model_trainer import ModelTrainer
from mlops.config.configuration import ConfigurationManager
from mlops.logger.logger import logger

STAGE_NAME = "Model Trainer stage"


class ModelTrainerTrainingPipeline:
    def __init__(self):
        config = ConfigurationManager()
        model_trainer_config = config.get_model_trainer_config()
        self.model_trainer = ModelTrainer(config=model_trainer_config)

    def initiate_model_training(self):
        for step in self.model_trainer.config.steps:
            name = step.name
            params = step.get("params", {})
            method = getattr(self.model_trainer, name)
            print(f"\n==> Executing step: {name}")
            method(**params)


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelTrainerTrainingPipeline()
        obj.initiate_model_training()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
