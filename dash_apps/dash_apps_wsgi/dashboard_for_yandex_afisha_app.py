import dash
from dash import dcc, html, Input, Output
from dash import no_update, ctx, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import dash_ag_grid as dag
# импортируем библиотеки
import pandas as pd
from sqlalchemy import create_engine

colorway_for_bar = ['rgba(128, 60, 170, 0.9)', '#049CB3', "rgba(112, 155, 219, 0.9)", "rgba(99, 113, 156, 0.9)", '#5c6bc0', '#B690C4', 'rgba(17, 100, 120, 0.9)', 'rgba(194, 143, 113, 0.8)', '#B690C4', '#03A9F4', '#8B9467', '#a771f2', 'rgba(102, 204, 204, 0.9)', 'rgba(168, 70, 90, 0.9)', 'rgba(50, 152, 103, 0.8)', '#8F7A7A', 'rgba(156, 130, 217, 0.9)'
                    ]
# default setting for Plotly express
px.defaults.template = "simple_white"
px.defaults.color_continuous_scale = color_continuous_scale = [
    [0, 'rgba(0.018, 0.79, 0.703, 1.0)'],
    [0.5, 'rgba(64, 120, 200, 0.9)'],
    [1, 'rgba(128, 60, 170, 0.9)']
]
# px.defaults.color_discrete_sequence = colorway_for_line
px.defaults.color_discrete_sequence = colorway_for_bar

