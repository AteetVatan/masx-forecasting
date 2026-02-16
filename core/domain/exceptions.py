class MasxError(Exception):
    pass


class LLMClientError(MasxError):
    pass


class LLMResponseParseError(MasxError):
    pass


class DoctrineProcessingError(MasxError):
    pass


class FileProcessingError(MasxError):
    pass


class ConfigurationError(MasxError):
    pass


class ForecastError(MasxError):
    pass


class ScoringError(MasxError):
    pass


class ScenarioError(MasxError):
    pass
