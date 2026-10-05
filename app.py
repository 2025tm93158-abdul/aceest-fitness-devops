"""ACEest Fitness & Gym - Flask web application."""
from datetime import date

from flask import Flask, jsonify, request

import fitness
from fitness import ValidationError

APP_VERSION = "1.0.0"


def create_app(config=None):
    """Application factory. Each app gets its own empty in-memory store."""
    app = Flask(__name__)
    app.config.update(TESTING=False)
    if config:
        app.config.update(config)

    store = {"clients": {}, "next_id": 1}

    # ---------- helpers ----------
    def today():
        return app.config.get("TODAY") or date.today()

    def json_body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ValidationError("request body must be a JSON object")
        return data

    def number(data, field, low, high, whole=False):
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(field + " must be a number")
        if whole and int(value) != value:
            raise ValidationError(field + " must be a whole number")
        if not low <= value <= high:
            raise ValidationError(
                "{} must be between {} and {}".format(field, low, high)
            )
        return int(value) if whole else value

    def text(data, field, max_len=50):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(field + " is required")
        value = value.strip()
        if len(value) > max_len:
            raise ValidationError(
                "{} must be at most {} characters".format(field, max_len)
            )
        return value

    def get_client(client_id):
        client = store["clients"].get(client_id)
        if client is None:
            raise LookupError("client {} not found".format(client_id))
        return client

    def client_view(client):
        bmi, category, _ = fitness.calculate_bmi(
            client["weight_kg"], client["height_cm"]
        )
        view = {k: v for k, v in client.items()
                if k not in ("progress", "workouts")}
        view["calories"] = fitness.calculate_calories(
            client["weight_kg"], client["program"]
        )
        view["bmi"] = bmi
        view["bmi_category"] = category
        return view

    # ---------- error handlers ----------
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify(error=str(err)), 400

    @app.errorhandler(LookupError)
    def handle_not_found(err):
        return jsonify(error=str(err.args[0])), 404

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify(error="resource not found"), 404

    @app.errorhandler(405)
    def handle_405(_err):
        return jsonify(error="method not allowed"), 405

    # ---------- general ----------
    @app.route("/")
    def home():
        return jsonify(
            message="Welcome to ACEest Fitness & Gym",
            version=APP_VERSION,
        )

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    # ---------- programs ----------
    @app.route("/programs")
    def list_programs():
        return jsonify(
            programs=[dict(code=code, **p)
                      for code, p in sorted(fitness.PROGRAMS.items())]
        )

    @app.route("/programs/<code>")
    def program_detail(code):
        key, program = fitness.get_program(code)
        return jsonify(code=key, **program)

    # ---------- clients ----------
    @app.route("/clients", methods=["POST"])
    def create_client():
        data = json_body()
        name = text(data, "name")
        if any(c["name"].lower() == name.lower()
               for c in store["clients"].values()):
            return jsonify(error="client '{}' already exists".format(name)), 409
        code, _ = fitness.get_program(data.get("program", ""))
        client = {
            "id": store["next_id"],
            "name": name,
            "age": number(data, "age", 10, 100, whole=True),
            "height_cm": number(data, "height_cm", 100, 250),
            "weight_kg": number(data, "weight_kg", 20, 300),
            "program": code,
            "membership_status": "Active",
            "membership_end": None,
            "progress": [],
            "workouts": [],
        }
        store["clients"][client["id"]] = client
        store["next_id"] += 1
        return jsonify(client_view(client)), 201

    @app.route("/clients")
    def list_clients():
        return jsonify(
            clients=[client_view(c) for c in store["clients"].values()]
        )

    @app.route("/clients/<int:client_id>")
    def client_detail(client_id):
        return jsonify(client_view(get_client(client_id)))

    @app.route("/clients/<int:client_id>/bmi")
    def client_bmi(client_id):
        client = get_client(client_id)
        bmi, category, risk = fitness.calculate_bmi(
            client["weight_kg"], client["height_cm"]
        )
        return jsonify(client=client["name"], bmi=bmi,
                       category=category, risk_note=risk)

    # ---------- membership ----------
    @app.route("/clients/<int:client_id>/membership")
    def get_membership(client_id):
        client = get_client(client_id)
        return jsonify(fitness.check_membership(
            client["membership_status"], client["membership_end"], today()
        ))

    @app.route("/clients/<int:client_id>/membership", methods=["PUT"])
    def update_membership(client_id):
        client = get_client(client_id)
        data = json_body()
        status = data.get("status")
        if status not in fitness.MEMBERSHIP_STATUSES:
            raise ValidationError(
                "status must be one of: "
                + ", ".join(fitness.MEMBERSHIP_STATUSES)
            )
        end = data.get("end_date")
        if end is not None:
            fitness.parse_date(end, "end_date")
        client["membership_status"] = status
        client["membership_end"] = end
        return jsonify(fitness.check_membership(status, end, today()))

    # ---------- weekly progress ----------
    @app.route("/clients/<int:client_id>/progress", methods=["POST"])
    def add_progress(client_id):
        client = get_client(client_id)
        data = json_body()
        entry = {
            "week": text(data, "week", 20),
            "adherence": fitness.validate_adherence(data.get("adherence")),
        }
        client["progress"].append(entry)
        return jsonify(entry), 201

    @app.route("/clients/<int:client_id>/progress")
    def get_progress(client_id):
        client = get_client(client_id)
        return jsonify(
            entries=client["progress"],
            average_adherence=fitness.average_adherence(client["progress"]),
        )

    # ---------- workouts ----------
    @app.route("/clients/<int:client_id>/workouts", methods=["POST"])
    def add_workout(client_id):
        client = get_client(client_id)
        data = json_body()
        workout_type = data.get("workout_type")
        if workout_type not in fitness.WORKOUT_TYPES:
            raise ValidationError(
                "workout_type must be one of: "
                + ", ".join(fitness.WORKOUT_TYPES)
            )
        day = data.get("date")
        fitness.parse_date(day, "date")
        workout = {
            "date": day,
            "workout_type": workout_type,
            "duration_min": number(data, "duration_min", 1, 600, whole=True),
            "notes": str(data.get("notes", ""))[:200],
        }
        client["workouts"].append(workout)
        return jsonify(workout), 201

    @app.route("/clients/<int:client_id>/workouts")
    def get_workouts(client_id):
        client = get_client(client_id)
        return jsonify(
            workouts=client["workouts"],
            total_minutes=sum(w["duration_min"] for w in client["workouts"]),
        )

    # ---------- program generator ----------
    @app.route("/clients/<int:client_id>/generate-program", methods=["POST"])
    def generate_client_program(client_id):
        client = get_client(client_id)
        data = request.get_json(silent=True) or {}
        program_type, plan = fitness.generate_program(data.get("program_type"))
        client["generated_plan"] = plan
        return jsonify(client=client["name"], program_type=program_type,
                       plan=plan)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
