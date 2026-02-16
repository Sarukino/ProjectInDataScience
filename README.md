# Project in Data Science – Volunteer Platform Visualization

This repository contains:

## Project_POC folder (Core project)

- `main.py`  
  The main Dash / Plotly application for visualizing and comparing volunteer platforms.

- `volunteer_data.xlsx`  
  The Excel workbook with all platform and feature data  
  (sheets: `Platforms`, `Features`, `PlatformFeatures`).

The core of the project is a small Dash web application.  
`main.py` reads the data from `volunteer_data.xlsx` (platforms, features, languages and links) and builds
an interactive interface where the user can explore volunteer platforms.

The main view is a sunburst chart that shows which platforms support which feature groups. On the left-hand side the user can filter by feature and by platform language. When a platform is clicked, a detail card appears with its name, main language, supported features and a link to the website. Two platforms can be marked for comparison; in that case the app hides the chart and shows both platforms side by side with a list of features that are unique to each of them.

In short, `main.py` plus `volunteer_data.xlsx` form the working prototype that demonstrates how heterogeneous volunteer platforms can be explored and compared in an interactive way.


> These two files together form the **final project deliverable**.

## Additional Python files

There are several other `.py` files in the folder.  
These are earlier prototypes, experiments, or concept versions that were used during development,  
but are **not part of the final application**.

## `files` folder

The `files` directory contains:

- different document versions (requirements, descriptions, etc.),
- and a few screenshots taken during development.

These documents were **required for the course** and document the project’s evolution.
