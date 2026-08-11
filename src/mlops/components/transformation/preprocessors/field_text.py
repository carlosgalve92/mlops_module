import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


class mb_woe_encoder(BaseEstimator, TransformerMixin):
    """
    Clase creada como encoder de woe sobre variables
    categoricas. Esta transformacion podría utilizarse
    en un pipeline de sklearn
    """

    def __init__(self, pc_min_other=0.05, keep_na=True):
        """ """
        self.pc_min_other = pc_min_other
        self.keep_na = keep_na
        self.dict_woe = {}
        self.feature_names_in_ = None

    def fit(self, X, y=None):
        """ """
        self.feature_names_in_ = X.columns.to_numpy()

        if isinstance(y, pd.DataFrame) or isinstance(y, pd.Series):
            y = y.values.squeeze()

        for c in self.feature_names_in_:
            self.dict_woe[c] = {"WOES": {}, "OTHERS": None}
            # Se eliminan registros con NAs
            target_sm = y[np.where(X[c].notna())]
            feature_sm = X.loc[(X[c].notna().values), [c]]

            df_aux = pd.concat(
                [
                    feature_sm.reset_index(drop=True),
                    pd.DataFrame(target_sm.reshape(-1, 1)),
                ],
                axis=1,
                ignore_index=False,
            )
            # Se calcula el numero de eventos por categoria
            event_x_cat = df_aux.groupby(c).sum()
            # Se calcula el numero de registros de cada categoria
            reg_x_cat = df_aux.groupby(c).count()
            # Se calcula el numero de no eventos por categoria
            non_event_x_cat = reg_x_cat - event_x_cat

            # Se calcula woe (Esta al reves de la teorica)
            woe = np.log((event_x_cat + 1) / (non_event_x_cat + 1))

            # Se resetean indices para tener columna con categorias
            woe = woe.reset_index()
            # Se renombran columnas
            woe.columns = ["CATEGORIA", "VALOR_WOE"]

            # Se calcula el numero de registros minimos que debe tener
            # una categoria para no ser considerada minoritaria
            lim_value_other = self.pc_min_other * len(y)

            # Se obtienen las categorias minoritarias
            ls_cat_excl = (
                reg_x_cat[(reg_x_cat < lim_value_other).values]
                .reset_index()
                .iloc[:, 0]
                .tolist()
            )

            # Se filtran WoE para quedarse solo con las categorias
            # mayoritarias
            woe_filtrado = woe[~(woe["CATEGORIA"].isin(ls_cat_excl))]
            # Se almacenan los woe en formato pares clave-valor de
            # categoria-valor
            self.dict_woe[c]["WOES"] = dict(
                zip(woe_filtrado["CATEGORIA"], woe_filtrado["VALOR_WOE"])
            )

            # Se calcula el woe comun para las clases minoritarias
            event_total_other = target_sm[
                np.where(~(feature_sm.isin(ls_cat_excl).values.squeeze()))
            ].sum()
            non_event_other = (
                target_sm[
                    np.where(~(feature_sm.isin(ls_cat_excl).values.squeeze()))
                ].size
                - event_total_other
            )
            self.dict_woe[c]["OTHERS"] = np.log(
                (event_total_other + 1) / (non_event_other + 1)
            )

        return self

    def transform(self, X):
        """ """
        for c in X.columns:
            X[c] = (
                X[c]
                .map(
                    lambda k: self._get_value_from_dict(
                        k, self.dict_woe[c]["WOES"], self.dict_woe[c]["OTHERS"]
                    )
                )
                .astype(np.float64)
            )

        return X

    # def fit_transform(self, X, y=None):
    #     """
    #     """
    #     return self.fit(X, y).transform(X)

    def _get_value_from_dict(self, key_dict, dict_values, value_other):
        """
        Función utilizada para que sustituye clave de un diccionario
        por su valor. En caso de que la clave sea None, np.nan,
        esta se sustituye por np.nan. Y para cuando no es
        desconocido el valor pero tampoco aparece en el diccionario
        se sustituye por value_other

        Keyword arguments:
        :key_dict: clave a sustituir por su valor
        :dict_values: diccionario con las tuplas clave-valor
        """
        if (pd.isna(key_dict)) and (self.keep_na):
            return np.nan
        else:
            return dict_values.get(key_dict, value_other)

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self)
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array(input_features, dtype=object)


class mb_clean_text(BaseEstimator, TransformerMixin):
    """ """

    def __init__(self, replace_value=None):
        """ """
        self.replace_value = replace_value

    def fit(self, X, y=None):
        """ """
        self.feature_names_in_ = X.columns.to_numpy()

        return self

    def transform(self, X):
        """ """
        for c in X.columns:
            X[c] = X[c].str.replace(r"_", "").str.strip()
            X.loc[(X[c] == ""), c] = self.replace_value

            if self.replace_value is not None:
                X.loc[(X[c].isna()), c] = self.replace_value

        return X

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self)
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array(input_features, dtype=object)
