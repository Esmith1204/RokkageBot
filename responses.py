from random import choice, randint


def get_responses(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return None
    elif ':3' in lowered:
        return ':3'
    elif 'meow' in lowered:
        return 'meow'