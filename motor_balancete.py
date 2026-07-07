from datetime import datetime


def normalizar_dia(dia_str):
    """
    Normaliza a string de dia para um número inteiro.

    Esta função tenta remover o ponto da string e convertê-la para um número inteiro.
    Se isso não funcionar, tente parser-a como data no formato dd/mm.
    Se ainda assim não funcionar, tente parserá como data no formato AAAAmmdd.
    Caso tudo falhe, retorna None.

    Args:
        dia_str (str): A string de dia a ser normalizada.

    Returns:
        int: O dia normalizado como um número inteiro.
    """

    # Tenta remover o ponto da string e convertê-la para um número inteiro
    try:
        dia = int(dia_str.replace(".", ""))
        if 1 <= dia <= 31:
            return dia
        else:
            raise ValueError
    except ValueError:
        pass  # Não foi possível converter para um número inteiro

    # Tenta parser-a como data no formato dd/mm
    try:
        dia = datetime.strptime(dia_str, "%d/%m").day
        return dia
    except ValueError:
        pass  # Não foi possível parser como data no formato dd/mm

    # Tenta parserá como data no formato AAAAmmdd
    try:
        dia = int(datetime.strptime(dia_str, "%Y%m%d").strftime("%d"))
        return dia
    except ValueError:
        pass  # Não foi possível parser como data no formato AAAAmmdd

    # Caso tudo falhe, retorna None
    return None
