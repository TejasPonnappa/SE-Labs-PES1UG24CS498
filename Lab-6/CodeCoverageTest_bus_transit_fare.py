import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def make_manifest(route_type="local", commuters=None, active=True, priority=False):
    return {
        "route_active": active,
        "route_type": route_type,
        "priority_boarding": priority,
        "commuters": commuters if commuters is not None else [],
    }


def commuter(zones=1, ptype="regular", blacklisted=False):
    return {"zones": zones, "type": ptype, "blacklisted": blacklisted}


def test_single_regular_local_ride():
    result = process_commute_manifest([make_manifest(commuters=[commuter(2)])], 2.0)
    assert result["total_fare"] == 4.5
    assert result["status"] == "COMPLETED"


def test_invalid_manifests_type_raises():
    with pytest.raises(ValueError):
        process_commute_manifest("not a list", 1.0)


def test_inactive_route_skipped():
    result = process_commute_manifest([make_manifest(active=False, commuters=[commuter()])], 1.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_student_express_fare():
    result = process_commute_manifest([make_manifest("express", [commuter(2, "student")])], 1.0)
    assert result["total_fare"] == 3.5


def test_senior_shuttle_fare():
    result = process_commute_manifest([make_manifest("shuttle", [commuter(2, "senior")])], 1.0)
    assert result["total_fare"] == pytest.approx(3.5)


def test_priority_boarding_adds_booking_fee():
    result = process_commute_manifest([make_manifest(commuters=[commuter(2)], priority=True)], 2.0)
    assert result["total_fare"] == 6.5


def test_unknown_route_type_rejected():
    result = process_commute_manifest([make_manifest("ferry", [commuter()])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_zero_zones_rejected():
    result = process_commute_manifest([make_manifest(commuters=[commuter(0)])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_on_express_voids_manifest():
    commuters = [commuter(1), commuter(1, blacklisted=True), commuter(1)]
    result = process_commute_manifest([make_manifest("express", commuters)], 1.0)
    assert result["total_fare"] == 0.0


def test_blacklisted_on_local_only_skips_that_commuter():
    commuters = [commuter(1, blacklisted=True), commuter(2)]
    result = process_commute_manifest([make_manifest("local", commuters)], 1.0)
    assert result["total_fare"] == 4.5


def test_audit_rejected_when_more_than_four_rejections():
    commuters = [commuter(0) for _ in range(5)] + [commuter(1)]
    result = process_commute_manifest([make_manifest("local", commuters)], 1.0)
    assert result == {"total_fare": 3.5, "status": "AUDIT_REJECTED"}


def test_turnstiles_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstiles_jam():
    assert inspect_smartcard_turnstiles([[0, 4, 5]]) == "TURNSTILE_JAM"


def test_turnstiles_operational():
    assert inspect_smartcard_turnstiles([[4, 0, 4, 0], [1, 2]]) == "OPERATIONAL"
