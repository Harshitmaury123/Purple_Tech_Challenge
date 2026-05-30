# System Architecture & Design

## 1. Architecture Overview
The Store Intelligence pipeline is designed to decouple heavy computer vision processing from the high-throughput REST API. It operates in two distinct logical layers, linked by a structured event stream.

### A. The Vision Pipeline (`/pipeline`)
* **Detection & Tracking:** Built using Ultralytics YOLOv8 for object detection and ByteTrack for persistent ID tracking across frames. 
* **Spatial Mapping Engine:** Instead of calculating bounding box centroids, the tracker isolates the bottom-center coordinate (the "feet") to accurately determine floor position. It uses OpenCV's `pointPolygonTest` to map these coordinates against predefined store zones.
* **State Management:** An in-memory dictionary tracks the active state and dwell time of every `visitor_id`, emitting structured JSON events (`ZONE_ENTER`, `ZONE_DWELL`, etc.) only when state changes or time thresholds are met.

### B. The Intelligence API (`/app`)
* **Web Framework:** FastAPI was selected for its async capabilities and native Pydantic integration, which strictly enforces the mandated event schema and automatically handles 422 Unprocessable Entity responses for malformed data.
* **Data Correlation:** POS transactions are loaded into memory on startup. The conversion rate engine uses a 5-minute rolling window, correlating a physical presence in the `CASH_COUNTER` zone with a digital POS timestamp to calculate the North Star Metric.
* **Containerization:** The API is packaged in a lightweight `python:3.10-slim` Docker container, exposing endpoints for real-time querying while isolating dependencies.

---

## 2. AI-Assisted Decisions

This system was built utilizing LLMs (Claude/ChatGPT/Gemini) as architectural sounding boards and pair programmers. Below are three key instances where AI shaped the design, including instances where its initial approach was overridden.

### Decision 1: Handling the Missing Spatial Data
* **The Situation:** The documentation stated a `store_layout.json` would be provided, but the dataset only included a 2D floor plan image. 
* **AI Suggestion:** The LLM suggested guessing the pixel coordinates by eyeballing the video frames and manually typing out a JSON file.
* **My Override:** I disagreed with this brittle approach. Instead, I prompted the AI to help me write a custom OpenCV tool (`mapper.py`) that allows a user to click on a video frame and dynamically generate the polygons for the JSON file. This resulted in a much more robust, production-ready solution to handle missing data.

### Decision 2: Timestamp Math & Type Errors
* **The Situation:** When building the `ZONE_DWELL` logic, the system needed to calculate if 30 seconds had passed since a visitor entered a zone.
* **AI Suggestion:** The AI generated logic that attempted to subtract two ISO-8601 string timestamps directly, resulting in a `TypeError`.
* **The Fix:** I caught the error during debugging and instructed the AI to refactor the state manager. We updated the logic to strictly parse incoming strings into Python `datetime` objects for time-delta math, while ensuring the emitted JSON still used the required ISO string format.

### Decision 3: POS Data Schema Adaptation
* **The Situation:** The problem statement provided a simple 4-column schema for the POS data, but the actual CSV file provided in the dataset contained 39 detailed columns with split date and time fields.
* **AI Suggestion:** Initially, the AI code relied on strict column indexing based on the PDF documentation.
* **The Pivot:** I fed the actual `csv.info()` schema to the LLM and we collaborated to write a robust `csv.DictReader` parser that safely extracted and concatenated the `order_date` and `order_time` fields into a unified timestamp, adapting the ingestion engine to the messy reality of the data without rewriting the core business logic.