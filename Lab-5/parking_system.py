import json
import random
from datetime import datetime, timedelta

# Global state
permits = {}
ZONES = ["A", "B", "C"]

def register_permit(vehicle_plate, zone_id, zone_records=[]):
    try:
        permit_no = "P" + str(random.randint(10000, 99999))
        expiry = datetime.now() + timedelta(days=180)
        permits[vehicle_plate] = {"zone": zone_id, "permit": permit_no, "expiry": expiry.strftime("%Y-%m-%d")}
        zone_records.append((vehicle_plate, zone_id))
        return permit_no
    except:
        return None

def revoke_permit(vehicle_plate):
    try:
        del permits[vehicle_plate]
    except:
        pass

def is_expired(vehicle_plate):
    try:
        expiry = datetime.strptime(permits[vehicle_plate]["expiry"], "%Y-%m-%d")
        return expiry < datetime.now()
    except:
        return False

def scan_zone(zone_id, plates_seen):
    flagged = []
    for p in plates_seen:
        if p not in permits or permits[p]["zone"] != zone_id or is_expired(p):
            flagged.append(p)
    return flagged

def load_permit_database(file="permits.json"):
    global permits
    try:
        permits = json.load(open(file))
    except:
        permits = {}

def save_permit_database(file="permits.json"):
    f = open(file, "w")
    json.dump(permits, f)
    f.close()

def setExpiry(vehicle_plate, date_text):
    permits[vehicle_plate]["expiry"] = date_text

def main():
    load_permit_database()
    register_permit("KA01AB1234", "A")
    register_permit("KA05XY9999", "Z")
    register_permit("", "B")
    register_permit(None, "C")
    setExpiry("KA01AB1234", "01/01/2020")
    revoke_permit("MH12ZZ0000")
    print("Flagged in zone A:", scan_zone("A", ["KA01AB1234", "KA05XY9999", "TN09QQ1111"]))
    plate = input("Plate to revoke (Enter to skip): ")
    revoke_permit(plate)
    save_permit_database()
    print("Permits on file:", len(permits))

main()
