import re


class SQLValidationError(ValueError):
    pass


def validate_read_only(sql: str) -> None:
    compact = " ".join(sql.lower().split())
    if not compact.startswith("select "):
        raise SQLValidationError("Only SELECT queries are allowed.")
    if ";" in compact or re.search(
        r"\b(insert|update|delete|drop|alter|attach|pragma|vacuum)\b", compact
    ):
        raise SQLValidationError("The query contains a blocked SQL operation.")
