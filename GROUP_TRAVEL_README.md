# AI-Powered Group Travel Planner & Memory Assistant

## Overview

An intelligent travel planning platform that helps groups collaboratively plan trips, generate optimized itineraries, and automatically organize travel memories using AI and machine learning.

Unlike typical AI trip planners that simply ask an LLM to generate an itinerary, this system combines:

* NLP Embeddings
* Vector Search
* Recommendation Systems
* Route Optimization
* Computer Vision
* Constraint Solving

to create itineraries that are both personalized and actually feasible.

---

# Problem Statement

Planning a trip for a group is difficult because:

* Different people have different interests
* Budgets vary
* Walking tolerance differs
* Attractions have opening/closing times
* Most AI trip planners hallucinate or generate impossible schedules
* Travel photos become disorganized after the trip

Current solutions focus on either:

* Basic recommendation systems
* GPT-generated itineraries
* Manual planning

but fail to combine personalization, optimization, and memory management.

---

# Proposed Solution

The platform consists of three major AI-powered modules:

## 1. Group Preference Understanding

The system learns the collective preferences of a group.

Each member provides:

* Interests
* Budget
* Preferred pace
* Walking tolerance
* Dietary restrictions
* Travel style

Example:

```json
{
  "interests": [
    "history",
    "local food",
    "photography"
  ],
  "budget": 100,
  "pace": "moderate"
}
```

Instead of using hard-coded categories, user preferences are converted into semantic embeddings.

Example:

```text
"I love historical architecture and local cuisine."
```

↓

```text
768-dimensional embedding vector
```

using Sentence Transformers.

---

# 2. Intelligent Attraction Recommendation

## POI Embeddings

Every attraction contains:

* Name
* Description
* Category
* Reviews
* Tags

Example:

```text
Victoria Memorial
A historic marble monument showcasing colonial architecture.
```

↓

```text
Embedding Vector
```

using the same transformer model.

---

## Vector Search

The project uses:

### pgvector

inside PostgreSQL.

Workflow:

```text
User Preferences
        ↓
Sentence Transformer
        ↓
User Embedding
        ↓
Vector Similarity Search
        ↓
Top Matching Attractions
```

Instead of keyword matching, recommendations are based on semantic similarity.

Example:

User likes:

```text
Historical places
```

System may recommend:

* Victoria Memorial
* Indian Museum
* St. Paul’s Cathedral

even if the user never explicitly typed those names.

---

# 3. Feasible Itinerary Generation

This is where the project becomes different from ordinary AI travel planners.

Most systems:

```text
User
 ↓
GPT
 ↓
Itinerary
```

Our system:

```text
User
 ↓
Embedding Search
 ↓
Candidate Attractions
 ↓
Constraint Optimization
 ↓
Feasible Itinerary
```

---

## Constraint Optimization

Uses:

### OR-Tools

Google's optimization library.

The itinerary is generated while satisfying:

* Budget constraints
* Walking distance limits
* Opening hours
* Travel times
* Rest breaks
* Meal schedules
* Hotel return time

Example:

```text
Budget ≤ $80
Walking ≤ 10 km
Dinner before 7 PM
```

The optimizer guarantees:

* Realistic schedules
* No impossible routes
* Maximum attraction coverage

---

## Optimization Objective

Maximize:

```text
User Satisfaction
+
Attraction Relevance
-
Travel Time
-
Cost
```

Subject to all constraints.

---

# 4. AI-Based Travel Memory Assistant

After the trip, users upload photos.

The system automatically organizes memories using computer vision.

---

## CLIP-Based Image Understanding

Uses:

### CLIP

(OpenAI Vision-Language Model)

Photos are classified into:

* Food
* Beach
* Museum
* Landscape
* Nature
* Architecture
* Group Photo

without training a custom model.

Example:

```text
Image
 ↓
CLIP
 ↓
["food", "restaurant", "group"]
```

---

## Smart Photo Search

