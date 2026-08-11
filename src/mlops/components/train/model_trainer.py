import pathlib

import pandas as pd
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from mlops.entity.config_entity import ModelTrainerConfig
from mlops.utils.common import load_bin, save_bin

MODEL_REGISTRY = {
    "XGBClassifier": XGBClassifier,
}


class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config
        self.pl_preprocess = None

    def read_file_train(self, train_file, target_column):
        """ """
        train = pd.read_csv(train_file)

        self.train_x = train.drop([target_column], axis=1)
        self.train_y = train[target_column]

    def load_pl_preprocess(self, pl_preprocess_path):
        self.pl_preprocess = load_bin(pl_preprocess_path)

    def create_model(self, model, dict_params):
        # model = globals().get(model)
        model = MODEL_REGISTRY.get(model)
        self.model = model(**dict_params)

    def build_pipeline(self):
        if self.pl_preprocess is None:
            self.pipeline = Pipeline([("model", self.model)])
        else:
            self.pipeline = Pipeline(
                [("preprocess", self.pl_preprocess), ("model", self.model)]
            )

    def train(self, model_name, version):
        self.pipeline.fit(self.train_x, self.train_y)

        save_bin(
            self.pipeline,
            pathlib.Path(self.config.root_dir).joinpath(
                f"{model_name}__{version}.joblib"
            ),
        )
