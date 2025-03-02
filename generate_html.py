import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import numpy as np


@dataclass
class BBox:
    """A bounding box class representing a rectangular region.

    Attributes:
        x1: The x-coordinate of the top-left corner
        y1: The y-coordinate of the top-left corner
        x2: The x-coordinate of the bottom-right corner
        y2: The y-coordinate of the bottom-right corner
    """
    x1: int
    y1: int
    x2: int
    y2: int

    def contains(self, child: 'BBox') -> bool:
        """Check if this bounding box contains another bounding box's center, has larger area,
        and has significant overlap.

        Args:
            child: Another BBox instance to check containment against

        Returns:
            bool: True if this box contains the other box's center, has larger area,
                 and has significant overlap (>50%), False otherwise
        """
        # Calculate center point of other bbox
        child_center_x = (child.x1 + child.x2) / 2
        child_center_y = (child.y1 + child.y2) / 2

        # Check if center point lies within this bbox
        center_contained = (self.x1 <= child_center_x <= self.x2 and
                            self.y1 <= child_center_y <= self.y2)

        # Calculate areas
        self_area = (self.x2 - self.x1) * (self.y2 - self.y1)
        child_area = (child.x2 - child.x1) * (child.y2 - child.y1)

        # Calculate overlap ratio
        overlap = child.overlap_ratio(self)

        # Return true if center is contained, this box has larger area, and overlap > 80%
        return center_contained and self_area > child_area and overlap > 0.6

    def overlap_ratio(self, child: 'BBox') -> float:
        """Calculate the overlap ratio between this box and another box.

        The overlap ratio is defined as the area of intersection divided by
        the area of this box.

        Args:
            child: Another BBox instance to calculate overlap with

        Returns:
            float: The overlap ratio between 0.0 and 1.0
        """
        x_left = max(self.x1, child.x1)
        y_top = max(self.y1, child.y1)
        x_right = min(self.x2, child.x2)
        y_bottom = min(self.y2, child.y2)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection = (x_right - x_left) * (y_bottom - y_top)
        self_area = (self.x2 - self.x1) * (self.y2 - self.y1)
        return intersection / self_area


class Element:
    """A class representing an HTML element with positioning information.

    This class models an HTML element with its class name, bounding box coordinates,
    and hierarchical relationship to other elements. It supports building a tree
    structure of nested elements based on their spatial relationships.

    Attributes:
        class_name (str): The CSS class name of the element
        bbox (BBox): The bounding box coordinates of the element
        class_id (int, optional): Numeric identifier for the element class
        children (Set[Element]): Set of child elements contained within this element
    """

    def __init__(self, class_name: str, bbox: BBox, class_id: int = None):
        """Initialize an Element instance.

        Args:
            class_name (str): The CSS class name of the element
            bbox (BBox): The bounding box coordinates of the element
            class_id (int, optional): Numeric identifier for the element class
        """
        self.class_name = class_name
        self.bbox = bbox
        self.class_id = class_id
        self.children: Set[Element] = set()

    def add_child(self, child: 'Element') -> None:
        """Add a child element to this element's children.

        This method handles the hierarchical relationship between elements by:
        1. Checking if the child should become a parent of existing children
        2. Checking if the child should be nested under an existing child
        3. Adding the child directly if no special relationship exists

        Args:
            child (Element): The element to add as a child
        """
        # Don't add if it's already a child
        if child in self.children:
            return

        # First check if any existing child should be a child of the new element
        children_to_move = set()
        for existing_child in self.children:
            if child.bbox.contains(existing_child.bbox):
                children_to_move.add(existing_child)
                child.add_child(existing_child)

        # Remove any children that were moved to the new child
        self.children -= children_to_move

        # Then check if the new child should be a child of any existing child
        for existing_child in self.children:
            if existing_child.bbox.contains(child.bbox):
                existing_child.add_child(child)
                return

        # If we get here, add the child directly to this element
        self.children.add(child)

    def pretty_print(self, indent: int = 0) -> None:
        """Pretty print this element and its children with indentation.

        Args:
            indent (int): Number of spaces to indent this element
        """
        print(" " * indent +
              f"Element(class='{self.class_name}', bbox={vars(self.bbox)}, class_id={self.class_id})")
        for child in sorted(self.children, key=lambda x: x.class_name):
            child.pretty_print(indent + 2)
            # print(child.class_name)


def determine_flex_direction(element: Element) -> str:
    """Determine if children are arranged in a row or column.

    Uses standard deviation of coordinates to determine alignment.
    Lower standard deviation indicates better alignment along that axis.

    Args:
        element: The parent element whose children's arrangement is being determined

    Returns:
        str: 'flex-row' for horizontal arrangement, 'flex-col' for vertical
    """
    if not element.children:
        return "flex-col"  # Default if no children

    # Get center points of all children
    points = []
    for child in element.children:
        x_center = (child.bbox.x1 + child.bbox.x2) / 2
        y_center = (child.bbox.y1 + child.bbox.y2) / 2
        points.append((x_center, y_center))

    x_coords, y_coords = zip(*points)  # Separate x and y coordinates

    std_x = np.std(x_coords)  # Standard deviation of x values
    std_y = np.std(y_coords)  # Standard deviation of y values

    # Lower standard deviation indicates better alignment along that axis
    # For row layout, x coordinates should vary more than y coordinates
    return "flex-row" if std_x > std_y else "flex-col"


def get_children_order(orientation: str, element: Element) -> List[Element]:
    if orientation == "flex-row":
        return sorted(element.children, key=lambda x: x.bbox.x1)
    else:
        return sorted(element.children, key=lambda x: x.bbox.y1)


