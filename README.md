🥗 Diet Automation MVP

A local-first, data-driven diet planning system built with Python & SQLite

Diet Automation MVP is a lightweight yet powerful application designed to automate weekly diet planning while preserving full control over data, logic, and user preferences.

This project goes beyond a simple CRUD demo — it demonstrates real-world software engineering practices, including relational data modeling, deterministic + randomized logic, and state-safe UI design.

🚀 Overview

Planning diets manually is repetitive, error-prone, and difficult to scale.

Diet Automation MVP solves this by:

Automating weekly meal combinations

Respecting nutrition constraints and preferences

Reducing decision fatigue with smart shuffling

Keeping all data local and owned by the user

⚠️ This is an MVP.
The code is currently public for demonstration purposes and will be made private once the project moves beyond MVP.

✨ Features
📝 Diet & Food Management

Create and manage multiple diets

Meal categories:

Predefined (Breakfast, Lunch, Dinner, Snack)

Fully customizable

Food items with:

Portion sizes

Preference ratings (1–5 ⭐)

Mandatory flag 🔒 (always included)

🎲 Weekly Plan Generator

Generates 7-day plans (Monday–Sunday)

Mandatory foods appear every day

Smart selection logic:

At least one food per food category per meal

Rating-weighted randomness (rating²)

Buttons:

🎲 Shuffle New Plan

🔄 Shuffle Again

⭐ Save to Favorites

⭐ Saved Plans

Store favorite weekly plans

Default naming with editable titles

Delete unwanted plans

Expand to view full 7-day details

🧠 Engineering Highlights

This project intentionally implements patterns often missing in junior portfolios:

✅ Persistent relational data (SQLite)

✅ Entity relationships (diet → meal categories → foods)

✅ Ordered entities using order_index

✅ Full CRUD operations

✅ Rating-weighted randomized selection

✅ Deterministic constraints + randomness combined

✅ State-safe Streamlit reruns

✅ Clear separation between UI and database logic

🧰 Tech Stack
Backend / Logic

Python

SQLite

Frontend

Streamlit

Tooling

PyCharm

Git & GitHub

Architecture

Local-first

No external APIs

No cloud dependency

Easily extensible into SaaS or desktop app

🎨 UI Direction

Clean and minimal

White + green color palette 🌱

Rounded buttons

Minimal hover effects

UX-first, no overdesign

🎯 Who This Project Is For

Python & automation developers

Backend / SQL-focused engineers

Companies hiring for data-driven roles

Clients needing local-first tools

Developers interested in clean logic over flashy UI

🛣️ Roadmap (Post-MVP)

Export weekly plans (PDF / image)

Nutrition rules & constraints

User profiles

Optional cloud sync

Public API

Desktop packaging

📬 Contact

If you’re looking for:

A developer who understands automation, data, and UX

Clean, scalable Python & SQL solutions

Someone who builds real systems, not just demos

Feel free to reach out.
