from pprint import pprint

from dotenv import load_dotenv

import lexmount
from lexmount import Lexmount


load_dotenv(override=True)


def main() -> None:
    client = Lexmount()

    print(f"lexmount version: {lexmount.__version__}")

    catalog = client.catalog_info()
    print("\nCatalog info:")
    pprint(catalog)

    if catalog["available"]:
        print("\nRegions:")
        for region in catalog["regions"]:
            print(
                "- {region_id} default={default} host={host} endpoint_ips={endpoint_ips}".format(
                    region_id=region.get("region_id"),
                    default=region.get("default"),
                    host=region.get("host"),
                    endpoint_ips=region.get("endpoint_ips"),
                )
            )

    client.close()


if __name__ == "__main__":
    main()
