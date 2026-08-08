import logging.config

import yaml


def setup_logging(config_path="./config/logger.yaml"):
    with open(config_path, "r") as file:
        config_log = yaml.safe_load(file)
        logging.config.dictConfig(config_log)


setup_logging()
logger = logging.getLogger("mlops")
