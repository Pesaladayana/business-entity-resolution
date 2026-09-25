import re
import unicodedata


def normalize_text(text):
    """
    General text normalization.

    Converts text into a simpler form so that
    small formatting differences do not prevent matching.
    """

    if text is None:
        return ""

    text = str(text)

    # Convert accented characters into their base form
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Convert to lowercase
    text = text.lower()

    # Replace punctuation with spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_business_name(name):
    """
    Normalize a business name.
    """

    return normalize_text(name)


def normalize_address(address):
    """
    Normalize a business address.
    """

    return normalize_text(address)


if __name__ == "__main__":

    print("Testing normalization...")

    name_examples = [
        "Prime Money",
        "PRIME MONEY",
        "Prime-Money Inc.",
        "Café Coffee"
    ]

    address_examples = [
        "17560 Ellis Road, Tahlequah, OK",
        "17560 ELLIS ROAD, TAHLEQUAH, OK",
        "123-A Main Street, Hyderabad"
    ]

    print("\nBusiness names:")

    for name in name_examples:
        print(name, "->", normalize_business_name(name))

    print("\nAddresses:")

    for address in address_examples:
        print(address, "->", normalize_address(address))