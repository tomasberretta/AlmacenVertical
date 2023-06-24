import logging


class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        color_formatter = ColorFormatter()
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(color_formatter)
        self.addHandler(console_handler)

    def info(self, message, **kwargs):
        super().info(msg=message)

    def error(self, message, **kwargs):
        super().error(msg=message)

    def warning(self, message, **kwargs):
        super().warning(msg=message)

    def debug(self, message, **kwargs):
        super().debug(msg=message)


class FlaskLogger(Logger):
    def __init__(self, app, name):
        self.name = name
        super().__init__(name)
        self._app = app

    def info(self, message, **kwargs):
        self._app.logger.info(message)

    def error(self, message, **kwargs):
        self._app.logger.error(message)

    def warning(self, message, **kwargs):
        self._app.logger.warning(message)

    def debug(self, message, **kwargs):
        self._app.logger.debug(message)


class ColorFormatter(logging.Formatter):
    grey = "\x1b[90;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: green + "%(asctime)s - %(name)s - %(levelname)s - %(message)s " + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
