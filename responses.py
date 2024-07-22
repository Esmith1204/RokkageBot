
def get_responses(user_input: str) -> str:
    lowered: str = user_input.lower()

    brainrot_list = set(['fart', 'geek', 'freak', 'gyat', 'sigma', 'skib', 'riz'])

    if ':3' in lowered:
        return ':3'
    elif 'meow' in lowered:
        return 'meow'
    else:
        for word in brainrot_list:
            if word in lowered:
                return 'https://tenor.com/view/cat-cats-orange-cat-orange-cats-cat-weird-gif-17010424884748616697'
    