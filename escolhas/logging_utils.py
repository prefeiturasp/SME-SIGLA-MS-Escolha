"""Módulo logging_utils."""

from __future__ import annotations

from typing import Any

from pythonjsonlogger import jsonlogger

from escolhas.middleware import get_correlation_id


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Representa CustomJsonFormatter."""

    def add_fields(
        self, log_record: Any, record: Any, message_dict: Any
    ) -> None:
        """Add fields.

        Args:
            log_record: Log record.
            record: Record.
            message_dict: Message dict.

        Returns:
            Nenhum valor.
        """
        super().add_fields(log_record, record, message_dict)
        cid = get_correlation_id()
        if cid:
            log_record["correlation_id"] = cid
        if record.name == "django.server" or record.module == "basehttp":
            keys_to_remove = ["request", "server_time", "process", "thread"]
            for key in keys_to_remove:
                log_record.pop(key, None)
            log_record["module"] = "http_access"
        if "levelname" in log_record:
            log_record["level"] = log_record.pop("levelname")
