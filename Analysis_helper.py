from pyNastran.bdf.bdf import BDF
from pyNastran.op2.op2 import OP2
import pandas as pd
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

def get_geometry(bdf_filename):

    """
    Loads a BDF/dat file and returns the element-to-node relationships
    and the 3D coordinates of all the nodes.
    """

    # Create a BDF object and read the file
    bdf = BDF()
    bdf.read_bdf(bdf_filename)

    # Build a dictionary that maps each element to its connected nodes
    # print(bdf.elements.items())
    elem_to_nodes = {}
    for eid, elem in bdf.elements.items():
        elem_to_nodes[eid] = elem.node_ids

    # Build a dictionary that maps each node to its (x, y, z) position
    # print(bdf.nodes.items())
    node_coords = {}
    for nid, node in bdf.nodes.items():
        node_coords[nid] = node.get_position()

    # Return both mappings so we can use them for plotting or further analysis
    return elem_to_nodes, node_coords

def get_flagged_elements(op2_file, stress_component="von_mises"):

    """
    Reads an OP2 file and finds which elements have unusually high stress values
    for the chosen stress component (like 'von_mises', 'oxx', or 'oyy').

    Returns a dictionary with each load case and a list of flagged elements that
    stand out as stress outliers.
    """

    # First, check that the user asked for a valid stress component
    valid_components = ["oxx", "oyy", "von_mises"]
    if stress_component not in valid_components:
        raise ValueError(f"Invalid stress_component '{stress_component}'. Valid options are: {valid_components}")

    # Load the OP2 file using pyNastran
    op2 = OP2()
    op2.read_op2(op2_file)

    # Get the stress results for CQUAD4 elements (plate elements)
    stress_obj = op2.op2_results.stress.cquad4_stress

    # Loop over each load case’s stress data
    # print(stress_obj.items())
    flagged_elements_by_case = {}
    for case_id, plate_stress in stress_obj.items():

        # Get the stress data and element-node mapping for this case
        stress_data = plate_stress.data[0]
        element_node = plate_stress.element_node

        # Put into dataframe for easier manipulation
        df = pd.DataFrame(
            stress_data,
            columns=["fiber_dist", "oxx", "oyy", "txy", "angle", "omax", "omin", "von_mises"]
        )

        # Add element and node columns to the dataframe
        df["element"] = element_node[:, 0]
        df["node"] = element_node[:, 1]

        # Keep only the columns we care about: element, node, and selected stress component
        filtered_df = df[["element", "node", stress_component]]

        # For each element, find the maximum stress value (across all its nodes)
        max_stress = filtered_df.groupby('element')[stress_component].max().reset_index()
        
        # Compute statistics to find threshhold for outliers
        mean_stress = max_stress[stress_component].mean()
        std_vm = max_stress[stress_component].std()
        threshold = mean_stress + 2 * std_vm

        # Flag elements whose max stress exceeds the threshold
        max_stress['is_outlier'] = max_stress[stress_component] > threshold

        # Collect the element IDs that are outliers
        flagged_elements = max_stress[max_stress['is_outlier']]['element'].tolist()

        # Store the flagged elements for this load case in the results dictionary
        flagged_elements_by_case[f"Case_{case_id}"] = flagged_elements

    # Return all flagged elements grouped by load case
    return flagged_elements_by_case

def create_element_heatmap(flagged_elements_by_case, elem_to_nodes, node_coords, selected_component):
    """
    Creates a heatmap of flagged elements across multiple load cases.
    
    Parameters:
    - flagged_elements_by_case: dict of {case_name: list of flagged element IDs}
    - elem_to_nodes: dict of {element ID: list of node IDs}
    - node_coords: dict of {node ID: np.array([x, y, z])}
    - stress_component: the stress component used for flagging (e.g., 'von_mises', 'oxx', 'oyy')
    """

    # Flatten all the flagged element IDs into one list
    all_flagged_elements = []
    for element_list in flagged_elements_by_case.values():
        all_flagged_elements.extend(element_list)

    # Count how many times each element showed up flagged
    elements_count = Counter(all_flagged_elements)

    # Find the center point of each element — average the positions of its nodes in XY plane
    element_centroids = {}
    for elem_id, node_ids in elem_to_nodes.items():
        coords = []
        for nid in node_ids:
            coord = node_coords[nid][:2] #only need x and y coordinates
            coords.append(coord)
        centroid = np.mean(coords, axis = 0)
        element_centroids[elem_id] = centroid

    # Set up the plot canvas
    fig, ax = plt.subplots()
    ax.set_title(f"Heatmap of flagged elements for: {selected_component}")

    # Draw every element as a light gray polygon outline, no fill — this is the wing mesh
    all_patches = []
    for elem_id, node_ids in elem_to_nodes.items():
        coords = []
        for nid in node_ids:
            coord = node_coords[nid][:2] #only need x and y coordinates
            coords.append(coord)
        polygon = Polygon(coords, closed=True, edgecolor='lightgray', facecolor='none', linewidth=0.5)
        all_patches.append(polygon)
    all_pc = PatchCollection(all_patches, match_original=True)
    ax.add_collection(all_pc)

    # Prepare the colored patches for flagged elements
    flagged_patches = []
    flagged_colors = []

    # Find the max count so we can scale the colors
    max_count = max(elements_count.values())

    # For each flagged element, make a filled polygon colored by how often it got flagged
    for elem_id, count in elements_count.items():
        node_ids = elem_to_nodes[elem_id]
        coords = []
        for nid in node_ids:
            coord = node_coords[nid][:2] #only need x and y coordinates
            coords.append(coord)
        polygon = Polygon(coords, closed=True, edgecolor='none')
        flagged_patches.append(polygon)

        # Normalize count for colormap [0,1]
        norm_count = count / max_count
        flagged_colors.append(norm_count)
    
    # Add all flagged polygons to the plot with a color scheme and some transparency
    flagged_pc = PatchCollection(flagged_patches, cmap='inferno', alpha=0.7)
    flagged_pc.set_array(np.array(flagged_colors))
    ax.add_collection(flagged_pc)

    # Add a colorbar to show frequency of flagged elements
    fig.colorbar(flagged_pc, ax=ax, label='Normalized frequency of flagged elements')

    # Let the plot zoom to fit everything and keep the shape from getting stretched out
    ax.autoscale()
    ax.set_aspect('equal')
    plt.show()
