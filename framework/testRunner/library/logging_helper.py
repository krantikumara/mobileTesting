import logging
import os


class LoggingHelper:
    """Contains helper methods for setting custom logging property values"""

    @staticmethod
    def configure_logging():
        """Configures logging accordingly"""
        # To-Do Make the parameters configurable (Like-> log level and format)
        logging.basicConfig(level="DEBUG", format="%(asctime)s %(levelname)s %(message)s")