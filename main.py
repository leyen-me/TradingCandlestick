import sys
from utils import setup_logging, setup_dotenv

setup_logging()
setup_dotenv()

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    commands = {
        None: "data_fetcher",
        "-a": "group_analyzer",
        "-b": "quant_analyzer",
    }
    
    if command in commands:
        module_name = commands[command]
        module = __import__(module_name, fromlist=[None])
        # module.run()