# NASTRAN Outlier Detection and Visualization Tool

This Python tool reads NASTRAN `.dat` and `.op2` files to identify and visualize elements that exhibit statistically high values across multiple load cases.

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
