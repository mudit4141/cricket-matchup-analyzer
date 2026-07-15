# 🏏 5-Way Cricket Player Matchup Engine

A high-performance, interactive web application built with **Streamlit** that delivers deep head-to-head analytics between any batter and bowler across all major cricket formats.

🔗 **Live App Link:** [Click here to use the App](https://cricket-matchup-analyzer-bkqz4wyez4ydpvkuggwuf7.streamlit.app/)

## 🚀 Key Features
* **5-Way Matchup Modes:** Filter historical records instantly by **All (Career Summary)**, **IPL**, **T20I**, **ODI**, or **Test** matches.
* **⚡ Smart Dynamic Filtering:** Selecting a batter automatically updates the bowler dropdown to show **only** the bowlers they have actually faced in the chosen format. No empty queries!
* **Advanced Analytics:** Computes advanced metrics on the fly, including Head-to-Head Strike Rate, Wicket Probability per ball, and Dot Ball Percentage.
* **Granular Timeline:** Displays a ball-by-ball historical timeline log of their actual face-offs.
* **🧠 Memory-Optimized Architecture:** Custom pipeline utilizing **Parquet columnar storage**, strict column loading, and downcasted data types (`int8`, `float32`, and category types) to bypass the 1 GB RAM limit on free-tier cloud hosting.

## 🛠️ Tech Stack
* **Frontend/App Framework:** Streamlit
* **Data Processing:** Pandas
* **Storage Engine:** PyArrow (Apache Parquet)

## 📦 Data Source
The underlying data is dynamically compiled and cleaned from the open-source ball-by-ball dataset provided by **Cricsheet**.
