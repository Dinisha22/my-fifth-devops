import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import datetime

# -----------------------------
# 🔐 API Keys & City Mapping
# -----------------------------
OPENWEATHER_API_KEY = "0e760c50ccd7ca39c6d4971105870117"
WAQI_API_TOKEN = "YOUR_WAQI_API_TOKEN"  # Replace with your AQI token

CITY_MAP = {
    "Andhra Pradesh": "Vijayawada",
    "Telangana": "Hyderabad",
    "Tamil Nadu": "Chennai",
    "Karnataka": "Bengaluru",
    "Maharashtra": "Mumbai",
    "Delhi": "New Delhi",
    "West Bengal": "Kolkata",
    "Gujarat": "Ahmedabad",
    "Rajasthan": "Jaipur",
    "Punjab": "Ludhiana",
    "Bihar": "Patna",
    "Kerala": "Thiruvananthapuram",
    "Madhya Pradesh": "Bhopal",
    "Uttar Pradesh": "Lucknow",
    "Odisha": "Bhubaneswar",
    "Jharkhand": "Ranchi",
    "Assam": "Guwahati",
    "Chhattisgarh": "Raipur",
    "Haryana": "Chandigarh",
    "Himachal Pradesh": "Shimla",
    "Uttarakhand": "Dehradun",
    "Goa": "Panaji",
    "Manipur": "Imphal",
    "Meghalaya": "Shillong",
    "Mizoram": "Aizawl",
    "Nagaland": "Kohima",
    "Tripura": "Agartala",
    "Sikkim": "Gangtok",
    "Arunachal Pradesh": "Itanagar"
}

# -----------------------------
# 🌤 Weather Utilities
# -----------------------------
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Could not fetch weather data."}
    data = response.json()
    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "description": data["weather"][0]["description"],
        "clouds": data["clouds"]["all"],
        "sunrise": data["sys"]["sunrise"],
        "sunset": data["sys"]["sunset"],
        "timezone": data["timezone"],
        "rainfall": data.get("rain", {}).get("1h", 0),
        "alerts": data.get("alerts", [])
    }

def format_unix_time(timestamp, timezone_offset):
    local_time = datetime.datetime.utcfromtimestamp(timestamp + timezone_offset)
    return local_time.strftime("%I:%M %p")

def moon_phase():
    today = datetime.datetime.now()
    diff = today - datetime.datetime(today.year, 1, 1)
    days = diff.days + 1
    lunation = 29.53058867
    phase_index = int((days % lunation) / lunation * 8)
    phases = [
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"
    ]
    return phases[phase_index]

def get_aqi(city):
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={WAQI_API_TOKEN}"
        response = requests.get(url)
        data = response.json()
        if data["status"] == "ok":
            return data["data"]["aqi"], data["data"].get("dominentpol", "")
        else:
            return None, None
    except:
        return None, None

def personalized_advice(temp, humidity, rainfall):
    tips = []
    if temp > 35:
        tips.append("Stay hydrated and avoid going out in the afternoon.")
    elif temp < 10:
        tips.append("Wear warm clothes and stay indoors if possible.")
    if humidity > 80:
        tips.append("High humidity! Avoid strenuous activity.")
    if rainfall > 0:
        tips.append("Carry an umbrella. Roads might be slippery.")
    if not tips:
        tips.append("Weather looks good. Have a great day!")
    return tips

# -----------------------------
# 📊 Chart plotting functions
# -----------------------------
def plot_chart(data, labels, chart_type, title, xlabel, ylabel):
    plt.figure(figsize=(8,4))
    if chart_type == "line":
        plt.plot(labels, data, marker='o')
    elif chart_type == "bar":
        plt.bar(labels, data)
    elif chart_type == "scatter":
        plt.scatter(labels, data)
    elif chart_type == "pie":
        plt.pie(data, labels=labels, autopct='%1.1f%%')
    else:
        st.error(f"Chart type '{chart_type}' not supported.")
        return
    plt.title(title)
    if chart_type != "pie":
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()

