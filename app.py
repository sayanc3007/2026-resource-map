import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# 1. LOAD THE EXCEL FILE
file_path = '2026 snapshot.xlsx'
df = pd.read_excel(file_path, sheet_name=0)
df = df[~df[df.columns[0]].astype(str).str.contains('Total', case=False, na=False)]
df = df[~df[df.columns[0]].astype(str).str.contains('Unallocated', case=False, na=False)]
df = df.dropna(subset=[df.columns[0]])  

# 2. EXTRACT RELEVANT COLUMNS (D through P correspond to indices 3 through 15)
country_col = df.columns[0] # Column A (Country Name)
widget_columns = df.columns[3:16].tolist() # Columns D through P

# 3. CLEAN DATA
# Ensure all selected columns are numeric (converts "-" or missing values to 0)
for col in widget_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 4. INITIALIZE THE DASH APP
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("2026 Snapshot: Global Resource Distribution", style={'fontFamily': 'Arial', 'textAlign': 'center'}),
   
    html.Div([
        html.Label("Select Resource Categories to Calculate (Columns D-P):", style={'fontWeight': 'bold'}),
        # Multi-select Checkboxes
        dcc.Checklist(
            id='resource-checkboxes',
            options=[{'label': col, 'value': col} for col in widget_columns],
            value=[widget_columns[0]],  # Select the first checkbox by default to show initial data
            inline=True,
            style={'fontFamily': 'Arial', 'padding': '15px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px', 'backgroundColor': '#f9f9f9', 'borderRadius': '8px'}
        )
    ], style={'marginBottom': '20px'}),
   
    # Choropleth Map Container
    dcc.Graph(id='choropleth-map', style={'height': '75vh'})
])

# 5. DEFINE INTERACTIVE LOGIC (Callback)
@app.callback(
    Output('choropleth-map', 'figure'),
    Input('resource-checkboxes', 'value')
)
def update_map(selected_cols):
    # Handle empty selection
    if not selected_cols:
        return px.choropleth(title="Please select at least one resource category from the checkboxes above.")
       
    # Dynamically sum the selected columns for each country row
    df['Dynamic_Total'] = df[selected_cols].sum(axis=1)
   
    brown_shades = ['#f9f6f0', '#e3d2bf', '#bf9f7d', '#966e4a', '#6e4523', '#401e05']

    fig = px.choropleth( 
        df, 
        locations=country_col, 
        locationmode='country names', 
        color='Dynamic_Total', 
        hover_name=country_col, 
        hover_data={country_col: False, 'Dynamic_Total': ':.2f'}, 
        color_continuous_scale=brown_shades, 
        labels={'Dynamic_Total': 'Total Resources'}, # <--- ADD THIS LINE 
        title="Total Resources for Selected Categories"   
    )
   
    # Layout styling for a clean world map
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showocean=True, oceancolor="LightBlue",
            showland=True, landcolor="White"
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        coloraxis_colorbar=dict(title="Total Resources")
    )
   
    return fig

# 6. RUN THE SERVER
if __name__ == '__main__':
    print("Starting dashboard... Open the provided http://127.0.0.1:8050 link in your web browser.")
    app.run(debug=True)
