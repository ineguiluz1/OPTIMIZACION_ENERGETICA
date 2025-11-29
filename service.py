"""
BentoML Service for Building Heat Load Prediction
Loads models directly from local files

Deploy with: bentoml serve service:BuildingHeatLoadService
"""

import bentoml
import joblib
import pandas as pd
import numpy as np
from pathlib import Path


# =============================================================================
# Model Classes (self-contained, no external dependencies)
# =============================================================================

def load_changepoint_parameters(csv_path, key_column):
    """
    Load changepoint parameters from CSV file.
    
    Args:
        csv_path: Path to CSV file with changepoint parameters
        key_column: Column name to use as lookup key (e.g., 'DATE_timestamp_week' or 'ClusterHour')
    
    Returns:
        Dictionary mapping key -> parameter dict
    """
    df = pd.read_csv(csv_path, sep=";")
    
    param_dict = {}
    for _, row in df.iterrows():
        key = int(row[key_column])
        param_dict[key] = {
            'slope_Temp': float(row['slope_Temp']),
            'slope_Irrad': float(row['slope_Irrad']),
            'intercept': float(row['intercept']),
            'minimum': float(row['minimum'])
        }
    
    return param_dict


def predict_power_from_parameters(temperature, solar_irradiation, slope_Temp, slope_Irrad, intercept, minimum):
    """
    Compute power prediction using changepoint model parameters.
    
    Args:
        temperature: Temperature value(s) in °C
        solar_irradiation: Solar irradiation value(s) in W/m²
        slope_Temp: Temperature sensitivity [kW/°C]
        slope_Irrad: Solar irradiation sensitivity [kW/(W/m²)]
        intercept: Base load [kW]
        minimum: Minimum operational load [kW]
    
    Returns:
        Predicted power [kW]
    """
    temp = np.atleast_1d(temperature)
    irrad = np.atleast_1d(solar_irradiation)
    
    # Core changepoint model
    power = intercept + slope_Temp * temp + slope_Irrad * irrad
    
    # Apply minimum threshold and non-negativity
    power = np.maximum(minimum, power)
    power = np.maximum(0.0, power)
    
    return power if power.shape[0] > 1 else float(power[0])


class TimeOfWeekChangepointModel:
    """Wrapper for Time-of-Week changepoint parameters."""
    
    def __init__(self, parameters_dict):
        self.parameters = parameters_dict
        self.model_type = "Time-of-Week Changepoint Model"
        self.num_models = len(parameters_dict)
    
    def predict(self, timestamp_week, temperature, solar_irradiation):
        """
        Predict power for given timestamp and weather conditions.
        
        Args:
            timestamp_week: Hour of week (0-167)
            temperature: Temperature in °C
            solar_irradiation: Solar irradiation in W/m²
        
        Returns:
            Predicted power in kW
        """
        if timestamp_week not in self.parameters:
            raise ValueError(f"timestamp_week {timestamp_week} not in valid range (0-167)")
        
        params = self.parameters[timestamp_week]
        return predict_power_from_parameters(
            temperature, solar_irradiation,
            params['slope_Temp'], params['slope_Irrad'],
            params['intercept'], params['minimum']
        )
    
    def predict_batch(self, timestamps_week, temperatures, solar_irradiations):
        """
        Predict power for multiple observations.
        
        Args:
            timestamps_week: Array of hour-of-week values (0-167)
            temperatures: Array of temperatures in °C
            solar_irradiations: Array of solar irradiations in W/m²
        
        Returns:
            Array of predicted powers in kW
        """
        timestamps_week = np.atleast_1d(timestamps_week)
        temperatures = np.atleast_1d(temperatures)
        solar_irradiations = np.atleast_1d(solar_irradiations)
        
        predictions = []
        for ts, temp, irrad in zip(timestamps_week, temperatures, solar_irradiations):
            predictions.append(self.predict(ts, temp, irrad))
        
        return np.array(predictions)


class ClusterChangepointModel:
    """Wrapper for cluster-based changepoint parameters."""
    
    def __init__(self, parameters_dict, cart_model=None, model_type="Cluster Changepoint Model"):
        self.parameters = parameters_dict
        self.cart_model = cart_model
        self.model_type = model_type
        self.num_clusters = len(parameters_dict)
    
    def predict(self, cluster_hour, temperature, solar_irradiation):
        """
        Predict power for given cluster-hour and weather conditions.
        
        Args:
            cluster_hour: Cluster-hour identifier (0-73 for 24h * ~3-4 clusters)
            temperature: Temperature in °C
            solar_irradiation: Solar irradiation in W/m²
        
        Returns:
            Predicted power in kW
        """
        if cluster_hour not in self.parameters:
            raise ValueError(f"cluster_hour {cluster_hour} not found in parameters")
        
        params = self.parameters[cluster_hour]
        return predict_power_from_parameters(
            temperature, solar_irradiation,
            params['slope_Temp'], params['slope_Irrad'],
            params['intercept'], params['minimum']
        )
    
    def predict_batch(self, cluster_hours, temperatures, solar_irradiations):
        """
        Predict power for multiple observations.
        
        Args:
            cluster_hours: Array of cluster-hour identifiers
            temperatures: Array of temperatures in °C
            solar_irradiations: Array of solar irradiations in W/m²
        
        Returns:
            Array of predicted powers in kW
        """
        cluster_hours = np.atleast_1d(cluster_hours)
        temperatures = np.atleast_1d(temperatures)
        solar_irradiations = np.atleast_1d(solar_irradiations)
        
        predictions = []
        for ch, temp, irrad in zip(cluster_hours, temperatures, solar_irradiations):
            predictions.append(self.predict(ch, temp, irrad))
        
        return np.array(predictions)


