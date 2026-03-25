"""Waste collection schedule app for Cure Afvalbeheer (Eindhoven, Geldrop-Mierlo, Valkenswaard).

Fetches waste collection dates from the MijnAfvalwijzer API and displays them
in a user-friendly web interface.
"""

import re
from datetime import datetime

import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_URL = (
    "https://api.mijnafvalwijzer.nl/webservices/appsinput/"
    "?apikey=5ef443e778f41c4f75c69459eea6e6ae0c2d92de729aa0fc61653815fbd6a8ca"
    "&method=postcodecheck&postcode={postcode}&street="
    "&huisnummer={huisnummer}&toevoeging={toevoeging}"
    "&app_name=afvalwijzer&platform=web&langs=nl"
    "&afvaldata={startdate}"
)

WASTE_TYPE_ICONS = {
    "gft": {"label": "GFT", "icon": "🌿", "color": "#4CAF50"},
    "restafval": {"label": "Restafval", "icon": "🗑️", "color": "#757575"},
    "papier": {"label": "Papier", "icon": "📦", "color": "#2196F3"},
    "pmd": {"label": "PMD", "icon": "♻️", "color": "#FF9800"},
    "plastic": {"label": "Plastic", "icon": "♻️", "color": "#FF9800"},
    "textiel": {"label": "Textiel", "icon": "👕", "color": "#9C27B0"},
    "kerstbomen": {"label": "Kerstbomen", "icon": "🎄", "color": "#2E7D32"},
    "grof": {"label": "Grof afval", "icon": "🪑", "color": "#795548"},
}

DEFAULT_WASTE_INFO = {"label": "", "icon": "🗑️", "color": "#607D8B"}


def validate_postcode(postcode):
    """Validate Dutch postal code format (4 digits + 2 letters)."""
    cleaned = postcode.strip().replace(" ", "").upper()
    if re.match(r"^\d{4}[A-Z]{2}$", cleaned):
        return cleaned
    return None


def validate_huisnummer(huisnummer):
    """Validate house number (positive integer)."""
    cleaned = huisnummer.strip()
    if cleaned.isdigit() and int(cleaned) > 0:
        return cleaned
    return None


def fetch_waste_data(postcode, huisnummer, toevoeging=""):
    """Fetch waste collection data from MijnAfvalwijzer API."""
    today = datetime.now()
    start_date = f"{today.year}-01-01"

    url = API_URL.format(
        postcode=postcode,
        huisnummer=huisnummer,
        toevoeging=toevoeging,
        startdate=start_date,
    )

    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # Parse upcoming collection dates
    upcoming = []
    ophaaldagen = data.get("ophaaldagen", {}).get("data", [])
    ophaaldagen_next = data.get("ophaaldagenNext", {}).get("data", [])

    all_items = ophaaldagen + ophaaldagen_next

    for item in all_items:
        date_str = item.get("date", "")
        waste_type = item.get("type", "").lower().strip()
        if not date_str or not waste_type:
            continue

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        if date_obj.date() < today.date():
            continue

        info = WASTE_TYPE_ICONS.get(waste_type, DEFAULT_WASTE_INFO)
        label = info["label"] or waste_type.capitalize()

        upcoming.append({
            "date": date_obj.strftime("%Y-%m-%d"),
            "date_display": date_obj.strftime("%A %d %B %Y"),
            "type": waste_type,
            "label": label,
            "icon": info["icon"],
            "color": info["color"],
            "days_until": (date_obj.date() - today.date()).days,
        })

    # Remove duplicates and sort
    seen = set()
    unique = []
    for item in upcoming:
        key = (item["date"], item["type"])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    unique.sort(key=lambda x: (x["date"], x["type"]))
    return unique


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ophaaldata", methods=["GET"])
def get_ophaaldata():
    postcode = request.args.get("postcode", "")
    huisnummer = request.args.get("huisnummer", "")
    toevoeging = request.args.get("toevoeging", "")

    validated_postcode = validate_postcode(postcode)
    if not validated_postcode:
        return jsonify({"error": "Ongeldige postcode. Gebruik formaat: 1234AB"}), 400

    validated_huisnummer = validate_huisnummer(huisnummer)
    if not validated_huisnummer:
        return jsonify({"error": "Ongeldig huisnummer."}), 400

    try:
        data = fetch_waste_data(validated_postcode, validated_huisnummer, toevoeging)
    except requests.exceptions.RequestException:
        return jsonify({"error": "Kon geen verbinding maken met de afvalkalender service."}), 502
    except (ValueError, KeyError):
        return jsonify({"error": "Onverwacht antwoord van de service."}), 502

    if not data:
        return jsonify({
            "error": "Geen ophaaldata gevonden voor dit adres. "
                     "Controleer of de postcode in het gebied van Cure valt "
                     "(Eindhoven, Geldrop-Mierlo, Valkenswaard)."
        }), 404

    return jsonify({"data": data})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