def load_annotations(annotations_file: str) -> List[any]:
    with open(annotations_file, 'r') as f:
        content = json.load(f)
    annotations = content["annotations"]
    return annotations


def parse_annotations(annotations: List[any]) -> List[Element]:
    elements = []
    for annotation in annotations:
        bbox = BBox(annotation["bbox"][0], annotation["bbox"]
                    [1], annotation["bbox"][2], annotation["bbox"][3])
        element = Element(annotation["class"], bbox, annotation["class_id"])
        elements.append(element)
    return elements


def create_tree(elements: List[Element]) -> Element:
    # Sort elements by area in descending order to process larger boxes first
    temp_elements = elements.copy()
    root = Element("root", BBox(0, 0, 0, 0))
    for element in temp_elements:
        root.add_child(element)
    return root


def generate_html(root: Element) -> str:
    """Generate HTML markup for the element tree with Tailwind CSS classes.

    Args:
        root: The root Element object of the tree

    Returns:
        str: Generated HTML markup
    """
    def get_tailwind_classes(element: Element) -> str:
        """Get appropriate Tailwind classes based on element type."""
        base_classes = "relative "

        match element.class_name:
            case "button":
                return base_classes + "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            case "div" | "div-bg":
                flex_dir = determine_flex_direction(element)
                return base_classes + f"flex {flex_dir} gap-4"
            case "footer":
                flex_dir = determine_flex_direction(element)
                return base_classes + f"flex {flex_dir} items-center justify-between w-full bg-gray-100 p-4"
            case "grid":
                return base_classes + "grid grid-cols-3 gap-4"
            case "header":
                flex_dir = determine_flex_direction(element)
                return base_classes + f"flex {flex_dir} items-center justify-between w-full bg-white p-4"
            case "heading":
                return base_classes + "text-2xl font-bold mb-4"
            case "icon":
                return base_classes + "w-6 h-6"
            case "image":
                return base_classes + "object-cover"
            case "input":
                return base_classes + "border rounded px-3 py-2 focus:outline-none focus:ring-2"
            case "list":
                flex_dir = determine_flex_direction(element)
                return base_classes + f"flex {flex_dir} gap-2"
            case "paragraph":
                return base_classes + "text-gray-600 leading-relaxed"
            case "section":
                flex_dir = determine_flex_direction(element)
                return base_classes + f"flex {flex_dir} gap-6 p-6"
            case "span":
                flex_dir = determine_flex_direction(element)
                return base_classes + f"flex {flex_dir} gap-2"
            case "text":
                return base_classes + "text-gray-800"
            case _:
                return base_classes

    def get_element_tag(class_name: str) -> str:
        """Get appropriate HTML tag based on element class."""
        match class_name:
            case "button":
                return "button"
            case "heading":
                return "h2"
            case "paragraph":
                return "p"
            case "image":
                return "img"
            case "input":
                return "input"
            case "span":
                return "span"
            case "text":
                return "span"
            case "header":
                return "header"
            case "footer":
                return "footer"
            case "section":
                return "section"
            case _:
                return "div"

    def generate_element_html(element: Element, indent: int = 0) -> str:
        """Recursively generate HTML for an element and its children."""
        if not element:
            return ""

        # Skip root element
        if element.class_name == "root":
            return "".join(generate_element_html(child, indent) for child in get_children_order(determine_flex_direction(element), element))

        indent_str = "  " * indent
        tag = get_element_tag(element.class_name)
        classes = get_tailwind_classes(element)

        # Calculate dimensions for image placeholders
        width = element.bbox.x2 - element.bbox.x1
        height = element.bbox.y2 - element.bbox.y1

        # Opening tag with appropriate placeholder content
        match element.class_name:
            case "image":
                html = f"{indent_str}<{tag} src='https://picsum.photos/{width}/{height}?random=1' alt='Placeholder' class='{classes}' data-id='{element.class_id}' data-type='{element.class_name}'>\n"
            case "button":
                html = f"{indent_str}<{tag} class='{classes}' data-id='{element.class_id}' data-type='{element.class_name}'>Click me\n"
            case "heading":
                html = f"{indent_str}<{tag} class='{classes}' data-id='{element.class_id}' data-type='{element.class_name}'>Sample Heading\n"
            case "paragraph":
                html = f"{indent_str}<{tag} class='{classes}' data-id='{element.class_id}' data-type='{element.class_name}'>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n"
            case "input":
                html = f"{indent_str}<{tag} type='text' placeholder='Enter text here...' class='{classes}' data-id='{element.class_id}' data-type='{element.class_name}'>\n"
            case "text" | "span":
                html = f"{indent_str}<{tag} class='{classes}' data-id='{element.class_id}' data-type='{element.class_name}'>Sample text\n"
            case _:
                html = f"{indent_str}<{tag} class='{classes}' data-id='{element.class_id}' data-type='{element.class_name}'>\n"

        # Only process children for non-self-closing tags
        if element.class_name not in ["image", "input"]:
            # Get flex direction for ordering children
            flex_dir = determine_flex_direction(element)
            if (element.class_name == "header"):
                print(flex_dir)
            # Generate children HTML in correct order
            ordered_children = get_children_order(flex_dir, element)
            for child in ordered_children:
                html += generate_element_html(child, indent + 1)

            # Closing tag
            html += f"{indent_str}</{tag}>\n"

        return html

    return generate_element_html(root)


def create_html_file(annotations_file: str, output_file: str):

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Layout</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
"""
    annotations = load_annotations(annotations_file)
    elements = parse_annotations(annotations)

    root = create_tree(elements)

    html += generate_html(root)

    html += """</body>
</html>"""

    # Write to file with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == "__main__":
    create_html_file("annotations.json", "output.html")
