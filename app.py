import math

import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import html, dash_table
from dash import dcc

from comparison_framework import SuitabilityScoreFramework

#Instantiates the Dash app and identify the server
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server

def create_dropdown(label_text: str = None, dropdown_list: list = None, select_multi: bool = None, dropdown_id: str=None):
    """
    This function creates either a single dropdown menu or a multi dropdown menu.

    Args:
        label_text: the text shown in the dash dropdown textbox as default
        dropdown_list: the list of items to include in the dropdown
        select_multi: whether you can select multiple choices (True) or a single choice (False)
        dropdown_id: the id relating to the CSS formatting

    Returns:
        A Row object for the dropdown
    """

    dropdown_row = dbc.Row(
        [
            dbc.Col(html.Label(children=label_text,
                               className='input-text'),
                                className='input-labels'),

            dbc.Col(dcc.Dropdown(dropdown_list,
                                value=dropdown_list[0],
                                 multi=select_multi,
                                 id=dropdown_id))
        ], className='dropdown-input'
    )

    return dropdown_row

def create_rangeslider(label_text: str = None, range_min: int = None, range_max: int = None, range_step: int = None, range_value: list = None, rangeslider_id: str = None):
    """
    This function creates a range slider between range_min and range_max values.
    Args:
        label_text: The text shown as default on the range slider
        range_min: The minimum value of the range slider
        range_max: The maximum value of the range slider
        rangeslider_id: The CSS id for formatting

    Returns:
        A row object including the range slider
    """

    range_slider_row = dbc.Row(
        [
            dbc.Col(html.Label(children=label_text,
                               className='input-text'),
                                className='input-labels'),
            dbc.Col(dcc.RangeSlider(min=range_min,
                                    max=range_max,
                                    step=range_step,
                                    value=range_value,
                                    id=rangeslider_id))
        ], className='rangeslider-input'
    )

    return range_slider_row

