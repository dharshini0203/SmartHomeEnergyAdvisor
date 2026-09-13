from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "energy.db"


def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appliances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appliance TEXT NOT NULL,
            power REAL NOT NULL,
            hours REAL NOT NULL,
            days INTEGER NOT NULL,
            units REAL NOT NULL,
            cost REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_recommendation(appliance, units):
    appliance = appliance.lower()

    if "ac" in appliance or "air conditioner" in appliance:
        return "Reduce AC usage by 1 hour per day and use an energy-efficient temperature setting."

    if "heater" in appliance:
        return "Reduce heater operating time and use an energy-efficient temperature setting."

    if "refrigerator" in appliance or "fridge" in appliance:
        return "Avoid frequent door opening and check that the refrigerator temperature is properly set."

    if "fan" in appliance:
        return "Use the fan at an appropriate speed and switch it off when the room is not occupied."

    if "light" in appliance:
        return "Switch off unnecessary lights and consider using LED bulbs."

    if "tv" in appliance or "television" in appliance:
        return "Switch off the TV completely instead of leaving it on standby."

    if "washing" in appliance:
        return "Run the washing machine with full loads and use eco mode when available."

    if "computer" in appliance or "laptop" in appliance:
        return "Enable power-saving mode and switch off the computer when it is not needed."

    return "Reduce unnecessary usage and consider choosing an energy-efficient appliance."


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():

    data = request.get_json()

    appliances = data.get("appliances", [])
    tariff = float(data.get("tariff", 8))

    total_units = 0
    total_cost = 0
    appliance_results = []

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for item in appliances:

        appliance = item["appliance"]
        power = float(item["power"])
        hours = float(item["hours"])
        days = int(item["days"])

        # Energy calculation
        units = (power * hours * days) / 1000

        # Cost calculation
        cost = units * tariff

        total_units += units
        total_cost += cost

        recommendation = get_recommendation(appliance, units)

        appliance_results.append({
            "appliance": appliance,
            "power": power,
            "hours": hours,
            "days": days,
            "units": round(units, 2),
            "cost": round(cost, 2),
            "recommendation": recommendation
        })

        cursor.execute("""
            INSERT INTO appliances
            (appliance, power, hours, days, units, cost)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            appliance,
            power,
            hours,
            days,
            units,
            cost
        ))

    conn.commit()
    conn.close()

    highest = None

    if appliance_results:
        highest = max(
            appliance_results,
            key=lambda x: x["units"]
        )

    return jsonify({
        "total_units": round(total_units, 2),
        "total_cost": round(total_cost, 2),
        "highest_consumer": highest,
        "appliances": appliance_results
    })


@app.route("/history")
def history():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    records = conn.execute("""
        SELECT * FROM appliances
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(record) for record in records])


if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )