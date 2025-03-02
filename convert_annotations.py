import json
import cv2
import os
import numpy as np
import sys


def yolo_to_bbox(x_center, y_center, width, height, img_width=1.0, img_height=1.0):
    """Convert YOLO format (x_center, y_center, width, height) to (x1, y1, x2, y2)"""
    x1 = (x_center - width/2) * img_width
    y1 = (y_center - height/2) * img_height
    x2 = (x_center + width/2) * img_width
    y2 = (y_center + height/2) * img_height
    return [int(x1), int(y1), int(x2), int(y2)]


try:
    # Create bbox directory if it doesn't exist
    os.makedirs('bbox', exist_ok=True)
    print("Created bbox directory")

    # Read the image
    image_path = 'images/image.png'
    print(f"Reading image from: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read the image from {image_path}")

    img_height, img_width = image.shape[:2]
    print(f"Image dimensions: {img_width}x{img_height}")

    # Generate random colors for each class
    np.random.seed(42)  # for reproducibility
    colors = np.random.randint(0, 255, size=(100, 3), dtype=np.uint8).tolist()

    # Read class names
    print("Reading class names...")
    with open('classes.txt', 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    print(f"Found {len(classes)} classes")

    # Read annotations
    print("Reading annotations...")
    annotations = []
    with open('labels/image.txt', 'r') as f:
        for line in f.readlines():
            parts = line.strip().split()
            if len(parts) == 5:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])

                # Convert to x1,y1,x2,y2 format with actual image dimensions
                bbox = yolo_to_bbox(x_center, y_center, width,
                                    height, img_width, img_height)

                # Draw bounding box
                color = colors[class_id]
                cv2.rectangle(image, (bbox[0], bbox[1]),
                              (bbox[2], bbox[3]), color, 2)

                # Add label
                label = f'{classes[class_id]}'
                (label_width, label_height), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(image, (bbox[0], bbox[1] - label_height - 5),
                              (bbox[0] + label_width + 5, bbox[1]), color, -1)
                cv2.putText(image, label, (bbox[0], bbox[1] - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                annotation = {
                    'class': classes[class_id],
                    'class_id': class_id,
                    'bbox': bbox
                }
                annotations.append(annotation)

    print(f"Processed {len(annotations)} annotations")

    # Save the annotated image
    output_image_path = 'bbox/annotated_image.png'
    print(f"Saving annotated image to: {output_image_path}")
    cv2.imwrite(output_image_path, image)

    # Save as JSON
    output = {
        'annotations': annotations
    }

    json_path = 'annotations.json'
    print(f"Saving annotations to: {json_path}")
    with open(json_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(
        f"Successfully converted {len(annotations)} annotations to {json_path}")
    print(f"Successfully saved annotated image to {output_image_path}")

except Exception as e:
    print(f"Error: {str(e)}", file=sys.stderr)
    sys.exit(1)
