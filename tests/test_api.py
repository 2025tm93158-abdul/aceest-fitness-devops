"""Tests for the Flask endpoints."""

CLIENT = {"name": "Abdul", "age": 28, "height_cm": 175,
          "weight_kg": 70, "program": "FL"}


# ---------- general ----------
def test_home(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "ACEest" in resp.get_json()["message"]


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_unknown_route_returns_json_404(client):
    resp = client.get("/nope")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_wrong_method_returns_json_405(client):
    assert client.delete("/health").status_code == 405


# ---------- programs ----------
def test_list_programs(client):
    programs = client.get("/programs").get_json()["programs"]
    assert [p["code"] for p in programs] == ["BG", "FL", "MG"]


def test_program_detail_and_unknown(client):
    ok = client.get("/programs/mg")
    assert ok.status_code == 200
    assert ok.get_json()["calorie_factor"] == 35
    assert client.get("/programs/ZZ").status_code == 400


# ---------- clients ----------
def test_create_client_returns_calories_and_bmi(client):
    resp = client.post("/clients", json=CLIENT)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["id"] == 1
    assert body["calories"] == 1540
    assert body["bmi"] == 22.9
    assert body["bmi_category"] == "Normal"
    assert body["membership_status"] == "Active"


def test_duplicate_client_name_is_a_conflict(client, new_client):
    resp = client.post("/clients", json={**CLIENT, "name": "ABDUL"})
    assert resp.status_code == 409


def test_list_and_get_clients(client, new_client):
    assert len(client.get("/clients").get_json()["clients"]) == 1
    assert client.get("/clients/1").get_json()["name"] == "Abdul"


def test_get_missing_client_is_404(client):
    assert client.get("/clients/99").status_code == 404


def test_each_test_starts_with_an_empty_store(client):
    assert client.get("/clients").get_json()["clients"] == []


def test_create_client_needs_a_json_body(client):
    assert client.post("/clients", data="not json").status_code == 400


def test_create_client_validation(client):
    bad_inputs = [
        {**CLIENT, "name": "   "},
        {**CLIENT, "age": 5},
        {**CLIENT, "age": 28.5},
        {**CLIENT, "height_cm": 20},
        {**CLIENT, "weight_kg": "heavy"},
        {**CLIENT, "weight_kg": True},
        {**CLIENT, "program": "XX"},
    ]
    for payload in bad_inputs:
        assert client.post("/clients", json=payload).status_code == 400, payload
    missing = {k: v for k, v in CLIENT.items() if k != "program"}
    assert client.post("/clients", json=missing).status_code == 400


def test_client_bmi_endpoint(client, new_client):
    body = client.get("/clients/1/bmi").get_json()
    assert body["bmi"] == 22.9
    assert body["category"] == "Normal"
    assert body["risk_note"]


# ---------- membership ----------
def test_default_membership_is_active(client, new_client):
    body = client.get("/clients/1/membership").get_json()
    assert body == {"status": "Active", "renewal_date": "N/A",
                    "is_active": True}


def test_update_membership_with_future_date(client, new_client):
    resp = client.put("/clients/1/membership",
                      json={"status": "Active", "end_date": "2027-03-31"})
    assert resp.status_code == 200
    assert resp.get_json()["is_active"] is True
    assert client.get("/clients/1/membership").get_json()["renewal_date"] \
        == "2027-03-31"


def test_membership_with_past_date_is_not_active(client, new_client):
    client.put("/clients/1/membership",
               json={"status": "Active", "end_date": "2026-01-01"})
    assert client.get("/clients/1/membership").get_json()["is_active"] is False


def test_update_membership_validation(client, new_client):
    assert client.put("/clients/1/membership",
                      json={"status": "Gold"}).status_code == 400
    assert client.put("/clients/1/membership",
                      json={"status": "Active",
                            "end_date": "31/03/2027"}).status_code == 400
    assert client.put("/clients/99/membership",
                      json={"status": "Active"}).status_code == 404


# ---------- progress ----------
def test_progress_entries_and_average(client, new_client):
    for week, value in (("Week 1", 80), ("Week 2", 90)):
        resp = client.post("/clients/1/progress",
                           json={"week": week, "adherence": value})
        assert resp.status_code == 201
    body = client.get("/clients/1/progress").get_json()
    assert len(body["entries"]) == 2
    assert body["average_adherence"] == 85.0


def test_progress_validation(client, new_client):
    assert client.post("/clients/1/progress",
                       json={"week": "Week 1",
                             "adherence": 150}).status_code == 400
    assert client.post("/clients/1/progress",
                       json={"adherence": 50}).status_code == 400


def test_empty_progress_average_is_zero(client, new_client):
    assert client.get("/clients/1/progress").get_json()[
        "average_adherence"] == 0.0


# ---------- workouts ----------
def test_log_workouts_and_total_minutes(client, new_client):
    for day, minutes in (("2026-10-01", 45), ("2026-10-03", 30)):
        resp = client.post("/clients/1/workouts", json={
            "date": day, "workout_type": "Strength",
            "duration_min": minutes, "notes": "Leg day"})
        assert resp.status_code == 201
    body = client.get("/clients/1/workouts").get_json()
    assert len(body["workouts"]) == 2
    assert body["total_minutes"] == 75


def test_workout_validation(client, new_client):
    good = {"date": "2026-10-01", "workout_type": "Mixed",
            "duration_min": 40}
    for patch in ({"workout_type": "Dancing"}, {"date": "yesterday"},
                  {"duration_min": 0}, {"duration_min": "long"}):
        assert client.post("/clients/1/workouts",
                           json={**good, **patch}).status_code == 400, patch


# ---------- program generator ----------
def test_generate_program_for_client(client, new_client):
    resp = client.post("/clients/1/generate-program",
                       json={"program_type": "Muscle Gain"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["program_type"] == "Muscle Gain"
    assert body["plan"] in ("Push/Pull/Legs", "Upper/Lower Split",
                            "Full Body Strength")


def test_generate_program_without_body_picks_something(client, new_client):
    resp = client.post("/clients/1/generate-program")
    assert resp.status_code == 200
    assert resp.get_json()["plan"]


def test_generate_program_rejects_unknown_type(client, new_client):
    resp = client.post("/clients/1/generate-program",
                       json={"program_type": "Yoga"})
    assert resp.status_code == 400
