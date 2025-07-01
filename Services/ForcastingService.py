import math

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor


class ForcastingService:
    def __init__(self, data, features, target):
        self.data = data
        self.features = features
        self.target = target
        self.model = None
        self.task_type = None
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None
        self.prepare_data()

    def prepare_data(self):
        # Подготовка данных только с выбранными признаками
        X = self.data[self.features]
        y = self.data[self.target]
        # Заполнение пропусков
        X = X.fillna(X.median())
        # Разделение на обучающую и тестовую выборки
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    def create_model(self, task_type: str, model_type: str, settings):
        # Создаем модель в зависимости от выбранного типа
        self.task_type = task_type
        if model_type == "Случайный лес":
            if task_type == "Классификация":
                self.model = RandomForestClassifier(
                    n_estimators=settings.get('n_estimators', 100),
                    max_depth=settings.get('max_depth', None),
                    min_samples_split=settings.get('min_samples_split', 2),
                    min_samples_leaf=settings.get('min_samples_leaf', 1),
                    random_state=42
                )
            else:
                self.model = RandomForestRegressor(
                    n_estimators=settings.get('n_estimators', 100),
                    max_depth=settings.get('max_depth', None),
                    min_samples_split=settings.get('min_samples_split', 2),
                    min_samples_leaf=settings.get('min_samples_leaf', 1),
                    random_state=42
                )

        elif model_type == "Логистическая регрессия":
            self.model = LogisticRegression(
                C=settings.get('C', 1.0),
                max_iter=settings.get('max_iter', 1000),
                random_state=42
            )

        elif model_type == "Линейная регрессия":
            self.model = LinearRegression()

        elif model_type == "K-ближайших соседей (KNN)":
            if task_type == "Классификация":
                self.model = KNeighborsClassifier(
                    n_neighbors=settings.get('n_neighbors', 5),
                    weights=settings.get('weights', 'uniform')
                )
            else:
                self.model = KNeighborsRegressor(
                    n_neighbors=settings.get('n_neighbors', 5),
                    weights=settings.get('weights', 'uniform')
                )

        elif model_type == "Дерево решений":
            if task_type == "Классификация":
                self.model = DecisionTreeClassifier(
                    max_depth=settings.get('max_depth', None),
                    min_samples_split=settings.get('min_samples_split', 2),
                    min_samples_leaf=settings.get('min_samples_leaf_tree', 1),
                    random_state=42
                )
            else:
                self.model = DecisionTreeRegressor(
                    max_depth=settings.get('max_depth', None),
                    min_samples_split=settings.get('min_samples_split', 2),
                    min_samples_leaf=settings.get('min_samples_leaf_tree', 1),
                    random_state=42
                )
        elif model_type == "Градиентный бустинг":
            if task_type == "Классификация":
                self.model = GradientBoostingClassifier(
                    n_estimators =settings.get('n_estimators', 100),
                    max_depth=settings.get('max_depth', None),
                    learning_rate=settings.get('learning_rate', 0.1),
                    random_state=42
                )
            else:
                self.model = GradientBoostingRegressor(
                    n_estimators=settings.get('n_estimators', 100),
                    max_depth=settings.get('max_depth', None),
                    learning_rate=settings.get('learning_rate', 0.1),
                    random_state=42
                )

    def train_model(self):
        self.model.fit(self.X_train, self.y_train)

    def evaluate_model(self):
        # Оценка модели
        y_pred = self.model.predict(self.X_test)
        if self.task_type == "Классификация":
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted')
            recall = recall_score(self.y_test, y_pred)
            f1 = f1_score(self.y_test, y_pred, average='weighted')
            roc_auc = roc_auc_score(self.y_test, y_pred)
            # Чувствительность и специфичность
            tn, fp, fn, tp = confusion_matrix(self.y_test, y_pred).ravel()
            sensitivity = tp / (tp + fn)
            specificity = tn / (tn + fp)
            return {
                "Доля правильных ответов (Accuracy)": round(accuracy, 4),
                "Точность (Precision)": round(precision, 4),
                "Полнота (Recall)": round(recall, 4),
                "Чувствительность": round(sensitivity, 4),
                "Специфичность": round(specificity, 4),
                "F1-Score": round(f1, 4),
                "ROC-AUC": round(roc_auc, 4)
            }
        elif self.task_type == "Прогнозирование":
            mae = mean_absolute_error(self.y_test, y_pred)
            mse = mean_squared_error(self.y_test, y_pred)
            rmse = math.sqrt(mse)
            r2 = r2_score(self.y_test, y_pred)
            return {
                "Средняя абсолютная ошибка (MAE)": round(mae, 4),
                "Средняя квадратичная ошибка (MSE)": round(mse, 4),
                "Корень из MSE (RMSE)": round(rmse, 4),
                "Коэффициент детерминации R²": round(r2, 4)
            }

    def get_info(self):
        info = pd.DataFrame()
        if hasattr(self.model, 'feature_importances_'):
            info = self.get_importance()
        elif hasattr(self.model, 'coef_'):
            info = self.get_coefs()
        elif isinstance(self.model, KNeighborsClassifier):
            # Пример: информация по 5 ближайшим соседям
            sample_data = self.X_test.iloc[0].values.reshape(1, -1)
            distances, indices = self.model.kneighbors(sample_data)

            data = {
                'Номер соседа': range(1, len(indices[0]) + 1),
                'Индекс в данных': indices[0],
                'Расстояние': distances[0]
            }
            info = pd.DataFrame(data)
        return info.to_string(index=False)

    def get_importance(self) -> pd.DataFrame:
        importance = pd.DataFrame({
            'Признак': self.features,
            'Важность': self.model.feature_importances_
        }).sort_values('Важность', ascending=False)
        return importance

    def get_coefs(self) -> pd.DataFrame:
        coefs = pd.DataFrame({
            'Признак': self.features,
            'Коэффициент': self.model.coef_[0] if self.task_type == "Классификация" else self.model.coef_
        }).sort_values('Коэффициент', key=abs, ascending=False)
        return coefs

    def make_prediction(self, data):
        return self.model.predict(data)[0]


