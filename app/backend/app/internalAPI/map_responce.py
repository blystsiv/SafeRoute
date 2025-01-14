import requests
import geojson
import aiohttp
import asyncio
import tensorflow as tf
from pandas import DataFrame

from app.backend.utility.coordinates import Grid

class mapResponce:
    def __init__(self, model_path="./app/backend/app/ml/model/model.h5") -> None:
        self._model = self.__load_model(model_path)

    def __load_model(self, path) -> tf.saved_model:
        model = tf.saved_model.load(path)
        return model
    
    def predict_from_grid(self, grid:Grid) -> Grid:
        try:
            values = {'pop_count_adj': [], 'income': []}
            for c in grid.chunks:
                values['pop_count_adj'].append(c.data['pop_count_adj']) 
                values['income'].append(c.data['income']) 
                
            prediction = self.predict_from_data(values)

            for i in len(grid.chunks):
                grid.chunks[i].data['crime_level'] = prediction[i]

        except Exception as e:
            raise ValueError(f"Grid prediction error: \n{e}")
    
    def predict_from_data(self, input_data: dict) -> list:
        try:
            if not set(input_data.keys()) >= {'pop_count_adj', 'income'}:
                raise ValueError(f"Keys not found for input_data({input_data.keys()}), should contain 'pop_count_adj', 'income'")
            
            values = DataFrame(input_data, index=[0])
            res = []
            for _, v in values.itertuples():
                res.append(self._model.predict(v))
            return res

        except Exception as e:
            raise ValueError(f"Prediction error: \n{e}")
