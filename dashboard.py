import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from sklearn.cluster import KMeans

# Supongamos que ya tienes los datos cargados en el DataFrame 'data'
# Aplica clustering para generar la columna 'Cluster' si no existe
X = data[['TotalSpending', 'Year']]  # Reemplaza con las columnas adecuadas
kmeans = KMeans(n_clusters=4, random_state=0)
data['Cluster'] = kmeans.fit_predict(X)

# Initialize the Dash application
app = dash.Dash(__name__)

# Prepare cluster summary
cluster_summary = data.groupby('Cluster').agg({
    'TotalSpending': 'mean',
    'Year': 'mean',
}).reset_index()

# Dashboard Layout
app.layout = html.Div([
    html.H1("Construction Spending Analysis"),

    # Filters
    html.Div([
        html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in sorted(data['Year'].unique())],
                value=sorted(data['Year'].unique()),
                multi=True
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Region:"),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': region, 'value': region} for region in sorted(data['Region'].unique())],
                value=sorted(data['Region'].unique()),
                multi=True
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
    ]),

    # Scatter Plot: Spending vs Year
    dcc.Graph(id='scatter-plot'),

    # Bar Chart: Average Spending by Cluster
    html.H2("Cluster Summary"),
    dcc.Graph(id='cluster-bar'),

    # Line Chart: Spending Trend by Year
    html.H2("Construction Spending Trend by Year"),
    dcc.Graph(id='trend-line'),
])

# Callback to update the scatter plot with labels
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)
def update_scatter(selected_years, selected_regions):
    filtered_data = data[data['Year'].isin(selected_years) & data['Region'].isin(selected_regions)]
    fig = px.scatter(
        filtered_data, x='Year', y='TotalSpending', color='Cluster',
        title='Construction Spending vs Year by Cluster',
        hover_data=['Region']
    )
    # Adding labels for each point
    fig.update_traces(textposition='top center')
    return fig

# Callback to update the clusters bar chart with labels
@app.callback(
    Output('cluster-bar', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)
def update_cluster_bar(selected_years, selected_regions):
    filtered_data = data[data['Year'].isin(selected_years) & data['Region'].isin(selected_regions)]
    cluster_summary = filtered_data.groupby('Cluster').agg({'TotalSpending': 'mean'}).reset_index()
    fig = px.bar(
        cluster_summary, x='Cluster', y='TotalSpending',
        title='Average Spending by Cluster',
        labels={'TotalSpending': 'Average Spending (in USD)', 'Cluster': 'Cluster'}
    )
    # Adding labels on top of the bars
    fig.update_traces(texttemplate='$%{y:,.2f}', textposition='outside')
    return fig

# Callback to update the spending trend by year with labels
@app.callback(
    Output('trend-line', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)
def update_trend_line(selected_years, selected_regions):
    filtered_data = data[data['Year'].isin(selected_years) & data['Region'].isin(selected_regions)]
    trend = filtered_data.groupby('Year').agg({'TotalSpending': 'sum'}).reset_index()
    fig = px.line(
        trend, x='Year', y='TotalSpending',
        title='Total Construction Spending Trend by Year',
        markers=True
    )
    # Adding labels on the line points
    fig.update_traces(texttemplate='$%{y:,.2f}', textposition='top center')
    return fig

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)


###open in port http://127.0.0.1:8050/