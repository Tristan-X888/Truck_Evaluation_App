# Truck_Evaluation_App
Truck_Evaluation_App is a Streamlit dashboard that analyses truck data from Excel files to decide whether to KEEP, SELL, or INSPECT each unit. It includes filters, charts, and Excel export, helping fleet managers make smart decisions based on cost, usage, ownership, and resale value.

🔍 Features:
✅ Upload Interface

Accepts 6 Excel files: maintenance, finance, odometer, vehicle distance, stub data, and truck paper listings

📊 Automated Decision Engine

Combines key metrics like total repair cost, ownership type, loan burden, usage history, and resale value

Assigns trucks into one of three categories: KEEP, SELL, or INSPECT

📈 Dynamic Charts

Pie Chart: Breakdown of fleet decisions

Bar Chart: Repair cost per truck

Line Chart: Cost vs. distance trends

🔎 Interactive Filters

Filter results by decision type and ownership class

📤 Excel Export

Download the filtered table directly as an Excel report

📁 Required Input Files:
Upload the following 6 .xlsx files through the app interface:

maintenancepo-truck.xlsx

truck-finance.xlsx

vehicle-distance-traveled.xlsx

truck-odometer-data-week-.xlsx

stub-data.xlsx

truck-paper.xlsx

⚙️ How to Run:
Install dependencies:
pip install streamlit pandas openpyxl plotly

Run the app:
streamlit run truck_evaluation_app.py

📤 Output:
Displays real-time evaluations
Export filtered evaluations to Excel (filtered_truck_evaluation.xlsx)
