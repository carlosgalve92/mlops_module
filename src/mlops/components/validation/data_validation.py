import pandas as pd

from mlops.entity.config_entity import DataValidationConfig


class DataValiadtion:
    def __init__(self, config: DataValidationConfig):
        self.config = config

    def validate_types_columns(self, status_file, local_data_file, schema) -> bool:
        try:
            validation_status = True
            with open(status_file, "w") as f:
                f.write(f"Validation status: {validation_status}")

            data = pd.read_csv(local_data_file)

            all_cols = list(data.columns)

            for name_col, type_col in schema.items():
                if (name_col not in all_cols) or (type_col != data[name_col].dtype):
                    print(name_col, type_col, data[name_col].dtype)
                    validation_status = False
                    with open(status_file, "w") as f:
                        f.write(f"Validation status: {validation_status}")

            return validation_status

        except Exception as e:
            raise e