# -----------------------------
# 💬 AtmosAI Chat UI
# -----------------------------
st.title("🌍 AtmosAI — Smart Weather Assistant")

user_input = st.text_input("💬 Ask me anything about weather in India:")

def extract_chart_type(text):
    chart_keywords = ["line", "bar", "scatter", "pie"]
    for kw in chart_keywords:
        if kw in text:
            return kw
    return None

def extract_parameter(text):
    parameters = ["temperature", "humidity", "pressure", "cloud", "rainfall", "rain"]
    for param in parameters:
        if param in text:
            return param
    return None

def extract_states(text):
    found_states = []
    for state in CITY_MAP.keys():
        if state.lower() in text:
            found_states.append(state)
    return found_states

if user_input:
    lowered = user_input.lower()
    matched_states = extract_states(lowered)
    chart_type = extract_chart_type(lowered)
    param = extract_parameter(lowered)

    if not matched_states:
        st.warning("🤖 I couldn't identify any Indian state in your prompt. Try again.")
    else:
        if len(matched_states) == 1:
            state = matched_states[0]
            city = CITY_MAP[state]
            weather = get_weather(city)
            if "error" in weather:
                st.error(weather["error"])
            else:
                st.subheader(f"📍 {state} — {weather['description'].capitalize()}")

                # Show raw data if asked
                if param:
                    # Map param to weather keys
                    weather_map = {
                        "temperature": weather["temperature"],
                        "humidity": weather["humidity"],
                        "pressure": weather["pressure"],
                        "cloud": weather["clouds"],
                        "rainfall": weather["rainfall"],
                        "rain": weather["rainfall"]
                    }
                    value = weather_map.get(param, None)
                    if value is not None:
                        st.write(f"🌡️ {param.capitalize()}: {value} {'°C' if param=='temperature' else '%' if param in ['humidity', 'cloud'] else 'hPa' if param=='pressure' else 'mm'}")

                # Show charts if asked
                if chart_type and param:
                    # For demonstration: generate dummy last 7 days data with some noise
                    base_value = weather_map.get(param, 0)
                    labels = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%a") for i in reversed(range(7))]
                    data = [max(base_value + (i - 3)*2 + np.random.randn(), 0) for i in range(7)]
                    title = f"{param.capitalize()} in {state} - Last 7 Days"
                    plot_chart(data, labels, chart_type, title, "Day", param.capitalize())

                # Show other details on demand
                if any(x in lowered for x in ["humidity", "pressure", "cloud", "sunrise", "sunset", "moon", "aqi", "alert", "tip", "advice", "suggestion"]):
                    if "humidity" in lowered:
                        st.write(f"💧 Humidity: {weather['humidity']} %")
                    if "pressure" in lowered:
                        st.write(f"🔵 Pressure: {weather['pressure']} hPa")
                    if "cloud" in lowered:
                        st.write(f"☁️ Cloud Coverage: {weather['clouds']} %")
                    if "sunrise" in lowered:
                        st.write(f"🌅 Sunrise: {format_unix_time(weather['sunrise'], weather['timezone'])}")
                    if "sunset" in lowered:
                        st.write(f"🌇 Sunset: {format_unix_time(weather['sunset'], weather['timezone'])}")
                    if "moon" in lowered:
                        st.write(f"🌙 Moon Phase: {moon_phase()}")
                    if "aqi" in lowered or "air" in lowered:
                        aqi, dom_pol = get_aqi(city)
                        if aqi:
                            st.write(f"🏣 AQI: {aqi} (Dominant Pollutant: {dom_pol.upper()})")
                    if "alert" in lowered:
                        if weather.get("alerts"):
                            st.warning("⚠️ Weather Alerts:")
                            for alert in weather["alerts"]:
                                st.write(f"- {alert.get('event', 'Alert')} from {alert.get('start')} to {alert.get('end')}")
                        else:
                            st.write("✅ No active weather alerts.")
                    if any(x in lowered for x in ["tip", "advice", "suggestion"]):
                        advice = personalized_advice(weather["temperature"], weather["humidity"], weather["rainfall"])
                        st.info("💡 Weather Tips:")
                        for tip in advice:
                            st.write(f"- {tip}")

        elif len(matched_states) > 1:
            # Compare multiple states for a parameter in a chart
            if param and chart_type:
                data = []
                labels = []
                for state in matched_states:
                    city = CITY_MAP[state]
                    weather = get_weather(city)
                    if "error" not in weather:
                        labels.append(state)
                        weather_map = {
                            "temperature": weather["temperature"],
                            "humidity": weather["humidity"],
                            "pressure": weather["pressure"],
                            "cloud": weather["clouds"],
                            "rainfall": weather["rainfall"],
                            "rain": weather["rainfall"]
                        }
                        data.append(weather_map.get(param, 0))
                if data and labels:
                    title = f"{param.capitalize()} Comparison"
                    plot_chart(data, labels, chart_type, title, "State", param.capitalize())
                else:
                    st.error("Could not fetch data for comparison.")
            else:
                st.info("Please specify parameter and chart type to compare multiple states.")

        else:
            st.info("Please mention at least one valid Indian state.")

