import cv2
import json
import numpy as np
import uuid
from datetime import datetime

class StoreTracker:
    def __init__(self, store_id, layout_path):
        self.store_id = store_id
        self.zones = self._load_zones(layout_path)
        self.active_sessions = {}
        
    def _load_zones(self, layout_path):
        with open(layout_path, 'r') as f:
            data = json.load(f)
        
        zones_raw = data['stores'][self.store_id]['zones']
        zones_np = {}
        for zone_name, points in zones_raw.items():
            zones_np[zone_name] = np.array(points, np.int32).reshape((-1, 1, 2))
        return zones_np

    def get_zone_for_feet(self, x1, y1, x2, y2):
        feet_x = (x1 + x2) / 2
        feet_y = y2  
        feet_point = (feet_x, feet_y)

        for zone_name, polygon in self.zones.items():
            if cv2.pointPolygonTest(polygon, feet_point, False) >= 0:
                return zone_name
        
        return "AISLE"

    def process_frame_detections(self, frame_timestamp, tracked_objects):
        events_to_emit = []

        # FIX: Parse the incoming ISO string back into a datetime object for math
        current_dt = datetime.strptime(frame_timestamp, "%Y-%m-%dT%H:%M:%SZ")

        for obj in tracked_objects:
            x1, y1, x2, y2, track_id, conf, cls = obj
            
            current_zone = self.get_zone_for_feet(x1, y1, x2, y2)
            
            if track_id not in self.active_sessions:
                visitor_id = f"VIS_{uuid.uuid4().hex[:6]}"
                
                self.active_sessions[track_id] = {
                    "visitor_id": visitor_id,
                    "current_zone": current_zone,
                    "zone_entry_dt": current_dt, # Store the datetime object, not the string!
                    "session_seq": 1
                }
                
                if current_zone == "ENTRY_THRESHOLD":
                    events_to_emit.append(self._create_event(track_id, "ENTRY", current_zone, frame_timestamp))
                    
            else:
                session = self.active_sessions[track_id]
                previous_zone = session["current_zone"]
                
                if current_zone != previous_zone:
                    if previous_zone != "AISLE":
                        events_to_emit.append(self._create_event(track_id, "ZONE_EXIT", previous_zone, frame_timestamp))
                    
                    if current_zone != "AISLE":
                        events_to_emit.append(self._create_event(track_id, "ZONE_ENTER", current_zone, frame_timestamp))
                    
                    session["current_zone"] = current_zone
                    session["zone_entry_dt"] = current_dt
                    
                elif current_zone != "AISLE":
                    # FIX: Calculate time difference using the datetime objects
                    dwell_time = (current_dt - session["zone_entry_dt"]).total_seconds()
                    
                    if dwell_time >= 30.0:
                        events_to_emit.append(self._create_event(track_id, "ZONE_DWELL", current_zone, frame_timestamp))
                        session["zone_entry_dt"] = current_dt 

        return events_to_emit

    def _create_event(self, track_id, event_type, zone_id, timestamp):
        session = self.active_sessions[track_id]
        event = {
            "event_id": str(uuid.uuid4()),
            "store_id": self.store_id,
            "visitor_id": session["visitor_id"],
            "event_type": event_type,
            "timestamp": timestamp, # Pass the original string to the JSON
            "zone_id": zone_id,
            "metadata": {
                "session_seq": session["session_seq"]
            }
        }
        session["session_seq"] += 1
        return event