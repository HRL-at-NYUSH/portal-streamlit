import streamlit as st
import pandas as pd
import numpy as np
import json
import altair as alt
from utils import get_variable_filter, is_numerical

def check_codes(var, data_meta):
    return 'codes' in data_meta[var] and data_meta[var]['codes'] is not None and len(data_meta[var]['codes']) > 0

@st.cache(show_spinner=False)
def load_data():
    with st.spinner('loading data...'):
        data_main = pd.read_parquet('data/ipums_full_count_nyc_census_coded_20210801.parquet')
        with open('data/meta.json', 'r') as f:
            data_meta = json.load(f)
        data_variable, data_filter = get_variable_filter('data/cons.json')
        name2id = {}
        for k, v in data_meta.items():
            if check_codes(k, data_meta):
                name2id[k] = {vv: int(kk) for kk, vv in v['codes'].items()}
        return data_main, data_meta, data_variable, data_filter, name2id

DATA_MAIN, DATA_META, DATA_VARIABLE, DATA_FILTER, NAME2ID = load_data()

def id2name(var, id_):
    id_ = str(id_)
    if var not in DATA_META or 'codes' not in DATA_META[var]:
        return id_
    return DATA_META[var]['codes'].get(id_, id_)

@st.cache
def name2id(var, name):
    if var in NAME2ID:
        return NAME2ID[var][name]
    return name

def main():
    # st.write(df.head())
    load_data()
    charts = {
        'Area Chart': area,
        'Line Graph': line,
        'Scatter Plot': scatter,
        'Bar Chart': bar,
        'Box Plot': box,
        'Heatmap': heat,
        'Histogram': hist,
    }
    st.title('HRL Portal')
    with st.sidebar:
        chart = st.selectbox('Select a chart type:', list(charts.keys()))
    # st.write(DATA_VARIABLE)
    # st.write(DATA_FILTER)
    charts[chart]()

@st.cache
def get_unique(var):
    if check_codes(var, DATA_META):
        return list(DATA_META[var]['codes'].values())
    return DATA_MAIN[var].unique().tolist()

def get_var_name(var):
    if var in DATA_META and 'name' in DATA_META[var]:
        name = DATA_META[var]['name']
        if name == var:
            return var
        return f"{var} ({name})"
    return var

def name2var(name):
    return name.split()[0]

def meta():
    st.header('Variables')
    for k, v in DATA_META.items():
        st.subheader(k)
        st.write(v['description'])

def area():
    with st.sidebar:
        var_name = st.selectbox('Select a variable:', [get_var_name(var) for var in DATA_VARIABLE['area']])
        var = name2var(var_name)
        st.write('Filters:')
        filters = {}
        for fvar in DATA_FILTER[var]:
            if fvar == 'YEAR':
                continue
            if is_numerical(fvar):
                names = st.slider(fvar, min(get_unique(fvar)), max(get_unique(fvar)), value=(min(get_unique(fvar)), max(get_unique(fvar))))
            else:
                names = st.multiselect(fvar, get_unique(fvar), default=get_unique(fvar))
            filters[fvar] = set([name2id(fvar, n) for n in names])
    st.header(f'Area Chart: {var_name}')
    with st.expander(f'{var}'):
        st.write(DATA_META.get(var, {}).get('description', ''))

    names = st.multiselect('Select values to display:', get_unique(var),
                           default=['Authors',
                                    'Musicians and music teachers',
                                    'Telephone operators',
                                    'Bus drivers','Cashiers'] if var == 'OCC1950' else ['Drugs and medicines',
                                                                                        'Fisheries',
                                                                                        'Glass and glass products',
                                                                                        ])
    vals = set([name2id(var, n) for n in names])
    df = get_area_data(var, filters, vals)
    # st.write(df)
    st.write(f'found {len(df)} records')
    if len(df) > 0:
        selection = alt.selection_multi(fields=[var], bind='legend')
        plot = alt.Chart(df, title=f'Count of Different {var} Values').mark_area().encode(alt.X('YEAR'),
                                                                                                         alt.Y('count', title='count', stack='zero'),
                                                                                                         alt.Color(var,
                                                                                                                   scale=alt.Scale(scheme='category20'),
                                                                                                                   legend=alt.Legend(orient='bottom')),
                                                                                          opacity=alt.condition(selection,
                                                                                                                alt.value(
                                                                                                                    1),
                                                                                                                alt.value(
                                                                                                                    0.3)),
                                                                                          tooltip='count'
                                                                                          )\
            .properties(width=650).add_selection(selection)
        st.write(plot)

@st.cache(show_spinner=False)
def get_area_data(var, filters, vals):
    # for k, v in filters.items():
    #     st.write(k)
    #     st.write(v)
    #     st.write(DATA_MAIN[k].unique())
    # st.write(len(DATA_MAIN))
    df = DATA_MAIN[['YEAR', var, *filters.keys()]]
    df = df[df[var].isin(vals)]
    with st.spinner('filtering...'):
        for fvar, fvals in filters.items():
            df = df[df[fvar].isin(fvals)]
    df = df[['YEAR', var]]
    # st.write(len(df))
    # st.write(df.head())
    with st.spinner('counting...'):
        groups = df.groupby([var, 'YEAR'])[var].count().to_frame().rename(columns={var: 'count'}).reset_index()
        groups[var] = groups[var].apply(lambda x: id2name(var, x))
    return groups

def line():
    st.header('Line Graph')

def scatter():
    st.header('Scatter Plot')

def bar():
    st.header('Bar Chart')

def box():
    st.header('Box Plot')

def heat():
    st.header('Heatmap')

def hist():
    st.header('Histogram')

if __name__ == '__main__':
    main()

