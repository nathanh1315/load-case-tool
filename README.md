# NASTRAN Outlier Detection and Visualization Tool

This Python tool reads NASTRAN `.dat` and `.op2` files to identify and visualize elements that exhibit statistically high values across multiple load cases. This tool was developed and tested using a simplified FEMAP model: a rectangular shell mesh fixed along one edge to represent the wing-fuselage connection.

## Features
- Parses `.dat` for element-to-node mapping and node coordinates.
- Reads `.op2` stress results and flags elements with stress above a statistical threshold.
- Creates a heatmap showing how often elements are flagged.

## Requirements
- Developed and tested with Python 3.11
- Dependencies listed in `requirements.txt`

## Usage
1. Make sure `Analysis_main.py`, `Analysis_helper.py`, and your `.dat` and `.op2` files are in the same folder.  
2. Run `Analysis_main.py`.  
3. Choose the stress component (`oxx`, `oyy`, or `von_mises`) when prompted.  
4. View the generated heatmap of flagged elements.

## Files
- `Analysis_main.py`: Main script for user interaction and running analysis.  
- `Analysis_helper.py`: Functions to parse files, flag elements, and plot heatmap.

## Output
This tool generates a heatmap visualizing how frequently each element was flagged as an outlier across multiple load cases. Areas with higher intensity indicate elements that are consistently identified as anomalous, helping prioritize further inspection or redesign.

<img width="1090" height="816" alt="image" src="https://github.com/user-attachments/assets/a57c6eb6-f357-4aa4-825e-cb61dbd83d28" />
