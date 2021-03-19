import logging.config


config = {
    "version" : 1.0,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "extra": {"format":"%(asctime)-16s %(name)-8s %(filename)-12s %(lineno)-6s %(funcName)-30s %(levelname)-8s %(message)s",
             "datefmt":"%m-%d %H:%M:%S"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "extra",
            "stream": "ext://sys.stdout"
        }       
    },

    "loggers" : {
        "console_logger" : {
            "handlers" : ["console"]
        }
    },
    
    "root" : {
        "level" : "DEBUG",
        "handlers" : ["console"]
    }

}    

logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

print(__name__)

logger.info('Warn message')