Users can search:

```text
Show me food photos
```

or

```text
Show me beach memories
```

without manually tagging images.

---

## Semantic Memory Search

CLIP embeddings are stored in pgvector.

Example:

```text
"sunset near water"
```

↓

Find visually similar photos.

This creates a semantic photo retrieval system.

---

# AI/ML Components

## NLP

### Sentence Transformers

Used for:

* User preference embeddings
* Attraction embeddings
* Semantic matching

Models:

```text
all-MiniLM-L6-v2
or
bge-small-en
```

---

## Recommendation System

Uses:

* Cosine Similarity
* Vector Retrieval
* Embedding Matching

to recommend attractions.

---

## Optimization

### OR-Tools

Used for:

* Route planning
* Scheduling
* Constraint satisfaction

This is the mathematical core of the itinerary engine.

---

## Computer Vision

### CLIP

Used for:

* Photo categorization
* Image embeddings
* Semantic image search

---

## Vector Database

### pgvector

Used for:

* Attraction retrieval
* Image retrieval
* Similarity search

---

# System Architecture

```text
                   ┌─────────────┐
                   │ User Input  │
                   └──────┬──────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │ Sentence Transformer    │
             └───────────┬─────────────┘
                         │
                         ▼
                 User Embedding
                         │
                         ▼
              ┌──────────────────┐
              │   pgvector DB    │
              └────────┬─────────┘
                       │
                       ▼
              Candidate Attractions
                       │
                       ▼
             ┌────────────────────┐
             │ OR-Tools Optimizer │
             └─────────┬──────────┘
                       │
                       ▼
               Final Itinerary
```

Photo Pipeline:

```text
Uploaded Image
       │
       ▼
      CLIP
       │
       ▼
Image Embedding
       │
       ▼
   pgvector
       │
       ▼
Semantic Search
```

---

# Technology Stack

## Backend

* Python
* FastAPI / Django
* Celery
* Redis

---

## Database

* PostgreSQL
* pgvector

---

## Machine Learning

* Sentence Transformers
* CLIP
* Scikit-Learn
* NumPy
* Pandas

---

## Optimization

* OR-Tools

---

## APIs

* Google Places API
* OpenStreetMap Overpass API

---

## Storage

* AWS S3

---

# Key Features

### Group Preference Modeling

Collect and aggregate preferences from multiple users.

### Semantic Attraction Recommendation

Recommend attractions using embeddings rather than keywords.

### Constraint-Aware Itinerary Planning

Generate schedules that are mathematically feasible.

### Automatic Photo Organization

Categorize travel photos using CLIP.

### Semantic Memory Search

Search memories using natural language.

### Budget-Aware Planning

Respect group spending constraints.

### Walking Distance Optimization

Avoid exhausting itineraries.

---

# Why This Project Stands Out

Most student projects:

```text
User
 ↓
ChatGPT API
 ↓
Result
```

This project demonstrates:

* Natural Language Processing
* Vector Databases
* Recommendation Systems
* Mathematical Optimization
* Computer Vision
* Information Retrieval
* Full Stack Development

The AI component is not just API calls; it directly drives recommendation, retrieval, optimization, and memory management.

---

# Future Enhancements

### Reinforcement Learning

Learn optimal travel sequences from user behavior.

### Satisfaction Prediction Model

Predict user ratings using:

* XGBoost
* LightGBM

### Weather-Aware Optimization

Modify itineraries based on forecast data.

### Multi-City Planning

Support long-duration trips across multiple destinations.

### Personalized Travel Reports

Generate post-trip summaries combining:

* Photos
* Visited attractions
* Expenses
* Highlights

---

# Expected Outcomes

The system will:

* Reduce trip planning effort
* Increase itinerary personalization
* Generate realistic schedules
* Automatically organize travel memories
* Provide semantic search over photos and attractions

while showcasing multiple advanced AI/ML concepts in a single production-ready application.
