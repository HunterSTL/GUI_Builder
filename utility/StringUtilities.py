_DEFAULT_LABEL_COLUMN_WIDTH = 30
_DEFAULT_INDENTATION = " " * 4  #uses spaces instead of tabs for stable visual alignment

def format_field(
    label: str,
    value: str | int | list[str],
    label_column_width: int = _DEFAULT_LABEL_COLUMN_WIDTH,
    indentation: str = _DEFAULT_INDENTATION
) -> str:
    """Format a labeled value with horizontal alignment."""
    if isinstance(value, list):
        value = ", ".join(value)
    return f"{indentation}{label + ':':<{label_column_width - len(indentation)}}{value}"

def format_mapping(
    label: str,
    mapping: dict[str, str | int],
    label_column_width: int = _DEFAULT_LABEL_COLUMN_WIDTH,
    indentation: str = _DEFAULT_INDENTATION
) -> str:
    """Format a labeled mapping with horizontal alignment."""
    child_indentation = indentation * 2
    lines = []

    for key, value in mapping.items():
        lines.append(f"{child_indentation}{key + ':':<{label_column_width - len(child_indentation)}}{value}")

    mapping_content = "\n".join(lines)
    return f"{indentation}{label}:\n{mapping_content}"

def format_mapping_changes(
    label: str,
    before_mapping: dict[str, object],
    after_mapping: dict[str, object],
    label_column_width: int = _DEFAULT_LABEL_COLUMN_WIDTH,
    indentation: str = _DEFAULT_INDENTATION
) -> str:
    """Format labeled mapping changes with horizontal alignment, omitting values that remained equal."""
    child_indentation = indentation * 2
    lines = []

    for key in before_mapping | after_mapping:
        before_value = before_mapping.get(key)
        after_value = after_mapping.get(key)

        if before_value != after_value:
            lines.append(f"{child_indentation}{key + ':':<{label_column_width - len(child_indentation)}}{before_value} → {after_value}")

    if not lines:
        lines.append(f"{child_indentation}no changes")

    changes = "\n".join(lines)
    return f"{indentation}{label}:\n{changes}"
