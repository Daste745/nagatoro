def format_bool(
    value: bool,
    *,
    positive: str | None = None,
    negative: str | None = None,
) -> str:
    if positive is None:
        positive = "Yes"

    if negative is None:
        negative = "No"

    if value:
        return positive
    else:
        return negative