# =============================================================================
# BentoML Service Definition
# =============================================================================

@bentoml.service(
    name="building_heat_load_predictor",
    resources={"cpu": "1"}
)
class BuildingHeatLoadService:
    """BentoML Service for Building Heat Load Prediction"""
    
    def __init__(self):
        """Load models from local files"""
        # Usar ruta absoluta basada en la ubicación del archivo
        base_dir = Path(__file__).parent
        output_dir = base_dir / "output"
        
        # Load Time-of-Week model
        tow_params_path = output_dir / "data_06_Changepoint_Pars_summ_TOW2.csv"
        tow_params = load_changepoint_parameters(tow_params_path, 'DATE_timestamp_week')
        self.tow_model = TimeOfWeekChangepointModel(tow_params)
        
        # Load Cluster-PRED model
        cluster_pred_params_path = output_dir / "data_09_Changepoint_Pars_summ_CLUST_PRED.csv"
        cart_model_path = output_dir / "data_09_cart_model.pkl"
        
        cluster_pred_params = load_changepoint_parameters(cluster_pred_params_path, 'ClusterHour_PRED')
        
        cart_data = joblib.load(cart_model_path)
        if isinstance(cart_data, dict) and 'model' in cart_data:
            self.cart_classifier = cart_data['model']
        else:
            self.cart_classifier = cart_data
        
        self.cluster_pred_model = ClusterChangepointModel(
            cluster_pred_params,
            cart_model=self.cart_classifier,
            model_type="Cluster Changepoint Model (CART-Predicted Clustering)"
        )
    
    @bentoml.api
    def predict_tow(self, timestamp_week: int, temperature: float, solar_irradiation: float) -> dict:
        """
        Predict using Time-of-Week model.
        
        Args:
            timestamp_week: Hour of week (0-167)
            temperature: Temperature in °C
            solar_irradiation: Solar irradiation in W/m²
        
        Returns:
            dict with power_kw prediction
        """
        prediction = self.tow_model.predict(timestamp_week, temperature, solar_irradiation)
        return {"power_kw": float(prediction)}
    
    @bentoml.api
    def predict_cluster_pred(self, cluster_hour: int, temperature: float, solar_irradiation: float) -> dict:
        """
        Predict using Cluster-PRED model (CART-predicted clustering).
        
        Args:
            cluster_hour: Cluster-hour identifier
            temperature: Temperature in °C
            solar_irradiation: Solar irradiation in W/m²
        
        Returns:
            dict with power_kw prediction
        """
        prediction = self.cluster_pred_model.predict(cluster_hour, temperature, solar_irradiation)
        return {"power_kw": float(prediction)}
    
    @bentoml.api
    def predict_batch_tow(self, timestamps_week: list, temperatures: list, solar_irradiations: list) -> dict:
        """Batch prediction using Time-of-Week model."""
        predictions = self.tow_model.predict_batch(
            np.array(timestamps_week),
            np.array(temperatures),
            np.array(solar_irradiations)
        )
        return {"predictions": predictions.tolist()}
    
    @bentoml.api
    def predict_batch_cluster_pred(self, cluster_hours: list, temperatures: list, solar_irradiations: list) -> dict:
        """Batch prediction using Cluster-PRED model."""
        predictions = self.cluster_pred_model.predict_batch(
            np.array(cluster_hours),
            np.array(temperatures),
            np.array(solar_irradiations)
        )
        return {"predictions": predictions.tolist()}
    
    # Expose model info as properties
    @property
    def tow_model_type(self):
        return self.tow_model.model_type
    
    @property
    def tow_num_models(self):
        return self.tow_model.num_models
    
    @property
    def cluster_pred_model_type(self):
        return self.cluster_pred_model.model_type
    
    @property
    def cluster_pred_num_clusters(self):
        return self.cluster_pred_model.num_clusters


# =============================================================================
# Service Instance for Streamlit
# =============================================================================

service_instance = BuildingHeatLoadService()
