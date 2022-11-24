import streamlit as st
import pandas as pd
import numpy as np
import json
from utils import get_variable_filter


DATA_MAIN = pd.read_parquet('data/ipums_full_count_nyc_census_coded_20210801.parquet')
with open('meta.json', 'r') as f:
    DATA_META = json.load(f)
DATA_VARIABLE, DATA_FILTER = get_variable_filter('cons.json', 'oov.json')
def main():
    # st.write(df.head())
    charts = {
        # '': meta,
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

@st.cache(show_spinner=False)
def get_unique(var):
    if 'codes' in DATA_META[var] and DATA_META[var]['codes'] is not None:
        return list(DATA_META[var].values())
    return DATA_MAIN[var].unique().tolist()


def meta():
    st.header('Variables')
    for k, v in DATA_META.items():
        st.subheader(k)
        st.write(v['description'])

def add_filter(var):
    pass

def area():
    with st.sidebar:
        var = st.selectbox('Select a variable:', list(DATA_VARIABLE['area']))
        col1, col2, col3 = st.columns(3)
        fvars, ops, fvals = [], [], []
        if st.button('add filter'):
            with col1:
                fvars.append(st.selectbox('Filter', list(DATA_FILTER[var])))
            with col2:
                ops.append(st.selectbox('', ['=', '≠']))
            with col3:
                fvals.append(st.multiselect('', get_unique(fvars[-1])))

    st.header('Area Chart')

@st.cache
def _area(var, fil):
    pass

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

