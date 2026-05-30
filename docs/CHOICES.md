# Architectural Choices & Trade-offs

## 1. Detection Model Selection
* **Options Considered:** YOLOv8 (Ultralytics), RT-DETR, MediaPipe.
* **What AI Suggested:** The LLM strongly recommended YOLOv8 for its extensive community support and out-of-the-box tracking integrations. It also suggested using a Vision-Language Model (VLM) like GPT-4V for zero-shot zone classification.
* **What I Chose & Why:** I chose **YOLOv8 nano (`yolov8n.pt`) paired with ByteTrack**. While the VLM suggestion for zone classification was interesting, it would introduce massive latency and API costs, making it unviable for processing 15fps video in real-time. YOLOv8 natively wraps ByteTrack via the `ultralytics` library, which allowed me to build a highly accurate, lightweight tracking pipeline that runs locally without external API dependencies. 

## 2. Event Schema Design Rationale
* **Options Considered:** A flat JSON structure vs. a nested schema with a dedicated `metadata` object.
* **What AI Suggested:** The AI initially generated a flat schema where every possible event property (like `queue_depth` or `sku_zone`) was a top-level key, often defaulting to `null`.
* **What I Chose & Why:** I chose the **nested schema** (implemented via Pydantic in `models.py`). A flat schema becomes incredibly brittle as the business logic expands. By nesting situational data inside a `metadata` object, the core fields (`event_id`, `timestamp`, `visitor_id`, `event_type`) remain strictly typed and predictable, while the `metadata` payload can flexibly expand for specific events (like `BILLING_QUEUE_JOIN`) without breaking downstream ingestion pipelines.

## 3. API Architecture (Storage Layer)
* **Options Considered:** SQLite vs. PostgreSQL vs. In-Memory Dictionary.
* **What AI Suggested:** The AI strongly pushed for SQLite to ensure data persistence across container restarts.
* **What I Chose & Why:** I overrode the AI and chose an **In-Memory Dictionary** for this specific challenge submission. Since the core requirement is to handle a high-throughput stream of events and calculate *real-time* metrics (like active queue spikes and 30-minute dead zones), the latency of disk writes was unnecessary for V1. The API acts as a real-time computation engine rather than a historical data warehouse. In a true production environment, I would connect this to a fast message broker like Redis or Kafka, rather than a relational database like SQLite.