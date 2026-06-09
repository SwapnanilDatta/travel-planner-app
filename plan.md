# AI-Powered Group Travel Planner - PLAN.md

## Project Goal

Build a collaborative AI-powered travel planning platform where groups can:

* Create travel groups
* Chat in real-time
* Collect preferences from all members
* Generate personalized attraction recommendations
* Create feasible day-wise itineraries
* Organize and search travel photos using AI

The project should prioritize recommendation systems, vector search, optimization, and computer vision rather than relying on LLM-generated itineraries.

---

# Core User Flow

```text
Register/Login
      ↓
Create Group
      ↓
Invite Members via Code
      ↓
Group Chat
      ↓
Lock Group
      ↓
All Members Submit Preferences
      ↓
Select Destination City
      ↓
Generate Group Recommendations
      ↓
Generate Itinerary
      ↓
Upload Photos
      ↓
Automatic Album Organization
```

---

# Tech Stack

## Backend

* Django
* Django REST Framework
* Django Channels
* Redis
* Celery

## Database

* PostgreSQL
* pgvector

## ML

* Sentence Transformers
* Scikit-Learn
* OR-Tools
* CLIP

## Data Sources

* OpenStreetMap
* Overpass API

## Storage

* Local Storage (MVP)
* AWS S3 (Future)

---

# Phase 1 — Authentication

## Features

* Register
* Login
* Logout

## Models

```python
User
UserProfile
```

---

# Phase 2 — Groups

## TravelGroup

```python
TravelGroup
-------------
id
name
host
invite_code
is_locked
created_at
```

## GroupMember

```python
GroupMember
-------------
group
user
joined_at
```

## Workflow

Host:

```text
Create Group
```

System:

```text
Generate Unique Invite Code
```

Members:

```text
Join Using Invite Code
```

Host:

```text
Lock Group
```

No additional users can join after lock.

---

# Phase 3 — Group Chat

Use:

* Django Channels
* Redis

## ChatMessage

```python
ChatMessage
-------------
group
sender
message
timestamp
```

Features:

* Real-time messaging
* Group-specific rooms

---

# Phase 4 — Trip Creation

Host creates trip.

```python
Trip
-------------
group
destination_city
start_date
end_date
hotel_name
hotel_lat
hotel_lon
```

Example:

```text
New Delhi
5 Days
Hotel Location
```

---

# Phase 5 — Preference Collection

Each member submits:

```python
UserPreference
-------------
user
group

budget

trip_style

walking_limit

interests

days

embedding
```

Example Interests:

```text
History
Architecture
Food
Nature
Photography
Museums
Nightlife
```

---

# Phase 6 — Embedding Pipeline

## Generate User Preference Text

Example:

```text
Interested in history, food and architecture.
Budget 15000.
Travel style moderate.
```

## Generate Embedding

Use:

```python
sentence-transformers/all-MiniLM-L6-v2
```

Store vector in pgvector.

---

# Phase 7 — POI Database

Create local POI dataset.

## POI Model

```python
POI
-------------
name
city
state

description

category

latitude
longitude

avg_visit_minutes

opening_time
closing_time

estimated_cost

embedding
```

## Data Source

Use:

* OpenStreetMap
* Overpass API

Store POIs city-wise.

Example:

```text
New Delhi
    Red Fort
    India Gate
    Qutub Minar

Mumbai
    Gateway of India
    Marine Drive
```

---

# Phase 8 — Recommendation Engine

## Step 1

Retrieve all user embeddings.

## Step 2

## Step 2

Retrieve Candidate POIs for EACH user individually.

Method:

```python
For user in group:
    user_top_pois = pgvector_search(user.embedding)
```

## Step 3

Pool all candidate POIs from all users into a unique candidate set.
This prevents the "mushy middle" problem where an averaged group vector points to a generic attraction nobody actually wants.

## Step 3

Filter POIs by selected city.

Example:

```sql
WHERE city = 'New Delhi'
```

## Step 4

Perform pgvector similarity search.

Retrieve:

```text
Top 20 Most Relevant Attractions
```

---

# Phase 9 — Conflict-Aware Recommendations

Problem:

```text
User A likes history
User B likes history
User C likes nature
```

Avoid recommending only historical sites.

## Approach

Calculate:

```python
similarity(user_embedding, poi_embedding)
```

for every user.

Final score:

```python
0.7 * average_score
+
0.3 * minimum_score
```

This prevents ignoring minority preferences.

---

# Phase 10 — Distance Matrix

For retrieved POIs:

Calculate pairwise distances.

Use:

```python
OSRM API (Open Source Routing Machine) or Google Distance Matrix API
```

*Note: Avoid using `geopy` (Haversine/straight-line distance). OSRM provides actual road/walking network travel times, which is essential for accurate itinerary routing.*

Example:

```text
Red Fort → India Gate
India Gate → Qutub Minar
```

Store:

```python
TravelDistance
```

or generate dynamically.

---

# Phase 11 — Itinerary Optimization

Use:

```python
Google OR-Tools
```

Input:

* Top POIs
* Budget
* Travel days
* Opening hours
* Visit duration
* Distance matrix

Constraints:

```text
Daily Time Limit

Budget Limit

Opening Hours (requires parsing OSM string hours into integer minutes)

Walking Limit

Hotel Return Time
```

Objective:

```text
Maximize Group Satisfaction
Minimize Travel Time
```

Output:

```text
Day 1
  Red Fort
  India Gate

Day 2
  Qutub Minar
  Humayun Tomb
```

---

# Phase 12 — Photo Memory System

Users upload photos.

## Photo Model

```python
Photo
-------------
group
user

image

embedding

predicted_category

uploaded_at
```

---

# Phase 13 — CLIP Processing

Generate:

```python
Image Embedding
```

using CLIP.

Predict categories:

```text
Food
Museum
Beach
Nature
Architecture
Group Photo
```

---

# Phase 14 — Automatic Albums

Create albums automatically.

Examples:

```text
Food Memories

Museum Visits

Nature Shots

Group Photos
```

No manual tagging required.

---

# Phase 15 — Semantic Photo Search

User query:

```text
show sunset photos
```

Convert query to embedding.

Search photo vectors.

Return:

```text
Top Matching Images
```

---

# MVP Definition

The project is considered MVP-complete when:

* Authentication works
* Groups work
* Invite code system works
* Group chat works
* Preference collection works
* Destination selection works
* Embedding generation works
* City-filtered recommendation works
* Top attractions are retrieved using pgvector

Do NOT build itinerary optimization or photo AI until MVP is complete.

---

# Development Order

1. Authentication
2. Groups
3. Invite Codes
4. Group Chat
5. Trip Creation
6. Preference Form
7. PostgreSQL + pgvector
8. Sentence Transformer Embeddings
9. POI Dataset
10. Recommendation Engine
11. Distance Matrix
12. OR-Tools Itinerary Generation
13. Photo Upload
14. CLIP Integration
15. Semantic Photo Search
