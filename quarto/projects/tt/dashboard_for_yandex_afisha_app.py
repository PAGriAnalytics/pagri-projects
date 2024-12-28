import dash
from dash import dcc, html, Input, Output
from dash import no_update, ctx, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash_iconify import DashIconify
import dash_daq as daq
# импортируем библиотеки
import pandas as pd
from sqlalchemy import create_engine

# db_config = {'user': 'praktikum_student', # имя пользователя
#             'pwd': 'Sdf4$2;d-d30pp', # пароль
#             'host': 'rc1b-wcoijxj3yxfsf3fs.mdb.yandexcloud.net',
#             'port': 6432, # порт подключения
#             'db': 'data-analyst-zen-project-db'} # название базы данных

# connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
#                                                 db_config['pwd'],
#                                                 db_config['host'],
#                                                 db_config['port'],
#                                                 db_config['db'])
# engine = create_engine(connection_string)
# df = pd.read_sql('select * from dash_visits', engine)
# df = df.sort_values('dt')

titles_for_axis = dict(
    visits = ['Количество визитов', 'количество визитов', 0]
    , visits_pct = ['Количество визитов, %', 'количество визитов, %', 0]
    , dt = ['Дата', 'дата', 1]
    # categorical column ['Именительный падеж', 'для кого / чего', 'по кому чему']
    # Распределение долей по городу и тарифу с нормализацией по городу
    , item_topic = ['Тема карточки', 'темы карточки', 'теме карточки']
    , source_topic = ['Тема источника', 'темы источника', 'теме источника']
    , age_segment = ['Возрастная группа', 'возрастная группа', 'возрастной группе']
)

full_filter_icon = DashIconify(
      icon="bx:filter",
      color="green",
      width=30,
      height=30
)

partial_filter_icon = DashIconify(
      icon="prime:filter-fill",
      color="green",
      width=20,
      height=20
)
checklist_all_values_item_topic = df['item_topic'].unique()
checklist_all_values_age_segment = df['age_segment'].unique()
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
# Создание Dash приложения с использованием Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE, dbc_css])
filter_item_topic = html.Div([
        dbc.Row([
            dbc.Col(dbc.Button("Select All", id='select-all-button_item_topic', n_clicks=0, color="link")),
            dbc.Col(dbc.Button("Clear", id='clear-button_item_topic', n_clicks=0, color="link"))
        ]),
        dbc.Row([
            dbc.Col(
            dcc.Checklist(
            options=[{'label': topic, 'value': topic} for topic in checklist_all_values_item_topic],
            value=checklist_all_values_item_topic,
            id="checklist_item_topic",
            style={'maxHeight': '200px', 'overflowY': 'scroll', 'accent-color': 'transparent'}))
        ]),        
      dbc.Row([
        dbc.Col(dbc.Button("Cancel", id='cancel-button_item_topic', outline=True, color="secondary", className="me-1")),
        dbc.Col(dbc.Button("Apply", id='apply-button_item_topic', outline=True, color="success", className="me-1")),
        ])
        ])
popover_item_topic = html.Div(
        [
        dbc.Button(id="popover_item_topic_target", children='Фильтр по темам карточек', n_clicks=0), # color=None, style={'background-color': 'transparent', 'border': 'none'}),
        dbc.Popover(
            id='popover_item_topic',
            children=filter_item_topic,
            target="popover_item_topic_target",
            body=True,
            trigger="click",
            placement='right',
                )
            ]
        )
filter_age_segment = html.Div([
        dbc.Row([
            dbc.Col(dbc.Button("Select All", id='select-all-button_age_segment', n_clicks=0, color="link")),
            dbc.Col(dbc.Button("Clear", id='clear-button_age_segment', n_clicks=0, color="link"))
        ]),
        dbc.Row([
            dbc.Col(
            dcc.Checklist(
            options=[{'label': topic, 'value': topic} for topic in checklist_all_values_age_segment],
            value=checklist_all_values_age_segment,
            id="checklist_age_segment",
            style={'maxHeight': '180px', 'overflowY': 'scroll', 'accent-color': 'transparent'}))
        ]),        
      dbc.Row([
        dbc.Col(dbc.Button("Cancel", id='cancel-button_age_segment', outline=True, color="secondary", className="me-1")),
        dbc.Col(dbc.Button("Apply", id='apply-button_age_segment', outline=True, color="success", className="me-1")),
        ])
        ])
