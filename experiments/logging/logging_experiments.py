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
            "level": "INFO",
            "formatter": "extra",
            "stream": "ext://sys.stdout"
        },
        "file_handler": {
            "class": "logging.handlers.WatchedFileHandler",
            "level": "INFO",
            "formatter": "extra",
            "filename": "experiments/logging/file_handler_m1.log",
            "mode": "a",
            "encoding": "utf-8"
      }
    },

    "loggers" : {
        "module1" : {
            "handlers" : ["file_handler"],
        },
        "module2" : {
            "handlers" : ["file_handler"],
        },
        "test_pkg.module3" : {
            "handlers" : ["file_handler"],
        }
    },
    
    "root" : {
        "level" : "DEBUG",
        "handlers" : ["console"]
    }

}    

logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

logger.info(f'This is info log from the main module.')
logger.debug(f'This is debug log from the main module.')
logger.warning(f'This is warning log from the main module.')
logger.critical(f'This is critical log from the main module.')

import module1 as m1
m1.test()

import module2 as m2
m2.test()

import test_pkg.module3 as m3
m3.test()