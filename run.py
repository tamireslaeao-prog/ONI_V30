import uvicorn
import os
import sys

# Ensure app directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting ONI Server (Headless/Detached)...")
    
    # Configure logging to file (Crucial for pythonw)
    log_config = uvicorn.config.LOGGING_CONFIG
    
    # Define file handler
    log_config["handlers"]["file"] = {
        "class": "logging.FileHandler",
        "filename": "server.log",
        "mode": "a",
        "formatter": "default",
        "encoding": "utf-8",
    }
    
    # Add file handler to existing loggers
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        if logger_name in log_config["loggers"]:
             logger_cfg = log_config["loggers"][logger_name]
             if "handlers" not in logger_cfg:
                 logger_cfg["handlers"] = []
             if "file" not in logger_cfg["handlers"]:
                logger_cfg["handlers"].append("file")

    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False, # Reload is dangerous in production/headless
        log_config=log_config,
        workers=1
    )