popover_age_segment = html.Div(
        [
        dbc.Button(id="popover_age_segment_target", children='Фильтр по возрастным категориям', n_clicks=0), # color=None, style={'background-color': 'transparent', 'border': 'none'}),
        dbc.Popover(
            id='popover_age_segment',
            children=filter_age_segment,
            target="popover_age_segment_target",
            body=True,
            trigger="click",
            placement='right',
                )
            ]
        )
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H4("Анализ взаимодействия пользователей с карточками статей Яндекс Дзен"),
                className="text-center text-primary font-weight-bold")
                # style={"padding": "5px", "border": "2px solid #007bff", "borderRadius": "5px", "backgroundColor": "#f8f9fa"})
        , dbc.Col(
            [dbc.Label('Фильтр по времени'),
        #     dcc.DatePickerRange(
        #     id='date-picker-range',
        #     start_date=df['dt'].min(),
        #     end_date=df['dt'].max(),
        #     display_format='YYYY-MM-DD',
        #     className="mb-4"
        # )
            dbc.Row([
                dbc.Col(dbc.Label('', id='date_range_slider_start_text', style={'fontSize': '12px', 'margin': '0', 'padding': '0'}), width=2),
                dbc.Col(dcc.RangeSlider(
                    id='date-picker-range',
                    min=0,
                    max=len(df) - 1,
                    value=[0, len(df) - 1],
                    marks=None,
                    step=1,  # шаг в 60 секунд
                ), width=8, style={'margin': '0', 'padding': '0'}),
                dbc.Col(dbc.Label('', id='date_range_slider_end_text', style={'fontSize': '12px', 'margin': '0', 'padding': '0'}), width=2)
            ])
            ], width=4),
    ]),
    dbc.Row([
        dbc.Col(dbc.Label('Дашборд фомирует интерактивные графики о событиях взаимодействия пользователей с карточками.\n Данные фильтруются по времени, теме карточки и возрастной категории.')),
        dbc.Col(popover_item_topic, width=3), 
        dbc.Col(popover_age_segment, width=3), 
    ]),
    
    
    dbc.Row([
        dbc.Col(
            dbc.Card(
               [
                   dbc.CardHeader('Количество визитов по темам карточек'),
                   dbc.CardBody(dcc.Graph(id='absolute-visits-by-item-graph'))]), width=4)
        , dbc.Col(
            dbc.Card(
               [
                   dbc.CardHeader('Количество визитов по темам карточек, %'),
                   dbc.CardBody(dcc.Graph(id='relative-visits-by-item-graph'))]), width=4)
        , dbc.Col(
            dbc.Card(
               [
                   dbc.CardHeader('Количество визитов по темам источников, %'),
                   dbc.CardBody(dcc.Graph(id='visits-by-source-graph'))]), width=4)
    ]),
    html.Br(),
    dbc.Row(
        dbc.Col(
            dbc.Card(
               [
                   dbc.CardHeader('Темы источников (столбцы) - темы карточек (строки)'),
                   dbc.CardBody(id='crosstab')]))),
    dcc.Store(id='store-checklist-value_item_topic', storage_type='memory'), 
    dcc.Store(id='store-checklist-value_age_segment', storage_type='memory')
], fluid=True)
@app.callback(
    [Output('date_range_slider_start_text', 'children'),
     Output('date_range_slider_end_text', 'children')],
    [Input('date-picker-range', 'value')]
)
def update_labels(selected_range):
    start_index, end_index = selected_range
    start_time = df['dt'].iloc[start_index].strftime('%H:%M:%S')
    end_time = df['dt'].iloc[end_index].strftime('%H:%M:%S')
    return start_time, end_time

