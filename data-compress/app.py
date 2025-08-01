from flask import Flask, session
from config import Config
from extensions import db
from routes import main
from dotenv import load_dotenv
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

load_dotenv()


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Main logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Format for logs
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(process)d] - %(module)s:%(lineno)d - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler with daily rotation
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        when="midnight",
        interval=1,
        backupCount=0,  # keep all log files
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log application start
    logger.info("=" * 80)
    logger.info(f"Application starting up (PID: {os.getpid()})")
    logger.info("=" * 80)

# Initialize logging
setup_logging()


def create_app():
    app = Flask(__name__)

    # add database config to app
    """
    You want to configure your Flask app with some settings like:

    Database connection

    Secret key

    Debug mode  

    Config class have those thing stored inside it as data member 

    from object is loading it and config is configuring it with flask app 
    """
    app.config.from_object(Config)

    # connect db with flask app
    db.init_app(app)

    app.register_blueprint(main)

    return app
