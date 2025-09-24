import math
from typing import Dict


def calculate_bonuses_for_level(level: int) -> Dict[str, int]:
    """
    Calcula os bônus de status, maestria e PH para um nível específico.
    Baseado em grupos de 5 níveis (k = ceil(level/5)).
    Escalável para níveis além de 200.
    """
    if level <= 1:
        return {"status": 0, "maestria": 0, "ph": 0}

    # Calcula o grupo k (1-indexed)
    k = math.ceil(level / 5)

    # Calcula status base: max(ceil(k/2) + 4, k + 1)
    base_status = max(math.ceil(k / 2) + 4, k + 1)
    base_mastery = base_status - 3

    # Se NÃO for múltiplo de 5: valores base
    if level % 5 != 0:
        status_points = base_status
        maestria_points = base_mastery
        ph_points = 0
    else:
        # Se for múltiplo de 5: dobra os pontos e atribui PH
        status_points = base_status * 2
        maestria_points = base_mastery * 2
        if k <= 2:
            ph_points = 2
        elif k <= 5:
            ph_points = 3
        else:
            ph_points = math.ceil(base_status / 2)

    return {
        "status": status_points,
        "maestria": maestria_points,
        "ph": ph_points,
    }


# Função auxiliar para gerar tabela de referência (opcional, para debug ou documentação)
def generate_level_table(start_level: int = 1, end_level: int = 200) -> None:
    """
    Gera e imprime uma tabela de níveis com bônus calculados.
    Útil para validação e documentação.
    """
    print(f"Tabela de Bônus por Nível ({start_level} a {end_level})")
    print("-" * 60)
    for L in range(start_level, end_level + 1):
        bonuses = calculate_bonuses_for_level(L)
        status = bonuses["status"]
        maestria = bonuses["maestria"]
        ph = bonuses["ph"]

        if ph == 0:
            print(f"Level {L:3d} = {status:3d} status, {maestria:3d} maestria")
        else:
            print(f"Level {L:3d} = {status:3d} status, {maestria:3d} maestria, {ph:2d} PH")


if __name__ == "__main__":
    print("Gerando tabela de níveis até o nível 200:")
    generate_level_table(200)