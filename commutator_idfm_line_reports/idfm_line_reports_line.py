import logging

_LOGGER = logging.getLogger(__name__)

class IdfmLineReportsLine:
    """The class abstracting line status."""

    def __init__(self, identifier, name, lineType, color, text_color):
        """Initialize the data object."""
        self.identifier = identifier
        self.name = name
        self.lineType = lineType
        self.color = color
        self.text_color = text_color
        self.severity_effect = ""
        self.severity_color = ""
        self.tmp_new_severity_effect = ""
        self.tmp_new_severity_color = ""

        _LOGGER.debug(f"New line, ID: {self.identifier}, Name: {self.name}, Color: {self.color}, Text Color: {self.text_color}")
