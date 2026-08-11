from mlops.components.evaluation.model_evaluation import ModelEvaluation
from mlops.config.configuration import ConfigurationManager
from mlops.logger.logger import logger

STAGE_NAME = "Model evaluation stage"


class ModelEvaluationTrainingPipeline:
    def __init__(self):
        config = ConfigurationManager()
        model_evaluation_config = config.get_model_evaluation_config()
        self.model_evaluation = ModelEvaluation(config=model_evaluation_config)

    def initiate_model_evaluation(self):
        for step in self.model_evaluation.config.steps:
            name = step.name
            params = step.get("params", {})
            method = getattr(self.model_evaluation, name)
            print(f"\n==> Executing step: {name}")
            method(**params)


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelEvaluationTrainingPipeline()
        obj.initiate_model_evaluation()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
