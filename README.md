# 🌅 Sunset & Sunrise Explorer

**Discover what makes sunsets *and* sunrises magical — with data!**  
This project is a fun and educational deep dive into the beautiful relationship between weather conditions and the quality of sunsets and sunrises.

---

## ✨ Project Purpose

This is a **non-commercial** project created purely **for fun and learning**. It’s an opportunity to explore new tools, build something meaningful, and gain insights into one of nature’s most beautiful daily events.

---

## 🔄 Workflow Overview

### 🛰️ Data Extraction
- Collects **weather data** from freely available public APIs.
- Extracts **sunset and sunrise prediction** data from open third-party sources.

### 🧹 Data Processing
- Cleans and enriches the collected data.
- Merges weather and sunset/sunrise data into a **single cohesive dataset**.

### 📊 Analysis
- Explores **what factors influence sunset and sunrise quality**.
- Identifies patterns and **correlations between weather conditions** and light quality.

---

## 🛠️ Technologies Used

- **Python** – Core language for data collection, processing, and analysis.
- **SQLite** – Lightweight database to store and manage extracted data.
- **Docker** – Containerizes the app for consistent performance across environments.
- **GitHub Actions** – Automates the **daily data pipeline**, from fetching to processing.

---

## ⚙️ How It Works

1. **Scheduled GitHub Action** runs the workflow daily.
2. Retrieves **free and public** weather + sunset/sunrise data via APIs and web sources.
3. Cleans and merges the data into a **central dataset**.
4. Stores the data locally for ongoing analysis and insights.

---

## 🎯 Goals

- Understand the **relationship between weather and sunset/sunrise quality**.
- Deliver insights useful for **photographers, travelers, and nature lovers**.
- Build a reliable, automated system for **continuous data exploration**.

---

## 📌 Note

All APIs used are **free and public**, and **no data is behind a paywall**.  
This project is **not monetized** — it exists purely to learn, experiment, and share joy in natural beauty. 🌄
