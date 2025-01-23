def format_curly_braces(text: str) -> str:
    """
    Replace '{' with '{{' and '}' with '}}'.
    """

    text = text.replace("{", "{{")
    return text.replace("}", "}}")
