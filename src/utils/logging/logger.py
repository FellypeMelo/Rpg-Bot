import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = 'rpg_bot.log', level=logging.INFO, max_bytes: int = 10485760, backup_count: int = 5):
    """
    Configura o sistema de logging para o bot.
    Logs serão escritos em um arquivo rotativo e também no console.
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger('rpg_bot')
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler for rotating logs
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Example usage (can be removed or modified for actual integration)
if __name__ == '__main__':
    logger = setup_logging(log_file='logs/rpg_bot.log', level=logging.DEBUG)
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")