def base_graph_for_bar_line_area(config: dict, titles_for_axis: dict = None, graph_type: str = 'bar'):
    # Проверка входных данных
    if not isinstance(config, dict):
        raise TypeError("config must be a dictionary")
    if 'df' not in config or not isinstance(config['df'], pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame")
    if 'x' not in config or not isinstance(config['x'], str):
        raise ValueError("x must be a string")
    if 'y' not in config or not isinstance(config['y'], str):
        raise ValueError("y must be a string")
    if 'func' in config and not isinstance(config['func'], str):
        raise ValueError("func must be a string")
    if 'barmode' in config and not isinstance(config['barmode'], str):
        raise ValueError("barmode must be a string")
    if 'func' not in config:
        config['func'] = None
    if 'barmode' not in config:
        config['barmode'] = 'group'
    if 'width' not in config:
        config['width'] = None
    if 'height' not in config:
        config['height'] = None
    if 'text' not in config:
        config['text'] = False
    if 'textsize' not in config:
        config['textsize'] = 14
    if 'xaxis_show' not in config:
        config['xaxis_show'] = True
    if 'yaxis_show' not in config:
        config['yaxis_show'] = True
    if 'showgrid_x' not in config:
        config['showgrid_x'] = True
    if 'showgrid_y' not in config:
        config['showgrid_y'] = True
    if 'sort' not in config:
        config['sort'] = True
    if 'top_n_trim_axis' not in config:
        config['top_n_trim_axis'] = None
    if 'top_n_trim_legend' not in config:
        config['top_n_trim_legend'] = None
    if 'sort_axis' not in config:
        config['sort_axis'] = True
    if 'sort_legend' not in config:
        config['sort_legend'] = True
    if 'textposition' not in config:
        config['textposition'] = None
    if 'legend_position' not in config:
        config['legend_position'] = 'right'
    if 'decimal_places' not in config:
        config['decimal_places'] = 1
    if 'show_group_size' not in config:
        config['show_group_size'] = False
    if pd.api.types.is_numeric_dtype(config['df'][config['y']]) and 'orientation' in config and config['orientation'] == 'h':
        config['x'], config['y'] = config['y'], config['x']

    if titles_for_axis:
        if not (config['func'] is None) and config['func'] not in ['mean', 'median', 'sum', 'count', 'nunique']:
            raise ValueError("func must be in ['mean', 'median', 'sum', 'count', 'nunique']")
        func_for_title = {'mean': ['Среднее', 'Средний', 'Средняя', 'Средние'], 'median': [
            'Медианное', 'Медианный', 'Медианная', 'Медианные'], 'sum': ['Суммарное', 'Суммарный', 'Суммарная', 'Суммарное']
            , 'count': ['Общее', 'Общее', 'Общее', 'Общие']}
        config['x_axis_label'] = titles_for_axis[config['x']][0]
        config['y_axis_label'] = titles_for_axis[config['y']][0]
        config['category_axis_label'] = titles_for_axis[config['category']
                                                ][0] if 'category' in config else None
        func = config['func']
        if pd.api.types.is_numeric_dtype(config['df'][config['y']]):
            numeric = titles_for_axis[config["y"]][1]
            cat = titles_for_axis[config["x"]][1]
            suffix_type = titles_for_axis[config["y"]][2]
        else:
            numeric = titles_for_axis[config["x"]][1]
            cat = titles_for_axis[config["y"]][1]
            suffix_type = titles_for_axis[config["x"]][2]
        if func == 'nunique':
            numeric_list = numeric.split()[1:]
            title = f"Количество уникальных {' '.join(numeric_list)}"
            title += f' в зависимости от {cat}'
        elif func is None:
            title = f' {numeric.capitalize()} в зависимости от {cat}'
        else:
            title = f'{func_for_title[func][suffix_type]}'
            title += f' {numeric} в зависимости от {cat}'
        if 'category' in config and config['category']:
            title += f' и {titles_for_axis[config["category"]][1]}'
        config['title'] = title
    else:
        if 'x_axis_label' not in config:
            config['x_axis_label'] = None
        if 'y_axis_label' not in config:
            config['y_axis_label'] = None
        if 'category_axis_label' not in config:
            config['category_axis_label'] = None
        if 'title' not in config:
            config['title'] = None
    if 'category' not in config:
        config['category'] = None
        config['category_axis_label'] = None
    if not isinstance(config['category'], str) and config['category'] is not None:
        raise ValueError("category must be a string")

    def human_readable_number(x, decimal_places):
        format_string = f"{{:.{decimal_places}f}}"

        if x >= 1e6 or x <= -1e6:
            return f"{format_string.format(x / 1e6)} M"
        elif x >= 1e3 or x <= -1e3:
            return f"{format_string.format(x / 1e3)} k"
        else:
            return format_string.format(x)

    def prepare_df(config: dict):
        df = config['df']
        color = [config['category']] if config['category'] else []
        if not (pd.api.types.is_numeric_dtype(df[config['x']]) or pd.api.types.is_numeric_dtype(df[config['y']])):
            raise ValueError("At least one of x or y must be numeric.")
        elif pd.api.types.is_numeric_dtype(df[config['y']]):
            cat_columns = [config['x']] + color
            num_column = config['y']
        else:
            cat_columns = [config['y']] + color
            num_column = config['x']
        if config['func'] is None:
            func = 'first'
        else:
            func = config.get('func', 'mean')  # default to 'mean' if not provided
        if pd.api.types.is_numeric_dtype(config['df'][config['y']]):
            ascending = False
        else:
            ascending = True
        func_df = (df[[*cat_columns, num_column]]
                  .groupby(cat_columns, observed=True)
                  .agg(num=(num_column, func), count=(num_column, 'count'))
                  .reset_index())
        if config['sort_axis']:
            func_df['temp'] = func_df.groupby(cat_columns[0], observed=True)[
                'num'].transform('sum')
            func_df = (func_df.sort_values(['temp', 'num'], ascending=ascending)
                    .drop('temp', axis=1)
                    )
        if not config['sort_legend']:
            if config['sort_axis']:
                func_df = (func_df.sort_values([cat_columns[0], cat_columns[1]], ascending=[False, True])
                        )
        func_df['count'] = func_df['count'].apply(
            lambda x: f'= {x}' if x <= 1e3 else 'больше 1000')


        return func_df.rename(columns={'num': num_column})
    df_for_fig = prepare_df(config)
    if config['top_n_trim_axis']:
        df_for_fig = df_for_fig.iloc[:config['top_n_trim_axis']]
    # if config['top_n_trim_legend']:
    #     df_for_fig = pd.concat([df_for_fig['data'].iloc[:, :config['top_n_trim_legend']], df_for_fig['data'].iloc[:, :config['top_n_trim_legend']]], axis=1, keys=['data', 'customdata'])
    # display(df_for_fig)
    x = df_for_fig[config['x']].values
    y = df_for_fig[config['y']].values
    x_axis_label = config['x_axis_label']
    y_axis_label = config['y_axis_label']
    color_axis_label = config['category_axis_label']
    color = df_for_fig[config['category']
                      ].values if config['category'] else None
    custom_data = [df_for_fig['count']]
    if 'text' in config and config['text']:
        if pd.api.types.is_numeric_dtype(config['df'][config['y']]):
            text = [human_readable_number(el, config['decimal_places']) for el in y]
        else:
            text = [human_readable_number(el, config['decimal_places']) for el in x]
    else:
        text = None
    # display(df_for_fig)
    # display(custom_data)
    if graph_type == 'bar':
        fig = px.bar(x=x, y=y, color=color,
                    barmode=config['barmode'], text=text, custom_data=custom_data)
    elif graph_type == 'line':
        fig = px.line(x=x, y=y, color=color,
                    text=text, custom_data=custom_data)
    elif graph_type == 'area':
        fig = px.area(x=x, y=y, color=color,
                    text=text, custom_data=custom_data)
    color = []
    for trace in fig.data:
        color.append(trace.marker.color)
    if x_axis_label:
        hovertemplate_x = f'{x_axis_label} = '
    else:
        hovertemplate_x = f'x = '
    if x_axis_label:
        hovertemplate_y = f'{y_axis_label} = '
    else:
        hovertemplate_y = f'y = '
    if x_axis_label:
        hovertemplate_color = f'<br>{color_axis_label} = '
    else:
        hovertemplate_color = f'color = '
    if pd.api.types.is_numeric_dtype(config['df'][config['y']]):
        hovertemplate = hovertemplate_x + \
            '%{x}<br>' + hovertemplate_y + '%{y:.4s}'
    else:
        hovertemplate = hovertemplate_x + \
            '%{x:.4s}<br>' + hovertemplate_y + '%{y}'
    if config['category']:
        hovertemplate += hovertemplate_color + '%{data.name}'
    if config['show_group_size']:
        hovertemplate += f'<br>Размер группы '
        hovertemplate += '%{customdata[0]}'
    # hovertemplate += f'<br>cnt_in_sum_pct = '
    # hovertemplate += '%{customdata[1]}'
    hovertemplate += '<extra></extra>'
    fig.update_traces(hovertemplate=hovertemplate, hoverlabel=dict(bgcolor="white"), textfont=dict(
        family='Segoe UI', size=config['textsize']  # Размер шрифта
        # color='black'  # Цвет текста
    ) # Положение текстовых меток (outside или inside))
    )
    if graph_type == 'bar':
        fig.update_traces(textposition='auto')
    elif graph_type == 'line':
        fig.update_traces(textposition='top center')
    elif graph_type == 'area':
        fig.update_traces(textposition='top center')
    fig.update_layout(
        # , title={'text': f'<b>{title}</b>'}
        # , margin=dict(l=50, r=50, b=50, t=70)
        margin=dict(t=80),
        width=config['width'], height=config['height'],
        title={'text': config["title"]}, xaxis_title=x_axis_label, yaxis_title=y_axis_label,
        title_font=dict(size=16, color="rgba(0, 0, 0, 0.7)"),
        font=dict(size=14, family="Segoe UI", color="rgba(0, 0, 0, 0.7)"),
        xaxis_title_font=dict(size=14, color="rgba(0, 0, 0, 0.7)"),
        yaxis_title_font=dict(size=14, color="rgba(0, 0, 0, 0.7)"),
        xaxis_tickfont=dict(size=14, color="rgba(0, 0, 0, 0.7)"),
        yaxis_tickfont=dict(size=14, color="rgba(0, 0, 0, 0.7)"),
        xaxis_linecolor="rgba(0, 0, 0, 0.4)",
        yaxis_linecolor="rgba(0, 0, 0, 0.4)",
        xaxis_tickcolor="rgba(0, 0, 0, 0.4)",
        yaxis_tickcolor="rgba(0, 0, 0, 0.4)",
        legend_title_font_color='rgba(0, 0, 0, 0.7)',
        legend_title_font_size = 14,
        legend_font_color='rgba(0, 0, 0, 0.7)',
        hoverlabel=dict(bgcolor="white"), xaxis=dict(
            visible=config['xaxis_show'], showgrid=config['showgrid_x'], gridwidth=1, gridcolor="rgba(0, 0, 0, 0.1)"
        ), yaxis=dict(
            visible=config['yaxis_show'], showgrid=config['showgrid_y'], gridwidth=1, gridcolor="rgba(0, 0, 0, 0.07)"
        ),
        legend=dict(
            title_font_color="rgba(0, 0, 0, 0.5)", font_color="rgba(0, 0, 0, 0.5)"
        )
    )
    if pd.api.types.is_numeric_dtype(config['df'][config['x']]):
        # Чтобы сортировка была по убыванию вернего значения, нужно отсортировать по последнего значению в x
        traces = list(fig.data)
        traces.sort(key=lambda x: x.x[-1])
        fig.data = traces
        color = color[::-1]
        for i, trace in enumerate(fig.data):
            trace.marker.color = color[i]
        fig.update_layout(legend={'traceorder': 'reversed'})
    if config['textposition']:
        fig.update_traces(textposition=config['textposition'])
    if config['legend_position'] == 'top':
        fig.update_layout(
            yaxis = dict(
                domain=[0, 0.95]
            )
            , legend = dict(
                title_text=color_axis_label
                , title_font_color='rgba(0, 0, 0, 0.7)'
                , font_color='rgba(0, 0, 0, 0.7)'
                , orientation="h"  # Горизонтальное расположение
                , yanchor="top"    # Привязка к верхней части
                , y=1.05         # Положение по вертикали (отрицательное значение переместит вниз)
                , xanchor="center" # Привязка к центру
                , x=0.5              # Центрирование по горизонтали
            )
        )
    elif config['legend_position'] == 'right':
        fig.update_layout(
                legend = dict(
                title_text=color_axis_label
                , title_font_color='rgba(0, 0, 0, 0.7)'
                , font_color='rgba(0, 0, 0, 0.7)'
                , orientation="v"  # Горизонтальное расположение
                # , yanchor="bottom"    # Привязка к верхней части
                , y=0.8         # Положение по вертикали (отрицательное значение переместит вниз)
                # , xanchor="center" # Привязка к центру
                # , x=0.5              # Центрирование по горизонтали
            )
        )
    else:
        raise ValueError("Invalid legend_position. Please choose 'top' or 'right'.")
    return fig

def bar(config: dict, titles_for_axis: dict = None):
    """
    Creates a bar chart using the Plotly Express library.

    Parameters:
    config (dict): A dictionary containing parameters for creating the chart.
        - df (DataFrame): A DataFrame containing data for creating the chart.
        - x (str): The name of the column in the DataFrame to be used for creating the X-axis.
        - x_axis_label (str): The label for the X-axis.
        - y (str): The name of the column in the DataFrame to be used for creating the Y-axis.
        - y_axis_label (str): The label for the Y-axis.
        - category (str): The name of the column in the DataFrame to be used for creating categories.
        If None or an empty string, the chart will be created without category.
        - top_n_trim_axis (int): The number of top categories axis to include in the chart.
        - top_n_trim_legend (int): The number of top categories legend to include in the chart.
        - sort_axis (bool): Whether to sort the categories on the axis (default is True).
        - sort_legend (bool): Whether to sort the categories in the legend (default is True).
        - category_axis_label (str): The label for the categories.
        - title (str): The title of the chart.
        - func (str): The function to be used for aggregating data (default is 'mean'). May be mean, median, sum, count, nunique
        - barmode (str): The mode for displaying bars (default is 'group').
        - width (int): The width of the chart (default is None).
        - height (int): The height of the chart (default is None).
        - text (bool):  Whether to display text on the chart (default is False).
        - textsize (int): Text size (default 14)
        - textposition (str): Text position (default 'auto'). May be 'auto', 'inside', 'outside', 'none'
        - xaxis_show (bool):  Whether to show the X-axis (default is True).
        - yaxis_show (bool):  Whether to show the Y-axis (default is True).
        - showgrid_x (bool):   Whether to show grid on X-axis (default is True).
        - showgrid_y (bool):   Whether to show grid on Y-axis (default is True).
        - legend_position (str): Положение легенды ('top', 'right')
        - decimal_places (int): The number of decimal places to display (default is 2).
        - show_group_size (bool):  Whether to show the group size (default is False).

    titles_for_axis (dict):  A dictionary containing titles for the axes.

    Returns:
    fig (plotly.graph_objs.Figure): The created chart.

    Example:
    titles_for_axis = dict(
        # numeric column ['Именительный падеж', 'мменительный падеж с маленькой буквы', 'род цифорой']
        # (0 - средний род, 1 - мужской род, 2 - женский род[) (Середнее образовние, средний доход, средняя температура) )
        age = ['Возраст', 'возраст', 1]
        , using_duration = ['Длительность использования', 'длительность использования', 2]
        , mb_used = ['Объем интернет трафика', 'объем интернет трафика', 1]
        , revenue = ['Выручка', 'выручка', 2]
        # categorical column ['Именительный падеж', 'для кого / чего', 'по кому чему']
        # Распределение долей по городу и тарифу с нормализацией по городу
        , city = ['Город', 'города', 'городу']
        , tariff = ['Тариф', 'тарифа', 'тарифу']
        , is_active = ['активный ли клиент', 'активности клиента', 'активности клиента']
    )
    config = dict(
        df = df
        , x = 'education'
        , x_axis_label = 'Образование'
        , y = 'total_income'
        , y_axis_label = 'Доход'
        , category = 'gender'
        , category_axis_label = 'Пол'
        , title = 'Доход в зависимости от пола и уровня образования'
        , func = 'mean'
        , barmode = 'group'
        , width = None
        , height = None
        , orientation = 'v'
        , text = False
        , textsize = 14
    )
    bar(config)
    """
    return base_graph_for_bar_line_area(config, titles_for_axis, 'bar')

def line(config: dict, titles_for_axis: dict = None):
    """
    Creates a line chart using the Plotly Express library.

    Parameters:
    config (dict): A dictionary containing parameters for creating the chart.
        - df (DataFrame): A DataFrame containing data for creating the chart.
        - x (str): The name of the column in the DataFrame to be used for creating the X-axis.
        - x_axis_label (str): The label for the X-axis.
        - y (str): The name of the column in the DataFrame to be used for creating the Y-axis.
        - y_axis_label (str): The label for the Y-axis.
        - category (str): The name of the column in the DataFrame to be used for creating categories.
        If None or an empty string, the chart will be created without category.
        - top_n_trim_axis (int): The number of top categories axis to include in the chart.
        - top_n_trim_legend (int): The number of top categories legend to include in the chart.
        - sort_axis (bool): Whether to sort the categories on the axis (default is True).
        - sort_legend (bool): Whether to sort the categories in the legend (default is True).
        - category_axis_label (str): The label for the categories.
        - title (str): The title of the chart.
        - func (str): The function to be used for aggregating data (default is 'mean'). May be mean, median, sum, count, nunique
        - barmode (str): The mode for displaying bars (default is 'group').
        - width (int): The width of the chart (default is None).
        - height (int): The height of the chart (default is None).
        - text (bool):  Whether to display text on the chart (default is False).
        - textsize (int): Text size (default 14)
        - textposition (str): Text position (default 'auto'). May be 'auto', 'inside', 'outside', 'none'
        - xaxis_show (bool):  Whether to show the X-axis (default is True).
        - yaxis_show (bool):  Whether to show the Y-axis (default is True).
        - showgrid_x (bool):   Whether to show grid on X-axis (default is True).
        - showgrid_y (bool):   Whether to show grid on Y-axis (default is True).
        - show_group_size (bool):  Whether to show the group size (default is False).

    titles_for_axis (dict):  A dictionary containing titles for the axes.

    Returns:
    fig (plotly.graph_objs.Figure): The created chart.

    Example:
    titles_for_axis = dict(
        # numeric column ['Именительный падеж', 'мменительный падеж с маленькой буквы', 'род цифорой']
        # (0 - средний род, 1 - мужской род, 2 - женский род[) (Середнее образовние, средний доход, средняя температура) )
        age = ['Возраст', 'возраст', 1]
        , using_duration = ['Длительность использования', 'длительность использования', 2]
        , mb_used = ['Объем интернет трафика', 'объем интернет трафика', 1]
        , revenue = ['Выручка', 'выручка', 2]
        # categorical column ['Именительный падеж', 'для кого / чего', 'по кому чему']
        # Распределение долей по городу и тарифу с нормализацией по городу
        , city = ['Город', 'города', 'городу']
        , tariff = ['Тариф', 'тарифа', 'тарифу']
        , is_active = ['активный ли клиент', 'активности клиента', 'активности клиента']
    )
    config = dict(
        df = df
        , x = 'education'
        , x_axis_label = 'Образование'
        , y = 'total_income'
        , y_axis_label = 'Доход'
        , category = 'gender'
        , category_axis_label = 'Пол'
        , title = 'Доход в зависимости от пола и уровня образования'
        , func = 'mean'
        , barmode = 'group'
        , width = None
        , height = None
        , orientation = 'v'
        , text = False
        , textsize = 14
    )
    line(config)
    """
    return base_graph_for_bar_line_area(config, titles_for_axis, 'line')

def area(config: dict, titles_for_axis: dict = None):
    """
    Creates a area chart using the Plotly Express library.

    Parameters:
    config (dict): A dictionary containing parameters for creating the chart.
        - df (DataFrame): A DataFrame containing data for creating the chart.
        - x (str): The name of the column in the DataFrame to be used for creating the X-axis.
        - x_axis_label (str): The label for the X-axis.
        - y (str): The name of the column in the DataFrame to be used for creating the Y-axis.
        - y_axis_label (str): The label for the Y-axis.
        - category (str): The name of the column in the DataFrame to be used for creating categories.
        If None or an empty string, the chart will be created without category.
        - top_n_trim_axis (int): The number of top categories axis to include in the chart.
        - top_n_trim_legend (int): The number of top categories legend to include in the chart.
        - sort_axis (bool): Whether to sort the categories on the axis (default is True).
        - sort_legend (bool): Whether to sort the categories in the legend (default is True).
        - category_axis_label (str): The label for the categories.
        - title (str): The title of the chart.
        - func (str): The function to be used for aggregating data (default is 'mean'). May be mean, median, sum, count, nunique
        - barmode (str): The mode for displaying bars (default is 'group').
        - width (int): The width of the chart (default is None).
        - height (int): The height of the chart (default is None).
        - text (bool):  Whether to display text on the chart (default is False).
        - textsize (int): Text size (default 14)
        - textposition (str): Text position (default 'auto'). May be 'auto', 'inside', 'outside', 'none'
        - xaxis_show (bool):  Whether to show the X-axis (default is True).
        - yaxis_show (bool):  Whether to show the Y-axis (default is True).
        - showgrid_x (bool):   Whether to show grid on X-axis (default is True).
        - showgrid_y (bool):   Whether to show grid on Y-axis (default is True).
        - show_group_size (bool):  Whether to show the group size (default is False).

    titles_for_axis (dict):  A dictionary containing titles for the axes.

    Returns:
    fig (plotly.graph_objs.Figure): The created chart.

    Example:
    titles_for_axis = dict(
        # numeric column ['Именительный падеж', 'мменительный падеж с маленькой буквы', 'род цифорой']
        # (0 - средний род, 1 - мужской род, 2 - женский род[) (Середнее образовние, средний доход, средняя температура) )
        age = ['Возраст', 'возраст', 1]
        , using_duration = ['Длительность использования', 'длительность использования', 2]
        , mb_used = ['Объем интернет трафика', 'объем интернет трафика', 1]
        , revenue = ['Выручка', 'выручка', 2]
        # categorical column ['Именительный падеж', 'для кого / чего', 'по кому чему']
        # Распределение долей по городу и тарифу с нормализацией по городу
        , city = ['Город', 'города', 'городу']
        , tariff = ['Тариф', 'тарифа', 'тарифу']
        , is_active = ['активный ли клиент', 'активности клиента', 'активности клиента']
    )
    config = dict(
        df = df
        , x = 'education'
        , x_axis_label = 'Образование'
        , y = 'total_income'
        , y_axis_label = 'Доход'
        , category = 'gender'
        , category_axis_label = 'Пол'
        , title = 'Доход в зависимости от пола и уровня образования'
        , func = 'mean'
        , barmode = 'group'
        , width = None
        , height = None
        , orientation = 'v'
        , text = False
        , textsize = 14
    )
    bar(config)
    """
    return base_graph_for_bar_line_area(config, titles_for_axis, 'area')
def make_df():
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
    df = pd.read_csv('/home/PAGriAnalytics/mysite/data/dash_visits.csv')
    df = df.sort_values('dt')
    return df

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
# dashboard_for_yandex_afisha_app = dash.Dash(__name__, requests_pathname_prefix='/dashboard_for_yandex_afisha/', external_stylesheets=[dbc.themes.SANDSTONE, dbc_css])
# dashboard_for_yandex_afisha_app.layout = html.Div("Dash app 2")
df = make_df()
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

checklist_all_values_item_topic = df['item_topic'].unique()
checklist_all_values_age_segment = df['age_segment'].unique()
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
dashboard_for_yandex_afisha_app = dash.Dash(__name__, requests_pathname_prefix='/dashboard_for_yandex_afisha/', external_stylesheets=[dbc.themes.SANDSTONE, dbc_css])
# Создание Dash приложения с использованием Bootstrap
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
            trigger="legacy",
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
            trigger="legacy",
            placement='right',
                )
            ]
        )
