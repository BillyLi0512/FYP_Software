from ultralytics import solutions
from collections import defaultdict
import cv2
from ultralytics.utils.checks import check_imshow, check_requirements
from ultralytics.utils.plotting import Annotator, colors
check_requirements("shapely>=2.0.0")
from shapely.geometry import LineString, Point, Polygon

# 重写ultralytics下计数对象的方法
class SubCounter(solutions.ObjectCounter):
    def extract_and_process_tracks(self, tracks):
        """Extracts and processes tracks for object counting in a video stream."""

        # Annotator Init and region drawing
        self.annotator = Annotator(self.im0, self.tf, self.names)

        # Draw region or line
        self.annotator.draw_region(reg_pts=self.reg_pts, color=self.region_color, thickness=self.region_thickness)

        if tracks[0].boxes.id is not None:
            boxes = tracks[0].boxes.xyxy.cpu()
            clss = tracks[0].boxes.cls.cpu().tolist()
            track_ids = tracks[0].boxes.id.int().cpu().tolist()

            # Extract tracks
            for box, track_id, cls in zip(boxes, track_ids, clss):
                # Draw bounding box
                self.annotator.box_label(box, label=f"{self.names[cls]}#{track_id}", color=colors(int(track_id), True))

                # Store class info
                if self.names[cls] not in self.class_wise_count:
                    self.class_wise_count[self.names[cls]] = {"upstream": 0, "downstream": 0}

                # Draw Tracks
                track_line = self.track_history[track_id]
                track_line.append((float((box[0] + box[2]) / 2), float((box[1] + box[3]) / 2)))
                if len(track_line) > 30:
                    track_line.pop(0)

                # Draw track trails
                if self.draw_tracks:
                    self.annotator.draw_centroid_and_tracks(
                        track_line,
                        color=self.track_color or colors(int(track_id), True),
                        track_thickness=self.track_thickness,
                    )

                prev_position = self.track_history[track_id][-2] if len(self.track_history[track_id]) > 1 else None

                # Count objects in any polygon
                if len(self.reg_pts) >= 3:
                    is_inside = self.counting_region.contains(Point(track_line[-1]))

                    if prev_position is not None and is_inside and track_id not in self.count_ids:
                        self.count_ids.append(track_id)

                        if (box[0] - prev_position[0]) * (self.counting_region.centroid.x - prev_position[0]) > 0:
                            self.in_counts += 1
                            self.class_wise_count[self.names[cls]]["upstream"] += 1
                        else:
                            self.out_counts += 1
                            self.class_wise_count[self.names[cls]]["downstream"] += 1

                # Count objects using line
                elif len(self.reg_pts) == 2:
                    if prev_position is not None and track_id not in self.count_ids:
                        distance = Point(track_line[-1]).distance(self.counting_region)
                        if distance < self.line_dist_thresh and track_id not in self.count_ids:
                            self.count_ids.append(track_id)

                            if (box[0] - prev_position[0]) * (self.counting_region.centroid.x - prev_position[0]) > 0:
                                self.in_counts += 1
                                self.class_wise_count[self.names[cls]]["upstream"] += 1
                            else:
                                self.out_counts += 1
                                self.class_wise_count[self.names[cls]]["downstream"] += 1

        labels_dict = {}

        for key, value in self.class_wise_count.items():
            if value["upstream"] != 0 or value["downstream"] != 0:
                if not self.view_in_counts and not self.view_out_counts:
                    continue
                elif not self.view_in_counts:
                    labels_dict[str.capitalize(key)] = f"downstream {value['downstream']}"
                    print(f"downstream: {value['downstream']}")
                elif not self.view_out_counts:
                    labels_dict[str.capitalize(key)] = f"upstream {value['upstream']}"
                    print(f"upstream: {value['upstream']}")
                else:
                    labels_dict[str.capitalize(key)] = f"upstream {value['upstream']} downstream {value['downstream']}"
                    print(f"upstream: {value['upstream']}; downstream: {value['downstream']}")

        if labels_dict:
            self.annotator.display_analytics(self.im0, labels_dict, self.count_txt_color, self.count_bg_color, 10)


import cv2
from ultralytics import YOLO, solutions

# Load the pre-trained YOLOv8 model
model = YOLO("best.pt")

cap = cv2.VideoCapture(0)  # 使用默认摄像头
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# Get video properties: width, height, and frames per second (fps)
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Define points for a line or region of interest in the video frame
line_points = [(3 * w / 4, 0), (3 * w / 4, h)]  # Line coordinates

# Specify classes to count, for example: person (0) and car (2)
classes_to_count = [0]  # Class IDs for person and car

# Initialize the video writer to save the output video
video_writer = cv2.VideoWriter("object_counting_output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# Initialize the Object Counter with visualization options and other parameters
counter = SubCounter(
    view_img=True,
    reg_pts=line_points,
    names=model.names,
    draw_tracks=True,
    line_thickness=2,
)

while cap.isOpened():
    ret, im0 = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break

    # Perform object tracking on the current frame, filtering by specified classes
    tracks = model.track(im0, persist=True, show=False, classes=classes_to_count)

    # Use the Object Counter to count objects in the frame and get the annotated image
    im0 = counter.start_counting(im0, tracks)

    # 在帧上绘制检测结果
    annotated_frame = tracks[0].plot()

    # 显示处理后的帧
    # cv2.imshow("YOLOv8 Real-Time Detection", annotated_frame)

    # Write the annotated frame to the output video
    video_writer.write(im0)

    # 按下 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()
video_writer.release()