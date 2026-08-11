import pathlib

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

from mlops.entity.config_entity import ModelEvaluationConfig
from mlops.utils.common import load_bin, save_json

load_dotenv()


class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def eval_metrics(self, actual, pred, threshold=0.5):
        gini = 2 * roc_auc_score(actual, pred) - 1
        f1 = f1_score(actual, np.where(pred > threshold, 1, 0))
        recall = recall_score(actual, np.where(pred > threshold, 1, 0))
        precision = precision_score(actual, np.where(pred > threshold, 1, 0))

        return {"gini": gini, "f1": f1, "recall": recall, "precision": precision}

    def read_files(self, train_data_path, test_data_path, target_column):
        """ """
        train_data = pd.read_csv(train_data_path)
        test_data = pd.read_csv(test_data_path)

        self.train_x = train_data.drop([target_column], axis=1)
        self.train_y = train_data[[target_column]]

        self.test_x = test_data.drop([target_column], axis=1)
        self.test_y = test_data[[target_column]]

    def get_metrics_model(self, path_model, local_metrics_file, model_name, version):
        model = load_bin(
            pathlib.Path(path_model).joinpath(f"{model_name}__{version}.joblib")
        )

        train_pred_y = model.predict_proba(self.train_x)
        test_pred_y = model.predict_proba(self.test_x)

        dict_metrics = {}

        dict_metrics.update(
            {
                f"{k}_train": v
                for k, v in self.eval_metrics(self.train_y, train_pred_y[:, 1]).items()
            }
        )

        dict_metrics.update(
            {
                f"{k}_test": v
                for k, v in self.eval_metrics(self.test_y, test_pred_y[:, 1]).items()
            }
        )

        save_json(local_metrics_file, dict_metrics)
