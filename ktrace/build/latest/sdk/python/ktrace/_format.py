from __future__ import annotations


COLOR_NAMES = (
    "Default",
    "BrightCyan",
    "BrightYellow",
    "DeepSkyBlue1",
    "Gold3",
    "LightSalmon1",
    "MediumSpringGreen",
    "MediumOrchid1",
    "LightSkyBlue1",
    "Orange3",
    "Red",
)


def normalize_color_or_throw(color_name: str) -> str:
    token = str(color_name).strip()
    if not token:
        raise ValueError("trace color name must not be empty")

    for candidate in COLOR_NAMES:
        if candidate.lower() == token.lower():
            return candidate

    raise ValueError(f"unknown trace color '{token}'")


def format_message(format_text: str, *args: object) -> str:
    text = str(format_text)
    formatted_args = [str(arg) for arg in args]

    out: list[str] = []
    arg_index = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "{":
            if i + 1 >= len(text):
                raise ValueError("unterminated '{' in trace format string")
            next_char = text[i + 1]
            if next_char == "{":
                out.append("{")
                i += 2
                continue
            if next_char == "}":
                if arg_index >= len(formatted_args):
                    raise ValueError("not enough arguments for trace format string")
                out.append(formatted_args[arg_index])
                arg_index += 1
                i += 2
                continue
            raise ValueError("unsupported trace format token")

        if ch == "}":
            if i + 1 < len(text) and text[i + 1] == "}":
                out.append("}")
                i += 2
                continue
            raise ValueError("unmatched '}' in trace format string")

        out.append(ch)
        i += 1

    if arg_index != len(formatted_args):
        raise ValueError("too many arguments for trace format string")

    return "".join(out)
