#!/usr/bin/env python3
"""Offline worldwide phone-number geolocation.

The worldwide generalization of the trick that cracked the Pingyang case
(signboard hotline 13758466320 -> prefix 1375846 -> Wenzhou): given phone
numbers found on signs, graffiti or business cards, print country, region
(city where libphonenumber geodata has it), carrier and timezones.

Fully offline - libphonenumber ships its geodata inside the package, so this
works from any network (including behind the GFW, where every online lookup
service may be slow or blocked).

Usage:
  uv run --with phonenumbers phone_lookup.py 13758466320 +33142685300
  # local-format numbers need an assumed region (ISO 3166-1 alpha-2):
  uv run --with phonenumbers phone_lookup.py --region CN 13758466320 15058677718

Dependencies: phonenumbers (via `uv run --with phonenumbers`)
"""
import sys

import phonenumbers
from phonenumbers import carrier, geocoder, timezone


def lookup(raw: str, default_region: str) -> None:
    raw = raw.strip()
    if not raw:
        return
    try:
        num = phonenumbers.parse(raw, default_region)
    except phonenumbers.NumberParseException as e:
        print(f"{raw:20s}  PARSE-ERROR: {e}")
        return
    valid = phonenumbers.is_valid_number(num)
    e164 = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    country = geocoder.country_name_for_number(num, "en")
    region = geocoder.description_for_number(num, "en") or "-"
    desc = geocoder.description_for_number(num, "zh") or region
    car = carrier.name_for_number(num, "en") or "-"
    tz = ", ".join(timezone.time_zones_for_number(num)) or "-"
    flag = "OK " if valid else "BAD"
    print(f"{raw:20s}  [{flag}] {e164:18s} country={country:12s} "
          f"region(en)={region:20s} region(zh)={desc:12s} carrier={car:15s} tz={tz}")


def main() -> None:
    args = sys.argv[1:]
    default_region = "CN"  # sensible default for a CN-based user; override with --region
    if "--region" in args:
        i = args.index("--region")
        default_region = args[i + 1].upper()
        del args[i:i + 2]
    if not args:
        print(__doc__)
        sys.exit(1)
    print(f"assumed region for local numbers: {default_region}")
    for raw in args:
        lookup(raw, default_region)


if __name__ == "__main__":
    main()
