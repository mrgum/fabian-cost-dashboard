import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Fabian Cost dashboard',
    page_icon=':dollar:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data(ttl='1d')
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/monthly-fabian-2024.csv'
    raw_cost_df = pd.read_csv(DATA_FILENAME)

    MIN_MONTH = 1
    MAX_MONTH = 8

    # The data above has columns like:

    # User,name,email,department,staff,student,2024-01,2024-02,2024-03,2024-04,2024-05,2024-06,2024-07,2024-08,Total
    # - User
    # - name
    # - [Stuff I don't care about for now]
    # - cost for 2024-01
    # - ...
    # - cost for 2024-08

    # ...but I want this instead:
    # - Name
    # - YearMonth
    # - Cost

    raw_cost_df.drop("User email department staff student".split(" "), axis=1, inplace=True)

    for x in range(MIN_MONTH, MAX_MONTH + 1):
        raw_cost_df[str(x)] = raw_cost_df[f"2024-{x:02}"]
        raw_cost_df.drop(f"2024-{x:02}", axis=1, inplace=True)

    # print(raw_cost_df.head())

    raw_cost_df['Name'] = raw_cost_df['name']
    # So let's pivot all those year-columns into two: YearMonth and Cost
    cost_df = raw_cost_df.melt(
        ['Name'],
        [str(x) for x in range(MIN_MONTH, MAX_MONTH + 1)],
        'YearMonth',
        'Cost',
    )

    # Convert years from string to integers
    cost_df['YearMonth'] = pd.to_numeric(cost_df['YearMonth'])

    return cost_df

cost_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :dollar: Fabian Cost dashboard

This is the cost per user of compute. There are additional non compute costs and costs for compute that are not
 attributed to a user
'''

# Add some spacing
''
''

min_value = cost_df['YearMonth'].min()
max_value = cost_df['YearMonth'].max()

from_year, to_year = st.slider(
    'Which months are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

users = cost_df['Name'].unique()

if not len(users):
    st.warning("Select at least one user")

selected_users = st.multiselect(
    'Which users would you like to view?',
    users,
    ['Liyuan Hu', 'Mukul Gupta', 'Clare Balboni'])

''
''
''

# Filter the data
filtered_cost_df = cost_df[
    (cost_df['Name'].isin(selected_users))
    & (cost_df['YearMonth'] <= to_year)
    & (from_year <= cost_df['YearMonth'])
]

st.header('Cost over time', divider='gray')

''

st.bar_chart(
    filtered_cost_df,
    x='YearMonth',
    y='Cost',
    color='Name',
    stack=True
)

''
''


first_year = cost_df[cost_df['YearMonth'] == from_year]
last_year = cost_df[cost_df['YearMonth'] == to_year]

st.header(f'Cost in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, user in enumerate(selected_users):
    col = cols[i % len(cols)]

    with col:
        first_cost = first_year[first_year['Name'] == user]['Cost'].iat[0] / 1000000000
        last_cost = last_year[last_year['Name'] == user]['Cost'].iat[0] / 1000000000

        if math.isnan(first_cost):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_cost / first_cost:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{user} Cost',
            value=f'{last_cost:,.02f}',
            delta=growth,
            delta_color=delta_color
        )
