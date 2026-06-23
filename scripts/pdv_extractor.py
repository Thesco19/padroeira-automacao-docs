import requests
import json

class PDVExtractor:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        try:
            response = self.session.post(self.url + '/login', data={'username': self.username, 'password': self.password})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao realizar login: {e}")
            return False
        return True

    def baixar_relatorio_financeiro(self):
        try:
            response = self.session.get(self.url + '/relatorio_financeiro')
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar relatório financeiro: {e}")
            return None

    def fechar(self):
        self.session.close()
