import os
import pandas as pd
import streamlit as st

from app.agents.graph import build_graph


os.environ["DISABLE_LLM"] = "true"


def run_search(criteria):
    graph = build_graph()

    state = {
        "criteria": criteria,
        "preferences": None,
        "plan": "",
        "google_flights_results": None,
        "expedia_results": None,
        "kayak_results": None,
        "merged_results": None,
        "search_results": [],
        "validated_results": None,
        "scored_results": None,
        "recommendation": "",
        "report": "",
        "next_agent": "",
        "errors": [],
        "completed": False,
    }

    return graph.invoke(state)


st.set_page_config(
    page_title="FlightFinder Multi-Agent AI",
    layout="wide",
)

st.title("FlightFinder Multi-Agent AI")
st.caption("LangGraph + Ollama + Multi-Agent Flight Search")

st.sidebar.header("Search Criteria")

origin = st.sidebar.text_input("Origin", "SFO")
destination = st.sidebar.text_input("Destination", "JFK")
depart_date = st.sidebar.date_input("Departure Date")
passengers = st.sidebar.number_input("Passengers", min_value=1, value=1)

max_price = st.sidebar.slider("Max Price", 100, 2000, 550, 50)
max_stops = st.sidebar.selectbox("Max Stops", [0, 1, 2], index=1)
required_checked_bags = st.sidebar.selectbox("Required Checked Bags", [0, 1, 2], index=0)

preferred_airlines = st.sidebar.multiselect(
    "Preferred Airlines",
    ["United", "Delta", "American", "JetBlue", "Alaska"],
    default=["United", "Delta"],
)

avoid_airlines = st.sidebar.multiselect(
    "Avoid Airlines",
    ["Spirit", "Frontier", "Allegiant"],
    default=["Spirit", "Frontier"],
)

prefer_nonstop = st.sidebar.checkbox("Prefer Nonstop", value=True)
redeye_allowed = st.sidebar.checkbox("Redeye Allowed", value=False)

max_layover_minutes = st.sidebar.slider(
    "Max Layover Minutes",
    30,
    300,
    120,
    15,
)

criteria = {
    "origin": origin.upper(),
    "destination": destination.upper(),
    "depart_date": str(depart_date),
    "return_date": None,
    "passengers": passengers,
    "max_price": max_price,
    "max_stops": max_stops,
    "required_checked_bags": required_checked_bags,
    "preferred_airlines": preferred_airlines,
    "avoid_airlines": avoid_airlines,
    "prefer_nonstop": prefer_nonstop,
    "max_layover_minutes": max_layover_minutes,
    "redeye_allowed": redeye_allowed,
}

if st.sidebar.button("Search Flights"):
    result = run_search(criteria)
    st.session_state["result"] = result

if "result" not in st.session_state:
    result = run_search(criteria)
    st.session_state["result"] = result
else:
    result = st.session_state["result"]

st.info(
    f"Searching {criteria['origin']} → {criteria['destination']} "
    f"on {criteria['depart_date']} | "
    f"Passengers: {criteria['passengers']} | "
    f"Max Price: ${criteria['max_price']} | "
    f"Max Stops: {criteria['max_stops']}"
)

flights = result["scored_results"]
best = flights[0]
alternatives = flights[1:]

st.subheader("Best Flight")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Airline", best["airline"])
col2.metric("Price", f"${best['price']}")
col3.metric("Stops", best["stops"])
col4.metric("Score", f"{best['overall_score']}/100")

st.write("## Best Flight Analysis")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Flight Summary")

    st.markdown(f"""
**Airline:** {best["airline"]}  
**Flight Number:** {best["flight_number"]}  
**Aircraft Model:** {best["aircraft_model"]}  

**Route:** {" -> ".join([x["airport"] for x in best["route"]])}

**Origin Airport:**  
{best["origin_airport_name"]}

**Destination Airport:**  
{best["destination_airport_name"]}

**Departure:**  
{best["departure_date_time"]}

**Arrival:**  
{best["arrival_date_time"]}

**Duration:** {best["duration_minutes"]} minutes

**Status:** {best["status"]}

**Delay:** {best["delay_minutes"]} minutes

**Source:** {best["source"]}
""")

with right_col:
    st.subheader("Score Breakdown")

    st.metric(
        "Overall Score",
        f"{best['overall_score']}/100"
    )

    breakdown_df = pd.DataFrame(
        [
            {"Metric": k, "Score": v}
            for k, v in best["score_breakdown"].items()
        ]
    )

    st.dataframe(
        breakdown_df,
        hide_index=True,
        use_container_width=True,
    )

    st.bar_chart(
        breakdown_df,
        x="Metric",
        y="Score",
    )

st.write("---")
st.header("Full Flight Report")

report_left, report_right = st.columns([2, 1])

with report_left:

    st.subheader("Flight Details")

    st.markdown(f"""
**Airline:** {best["airline"]}

**Flight Number:** {best["flight_number"]}

**Aircraft Model:** {best["aircraft_model"]}

**Route:** {" -> ".join([x["airport"] for x in best["route"]])}

**Origin Airport:** {best["origin_airport_name"]}

**Destination Airport:** {best["destination_airport_name"]}

**Departure:** {best["departure_date_time"]}

**Arrival:** {best["arrival_date_time"]}

**Duration:** {best["duration_minutes"]} minutes

**Flight Status:** {best["status"]}

**Delay:** {best["delay_minutes"]} minutes

**Source:** {best["source"]}
""")

    st.subheader("AI Explanation")

    explanation = result["report"]

    if "FLIGHT DETAILS" in explanation:
        try:
            explanation = (
                explanation
                .split("FLIGHT DETAILS")[1]
                .split("ROUTE DETAILS")[0]
            )
        except Exception:
            pass

    st.write(explanation)

with report_right:

    st.subheader("Scoring")

    st.metric(
        "Overall Score",
        f"{best['overall_score']}/100"
    )

    score_df = pd.DataFrame(
        [
            {
                "Metric": k.replace("_", " ").title(),
                "Score": v,
            }
            for k, v in best["score_breakdown"].items()
        ]
    )

    st.dataframe(
        score_df,
        hide_index=True,
        use_container_width=True,
    )

    st.bar_chart(
        score_df,
        x="Metric",
        y="Score",
    )


st.write("---")
st.header("Route & Layover Details")

route_col, layover_col = st.columns(2)

with route_col:

    st.subheader("Route")

    route_text = " → ".join(
        [
            airport["airport"]
            for airport in best["route"]
        ]
    )

    st.success(route_text)

with layover_col:

    st.subheader("Layovers")

    if best["layovers"]:
        layover_df = pd.DataFrame(best["layovers"])
        st.dataframe(
            layover_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No layovers")


st.write("### Alternative Flights")

if alternatives:
    alt_df = pd.DataFrame(
        [
            {
                "Airline": flight["airline"],
                "Flight": flight["flight_number"],
                "Aircraft": flight["aircraft_model"],
                "Route": " -> ".join([x["airport"] for x in flight["route"]]),
                "Price": flight["price"],
                "Stops": flight["stops"],
                "Checked Bags": flight["checked_bags"],
                "Carry-on Bags": flight["carry_on_bags"],
                "Duration": flight["duration_minutes"],
                "Status": flight["status"],
                "Delay": flight["delay_minutes"],
                "Score": flight["overall_score"],
                "Source": flight["source"],
            }
            for flight in alternatives
        ]
    )

    st.dataframe(
        alt_df,
        use_container_width=True,
    )
else:
    st.info("No alternative flights matched the criteria.")

