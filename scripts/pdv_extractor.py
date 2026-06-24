import requests
import json
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

class PDVExtractor:
    def __init__(self):
        self.url = os.getenv('URL')
        self.username = os.getenv('USER')
        self.password = os.getenv('PASSWORD')
        self.session = requests.Session()

    def login(self):
        try:
            response = self.session.post(self.url + '/login', data={'username': self.username, 'password': self.password})
            response.raise_for_status()
            logging.info("Login realizado com sucesso")
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao realizar login: {e}")
            return False
        return True

    def baixar_relatorio_financeiro(self, formato='json'):
        try:
            if formato == 'html':
                response = self.session.get(self.url + '/relatorio_financeiro', headers={'Accept': 'text/html'})
            elif formato == 'csv':
                response = self.session.get(self.url + '/relatorio_financeiro', headers={'Accept': 'text/csv'})
            else:
                response = self.session.get(self.url + '/relatorio_financeiro')
            response.raise_for_status()
            if formato == 'html' or formato == 'csv':
                logging.info(f"Relatório financeiro baixado em formato {formato}")
                return response.text
            else:
                logging.info("Relatório financeiro baixado em formato json")
                return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao baixar relatório financeiro: {e}")
            return None

    def fechar(self):
        self.session.close()
