"""Campus parking permit manager.

Issues permits for vehicles in zones A to C, revokes them, checks for
expired permits and flags vehicles that should not be parked in a zone.
"""
import json
import secrets
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%d"
ZONES = ["A", "B", "C"]


def register_permit(permits, vehicle_plate, zone_id, zone_records=None):
    """Issue a permit and return its number, or None if the input is invalid."""
    if not vehicle_plate or zone_id not in ZONES:
        return None
    if zone_records is None:
        zone_records = []
    permit_no = "P" + str(secrets.randbelow(90000) + 10000)
    expiry = datetime.now() + timedelta(days=180)
    permits[vehicle_plate] = {
        "zone": zone_id,
        "permit": permit_no,
        "expiry": expiry.strftime(DATE_FORMAT),
    }
    zone_records.append((vehicle_plate, zone_id))
    return permit_no


def revoke_permit(permits, vehicle_plate):
    """Remove a vehicle's permit, reporting if it does not have one."""
    if permits.pop(vehicle_plate, None) is None:
        print("No permit to revoke for:", vehicle_plate)


def is_expired(permits, vehicle_plate):
    """Return True if the plate's permit has expired or its date is invalid."""
    try:
        expiry = datetime.strptime(permits[vehicle_plate]["expiry"],
                                   DATE_FORMAT)
    except (KeyError, ValueError):
        return True
    return expiry < datetime.now()


def scan_zone(permits, zone_id, plates_seen):
    """Return the plates seen that may not park in the given zone."""
    return [
        plate for plate in plates_seen
        if plate not in permits
        or permits[plate]["zone"] != zone_id
        or is_expired(permits, plate)
    ]


def load_permit_database(file="permits.json"):
    """Load permits from a JSON file, returning {} if it is missing or bad."""
    try:
        with open(file, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def save_permit_database(permits, file="permits.json"):
    """Write permits to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(permits, handle)


def set_expiry(permits, vehicle_plate, date_text):
    """Set a permit's expiry date; return False if the date or plate is bad."""
    try:
        datetime.strptime(date_text, DATE_FORMAT)
    except ValueError:
        print("Invalid date (use YYYY-MM-DD):", date_text)
        return False
    if vehicle_plate not in permits:
        print("No permit for:", vehicle_plate)
        return False
    permits[vehicle_plate]["expiry"] = date_text
    return True


def main():
    """Run a small demonstration of the permit manager."""
    permits = load_permit_database()
    register_permit(permits, "KA01AB1234", "A")
    register_permit(permits, "KA05XY9999", "Z")
    register_permit(permits, "", "B")
    register_permit(permits, None, "C")
    set_expiry(permits, "KA01AB1234", "2020-01-01")
    revoke_permit(permits, "MH12ZZ0000")
    print("Flagged in zone A:",
          scan_zone(permits, "A", ["KA01AB1234", "KA05XY9999", "TN09QQ1111"]))
    plate = input("Plate to revoke (Enter to skip): ").strip()
    if plate:
        revoke_permit(permits, plate)
    save_permit_database(permits)
    print("Permits on file:", len(permits))


if __name__ == "__main__":
    main()
