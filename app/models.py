from pydantic import BaseModel, Field
from typing import Optional

class EventMetadata(BaseModel):
    queue_depth: Optional[int] = None
    sku_zone: Optional[str] = None
    session_seq: int

class StoreEvent(BaseModel):
    event_id: str
    store_id: str
    camera_id: Optional[str] = "CAM_UNKNOWN" 
    visitor_id: str
    event_type: str
    timestamp: str # ISO-8601 UTC
    zone_id: Optional[str] = None
    dwell_ms: Optional[int] = 0
    is_staff: Optional[bool] = False
    confidence: Optional[float] = 1.0
    metadata: EventMetadata