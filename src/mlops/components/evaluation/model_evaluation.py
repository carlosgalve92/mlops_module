import os
import pathlib
from urllib.parse import urlparse

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

from mlops.entity.config_entity import ModelEvaluationConfig
from mlops.utils.common import load_bin, save_json

load_dotenv(override=True)


class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config
        # Se inicializan aqui para poder validar mas tarde que read_files() se
        # ejecuto antes que log_into_mlflow() (evita un AttributeError opaco).
        self.train_x = None
        self.train_y = None
        self.test_x = None
        self.test_y = None

    def eval_metrics(self, actual, pred, threshold=0.5):
        # sklearn espera etiquetas 1D. self.train_y / self.test_y son DataFrames
        # de forma (n, 1); si no se aplanan, roc_auc_score puede fallar o
        # interpretarlos como formato multietiqueta.
        actual = np.asarray(actual).ravel()
        pred = np.asarray(pred).ravel()
        pred_label = np.where(pred > threshold, 1, 0)

        gini = 2 * roc_auc_score(actual, pred) - 1
        f1 = f1_score(actual, pred_label)
        recall = recall_score(actual, pred_label)
        precision = precision_score(actual, pred_label)

        # float() nativo: evita problemas de serializacion (np.float64) en save_json
        return {
            "gini": float(gini),
            "f1": float(f1),
            "recall": float(recall),
            "precision": float(precision),
        }

    def read_files(self, train_data_path, test_data_path, target_column):
        """Carga los CSV de train/test y separa features (x) del target (y)."""
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

    def log_into_mlflow(self, path_model, local_metrics_file, model_name, version):
        # read_files() debe haberse ejecutado antes: define train_x/test_x/etc.
        if self.train_x is None or self.test_x is None:
            raise RuntimeError(
                "Debes llamar a read_files(...) antes de log_into_mlflow(...)."
            )

        model = load_bin(
            pathlib.Path(path_model).joinpath(f"{model_name}__{version}.joblib")
        )

        container_name = os.getenv("CONTAINER_NAME_MLFLOW")
        storage_account = os.getenv("STORAGE_ACCOUNT_MLFLOW")

        # Sin estas variables el artifact_location quedaria como
        # "abfss://None@None..." y el fallo aparecería mas tarde y de forma opaca.
        if not container_name or not storage_account:
            raise ValueError(
                "Faltan las variables de entorno CONTAINER_NAME_MLFLOW y/o "
                "STORAGE_ACCOUNT_MLFLOW. Revisa el fichero .env "
                "(hay una plantilla en .env_template)."
            )

        experiment_name = f"Experimentos_modelo_{model_name}_{version}_001"
        artifact_location = (
            f"abfss://{container_name}@{storage_account}.dfs.core.windows.net/"
        )

        # Crear el experimento solo si no existe. Evita el except generico que
        # enmascaraba cualquier error real (p. ej. de autenticacion en Azure).
        if mlflow.get_experiment_by_name(experiment_name) is None:
            mlflow.create_experiment(
                experiment_name,
                artifact_location=artifact_location,
            )

        mlflow.set_experiment(experiment_name)
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        with mlflow.start_run(run_name=f"eval_{model_name}_{version}"):
            train_pred_y = model.predict_proba(self.train_x)
            test_pred_y = model.predict_proba(self.test_x)

            dict_metrics = {}
            dict_metrics.update(
                {
                    f"{k}_train": v
                    for k, v in self.eval_metrics(
                        self.train_y, train_pred_y[:, 1]
                    ).items()
                }
            )
            dict_metrics.update(
                {
                    f"{k}_test": v
                    for k, v in self.eval_metrics(
                        self.test_y, test_pred_y[:, 1]
                    ).items()
                }
            )

            save_json(local_metrics_file, dict_metrics)

            mlflow.log_metrics(dict_metrics)
            mlflow.log_params(model.get_params())
            # Adjuntar el JSON de metricas como artefacto del run (viaja al
            # artifact store junto al modelo, no se queda solo en local).
            mlflow.log_artifact(local_metrics_file)

            # El Model Registry no funciona con un backend de tipo "file store".
            if tracking_url_type_store == "file":
                raise Exception(
                    "Falta configurar el fichero .env (se ha dejado una "
                    "plantilla (.env_template) con las variables a definir "
                    "para usar un repositorio remoto)."
                )

            # El modelo se sirve devolviendo PROBABILIDADES. pyfunc_predict_fn
            # hace que la representacion pyfunc (mlflow models serve /
            # mlflow.pyfunc.load_model) llame a predict_proba en lugar de
            # predict. La firma se infiere con predict_proba para que la salida
            # declarada (una columna por clase, en el orden de model.classes_)
            # coincida con lo que devuelve el servicio.
            input_example = self.train_x.head(5)
            signature = mlflow.models.infer_signature(
                input_example, model.predict(input_example)
            )

            mlflow.sklearn.log_model(
                sk_model=model,
                name=model_name,
                registered_model_name=model_name,
                signature=signature,
                input_example=input_example,
                skops_trusted_types=[
                    "box.box_list.BoxList",
                    "mlops.components.transformation.preprocessors.field_number.mb_simple_imputer",
                    "mlops.components.transformation.preprocessors.field_number.mb_standard_scaler",
                    "mlops.components.transformation.preprocessors.field_text.mb_clean_text",
                    "mlops.components.transformation.preprocessors.field_text.mb_woe_encoder",
                    "mlops.components.transformation.preprocessors.field_text_to_number.mb_clean_text_number",
                    "numpy.dtype",
                    "xgboost.core.Booster",
                    "xgboost.sklearn.XGBClassifier",
                ],
            )

        client = mlflow.tracking.MlflowClient()

        client.update_registered_model(
            name=model_name,
            description=f"Modelo {model_name} orientado a la originacion de creditos",
        )

        # search_model_versions NO garantiza el orden de la lista, por lo que
        # versions[0] no tiene por que ser la ultima. Ordenamos explicitamente
        # por numero de version para identificar la mas reciente con seguridad.
        versions = client.search_model_versions(f"name='{model_name}'")
        versions = sorted(versions, key=lambda v: int(v.version), reverse=True)

        latest_version = versions[0].version
        client.set_model_version_tag(model_name, latest_version, "status", "active")
        client.set_registered_model_alias(model_name, "production", latest_version)
        client.update_model_version(
            name=model_name,
            version=latest_version,
            description=f"Version {latest_version} del modelo {model_name}",
        )

        # Archivar todas las versiones anteriores.
        for v in versions[1:]:
            client.set_model_version_tag(model_name, v.version, "status", "archived")
