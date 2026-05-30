# Store Intelligence - Real-Time Retail Analytics

This repository contains an end-to-end computer vision and analytics pipeline designed to convert raw physical retail data (CCTV footage) into actionable business metrics like conversion rates and operational anomalies.

The system is decoupled into two layers:
1. **The Vision Pipeline (`/pipeline`)**: Processes raw video to extract structured behavioral events using YOLOv8 and ByteTrack.
2. **The Intelligence API (`/app`)**: A real-time FastAPI ingestion engine that correlates physical events with POS transactions to calculate business metrics.

---

## 🚀 Quick Start (Acceptance Gate)

This project is fully containerized. To launch the Intelligence API and its dependencies, run:

```bash
# 1. Clone the repository
git clone 
cd store-intelligence

# 2. Start the API
docker compose up --build

The API will be available at: http://localhost:8000
Interactive Swagger Documentation available at: http://localhost:8000/docs

📂 Data Setup & Mock Assumptions
To evaluate this system, place the provided datasets into the /data directory:

CCTV Footage .mp4 clips.
Brigade_Bangalore_10_April_26 (1)bc6219c.csv (POS Transactions).

Important Note on store_layout.json:
The challenge documentation referenced a store_layout.json file containing spatial boundaries, but the dataset only provided a 2D architectural floor plan image.

To maintain a fully automated, end-to-end pipeline, I generated a mock store_layout.json located in /data. This JSON maps the logical zones (e.g., CASH_COUNTER, MAKEUP_UNIT) to estimated pixel polygons on the camera feed. In a production scenario, these coordinates would be accurately mapped using a custom OpenCV polygon-drawing tool to align the physical floor plan with the camera's specific perspective view.

🧠 Generating the Event Stream (Pipeline)
To generate events from the raw CCTV footage and feed them into the API, run the detection pipeline locally.

Bash
# Navigate to the pipeline directory
cd pipeline

# Install CV dependencies (Recommended in a virtual environment)
pip install -r requirements.txt

# Run the tracker on a sample video
python detect.py --video ../data/clips/entry_cam_01.mp4 
Note: This generates a generated_events.jsonl file in the /data directory.

To ingest these events into the running API:

Bash
python ../app/ingest_test.py
📡 Core API Endpoints
Once data is ingested, the following endpoints expose the real-time store intelligence:

GET /health - System status and ingestion counts.

POST /events/ingest - Accepts structured batches of events (Idempotent).

GET /stores/{id}/metrics - Returns unique visitors, zone dwell times, and the Conversion Rate based on a 5-minute POS correlation window.

GET /stores/{id}/funnel - Calculates session drop-off from Entry -> Zone Visit -> Billing Queue -> Purchase.

GET /stores/{id}/anomalies - Detects live operational issues (e.g., Dead Zones, Queue Spikes).

📑 Documentation
Please refer to the /docs folder for detailed architectural reasoning:

DESIGN.md: System architecture and AI-Assisted Decisions.

CHOICES.md: Technical trade-offs regarding model selection, schema design, and storage.