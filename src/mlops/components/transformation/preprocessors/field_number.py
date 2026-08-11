import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted


class mb_standard_scaler(StandardScaler):
    """ """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feature_names_in_ = None

    def fit(self, X, y=None):
        # Guardamos los nombres de columnas si es DataFrame
        if isinstance(X, pd.DataFrame):
            self.feature_names_in_ = X.columns.to_numpy()
        else:
            self.feature_names_in_ = None
        return super().fit(X, y)

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self)
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array(input_features, dtype=object)


class mb_simple_imputer(SimpleImputer):
    """ """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feature_names_in_ = None

    def fit(self, X, y=None):
        # Guardamos los nombres de columnas si es DataFrame
        if isinstance(X, pd.DataFrame):
            self.feature_names_in_ = X.columns.to_numpy()
        else:
            self.feature_names_in_ = None
        return super().fit(X, y)

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self)
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array(input_features, dtype=object)
