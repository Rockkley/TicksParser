"""Entry point to the program"""
import logging
from datetime import datetime
import gui

# Logger settings
logger = logging.getLogger(__name__)
logfile = logging.FileHandler(f'logs/{datetime.now().strftime("%Y-%m-%d")}.log')
log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logfile.setFormatter(log_format)
logger.addHandler(logfile)
logging.basicConfig(datefmt="%d-%m-%y %H:%M:%S", level=logging.INFO)


if __name__ == "__main__":
    logger.info("Launching program...")
    gui.run()

