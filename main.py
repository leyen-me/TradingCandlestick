import sys
from utils import setup_logging, setup_dotenv
from data_fetcher import run as data_fetcher_run
from quant_analyzer import run as quant_analyzer_run

setup_logging()
setup_dotenv()

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    commands = {
        None: data_fetcher_run,
        "-b": quant_analyzer_run
    }
    
    if command in commands:
        commands[command]()