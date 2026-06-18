import unittest
from conversor import ConversorMoedas

class TestConversorMoedas(unittest.TestCase):
    def test_conversao(self):
        conversor = ConversorMoedas()
        self.assertAlmostEqual(conversor.converter(100, 'USD', 'EUR'), 88.0)
        self.assertAlmostEqual(conversor.converter(100, 'EUR', 'USD'), 113.64)
        self.assertAlmostEqual(conversor.converter(100, 'USD', 'BRL'), 520.0)

    def test_cache(self):
        conversor = ConversorMoedas()
        resultado1 = conversor.converter(100, 'USD', 'EUR')
        resultado2 = conversor.converter(100, 'USD', 'EUR')
        self.assertEqual(resultado1, resultado2)

    def test_moeda_nao_suportada(self):
        conversor = ConversorMoedas()
        with self.assertRaises(ValueError):
            conversor.converter(100, 'USD', 'JPY')

if __name__ == '__main__':
    unittest.main()
