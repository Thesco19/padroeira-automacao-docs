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

    def converter(self, valor: float, moeda_origem: str, moeda_destino: str) -> float:
        if moeda_origem not in self.taxas_de_cambio or moeda_destino not in self.taxas_de_cambio:
            raise ValueError("Moeda não suportada")

        chave_cache = f"{moeda_origem}_{moeda_destino}_{datetime.now().minute}"
        if chave_cache in self.cache:
            return self.cache[chave_cache]

        taxa_de_cambio = self.taxas_de_cambio[moeda_destino] / self.taxas_de_cambio[moeda_origem]
        resultado = valor * taxa_de_cambio
        self.cache[chave_cache] = resultado
        return resultado
