import logging
import os
from collections import namedtuple

from rich.console import Console
from rich.traceback import install

from gptcx import version

__version__ = version.__version__


Point = namedtuple("Point", ["pos", "ele", "time", "hr"])


def configure_colored_logging(
    given_logger=None,
    level=logging.INFO,
    fmt="%(levelname)-8s %(name)-25s:%(lineno)4d - %(message)-50s",
):
    """Configures the given logger; format, logging level, style, etc"""
    import coloredlogs

    def add_notice_log_level():
        """Creates a new 'notice' logging level"""
        # inspired by:
        # https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility
        NOTICE_LEVEL_NUM = 25
        logging.addLevelName(NOTICE_LEVEL_NUM, "NOTICE")

        def notice(self, message, *args, **kws):
            if self.isEnabledFor(NOTICE_LEVEL_NUM):
                self._log(NOTICE_LEVEL_NUM, message, args, **kws)

        logging.Logger.notice = notice

    # Add an extra logging level above INFO and below WARNING
    add_notice_log_level()

    # More style info at:
    # https://coloredlogs.readthedocs.io/en/latest/api.html
    field_styles = coloredlogs.DEFAULT_FIELD_STYLES.copy()
    field_styles["asctime"] = {}
    level_styles = coloredlogs.DEFAULT_LEVEL_STYLES.copy()
    level_styles["debug"] = {"color": "white", "faint": True}
    level_styles["notice"] = {"color": "cyan", "bold": True}

    coloredlogs.install(
        logger=given_logger or logger,
        level=level,
        use_chroot=False,
        fmt=fmt,
        level_styles=level_styles,
        field_styles=field_styles,
    )


def set_logger(context, level):
    logger = logging.getLogger(context)
    configure_colored_logging(logger, level=level)
    return logger


install()
console = Console()
logger = set_logger(__name__, level=os.environ.get("LOG_LEVEL", logging.INFO))
