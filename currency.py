"""Helper functions to correctly convert between currencies.

Team Fortress 2 economic uses currencies like Mann Co. Supply Crate Keys, refined metal,
reclaimed metal and scrap metal. Half-scrap is only used here, because really cheap items,
like commonly dropped crates are traded for 'weapons', which often cost half a scrap.

1 refined = 3 reclaimed = 9 scrap = 18 half-scrap (weapons).
"""


def refined_to_half_scrap(metal):
    """Converts refined currency to half-scrap."""

    if not metal:
        return 0

    return round(metal * 9 * 2)


def keys_to_half_scrap(keys, key_price):
    """Converts key currency to half-scrap."""

    if not keys:
        return 0

    return keys * key_price


def scraptf_item_price_to_half_scrap(text, key_price):
    """Converts Scrap.tf item prices to their half-scrap equivalent.

    Scrap.tf uses only keys and refined.
    """

    text_splitted = text.split() # Example text_splitted: ['1', 'key,', '13.66', 'refined']
    keys = 0
    refined = 0

    if "key" in text_splitted[1]:
        keys = int(text_splitted[0])

        if len(text_splitted) > 2:
            refined = float(text_splitted[2])
    else:
        refined = float(text_splitted[0])

    return keys_to_half_scrap(keys, key_price) + refined_to_half_scrap(refined)
