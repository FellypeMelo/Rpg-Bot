from typing import Dict, Any

class Formatter:
    @staticmethod
    def format_character_sheet(character_data: Dict[str, Any]) -> str:
        """
        Formata os dados de um personagem em uma string legível para o Discord.
        """
        name = character_data.get("name", "N/A")
        alias = character_data.get("alias", "Nenhum")
        class_name = character_data.get("class_name", "N/A")
        level = character_data.get("level", 1)
        experience = character_data.get("experience", 0)
        
        attributes = character_data.get("attributes", {})
        modifiers = character_data.get("modifiers", {})
        
        hp = character_data.get("hp", 0)
        max_hp = character_data.get("max_hp", 0)
        chakra = character_data.get("chakra", 0)
        max_chakra = character_data.get("max_chakra", 0)
        fp = character_data.get("fp", 0)
        max_fp = character_data.get("max_fp", 0)
        
        masteries = character_data.get("masteries", {})
        ph_points = character_data.get("ph_points", 0)
        status_points_available = character_data.get("status_points", 0)
        mastery_points_available = character_data.get("mastery_points", 0)
        
        updated_at = character_data.get("updated_at", "N/A")

        response_message = (
            f"**Ficha de Personagem: {name}** (ID: `{character_data.get('id', 'N/A')}`)\n"
            f"Alias: {alias}\n"
            f"Classe: {class_name} | Nível: {level} | XP: {experience}\n\n"
            f"**Atributos Base:**\n"
            + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in attributes.items()]) + "\n\n"
            f"**Modificadores:**\n"
            + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in modifiers.items()]) + "\n\n"
            f"**Pontos de Vida/Habilidade:**\n"
            f"- HP: {hp}/{max_hp}\n"
            f"- Chakra: {chakra}/{max_chakra}\n"
            f"- FP: {fp}/{max_fp}\n\n"
            f"**Maestrias:**\n"
            + (", ".join([f"{m.capitalize()}: {v}" for m, v in masteries.items()]) if masteries else "Nenhuma") + "\n\n"
            f"**Pontos Disponíveis:**\n"
            f"- PH: {ph_points}\n"
            f"- Status: {status_points_available}\n"
            f"- Maestria: {mastery_points_available}\n\n"
            f"Última Atualização: {updated_at}"
        )
        return response_message

    @staticmethod
    def format_progress_report(report_data: Dict[str, Any]) -> str:
        """
        Formata os dados de um relatório de progresso em uma string legível para o Discord.
        """
        character_name = report_data.get("character_name", "N/A")
        level = report_data.get("level", 1)
        experience = report_data.get("experience", 0)
        attributes = report_data.get("attributes", {})
        modifiers = report_data.get("modifiers", {})
        hp = report_data.get("hp", "0/0")
        chakra = report_data.get("chakra", "0/0")
        fp = report_data.get("fp", "0/0")
        masteries = report_data.get("masteries", {})
        ph_points = report_data.get("ph_points", 0)
        status_points_available = report_data.get("status_points_available", 0)
        mastery_points_available = report_data.get("mastery_points_available", 0)
        last_updated = report_data.get("last_updated", "N/A")

        response_message = (
            f"**Relatório de Progresso: {character_name}** (ID: `{report_data.get('character_id', 'N/A')}`)\n"
            f"Nível: {level} | XP: {experience}\n\n"
            f"**Atributos:**\n"
            + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in attributes.items()]) + "\n\n"
            f"**Modificadores:**\n"
            + "\n".join([f"- {attr.capitalize()}: {value}" for attr, value in modifiers.items()]) + "\n\n"
            f"**Pontos de Vida/Habilidade:**\n"
            f"- HP: {hp}\n"
            f"- Chakra: {chakra}\n"
            f"- FP: {fp}\n\n"
            f"**Maestrias:**\n"
            + (", ".join([f"{m.capitalize()}: {v}" for m, v in masteries.items()]) if masteries else "Nenhuma") + "\n\n"
            f"**Pontos Disponíveis:**\n"
            f"- PH: {ph_points}\n"
            f"- Status: {status_points_available}\n"
            f"- Maestria: {mastery_points_available}\n\n"
            f"Última Atualização: {last_updated}"
        )
        return response_message

    @staticmethod
    def format_usage_statistics(stats_data: Dict[str, Any]) -> str:
        """
        Formata os dados de estatísticas de uso em uma string legível para o Discord.
        """
        total_characters = stats_data.get("total_characters", 0)
        class_distribution = stats_data.get("class_distribution", {})
        average_character_level = stats_data.get("average_character_level", 0.0)

        class_distribution_str = "\n".join([f"- {cls}: {count}" for cls, count in class_distribution.items()]) if class_distribution else "Nenhuma classe registrada."

        response_message = (
            f"**Estatísticas de Uso do RPG Bot**\n\n"
            f"Total de Personagens Registrados: {total_characters}\n"
            f"Nível Médio dos Personagens: {average_character_level}\n\n"
            f"**Distribuição de Classes:**\n"
            f"{class_distribution_str}\n\n"
            f"*(Mais estatísticas em breve!)*"
        )
        return response_message