dashboard_for_yandex_afisha_app.layout = dbc.Container([
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
    dcc.Store(id='store-checklist-value_age_segment', storage_type='memory'),
#     dcc.Interval(id='interval_graphs', interval=60000),
#     dcc.Interval(id='interval_df', interval=600000)
], fluid=True)

@dashboard_for_yandex_afisha_app.callback(
    [Output('date_range_slider_start_text', 'children'),
    Output('date_range_slider_end_text', 'children')],
    [Input('date-picker-range', 'value')]
)
def update_labels(selected_range):
    start_index, end_index = selected_range
    start_time = df['dt'].iloc[start_index].strftime('%H:%M:%S')
    end_time = df['dt'].iloc[end_index].strftime('%H:%M:%S')
    return start_time, end_time

@dashboard_for_yandex_afisha_app.callback(
    Output('absolute-visits-by-item-graph', 'figure'),
    Output('relative-visits-by-item-graph', 'figure'),
    Output('visits-by-source-graph', 'figure'),
    Output('crosstab', 'children'),
    Input('date-picker-range', 'value'),
    Input('checklist_item_topic', 'value'),
    Input('checklist_age_segment', 'value'),
    # Input('interval_graphs', 'n_intervals')
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
    df_aggregated_by_source_topic.rename(columns={'visits': 'visits_pct'}, inplace=True)
    config = dict(
        df = df_aggregated_by_item_topic
        , x = 'dt'
        , y = 'visits'
        , category = 'item_topic'
        , width = None
        , height = None
        , orientation = 'v'
    )
    visits_by_item_topic_absolute_fig = area(config, titles_for_axis)
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
    visits_by_item_topic_pct_fig = area(config, titles_for_axis)
    visits_by_item_topic_pct_fig.update_layout(title_text=None, showlegend=False, margin=dict(l=0, r=0, b=0, t=0))
    config = dict(
        df = df_aggregated_by_source_topic
        , x = 'source_topic'
        , y = 'visits_pct'
        , text = True
        , width = None
        , height = None
        , orientation = 'h'
        , showgrid_y = False
    )
    visits_by_source_topic_fig = bar(config, titles_for_axis)
    visits_by_source_topic_fig = visits_by_source_topic_fig.update_layout(title_text=None, showlegend=False, margin=dict(l=0, r=0, b=0, t=0))
    crosstab = filtered_df_origin.pivot_table(index = 'item_topic', columns = 'source_topic', values='visits', aggfunc='sum').fillna(0).astype(int).reset_index().rename(columns={'item_topic': ' '})
    rowData = crosstab.to_dict('records')
    min_visits = crosstab.select_dtypes(include=['number']).min().min()
    max_visits = crosstab.select_dtypes(include=['number']).max().max()
    table_component = dag.AgGrid(
        rowData=rowData, columnDefs=[{"field": i, 'headerName': i.replace('_', ' '), "cellStyle": {"fontSize": "14px"}, 'type': 'numeric', 'editable': False, "tooltipField": i, "minWidth": 100
                                            , "cellStyle": {"function": "heatMap(params)"}
                                            , "cellRendererParams": {"min": min_visits, "max": max_visits},} if pd.api.types.is_numeric_dtype(crosstab[i])
                                        else {"field": i, 'headerName': i.replace('_', ' '), "cellStyle": {"fontSize": "14px"}, 'type': 'text', 'editable': False, "tooltipField": i, "minWidth": 100} for i in crosstab.columns]  # , 'type': 'numeric', "valueFormatter": {"function": "Number(params.value).toFixed(1)"}} , , 'autoSizeColumn': True
        # , columnSizeOptions = {"skipHeader": True}
        , columnSize="responsiveSizeToFit", defaultColDef={"sortable": True, "filter": False, "animateRows": True, "wrapHeaderText": True, "autoHeaderHeight": True}, dashGridOptions={"pagination": True, 'paginationPageSize': 10, "animateRows": True, "animateColumns": True}
        # ag-theme-quartz, ag-theme-quartz-dark, ag-theme-alpine, ag-theme-alpine-dark, ag-theme-balham, ag-theme-balham-dark, ag-theme-material.
    )
    return visits_by_item_topic_absolute_fig, visits_by_item_topic_pct_fig, visits_by_source_topic_fig, table_component

@dashboard_for_yandex_afisha_app.callback(
    [Output("popover_item_topic", "is_open"), Output("checklist_item_topic", "value"), Output("store-checklist-value_item_topic", "data"),
    Output("popover_age_segment", "is_open"), Output("checklist_age_segment", "value"), Output("store-checklist-value_age_segment", "data")],
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
