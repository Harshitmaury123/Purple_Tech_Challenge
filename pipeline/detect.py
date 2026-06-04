import cv2
from ultralytics import YOLO
import argparse
import os
import json
from datetime import datetime, timedelta
from tracker import StoreTracker  # Importing our new logic

def run_pipeline(video_path, store_id, layout_path, output_jsonl):
    print(f"Loading YOLOv8 model and initializing tracker for {store_id}...")
    model = YOLO('yolov8n.pt') 
    
    # Initialize our Event Engine
    tracker = StoreTracker(store_id, layout_path)

    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0: fps = 15 # Fallback if OpenCV fails to read fps
    
    # We need a base timestamp to simulate real-world time. 
    # In production, this comes from the camera's RTSP stream metadata.
    base_time = datetime.fromisoformat("2026-04-10T12:16:00Z") 
    
    frame_count = 0
    total_events_emitted = 0

    # Open the file to append our JSON events
    with open(output_jsonl, 'w') as f_out:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
                
            frame_count += 1
            
            # Calculate the exact ISO-8601 timestamp for this specific frame
            current_time = base_time + timedelta(seconds=(frame_count / fps))
            iso_timestamp = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Run YOLO + ByteTrack
            results = model.track(frame, persist=True, tracker="bytetrack.yaml", classes=[0], verbose=False)
            
            tracked_objects = []
            
            # Safely extract bounding boxes and tracking IDs
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().numpy()
                confs = results[0].boxes.conf.cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                
                for box, t_id, conf, cls in zip(boxes, track_ids, confs, classes):
                    x1, y1, x2, y2 = box
                    # Append to our list: [x1, y1, x2, y2, track_id, conf, class]
                    tracked_objects.append([x1, y1, x2, y2, int(t_id), float(conf), int(cls)])
            
            # Pass the frame's data to our Event Engine
            events = tracker.process_frame_detections(iso_timestamp, tracked_objects)
            
            # Write any generated events to our JSONL file
            for event in events:
                f_out.write(json.dumps(event) + '\n')
                print(f"EMITTED: {event['event_type']} for {event['visitor_id']} in {event['zone_id']}")
                total_events_emitted += 1

            # --- Visualization for Debugging ---
            annotated_frame = results[0].plot()
            cv2.putText(annotated_frame, f"Events: {total_events_emitted}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow("Phase 2: Event Pipeline", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nPipeline finished. {total_events_emitted} events saved to {output_jsonl}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Store Intelligence Vision Pipeline")
    parser.add_argument("--video", type=str, required=True, help="Path to raw CCTV mp4")
    parser.add_argument("--store", type=str, default="ST1008", help="Store ID")
    parser.add_argument("--layout", type=str, default="../data/store_layout.json", help="Path to layout JSON")
    parser.add_argument("--output", type=str, default="../data/generated_events.jsonl", help="Output JSONL file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Could not find video at {args.video}")
    elif not os.path.exists(args.layout):
        print(f"Error: Could not find layout JSON at {args.layout}")
    else:
        run_pipeline(args.video, args.store, args.layout, args.output)