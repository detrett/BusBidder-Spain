def parse_boolean(value):
    """
    Convert strings "true" or "false" into a Python boolean.
        Args:
            value: The text read from a CSV field.

        Returns:
            True or False, depending on the text.

        Raises:
            ValueError: If the text is not "true" or "false".
    """
    normalized = value.strip().lower()

    if normalized not in ("true", "false"):
        raise ValueError(f"Expected 'true' or 'false', got {value!r}.")

    return normalized == "true"

