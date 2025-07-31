from Analysis_helper import get_geometry, get_flagged_elements, create_element_heatmap


# ----- File Paths -----
bdf_file = "Wing_for_tool-0001.dat"
op2_file = "wing_for_tool-0016.op2"

# List of stress options for user selection
stress_options = [
    ("oxx", "Normal stress x direction"),
    ("oyy", "Normal stress y direction"),
    ("von_mises", "Equivalent von Mises stress"),
]

# Print options for user to select
print("Select the stress component to analyze:")
for i, (key, desc) in enumerate(stress_options, start=1):
    print(f"{i}. {desc} ({key})")

# Keep asking the user until they enter a valid choice
while True:
    try:
        # Prompt user for a number corresponding to the stress component
        choice = int(input("Enter the number corresponding to your choice: "))

        # Check if the choice is within the valid range
        if 1 <= choice <= len(stress_options):

            # If valid, get the key for the selected stress component
            selected_component = stress_options[choice - 1][0]
            break  # valid input, exit loop
        else:
            # Inform user if the number is out of valid range
            print(f"Please enter a number between 1 and {len(stress_options)}.")
    except ValueError:
        # Handle the case where input is not an integer
        print("Invalid input. Please enter a valid number.")

print(selected_component)

# ----- Step 1: Parse Geometry -----
elem_to_nodes, node_coords = get_geometry(bdf_file)

# ----- Step 2: Flag Elements from .op2 -----
flagged_elements_by_case = get_flagged_elements(op2_file, selected_component)
print(flagged_elements_by_case)

# ----- Step 3: Visualize Heatmap -----
create_element_heatmap(flagged_elements_by_case, elem_to_nodes, node_coords)
