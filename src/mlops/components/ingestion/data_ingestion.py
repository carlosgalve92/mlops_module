import os

import kaggle

from mlops.entity.config_entity import DataIngestionConfig
from mlops.logger.logger import logger


# Component-Data Ingestion
class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    # Downloading file
    def download_file(self, local_data_file, source_URL):
        if not os.path.exists(local_data_file):
            #
            kaggle.api.dataset_download_files(
                source_URL, path=self.config.root_dir, unzip=True
            )
            #
            logger.info(f"{local_data_file} download!")
        else:
            logger.info("File already exists")
