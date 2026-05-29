from pythonjsonlogger import jsonlogger

from escolhas.middleware import get_correlation_id


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # 1. Injetar Correlation ID
        cid = get_correlation_id()
        if cid:
            log_record["correlation_id"] = cid

        # 2. Limpeza de logs do basehttp (servidor de dev do Django)
        # Esses logs poluem com objetos socket e dados redundantes
        if record.name == "django.server" or record.module == "basehttp":
            # Remove campos pesados/desnecessários que o Django envia
            keys_to_remove = ["request", "server_time", "process", "thread"]
            for key in keys_to_remove:
                log_record.pop(key, None)

            # Opcional: Simplificar o nome do módulo para identificar que é log de rede  # noqa: E501
            log_record["module"] = "http_access"

        # 3. Filtro Global (remover qualquer campo que você nunca queira ver)
        # Por exemplo, se quiser remover o 'funcName' ou 'process' de todos:
        # log_record.pop('process', None)

        # 4. Renomear campos para brevidade (ex: levelname -> level)
        if "levelname" in log_record:
            log_record["level"] = log_record.pop("levelname")