@app.callback(
    Output('absolute-visits-by-item-graph', 'figure'),
    Output('relative-visits-by-item-graph', 'figure'),
    Output('visits-by-source-graph', 'figure'),
    Output('crosstab', 'children'),
    Input('date-picker-range', 'value'),
    Input('checklist_item_topic', 'value'),
    Input('checklist_age_segment', 'value'),
    # Input('age-segment-dropdown', 'value')
)
def update_graphs(value, selected_item_topics, selected_age_segments):
    # Фильтрация данных    
    if not selected_item_topics or not selected_age_segments or value[0] >= value[1]:
        return {}, {}, {}, {}
    filtered_df = df[
        (df['dt'] >= df['dt'].iloc[value[0]]) &
        (df['dt'] <= df['dt'].iloc[value[1]])
    ]
    # print('ok')
    # print(selected_item_topics)
    # print(selected_age_segments)
    filtered_df = filtered_df[filtered_df['item_topic'].isin(selected_item_topics)]
    filtered_df = filtered_df[filtered_df['age_segment'].isin(selected_age_segments)]
    filtered_df_origin = filtered_df.copy()
    top_item_topics = filtered_df.groupby('item_topic')['visits'].sum().sort_values(ascending=False).head(10).index.values
    filtered_df['item_topic'] = filtered_df['item_topic'].apply(lambda x: x if x in top_item_topics else 'Другое')
    df_aggregated_by_item_topic = filtered_df.groupby(['dt', 'item_topic'])[['visits']].sum()
    df_aggregated_by_item_topic['all_visits'] = df_aggregated_by_item_topic.groupby('dt')['visits'].transform('sum')
    df_aggregated_by_item_topic['visits_pct'] = df_aggregated_by_item_topic['visits'] * 100 / df_aggregated_by_item_topic['all_visits']
    df_aggregated_by_item_topic = df_aggregated_by_item_topic.reset_index()
    top_source_topic = filtered_df.groupby('source_topic')['visits'].sum().sort_values(ascending=False).head(10).index.values
    # print(filtered_df.shape[0])
    filtered_df['source_topic'] = filtered_df['source_topic'].apply(lambda x: x if x in top_source_topic else 'Другое')
    df_aggregated_by_source_topic = (filtered_df.groupby('source_topic')[['visits']].sum() *100 / filtered_df.visits.sum()).sort_values('visits', ascending=False).reset_index()
    config = dict(
        df = df_aggregated_by_item_topic
        , x = 'dt'  
        , y = 'visits'
        , category = 'item_topic'
        , width = None
        , height = None
        , orientation = 'v'
    )
    visits_by_item_topic_absolute_fig = pagri_data_tools.area(config, titles_for_axis)
    visits_by_item_topic_absolute_fig = visits_by_item_topic_absolute_fig.update_layout(title_text=None, showlegend=False, margin=dict(l=0, r=0, b=0, t=0))    
    config = dict(
        df = df_aggregated_by_item_topic
        , x = 'dt'  
        , y = 'visits_pct'
        , category = 'item_topic'
        , width = None
        , height = None
        , orientation = 'v'
    )
    # display(df_aggregated_by_source_topic)
    visits_by_item_topic_pct_fig = pagri_data_tools.area(config, titles_for_axis)
    visits_by_item_topic_pct_fig.update_layout(title_text=None, showlegend=False, margin=dict(l=0, r=0, b=0, t=0))    
    config = dict(
        df = df_aggregated_by_source_topic
        , x = 'source_topic'  
        , y = 'visits'
        , width = None
        , height = None
        , orientation = 'h'
        , showgrid_y = False
    )
    visits_by_source_topic_fig = pagri_data_tools.bar(config, titles_for_axis)
    visits_by_source_topic_fig = visits_by_source_topic_fig.update_layout(title_text=None, showlegend=False, margin=dict(l=0, r=0, b=0, t=0))    
    crosstab = filtered_df_origin.pivot_table(index = 'item_topic', columns = 'source_topic', values='visits', aggfunc='sum').fillna(0).astype(int).reset_index().rename(columns={'item_topic': ' '})
    rowData = crosstab.to_dict('records')
    table_component = dag.AgGrid(
        rowData=rowData, columnDefs=[{"field": i, 'headerName': i.replace('_', ' '), "cellStyle": {"fontSize": "14px"}, 'type': 'numeric', 'editable': False, "tooltipField": i, "minWidth": 100} if pd.api.types.is_numeric_dtype(crosstab[i])
                                        else {"field": i, 'headerName': i.replace('_', ' '), "cellStyle": {"fontSize": "14px"}, 'type': 'text', 'editable': False, "tooltipField": i, "minWidth": 100} for i in crosstab.columns]  # , 'type': 'numeric', "valueFormatter": {"function": "Number(params.value).toFixed(1)"}} , , 'autoSizeColumn': True
        # , columnSizeOptions = {"skipHeader": True}
        , columnSize="responsiveSizeToFit", defaultColDef={"sortable": True, "filter": False, "animateRows": True, "wrapHeaderText": True, "autoHeaderHeight": True}, dashGridOptions={"pagination": True, 'paginationPageSize': 10, "animateRows": True, "animateColumns": True}
        # ag-theme-quartz, ag-theme-quartz-dark, ag-theme-alpine, ag-theme-alpine-dark, ag-theme-balham, ag-theme-balham-dark, ag-theme-material.
    )
    return visits_by_item_topic_absolute_fig, visits_by_item_topic_pct_fig, visits_by_source_topic_fig, table_component