# -----------------------------
# 📍 Quick Weather Block (No Prompt)
# -----------------------------
st.markdown("---")
st.subheader("📍 Quick Live Weather (No Prompt Needed)")
selected_state = st.selectbox("Select a state to instantly view weather", ["-- Select --"] + list(CITY_MAP.keys()))

if selected_state and selected_state != "-- Select --":
    city = CITY_MAP[selected_state]
    weather = get_weather(city)
    if "error" in weather:
        st.error(weather["error"])
    else:
        st.subheader(f"📍 {selected_state} — {weather['description'].capitalize()}")
        st.write(f"🌡️ Temperature: {weather['temperature']} °C")
        st.write(f"💧 Humidity: {weather['humidity']} %")
        st.write(f"🔵 Pressure: {weather['pressure']} hPa")
        st.write(f"☔️ Rainfall (last hour): {weather['rainfall']} mm")
        st.write(f"★️ Cloud Coverage: {weather['clouds']} %")
        st.write(f"🌙 Moon Phase: {moon_phase()}")
        st.write(f"🌅 Sunrise: {format_unix_time(weather['sunrise'], weather['timezone'])}")
        st.write(f"🌇 Sunset: {format_unix_time(weather['sunset'], weather['timezone'])}")

        aqi, dom_pol = get_aqi(city)
        if aqi:
            st.write(f"🏣 AQI: {aqi} (Dominant Pollutant: {dom_pol.upper()})")

        if weather.get("alerts"):
            st.warning("⚠️ Weather Alerts:")
            for alert in weather["alerts"]:
                st.write(f"- {alert.get('event', 'Alert')} from {alert.get('start')} to {alert.get('end')}")

        advice = personalized_advice(weather["temperature"], weather["humidity"], weather["rainfall"])
        st.info("💡 Weather Tips:")
        for tip in advice:
            st.write(f"- {tip}")

# -----------------------------
# ⭐ Favorites Section
# -----------------------------
st.markdown("---")
st.subheader("⭐ Favorites")
favorite_states = st.multiselect("Select your favorite states:", list(CITY_MAP.keys()))
if st.button("📌 Show Live Weather for Favorites"):
    if favorite_states:
        for state in favorite_states:
            city = CITY_MAP[state]
            weather = get_weather(city)
            if "error" in weather:
                st.error(f"{state}: {weather['error']}")
            else:
                st.markdown(f"---\n### 📍 {state}")
                st.write(f"🌡️ Temperature: {weather['temperature']} °C")
                st.write(f"💧 Humidity: {weather['humidity']} %")
                st.write(f"🔵 Pressure: {weather['pressure']} hPa")
                st.write(f"☁️ Cloud Coverage: {weather['clouds']} %")
                aqi, dom_pol = get_aqi(city)
                if aqi:
                    st.write(f"🏣 AQI: {aqi} (Dominant Pollutant: {dom_pol.upper()})")
    else:
        st.info("Please select at least one state to show favorites.")