def create_datatable(datatable_id):
    """
    This function creates a datatable based on the data passed to it from the callback.

    Args:
        datatable_id: the id of the data table within the app to display the data

    Returns:
        a Row object containing a data table
    """

    datatable_row = dbc.Row(
        [
            dash_table.DataTable(id=datatable_id,
                                 style_data={'backgroundColor': '#fff',
                                             'color': '#3E3E3E',
                                             'border': '1px solid #343a40'},
                                 style_header={'backgroundColor': '#004569',
                                               'color': 'white',
                                               'border': '1px solid #343a40'},
                                 style_table={'overflowX': 'auto'},
                                 style_cell={'height': 'auto',
                                             'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                                             'whiteSpace': 'normal', 'textAlign': 'left'},
                                 sort_action='custom',
                                 sort_mode='single',
                                 sort_by=[]
                                 )
        ]
    )

    return datatable_row

def convert_list_as_string(ls_as_string: list):
    """
    Data is contained in a list gets saved as a string when on disk. This function coverts the string back into a list

    Args:
        ls_as_string: the string which has values in a list within it

    Returns:
        a list of values, which are not whitespace, within that string
    """
    ls_as_string = ls_as_string[2:-2]
    if "'s" not in ls_as_string:
        string_to_list = ls_as_string.split("'")
        ls_as_ls = [x for x in string_to_list if not x.isspace()]
    else:
        string_to_list = ls_as_string.split('"')
        contains_apostrophe = [x for x in string_to_list if "'s" in x]
        not_contains_apostrophe = [x for x in string_to_list if x not in contains_apostrophe]
        not_contains_apostrophe_as_ls = [x.split("'") for x in not_contains_apostrophe]
        not_contains_apostrophe_as_ls = [item for sublist in not_contains_apostrophe_as_ls for item in sublist]
        ls_as_ls = [x for x in not_contains_apostrophe_as_ls if not x.isspace()]
        ls_as_ls = ls_as_ls + contains_apostrophe

    return ls_as_ls

def convert_col_with_ls(df_col):

    df_col = df_col.apply(lambda x: convert_list_as_string(x))

    unique_list = []

    for x in range(0, len(df_col)):
        unique_list.extend(df_col[x])

    unique_list = sorted(list(set(unique_list)))

    return unique_list

ss = SuitabilityScoreFramework()
ss.framework_weighting = {'Location': 5,
                           'Salary': 5,
                           'Skills': 3,
                           'Experience': 3,
                           'WFH': 3,
                           'Sector': 3,
                           'Area': 3,
                           'Expertise' : 5,
                           'Last Move': 3,
                           'Move Status': 5,
                           }
dummy_data_df = pd.read_csv('Dummy_Candidate_Data.csv')

sectors = sorted(list(dummy_data_df['Sector'].unique()))
locations = sorted(list(dummy_data_df['Location'].unique()))
all_mapped_distances = {'London': {'London': 0.0,
  'Manchester': 327.0534023452525,
  'Leeds': 328.54296482510466,
  'Edinburgh': 651.9728973902871,
  'Birmingham': 212.02048615776175,
  'Glasgow': 694.2705845566147,
  'Liverpool': 367.924008163767,
  'Bristol': 237.1499097041376,
  'Sheffield': 276.1494460389414,
  'Cardiff': 288.67655028845087,
  'Belfast': 678.9959441045239,
  'Nottingham': 212.36976463568564,
  'Dublin': 620.1974113114027},
 'Manchester': {'London': 327.0534023452525,
  'Manchester': 0.0,
  'Leeds': 76.3419704540872,
  'Edinburgh': 339.82577522112757,
  'Birmingham': 135.45078654882843,
  'Glasgow': 369.247420001182,
  'Liverpool': 70.16581598512694,
  'Bristol': 268.54923272562064,
  'Sheffield': 72.95851341336338,
  'Cardiff': 280.16617941923903,
  'Belfast': 370.8999539925509,
  'Nottingham': 123.06099275400156,
  'Dublin': 368.8502225572842},
 'Leeds': {'London': 328.54296482510466,
  'Manchester': 76.3419704540872,
  'Leeds': 0.0,
  'Edinburgh': 323.5300463192462,
  'Birmingham': 176.129439098532,
  'Glasgow': 372.8685556755922,
  'Liverpool': 142.98690679967604,
  'Bristol': 323.00410747307467,
  'Sheffield': 55.34818294496408,
  'Cardiff': 342.57321325563066,
  'Belfast': 416.8184504751833,
  'Nottingham': 117.39021168274492,
  'Dublin': 436.4260243579798},
 'Edinburgh': {'London': 651.9728973902871,
  'Manchester': 339.82577522112757,
  'Leeds': 323.5300463192462,
  'Edinburgh': 0.0,
  'Birmingham': 475.27071417203297,
  'Glasgow': 100.02038747358328,
  'Liverpool': 339.1346663005028,
  'Bristol': 597.993046341532,
  'Sheffield': 376.2427617543404,
  'Cardiff': 596.4151580003646,
  'Belfast': 307.8224573231335,
  'Nottingham': 439.94271043814035,
  'Dublin': 448.1443703814557},
 'Birmingham': {'London': 212.02048615776175,
  'Manchester': 135.45078654882843,
  'Leeds': 176.129439098532,
  'Edinburgh': 475.27071417203297,
  'Birmingham': 0.0,
  'Glasgow': 500.7774465541888,
  'Liverpool': 158.78247239585613,
  'Bristol': 149.73432132800136,
  'Sheffield': 124.88094440508978,
  'Cardiff': 178.71035309864465,
  'Belfast': 467.05961872466037,
  'Nottingham': 93.02127419339682,
  'Dublin': 416.5678505090497},
 'Glasgow': {'London': 694.2705845566147,
  'Manchester': 369.247420001182,
  'Leeds': 372.8685556755922,
  'Edinburgh': 100.02038747358328,
  'Birmingham': 500.7774465541888,
  'Glasgow': 0.0,
  'Liverpool': 349.07586401341024,
  'Bristol': 605.9238758586514,
  'Sheffield': 420.0964923374065,
  'Cardiff': 595.8000787505088,
  'Belfast': 226.21537275728448,
  'Nottingham': 483.0932413032937,
  'Dublin': 384.68080475666574},
 'Liverpool': {'London': 367.924008163767,
  'Manchester': 70.16581598512694,
  'Leeds': 142.98690679967604,
  'Edinburgh': 339.1346663005028,
  'Birmingham': 158.78247239585613,
  'Glasgow': 349.07586401341024,
  'Liverpool': 0.0,
  'Bristol': 259.5755303540825,
  'Sheffield': 141.31374426210272,
  'Cardiff': 258.02267281128474,
  'Belfast': 313.9210365040131,
  'Nottingham': 181.2186086908623,
  'Dublin': 299.0373970395838},
 'Bristol': {'London': 237.1499097041376,
  'Manchester': 268.54923272562064,
  'Leeds': 323.00410747307467,
  'Edinburgh': 597.993046341532,
  'Birmingham': 149.73432132800136,
  'Glasgow': 605.9238758586514,
  'Liverpool': 259.5755303540825,
  'Bristol': 0.0,
  'Sheffield': 274.0837957058634,
  'Cardiff': 51.55129337880057,
  'Belfast': 519.3778024726266,
  'Nottingham': 238.3285852260219,
  'Dublin': 418.15547456953044},
 'Sheffield': {'London': 276.1494460389414,
  'Manchester': 72.95851341336338,
  'Leeds': 55.34818294496408,
  'Edinburgh': 376.2427617543404,
  'Birmingham': 124.88094440508978,
  'Glasgow': 420.0964923374065,
  'Liverpool': 141.31374426210272,
  'Bristol': 274.0837957058634,
  'Sheffield': 0.0,
  'Cardiff': 298.12346798446157,
  'Belfast': 442.003312408971,
  'Nottingham': 63.78938653227092,
  'Dublin': 440.226797720866},
 'Cardiff': {'London': 288.67655028845087,
  'Manchester': 280.16617941923903,
  'Leeds': 342.57321325563066,
  'Edinburgh': 596.4151580003646,
  'Birmingham': 178.71035309864465,
  'Glasgow': 595.8000787505088,
  'Liverpool': 258.02267281128474,
  'Bristol': 51.55129337880057,
  'Sheffield': 298.12346798446157,
  'Cardiff': 0.0,
  'Belfast': 491.4719912419304,
  'Nottingham': 271.19746033448587,
  'Dublin': 378.44601166059954},
 'Belfast': {'London': 678.9959441045239,
  'Manchester': 370.8999539925509,
  'Leeds': 416.8184504751833,
  'Edinburgh': 307.8224573231335,
  'Birmingham': 467.05961872466037,
  'Glasgow': 226.21537275728448,
  'Liverpool': 313.9210365040131,
  'Bristol': 519.3778024726266,
  'Sheffield': 442.003312408971,
  'Cardiff': 491.4719912419304,
  'Belfast': 0.0,
  'Nottingham': 492.5846784062072,
  'Dublin': 174.15078798282545},
 'Nottingham': {'London': 212.36976463568564,
  'Manchester': 123.06099275400156,
  'Leeds': 117.39021168274492,
  'Edinburgh': 439.94271043814035,
  'Birmingham': 93.02127419339682,
  'Glasgow': 483.0932413032937,
  'Liverpool': 181.2186086908623,
  'Bristol': 238.3285852260219,
  'Sheffield': 63.78938653227092,
  'Cardiff': 271.19746033448587,
  'Belfast': 492.5846784062072,
  'Nottingham': 0.0,
  'Dublin': 472.8392412197905},
 'Dublin': {'London': 620.1974113114027,
  'Manchester': 368.8502225572842,
  'Leeds': 436.4260243579798,
  'Edinburgh': 448.1443703814557,
  'Birmingham': 416.5678505090497,
  'Glasgow': 384.68080475666574,
  'Liverpool': 299.0373970395838,
  'Bristol': 418.15547456953044,
  'Sheffield': 440.226797720866,
  'Cardiff': 378.44601166059954,
  'Belfast': 174.15078798282545,
  'Nottingham': 472.8392412197905,
  'Dublin': 0.0}}

wfh_days = sorted(list(dummy_data_df['WFH Days'].unique()))
experience_years = sorted(list(dummy_data_df['Years Experience'].unique()))
last_move_years = sorted(list(dummy_data_df['Last Moved Years'].unique()))
salary_min = dummy_data_df['Min Salary'].min()
salary_min = int(math.floor(salary_min / 10000)) * 10000
salary_max = dummy_data_df['Max Salary'].max()
salary_max = int(math.ceil(salary_max / 10000)) * 10000
move_types = ['Urgently Looking', 'Actively Looking', 'Open Minded', 'Unlikely to Move']

unique_skills = convert_col_with_ls(dummy_data_df['Skills'])
unique_areas = ['London Market', "Lloyd's Syndicate", 'Consultancy', 'Personal Lines', 'Commercial Lines', 'Reinsurer', 'Broker', 'Reinsurance Broker', 'Regulator']

dummy_data_df['Skills'] = dummy_data_df['Skills'].apply(lambda x: convert_list_as_string(x))
dummy_data_df['Minor Expertise'] = dummy_data_df['Minor Expertise'].apply(lambda x: convert_list_as_string(x))

applayout = [
    dbc.Container(
        [
            dbc.Col(html.H1("Foxy Prospecting")),
            create_dropdown(label_text="Select the sector that you wish to search:", dropdown_list=sectors, select_multi=False, dropdown_id='sector-input'),
            create_dropdown(label_text="Select the candidate's contract type:", dropdown_list=['Permanent', 'Contractor'], select_multi=True, dropdown_id='contract-type-input'),
            create_dropdown(label_text="Select the location that you wish to search:", dropdown_list=locations, select_multi=False, dropdown_id='location-input'),
            create_rangeslider(label_text="Select the salary range that you wish to search:", range_min=salary_min, range_max=salary_max, range_step=20000, range_value=[salary_min * 2, salary_max / 2], rangeslider_id='salary-input'),
            create_rangeslider(label_text="Select the years of experience that you wish to search:", range_min=experience_years[0], range_max=experience_years[-1], range_step=1, range_value=[3, 5], rangeslider_id='years-experience-input'),
            create_rangeslider(label_text="Select the WFH days that you wish to search:", range_min=wfh_days[0], range_max=wfh_days[-1], range_step=1, range_value=[2, 3], rangeslider_id='wfh-input'),
            create_rangeslider(label_text="Select the years since last move that you wish to search:", range_min=last_move_years[0], range_max=last_move_years[-1], range_step=1, range_value=[3, 5], rangeslider_id='last-moved-input'),
            create_dropdown(label_text="Select the most desired candidate experience:", dropdown_list=unique_areas, select_multi=False, dropdown_id='major-experience-input'),
            create_dropdown(label_text="Select other desired candidate experience:", dropdown_list=unique_areas, select_multi=True, dropdown_id='minor-experience-input'),
            create_dropdown(label_text="Select the desired candidate skills:", dropdown_list=unique_skills, select_multi=True, dropdown_id='skills-input'),
            create_dropdown(label_text="Select the latest movement status of the candidate:", dropdown_list=move_types, select_multi=True, dropdown_id='move-status-input'),
            dbc.Row(dbc.Col(html.Button(id='submit-button-state', n_clicks=0, children=['Submit'], className='submit-button'), width={'offset' : 6}))
        ], className='user-selections'
    ),
    dbc.Container(
        [
            create_datatable(datatable_id='prospecting-outputs')
        ]
    )
]

@app.callback(
    Output('prospecting-outputs', 'data'),
    Output('prospecting-outputs', 'columns'),
    Input('submit-button-state', 'n_clicks'),
    State('sector-input', 'value'),
    State('contract-type-input', 'value'),
    State('location-input', 'value'),
    State('salary-input', 'value'),
    State('years-experience-input', 'value'),
    State('wfh-input', 'value'),
    State('last-moved-input', 'value'),
    State('major-experience-input', 'value'),
    State('minor-experience-input', 'value'),
    State('skills-input', 'value'),
    State('move-status-input', 'value')
)

def display_prospecting_outputs(n_clicks, sector_input, contract_type_input, location_input, salary_input, experience_input, wfh_input, last_moved_input, major_expertise_input, minor_expertise_input, skills_input, move_status_input, df=dummy_data_df):


    if n_clicks > 0:

        if type(skills_input) is str:
            skills_input = [skills_input]

        if (type(contract_type_input)) is str:
            contract_type_input = [contract_type_input]

        data_df = df.copy()
        data_df = data_df.loc[data_df['Job Type'].isin(contract_type_input)]

        data_df['Salary Score'] = data_df.apply(lambda row: ss.apply_framework_to_salary(input_salary=salary_input, data_min_salary=row['Min Salary'], data_max_salary=row['Max Salary']), axis=1)
        data_df['Location Score'] = data_df['Location'].apply(lambda x: ss.apply_framework_location(input_location=location_input, data_location=x, all_mapped_distances=all_mapped_distances))
        data_df['Sector Score'] = data_df['Sector'].apply(lambda x: ss.apply_framework_to_sector(input_sector=sector_input, data_sector=x))
        data_df['WFH Score'] = data_df['WFH Days'].apply(lambda x: ss.apply_framework_to_wfh(input_wfh=wfh_input, data_wfh=x))
        data_df['Skills Score'] = data_df.apply(lambda row: ss.apply_framework_to_skills(input_skills=skills_input, data_skills=row['Skills']), axis=1)
        data_df['Years Experience Score'] = data_df['Years Experience'].apply(lambda x: ss.apply_framework_experience_prospecting(input_experience=experience_input, data_experience=x))
        data_df['Minor Expertise Score'] = data_df['Minor Expertise'].apply(lambda x: ss.apply_framework_to_areas(input_areas=minor_expertise_input, data_areas=x))
        data_df['Major Expertise Score'] = data_df['Major Expertise'].apply(lambda x: ss.apply_framework_to_area_of_expertise(input_expertise=major_expertise_input, data_expertise=x))
        data_df['Move Score'] = data_df['Last Moved Years'].apply(lambda x: ss.apply_framework_to_last_moved(input_moved=last_moved_input, data_moved=x))
        data_df['Status Score'] = data_df['Move Status'].apply(lambda x: ss.apply_framework_to_move_status(input_move_status=move_status_input, data_move_status=x))
        data_df['Matched Skills'] = data_df['Skills'].apply(lambda x: list(set(x).intersection(skills_input)))

        data_df['Suitability Score'] = data_df.apply(lambda row:
                                           ss.apply_framework(salary_score=row['Salary Score'],
                                           location_score=row['Location Score'],
                                           sector_score=row['Sector Score'],
                                           experience_score=row['Years Experience Score'],
                                           wfh_score=row['WFH Score'],
                                           skills_score=row['Skills Score'],
                                           area_score=row['Minor Expertise Score'],
                                           expertise_score=row['Major Expertise Score'],
                                           move_score=row['Move Score'],
                                           status_score=row['Status Score']
                                           ), axis=1)

        data_df['Skills'] = data_df['Skills'].apply(lambda x: ', '.join(x) if type(x) is list else x)
        data_df['Minor Expertise'] = data_df['Minor Expertise'].apply(lambda x: ', '.join(x) if type(x) is list else x)
        data_df['Matched Skills'] = data_df['Matched Skills'].apply(lambda x: ', '.join(x) if type(x) is list else x)

        data_df = data_df.sort_values(by='Suitability Score', ascending=False)[:25]
        data_df['Max Salary'] = data_df['Max Salary'].apply(lambda x: int(math.ceil(x / 1000)) * 1000)
        data_df = data_df.loc[:, ['Suitability Score', 'Location', 'Sector', 'Major Expertise', 'Minor Expertise', 'Min Salary', 'Max Salary', 'Years Experience', 'WFH Days', 'Skills', 'Matched Skills', 'Job Type', 'Last Moved Years', 'Move Status']]
        data_df['Request Representation'] = ["[Send Email]('https://www.google.com')"] * len(data_df)
        data_cols = [{'id': x , 'name' : x} for x in data_df.columns]
        data_cols[-1] = {'id' : 'Request Representation', 'name' : 'Request Representation', 'presentation' : 'markdown'}

        return data_df.to_dict('records'), data_cols

    else:
        return (None, None)

app.layout = dbc.Container(
    children=applayout,
    fluid=True
)

if __name__ == '__main__':
    app.run_server(debug=True)