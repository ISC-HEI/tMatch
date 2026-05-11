import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from zoneinfo import ZoneInfo


class LogType(Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass
class LogRecord:
    uuid: str
    type: LogType
    timestamp: str
    message: str


DEFAULT_LOG_PATH = Path("./logs")
LOG_FILE_NAME = "latest.log"

TYPE_CHAR_MAP = {
    LogType.INFO: "I",
    LogType.WARN: "W",
    LogType.ERROR: "E",
}


class Logger:
    _instance: "Logger | None" = None
    _initialized: bool = False

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if Logger._initialized:
            return

        self.log_path = DEFAULT_LOG_PATH
        self.log_file_path = self.log_path / LOG_FILE_NAME

        Logger._initialized = True

    def is_initialized(self) -> bool:
        return self._initialized

    def init(self) -> None:
        self.log_path.mkdir(parents=True, exist_ok=True)
        self._rename_latest()

    def _parse_timestamp_from_line(self, line: str) -> str | None:
        try:
            parts = line.split("]", 1)
            if len(parts) < 2:
                return None
            ts_part = parts[1].split("|", 1)[0].strip()
            return ts_part.split(" (")[0]
        except (IndexError, ValueError):
            return None

    def _rename_latest(self) -> None:
        latest = self.log_file_path

        if latest.exists():
            with open(latest, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()

            if first_line:
                ts = self._parse_timestamp_from_line(first_line)
                if ts:
                    safe_ts = ts.replace(":", "-").replace(".", "-")
                    archive_name = f"{safe_ts}.log"
                    latest.rename(self.log_path / archive_name)

    def _format_timestamp(self, iso_timestamp: str) -> str:
        dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
        dt_cet = dt.astimezone(ZoneInfo("Europe/Paris"))
        return dt_cet.strftime("%d-%m-%Y %H:%M:%S (%Z)")

    def _build_record(self, log_type: LogType, message: str) -> LogRecord:
        return LogRecord(
            uuid=str(uuid.uuid4()),
            type=log_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            message=message,
        )

    def _write_record(self, record: LogRecord) -> None:
        type_char = TYPE_CHAR_MAP[record.type]
        formatted_ts = self._format_timestamp(record.timestamp)
        log_line = f"[{type_char}] {formatted_ts} | {record.message}"

        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        print(log_line)

    def info(self, message: str) -> None:
        record = self._build_record(LogType.INFO, message)
        self._write_record(record)

    def warn(self, message: str) -> None:
        record = self._build_record(LogType.WARN, message)
        self._write_record(record)

    def error(self, message: str) -> None:
        record = self._build_record(LogType.ERROR, message)
        self._write_record(record)


_logger = Logger()
_logger.init()


def get_logger() -> Logger:
    return _logger


logger = _logger
