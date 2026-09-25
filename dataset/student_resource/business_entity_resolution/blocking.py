from normalization import normalize_business_name


def create_name_block_key(business_name, country):
    name = normalize_business_name(business_name)
    country = str(country).strip().lower()

    name = name.replace(" ", "")
    prefix = name[:3]

    return f"{country}_{prefix}"


def create_address_block_key(business_address, country):
    address = normalize_business_name(business_address)
    country = str(country).strip().lower()

    tokens = address.split()
    useful_tokens = [token for token in tokens if len(token) >= 4]

    if not useful_tokens:
        return f"{country}_unknown"

    address_token = useful_tokens[0]

    return f"{country}_{address_token}"


if __name__ == "__main__":
    examples = [
        (
            "Prime Money",
            "17560 Ellis Road, Tahlequah, OK",
            "US"
        ),
        (
            "Prabhav Business Center",
            "797, Lake Town Block A, Kolkata, Howrah, West Bengal",
            "India"
        ),
        (
            "Dream Construction Limited",
            "H.No.16-11-23/37/A, 2Nd Floor, Flat No.207, Sagar Hotel Building, Hyderabad, Telangana",
            "India"
        )
    ]

    print("Testing blocking keys...\n")

    for name, address, country in examples:
        name_key = create_name_block_key(name, country)
        address_key = create_address_block_key(address, country)

        print("Business:", name)
        print("Name key:", name_key)
        print("Address key:", address_key)
        print()