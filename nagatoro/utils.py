def format_bool(
    value: bool,
    *,
    positive: str = "Yes",
    negative: str = "No",
) -> str:
    return positive if value else negative
