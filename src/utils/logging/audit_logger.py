import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_audit_logging(log_file: str = 'audit.log', level=logging.INFO, max_bytes: int = 10485760, backup_count: int = 7):
    """
    Configura o sistema de logging de auditoria para o bot.
    Logs de auditoria serão escritos em um arquivo rotativo.
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger('rpg_bot_audit')
    logger.setLevel(level)

    # Prevent duplicate handlers if called multiple times
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # File handler for rotating logs
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

class AuditLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_action(self, user_id: str, action: str, details: str = ""):
        """
        Registra uma ação de auditoria.
        """
        self.logger.info(f"USER_ID: {user_id} | ACTION: {action} | DETAILS: {details}")

# Example usage (can be removed or modified for actual integration)
if __name__ == '__main__':
    audit_logger_instance = AuditLogger(setup_audit_logging(log_file='logs/audit.log'))
    audit_logger_instance.log_action("user123", "CREATE_CHARACTER", "Character 'Gandalf' created.")
    audit_logger_instance.log_action("user456", "UPDATE_CHARACTER", "Character 'Aragorn' level updated to 5.")