# @app.callback(
#     Output("my-ag-grid", "rowData"),
#     Input("store-checklist-value", 'data'),
# )
# def update_ag_grid(data):
#   if data is not None:
#     return ag_grid_data_df[ag_grid_data_df["value"].isin(data)].to_dict('records')
#   return no_update


@app.callback(
    [Output("popover_item_topic", "is_open"), Output("checklist_item_topic", "value", allow_duplicate=True), Output("store-checklist-value_item_topic", "data"),
     Output("popover_age_segment", "is_open"), Output("checklist_age_segment", "value", allow_duplicate=True), Output("store-checklist-value_age_segment", "data")],
    [Input("select-all-button_item_topic", 'n_clicks'), Input("clear-button_item_topic", "n_clicks"), Input("cancel-button_item_topic", 'n_clicks'), Input("apply-button_item_topic", "n_clicks")],
    [State("checklist_item_topic", "options"), State("checklist_item_topic", "value")],
    [Input("select-all-button_age_segment", 'n_clicks'), Input("clear-button_age_segment", "n_clicks"), Input("cancel-button_age_segment", 'n_clicks'), Input("apply-button_age_segment", "n_clicks")],
    [State("checklist_age_segment", "options"), State("checklist_age_segment", "value")],    
    prevent_initial_call=True
)
def update_popover(select_all_button_n_clicks_item_topic, clear_button_n_clicks_item_topic, cancel_n_clicks_item_topic, apply_n_clicks_item_topic, options_item_topic, value_item_topic,
                   select_all_button_n_clicks_age_segment, clear_button_n_clicks_age_segment, cancel_n_clicks_age_segment, apply_n_clicks_age_segment, options_age_segment, value_age_segment):
    # print(ctx.triggered_id)
    if ctx.triggered_id == 'select-all-button_item_topic':
        return no_update, checklist_all_values_item_topic, no_update, no_update, no_update, no_update

    elif ctx.triggered_id == 'clear-button_item_topic':
        return no_update, [], no_update, no_update, no_update, no_update

    elif ctx.triggered_id == 'cancel-button_item_topic':
        return False, checklist_all_values_item_topic, checklist_all_values_item_topic, no_update, no_update, no_update

    elif ctx.triggered_id == 'apply-button_item_topic':
        return False, no_update, value_item_topic, no_update, no_update, no_update
    
    if ctx.triggered_id == 'select-all-button_age_segment':
        return no_update, no_update, no_update, no_update, checklist_all_values_age_segment, no_update

    elif ctx.triggered_id == 'clear-button_age_segment':
        return no_update, no_update, no_update, no_update, [], no_update

    elif ctx.triggered_id == 'cancel-button_age_segment':
        return no_update, no_update, no_update, False, checklist_all_values_age_segment, checklist_all_values_age_segment

    elif ctx.triggered_id == 'apply-button_age_segment':
        return no_update, no_update, no_update, False, no_update, value_age_segment


    return no_update

if __name__ == '__main__':
    app.run_server(debug=False)