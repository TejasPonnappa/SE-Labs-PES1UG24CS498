import math

def parse_transit_corridor(corridor_code):
    if not isinstance(corridor_code, str):
        return "Invalid corridor code"
    parts = corridor_code.strip().split('-')
    if len(parts) != 3:
        return "Invalid corridor code"
    orig, dest, zones_str = (p.strip() for p in parts)
    if not orig or not dest:
        return "Invalid corridor code"
    try:
        zones = int(zones_str)
    except ValueError:
        return "Invalid corridor code"
    if zones <= 0:
        return "Invalid corridor code"
    base_fare = 2.50 + (zones * 0.75)
    return f"Route {orig.upper()}->{dest.upper()}: {zones} Zones, Fare ${base_fare:.2f}"

def lookup_concession_discount(category_name):
    if not isinstance(category_name, str):
        return None
    category = category_name.strip().upper()
    discounts = {
        "STANDARD": 1.00,
        "STUDENT": 0.50,
        "SENIOR": 0.35,
        "MILITARY": 0.20,
        "CHILD": 0.00
    }
    return discounts.get(category)

def compute_passenger_density(occupancy_ratio_str):
    if not isinstance(occupancy_ratio_str, str):
        return None
    parts = occupancy_ratio_str.split('/')
    if len(parts) != 2:
        return None
    try:
        passengers = float(parts[0])
        km = float(parts[1])
        density = passengers / km
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
    if not math.isfinite(density):
        return None
    return round(density, 2)

def main():
    print("==== Running parse_transit_corridor ====")
    c_input = input("Enter corridor (e.g. DT-UP-3): ")
    print(parse_transit_corridor(c_input))

    print("\n==== Running lookup_concession_discount ====")
    cat_input = input("Enter concession category (e.g. STUDENT, SENIOR): ")
    result = lookup_concession_discount(cat_input)
    print("Multiplier:", result if result is not None else "Unknown category")

    print("\n==== Running compute_passenger_density ====")
    d_input = input("Enter passengers/km (e.g. 50/10.0): ")
    result = compute_passenger_density(d_input)
    print("Density:", result if result is not None else "Invalid input")

if __name__ == "__main__":
    main()
