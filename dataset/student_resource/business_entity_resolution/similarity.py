from normalization import normalize_business_name, normalize_address


def jaccard_similarity(text1, text2):
    """
    Calculate Jaccard similarity between two pieces of text.

    Jaccard = size of intersection / size of union
    """

    if not text1 or not text2:
        return 0.0

    words1 = set(text1.split())
    words2 = set(text2.split())

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def name_similarity(name1, name2):
    """
    Compare two business names.
    """

    name1 = normalize_business_name(name1)
    name2 = normalize_business_name(name2)

    return jaccard_similarity(name1, name2)


def address_similarity(address1, address2):
    """
    Compare two business addresses.
    """

    address1 = normalize_address(address1)
    address2 = normalize_address(address2)

    return jaccard_similarity(address1, address2)


if __name__ == "__main__":

    print("Testing similarity functions...\n")

    name1 = "Prime Money"
    name2 = "Prime Money Inc."

    address1 = "17560 Ellis Road, Tahlequah, OK"
    address2 = "17560 Ellis Rd Tahlequah Oklahoma"

    print("Name 1:", name1)
    print("Name 2:", name2)

    print(
        "Name similarity:",
        name_similarity(name1, name2)
    )

    print()

    print("Address 1:", address1)
    print("Address 2:", address2)

    print(
        "Address similarity:",
        address_similarity(address1, address2)
    )