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


# --- input validation: both operands of the `or` and the pass-through ---
def test_single_regular_local_ride():
    result = process_commute_manifest([make_manifest(commuters=[commuter(2)])], 2.0)
    assert result == {"total_fare": 4.5, "status": "COMPLETED"}


def test_manifests_not_a_list_raises():
    with pytest.raises(ValueError):
        process_commute_manifest("not a list", 1.0)


def test_negative_booking_fee_raises():
    with pytest.raises(ValueError):
        process_commute_manifest([], -1.0)


def test_empty_manifest_list_is_zero_ridership():
    assert process_commute_manifest([], 1.0) == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


# --- route_active true / false ---
def test_inactive_route_skipped():
    result = process_commute_manifest([make_manifest(active=False, commuters=[commuter()])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_missing_route_active_defaults_to_inactive():
    result = process_commute_manifest([{"commuters": [commuter()]}], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


# --- route_type: express / shuttle / local / unknown ---
def test_express_regular():
    result = process_commute_manifest([make_manifest("express", [commuter(2)])], 1.0)
    assert result["total_fare"] == 8.0


def test_shuttle_regular():
    result = process_commute_manifest([make_manifest("shuttle", [commuter(2)])], 1.0)
    assert result["total_fare"] == 6.0


def test_missing_route_type_defaults_to_local():
    manifest = {"route_active": True, "commuters": [commuter(2)]}
    assert process_commute_manifest([manifest], 1.0)["total_fare"] == 4.5


def test_unknown_route_type_rejected():
    result = process_commute_manifest([make_manifest("ferry", [commuter()])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


# --- passenger types: student / senior / regular ---
def test_student_fare():
    result = process_commute_manifest([make_manifest("express", [commuter(2, "student")])], 1.0)
    assert result["total_fare"] == 3.5


def test_senior_fare():
    result = process_commute_manifest([make_manifest("shuttle", [commuter(2, "senior")])], 1.0)
    assert result["total_fare"] == pytest.approx(3.5)


def test_unknown_passenger_type_charged_regular():
    result = process_commute_manifest([make_manifest("local", [commuter(2, "tourist")])], 1.0)
    assert result["total_fare"] == 4.5


def test_commuter_defaults_when_keys_missing():
    result = process_commute_manifest([make_manifest("local", [{}])], 1.0)
    assert result["total_fare"] == 3.5


# --- zones <= 0 ---
def test_zero_zones_rejected():
    result = process_commute_manifest([make_manifest(commuters=[commuter(0)])], 1.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_negative_zones_rejected():
    result = process_commute_manifest([make_manifest(commuters=[commuter(-2), commuter(1)])], 1.0)
    assert result["total_fare"] == 3.5


# --- blacklisted: express (break) vs non-express (continue) ---
def test_blacklisted_on_express_voids_manifest():
    commuters = [commuter(1), commuter(1, blacklisted=True), commuter(1)]
    result = process_commute_manifest([make_manifest("express", commuters)], 1.0)
    assert result["total_fare"] == 0.0


def test_blacklisted_on_local_skips_only_that_commuter():
    commuters = [commuter(1, blacklisted=True), commuter(2)]
    result = process_commute_manifest([make_manifest("local", commuters)], 1.0)
    assert result["total_fare"] == 4.5


# --- priority boarding true / false ---
def test_priority_boarding_adds_fee():
    result = process_commute_manifest([make_manifest(commuters=[commuter(2)], priority=True)], 2.0)
    assert result["total_fare"] == 6.5


def test_no_priority_boarding_no_fee():
    result = process_commute_manifest([make_manifest(commuters=[commuter(2)], priority=False)], 2.0)
    assert result["total_fare"] == 4.5


def test_missing_priority_boarding_defaults_false():
    manifest = {"route_active": True, "route_type": "local", "commuters": [commuter(2)]}
    assert process_commute_manifest([manifest], 5.0)["total_fare"] == 4.5


# --- final status: audit rejected / zero / completed ---
def test_audit_rejected_over_four_rejections():
    commuters = [commuter(0) for _ in range(5)] + [commuter(1)]
    result = process_commute_manifest([make_manifest("local", commuters)], 1.0)
    assert result == {"total_fare": 3.5, "status": "AUDIT_REJECTED"}


def test_exactly_four_rejections_not_audited():
    commuters = [commuter(0) for _ in range(4)] + [commuter(1)]
    result = process_commute_manifest([make_manifest("local", commuters)], 1.0)
    assert result["status"] == "COMPLETED"


def test_multiple_manifests_accumulate():
    manifests = [make_manifest("local", [commuter(2)]), make_manifest("shuttle", [commuter(1)])]
    assert process_commute_manifest(manifests, 1.0)["total_fare"] == 9.5


# --- turnstiles ---
def test_turnstiles_empty_is_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstiles_none_is_no_data():
    assert inspect_smartcard_turnstiles(None) == "NO_DATA"


def test_turnstiles_two_consecutive_failures_jam():
    assert inspect_smartcard_turnstiles([[0, 4, 5]]) == "TURNSTILE_JAM"


def test_turnstiles_streak_reset_is_operational():
    assert inspect_smartcard_turnstiles([[4, 0, 4, 0], [1, 2]]) == "OPERATIONAL"


def test_turnstiles_jam_found_on_later_device():
    assert inspect_smartcard_turnstiles([[0, 0], [5, 5]]) == "TURNSTILE_JAM"


def test_turnstiles_empty_device_reading():
    assert inspect_smartcard_turnstiles([[]]) == "OPERATIONAL"
