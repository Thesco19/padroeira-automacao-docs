from datetime import datetime, timedelta
from typing import Dict

class ConversorMoedas:
    def __init__(self):
        self.taxas_de_cambio = {
            'USD': 1.0,
            'EUR': 0.88,
            'BRL': 5.20
        }
        self.cache = {}
        self.valor = 0
        self.moeda_origem = ''
        self.moeda_destino = ''

