#!/usr/bin/env python3
import unittest
import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente para bancos de dados de teste
load_dotenv()

# Adiciona o diretório 'src' ao caminho do sistema para que os módulos possam ser importados
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    # Define as suítes de teste na ordem lógica de execução
    test_suites = [
        'tests.unit.core.calculators.test_dice_roller',
        'tests.unit.core.calculators.test_attribute_calc',
        'tests.unit.core.calculators.test_modifier_calc',
        'tests.unit.core.entities.test_character',
        'tests.unit.core.entities.test_class_template',
        'tests.unit.core.entities.test_combat_session',
        'tests.unit.core.services.test_character_service',
        'tests.unit.core.services.test_combat_service',
        'tests.unit.core.services.test_levelup_service',
        'tests.unit.core.services.test_report_service',
        'tests.integration.database.test_redis_repository',
        'tests.integration.database.test_mongodb_repository',
        'tests.integration.discord.test_character_commands',
        'tests.integration.discord.test_combat_commands',
        'tests.integration.discord.test_levelup_commands',
        'tests.integration.discord.test_report_commands',
    ]
    
    # Carrega e executa os testes
    loader = unittest.TestLoader()
    suites = [loader.loadTestsFromName(name) for name in test_suites]
    suite = unittest.TestSuite(suites)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(not result.wasSuccessful())