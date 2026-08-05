VALID_ANCHORS = {"n", "ne", "e", "se", "s", "sw", "w", "nw", "center"}

def is_non_empty_string(
    value: object
) -> bool:
    return isinstance(value, str) and value != ""

def is_valid_hex_color_code(
    value: object
) -> bool:
    if not isinstance(value, str):
        return False
    if not len(value) == 7:
        return False
    if not value[:1] == "#":
        return False
    for character in value[1:]:
        if character not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "A", "B", "C", "D", "E", "F"}:
            return False
    return True

def is_valid_integer(
    value: object
) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)

def is_positive_integer(
    value: object
) -> bool:
    return is_valid_integer(value) and value >= 1

def is_valid_anchor(
    value: object
) -> bool:
    return isinstance(value, str) and value in VALID_ANCHORS
