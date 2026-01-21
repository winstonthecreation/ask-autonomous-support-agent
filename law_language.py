import re

LAW_PATTERN = re.compile(
    r"LAW\s*{\s*"
    r"when\s+(?P<field>\w+)\s*(?P<op>>|<|==|!=)\s*(?P<value>\w+)\s*"
    r"block\s+(?P<tool>\w+)\s*"
    r"because\s+\"(?P<reason>[^\"]+)\"\s*"
    r"}",
    re.IGNORECASE
)


def parse_law_script(text: str):
    match = LAW_PATTERN.search(text)
    if not match:
        raise ValueError("Invalid LawScript")

    return {
        "field": match.group("field"),
        "operator": match.group("op"),
        "value": match.group("value"),
        "tool": match.group("tool"),
        "reason": match.group("reason")
    }
