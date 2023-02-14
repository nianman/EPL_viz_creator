import streamlit as st
import numpy as np
import requests
import pandas as pd
import plotly.express as px
from io import StringIO, BytesIO
import base64

available_seasons = ['2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019', '2017-2018']


@st.experimental_memo(experimental_allow_widgets=True)
def get_data():
    with st.container():
        st.header('Select season to be displayed')
        season = st.radio("Select the season",
                          available_seasons)
        # '2018-2019', '2017-2018' have problem with point sizes for some reason or another
    team_url = f'https://fbref.com/en/comps/9/{season}'
    team_data = pd.read_html(team_url)

    stat_list = ['stats', 'shooting', 'passing', 'passing_types', 'gca', 'defense',
                 'possession', 'misc']
    player_data = []
    for stat in stat_list:
        player_url = f'https://fbref.com/en/comps/9/{season}/{stat}/{season}-Premier-League-Stats#all_stats_standard'
        response = requests.get(player_url).text.replace('<!--', '').replace('-->', '')
        player_data.append(pd.read_html(response, header=1)[2])
    return [team_data, player_data, season]


[team_data, player_data, season] = get_data()



def create_team_table(team_data):
    df_attack = team_data[0]
    df_attack.columns = ['_'.join(col) for col in df_attack.columns.values]
    df_attack.rename(columns={list(df_attack)[1]: 'Club'}, inplace=True)

    df_defense = team_data[1]
    df_defense.columns = ['_'.join(col) for col in df_defense.columns.values]
    df_defense.rename(columns={list(df_defense)[1]: 'Club'}, inplace=True)

    for i in range(2, 24):
        if i % 2 == 0 and i not in [4, 6, 16, 20]:
            df_att = team_data[i]
            df_att.columns = [f'{i}_'.join(col) for col in df_att.columns.values]
            df_att.rename(columns={list(df_att)[0]: 'Club'}, inplace=True)
            df_attack = df_attack.merge(df_att, on='Club')

        if i % 2 == 1 and i not in [1, 5, 7, 17, 19, 21, 23]:
            df_def = team_data[i]
            df_def.columns = [f'{i}_'.join(col) for col in df_def.columns.values]

            df_def.rename(columns={list(df_def)[0]: 'Club'}, inplace=True)
            df_def['Club'] = df_def['Club'].str.slice_replace(0, 3, '')
            df_defense = df_defense.merge(df_def, on='Club')
    if season == available_seasons[0]:
        df_attack.drop(['L_a_s_t_ _5'], axis=1, inplace=True)

    df_attack.columns = ['Standing', 'Club', 'Matches', 'Won', 'Draw', 'Lost', 'Goals', 'Goals_against',
                         'Goal_difference', 'Points', 'Points_Per_Match', '-', '-', '-', '-', '-', '-', '-', '-',
                         'Number of Players', 'Age', 'Possession', 'Matches', '-', '-', '-', '-', '-', '-', 'NPG',
                         'Penalty Goals', 'Penaltie Attempted', 'Yellow Cards', 'Red Cards', 'xG', 'NPxG', 'xAG',
                         'NPxG+xAG', '-', '-', 'GoalsP90', '-', '-', 'NPGP90', '-', 'xGP90', '-', '-', 'NPxGP90', '-',
                         '-', '-', '-', '-', '-', '-', 'ShotsP90', '-', '-', '-', 'Shot Distance', 'Free Kick Shots',
                         '-', '-', '-', '-', 'NPxG/Shot', 'G-xG', 'NPG-NPxG',
                         '-', '-', 'Total Passes Completed', 'Total Passes Attempted', 'Total Passes Completion%', '-',
                         '-', 'Short Passes Completed', 'Short Passes Attempted', 'Short Passes Completion%',
                         'Medium Passes Completed', 'Medium Passes Attempted', 'Medium Passes Completion%',
                         'Long Passes Completed', 'Long Passes Attempted', 'Long Passes Completion%', '-', '-', '-',
                         '-', '-', 'Passes into Attacking3rd', 'Passes into Penalty Area', '-', 'Progressive Passes',
                         '-', '-', '-', '-', '-', '-', 'Through Balls', '-', 'Crosses', 'Throw Ins', 'Corner Kicks',
                         'Inswing Corner Kicks', 'Outswing Corner Kicks', 'Straight Corner Kicks', '-', '-', '-',
                         '-', '-', '-', 'SCAP90', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-',
                         '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', 'Dribbles Attempted', 'Successful Dribbles',
                         'Dribbles Success%', '-', '-', '-', '-', '-', 'Progressive Carries', 'Carries into Final3rd',
                         'Carries into Penalty Area', '-', '-', '-', '-',
                         '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', 'OG', '-', '-', '-',
                         '% of Aerials Won']
    df_defense.columns = ['-', 'Club', 'Matches_home', 'Won_home', 'Draws_home', 'Lost_home', 'Goals_home',
                          'Goals_Against_home', 'Goal_difference_home', 'Points_home', 'Points_Pet_Match_home',
                          'xG_home', 'xGA_home', 'xG_difference_home', 'xG_differenceP90_home', 'Matches_away',
                          'Won_away', 'Draw_away', 'Lost_away', 'Goals_away', 'Goals_Against_away',
                          'Goals_difference_away', 'Points_away', 'Points_Per_Match_away', 'xG_away', 'xGA_away',
                          'xG_difference_away', 'xG_differenceP90_away',
                          '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', 'NPG_against', 'Penalty Goals_against',
                          'Penalties_against', 'Yellow Cards_against', 'Red Cards_against', 'xG_against',
                          'NPxG_against', '-', '-', '-', '-', 'GoalsP90_against', '-', '-', 'NPGP90_against', '-',
                          'xGP90_against', '-', '-', 'NPxGP90_against', '-',
                          '-', '-', '-', '-', '-', '-', 'ShotsP90_against', '-', '-', '-', 'Shot Distance_against',
                          'Free Kick Shots_against', '-', '-', '-', '-', 'NPxG/Shot_against', 'G-xG_against',
                          'NPG-NPxG_against',
                          '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-',
                          '-', '-', 'Passes into Attacking3rd_against', 'Passes into Penalty Area_against', '-', '-',
                          '-', '-', '-', '-', '-', '-', 'Through Balls_against', '-', 'Crosses_against', '-',
                          'Corner Kicks_against', 'Inswing Corner Kicks_against', 'Outswing Corner Kicks_against',
                          'Straight Corner Kicks_against', '-', '-', '-',
                          '-', '-', '-', 'SCAP90_against', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-',
                          '-', '-'
                          ]
    df_attack.drop(['-'], axis=1, inplace=True)
    df_defense.drop(['-'], axis=1, inplace=True)
    return df_attack.merge(df_defense, on='Club')


fbref_table = create_team_table(team_data)
print(fbref_table.dtypes)
# fbref_table.update(fbref_table.select_dtypes(include=np.number).applymap('{:,g}'.format))
# for column in fbref_table.columns:
#     fbref_table[column] = pd.to_numeric(fbref_table[column], errors='ignore')
# fbref_table = fbref_table.iloc[:, 1:]
# fbref_table.index += 1

colours = {'Arsenal': 'rgb(239, 1, 7)',
           'Manchester City': 'rgb(108, 171, 221)',
           'Newcastle Utd': 'rgb(45, 41, 38)',
           'Manchester Utd': 'rgb(218, 41, 28)',
           'Tottenham': 'rgb(19, 34, 87)',
           'Liverpool': 'rgb(200, 16, 46)',
           'Fulham': 'rgb(0,0,0)',
           'Brighton': 'rgb(0, 87, 184)',
           'Brentford': 'rgb(255, 40, 40)',
           'Chelsea': 'rgb(3, 70, 148)',
           'Aston Villa': 'rgb(103,14,54)',
           'Crystal Palace': 'rgb(27, 69, 143)',
           'Leicester City': 'rgb(0,83,160)',
           'Leeds United': 'rgb(29, 66, 138)',
           "Nott'ham Forest": 'rgb(255, 50, 50)',
           'Bournemouth': 'rgb(218, 41, 28)',
           'West Ham': 'rgb(122, 38, 58)',
           'Everton': 'rgb(39,68,136)',
           'Wolves': 'rgb(253,185,19)',
           'Southampton': 'rgb(215, 25, 32)',
           'Sheffield Utd': 'rgb(238, 39, 55)',
           'Huddersfield': 'rgb(14, 99, 173)',
           'Cardiff City': 'rgb(0, 112, 181)',
           'Burnley': 'rgb(108,29,69)',
           'Norwich City': 'rgb(255, 242, 0)',
           'Watford': 'rgb(251,238,35)',
           'Stoke City': 'rgb(224, 58, 62)',
           'Swansea City': 'rgb(0, 0, 0)',
           'West Brom': 'rgb(18, 47, 103)'
           }

st.title(f'English Premier League {season}')

players, teams = st.tabs(['Players', 'Teams'])


with players:
    for id, table in enumerate(player_data):
        table.drop([table.columns[0]], axis=1, inplace=True)
        table.drop([table.columns[-1]], axis=1, inplace=True)
        table.fillna(0, inplace=True)

        table.drop(table[table['Player'] == "Player"].index, inplace=True, axis=0)
        table['Nation'] = table['Nation'].apply(lambda x: str(x).split(' ')[1] if (len(str(x).split(' ')) > 1) else x)
        for column in table.columns:
            table[column] = pd.to_numeric(table[column], errors='ignore')

        table.index += 1
        if id == 0:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Matches Played',
                             'Starts', 'Minutes', 'Minutes/90', 'Goals', 'Assists', 'G+A', 'NPGoals',
                             'Penalty Goals', 'Penalty Attempts', 'Yellow Cards', 'Red Cards', 'xG', 'NPxG',
                             'xAG', 'NPxG+xAG', 'Progressive Carries', 'Progressive Passes', 'Progressive Passes Received',
                             'GoalsP90', 'AssistsP90', 'Goals+AssistsP90', 'NPGoalsP90', 'NPGoals+AssistsP90',
                             'xGP90', 'xAGP90', 'xG+xAGP90', 'NPxGP90', 'NPxG+xAGP90']
        if id == 1:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Minutes/90', 'Goals',
                             'Shots', 'Shots on Target', '% of Shots on Target', 'ShotsP90', 'Shots On TargetP90',
                             'Goals per Shot', 'Goals per Shot on Target', 'Average Distance', 'Free Kicks',
                             'Penalty Goals', 'Penalty Kicks', 'xG', 'NPxG', 'NPxG per Shot', 'Goals-xG', 'NPxG-xG']
        if id == 2:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Minutes/90',
                             'Total Passes Completed',
                             'Total Passes Attempted', 'Total Passes Completion%', 'Total Distance',
                             'Total Progressive Distance',
                             'Short Passes Completed', 'Short Passes Attempted', 'Short Passes Completion%',
                             'Medium Passes Completed', 'Medium Passes Attempted', 'Medium Passes Completion%',
                             'Long Passes Completed', 'Long Passes Attempted', 'Long Passes Completion%',
                             'Assists', 'xAG', 'xA', 'Assists-xAG', 'Passes that lead to Shots', 'Passes into 1/3',
                             'Passes into 18yardbox', 'Completed Crosses into 18yardbox', 'Progressive Passes'
                             ]
        if id == 3:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Minutes/90',
                             'Passes Attempted', 'Live-ball Passes', 'Dead-ball Passes',
                             'Passes attempted from free-kicks',
                             'Passes in Channels', 'Passes that travel 40yards+ in width', 'Crosses', 'Throw-Ins',
                             'Corner Kicks', 'Inswinging Corner Kicks', 'Outswinging Corner Kicks',
                             'Straight Corner Kicks',
                             'Passes Completed', 'Passes in Offside', 'Passes got Blocked']
        if id == 4:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Minutes/90',
                             'Shot-creating Actions', 'Shot-creating ActionsP90', 'Live-ball SCA', 'Dead-ball SCA',
                             'Dribbles lead to SCA', 'Shots lead to SCA', 'Fouls drawn lead to SCA',
                             'Defensive action lead to SCA',
                             'Goal-creating Actions', 'Goal-creating ActionsP90', 'Live-ball GCA', 'Dead-ball GCA',
                             'Dribbles lead to GCA', 'Shots lead to GCA', 'Fouls drawn lead to GCA',
                             'Defensive action lead to GCA']
        if id == 5:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Minutes/90',
                             'Tackles', 'Tackles won', 'Tackles Def3rd', 'Tackles Mid3rd', 'Tackles Att3rd',
                             'Dribblers Tackled', 'Dribblers Tackling Attempted', 'Dribblers Tackled%',
                             'Dribblers Tackling Failed', 'Blocks', 'Shot Blocks', 'Pass Blocks',
                             'Interceptions', 'Tackles+Interceptions', 'Clearances', 'Errors leading to shot']
        if id == 6:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Minutes/90',
                             'Touches', 'Touches Defensive Penalty Area', 'Touches Def3rd',
                             'Touches Mid3rd', 'Touches Att3rd', 'Touches Attacking Penalty Area',
                             'Live-ball Touches', 'Dribbles Attempted', 'Successful Dribbles', 'Dribbles Success%',
                             'Times Tackled', 'Tackled%', 'Carries', 'Total Carrying Distance',
                             'Progressive Carrying Distance', 'Progressive Carries', 'Carries into Att3rd',
                             'Carries into Penalty Box', 'Miscontrols', 'Dispossessed', 'Passes Received', 'Progressive Passes Received']
        if id == 7:
            table.columns = ['Name', 'Nation', 'Position', 'Club', 'Age', 'Birth Date', 'Minutes/90',
                             'Yellow Cards', 'Red Cards', 'Second Yellow', 'Fouls Committed', 'Fouls Drawn',
                             'Offsides', 'Crosses', 'Interceptions', 'Tackles won Possession', 'Penalties Won',
                             'Penalties Conceded', 'Own Goals', 'Loose Balls Recovered', 'Aerial Won', 'Aerial Lost',
                             'Aerial Won%']

    with st.container():
        selected_club = st.selectbox('Select a Club', fbref_table['Club'].unique(),
                                     help='Select which club you want to select players from.',
                                     index=0)

        club_players = player_data[0].loc[player_data[0]['Club'] == selected_club]['Name'].reset_index(drop=True)
        selected_players = st.multiselect('Add players', club_players,
                                          help='Select players from this club. If you want to add player from another club just change selection in the first row.')


        def add_players():
            if 'players_list' not in st.session_state and len(selected_players) > 0:
                st.session_state['players_list'] = []
                for i in selected_players:
                    st.session_state.players_list.append(i)

            else:
                for i in selected_players:
                    if i not in st.session_state['players_list']:
                        st.session_state.players_list.append(i)


        player_submit_button = st.button('Add', on_click=add_players)


    def clear_list():
        del st.session_state['players_list']


    if 'players_list' in st.session_state:
        standard, shooting, passing, passing_types, gca, defense, possession, misc = st.tabs(['Standard', 'Shooting',
                                                                                              'Passing', 'Pass Types',
                                                                                              'Goal Creating Actions',
                                                                                              'Defense',
                                                                                              'Possession',
                                                                                              'Miscellaneous'])
        standard_player = player_data[0].loc[player_data[0]['Name'].isin(st.session_state.players_list)].reset_index(
            drop=True)
        shooting_player = player_data[1].loc[player_data[1]['Name'].isin(st.session_state.players_list)].reset_index(
            drop=True)
        passing_player = player_data[2].loc[player_data[2]['Name'].isin(st.session_state.players_list)].reset_index(
            drop=True)
        passing_types_player = player_data[3].loc[
            player_data[3]['Name'].isin(st.session_state.players_list)].reset_index(drop=True)
        gca_player = player_data[4].loc[player_data[4]['Name'].isin(st.session_state.players_list)].reset_index(
            drop=True)
        defense_player = player_data[5].loc[player_data[5]['Name'].isin(st.session_state.players_list)].reset_index(
            drop=True)
        possession_player = player_data[6].loc[player_data[6]['Name'].isin(st.session_state.players_list)].reset_index(
            drop=True)
        misc_player = player_data[7].loc[player_data[7]['Name'].isin(st.session_state.players_list)].reset_index(
            drop=True)

        with standard:
            st.dataframe(standard_player)
            with st.container():
                player_scatter_feature1 = st.selectbox('Select X-axis', standard_player.columns[1:],
                                                       help='Select a column that you want to represent horizontal axis.',
                                                       index=9)
                player_scatter_feature2 = st.selectbox('Select Y-axis', standard_player.columns[1:],
                                                       help='Select a column that you want to represent vertical axis.',
                                                       index=10)
                player_scatter_feature3 = st.selectbox('Select Point Sizes', standard_player.columns[1:],
                                                       help='Select a column that you want to represent point size.',
                                                       index=7)
            fig = px.scatter(standard_player, player_scatter_feature1, player_scatter_feature2, text='Name',
                             color='Club',
                             color_discrete_map=colours, size=player_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {player_scatter_feature3}'
            )

            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )

        with shooting:
            st.dataframe(shooting_player)
            with st.container():
                shooting_scatter_feature1 = st.selectbox('Select X-axis', shooting_player.columns[1:],
                                                         help='Select a column that you want to represent horizontal axis.',
                                                         index=7)
                shooting_scatter_feature2 = st.selectbox('Select Y-axis', shooting_player.columns[1:],
                                                         help='Select a column that you want to represent vertical axis.',
                                                         index=20)
                shooting_scatter_feature3 = st.selectbox('Select Point Sizes', shooting_player.columns[1:],
                                                         help='Select a column that you want to represent vertical axis.',
                                                         index=9)
            fig = px.scatter(shooting_player, shooting_scatter_feature1, shooting_scatter_feature2, text='Name',
                             color='Club',
                             color_discrete_map=colours,
                             size=shooting_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {shooting_scatter_feature3}'
            )
            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )
        with passing:
            st.dataframe(passing_player)
            with st.container():
                passing_scatter_feature1 = st.selectbox('Select X-axis', passing_player.columns[1:],
                                                        help='Select a column that you want to represent horizontal axis.',
                                                        index=6)
                passing_scatter_feature2 = st.selectbox('Select Y-axis', passing_player.columns[1:],
                                                        help='Select a column that you want to represent vertical axis.',
                                                        index=10)
                passing_scatter_feature3 = st.selectbox('Select Point Sizes', passing_player.columns[1:],
                                                        help='Select a column that you want to represent point sizes.',
                                                        index=21)

            fig = px.scatter(passing_player, passing_scatter_feature1, passing_scatter_feature2, text='Name',
                             color='Club',
                             color_discrete_map=colours,
                             size=passing_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {passing_scatter_feature3}'
            )
            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )
        with passing_types:
            st.dataframe(passing_types_player)
            with st.container():
                pass_types_scatter_feature1 = st.selectbox('Select X-axis', passing_types_player.columns[1:],
                                                           help='Select a column that you want to represent horizontal axis.',
                                                           index=10)
                pass_types_scatter_feature2 = st.selectbox('Select Y-axis', passing_types_player.columns[1:],
                                                           help='Select a column that you want to represent vertical axis.',
                                                           index=7)
                pass_types_scatter_feature3 = st.selectbox('Select Point Sizes', passing_types_player.columns[1:],
                                                           help='Select a column that you want to represent point sizes.',
                                                           index=12)

            fig = px.scatter(passing_types_player, pass_types_scatter_feature1, pass_types_scatter_feature2,
                             text='Name',
                             color='Club',
                             color_discrete_map=colours,
                             size=pass_types_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {pass_types_scatter_feature3}'
            )
            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )
        with gca:
            st.dataframe(gca_player)
            with st.container():
                gca_scatter_feature1 = st.selectbox('Select X-axis', gca_player.columns[1:],
                                                    help='Select a column that you want to represent horizontal axis.',
                                                    index=16)
                gca_scatter_feature2 = st.selectbox('Select Y-axis', gca_player.columns[1:],
                                                    help='Select a column that you want to represent vertical axis.',
                                                    index=7)
                gca_scatter_feature3 = st.selectbox('Select Point Sizes', gca_player.columns[1:],
                                                    help='Select a column that you want to represent point sizes.',
                                                    index=8)
            fig = px.scatter(gca_player, gca_scatter_feature1, gca_scatter_feature2,
                             text='Name',
                             color='Club',
                             color_discrete_map=colours,
                             size=gca_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {gca_scatter_feature3}'
            )
            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )
        with defense:
            st.dataframe(defense_player)
            with st.container():
                defense_scatter_feature1 = st.selectbox('Select X-axis', defense_player.columns[1:],
                                                        help='Select a column that you want to represent horizontal axis.',
                                                        index=13)
                defense_scatter_feature2 = st.selectbox('Select Y-axis', defense_player.columns[1:],
                                                        help='Select a column that you want to represent vertical axis.',
                                                        index=19)
                defense_scatter_feature3 = st.selectbox('Select Point Sizes', defense_player.columns[1:],
                                                        help='Select a column that you want to represent point sizes.',
                                                        index=7)
            fig = px.scatter(defense_player, defense_scatter_feature1, defense_scatter_feature2, text='Name',
                             color='Club',
                             color_discrete_map=colours,
                             size=defense_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {defense_scatter_feature3}'
            )
            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )
        with possession:
            st.dataframe(possession_player)
            with st.container():
                possession_scatter_feature1 = st.selectbox('Select X-axis', possession_player.columns[1:],
                                                           help='Select a column that you want to represent horizontal axis.',
                                                           index=13)
                possession_scatter_feature2 = st.selectbox('Select Y-axis', possession_player.columns[1:],
                                                           help='Select a column that you want to represent vertical axis.',
                                                           index=11)
                possession_scatter_feature3 = st.selectbox('Select Point Sizes', possession_player.columns[1:],
                                                           help='Select a column that you want to represent point sizes.',
                                                           index=14)
            fig = px.scatter(possession_player, possession_scatter_feature1, possession_scatter_feature2, text='Name',
                             color='Club',
                             color_discrete_map=colours,
                             size=possession_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {possession_scatter_feature3}'
            )
            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )
        with misc:
            st.dataframe(misc_player)
            with st.container():
                misc_scatter_feature1 = st.selectbox('Select X-axis', misc_player.columns[1:],
                                                     help='Select a column that you want to represent horizontal axis.',
                                                     index=21)
                misc_scatter_feature2 = st.selectbox('Select Y-axis', misc_player.columns[1:],
                                                     help='Select a column that you want to represent vertical axis.',
                                                     index=18)
                misc_scatter_feature3 = st.selectbox('Select Point Sizes', misc_player.columns[1:],
                                                     help='Select a column that you want to represent point sizes.',
                                                     index=9)
            fig = px.scatter(misc_player, misc_scatter_feature1, misc_scatter_feature2, text='Name',
                             color='Club',
                             color_discrete_map=colours,
                             size=misc_scatter_feature3)
            fig.update_traces(textposition="top center")
            fig.update_layout(
                autosize=False,
                width=700,
                height=550,
                legend={'itemsizing': 'constant'},
                legend_title_text=f'Point Size: {misc_scatter_feature3}'
            )
            fig.update_yaxes(
                title_standoff=15,
                automargin=True)
            st.plotly_chart(fig)
            mybuff = StringIO()
            fig.write_html(mybuff, include_plotlyjs='cdn')
            html_bytes = mybuff.getvalue().encode()

            st.download_button(
                label='Download as HTML',
                data=html_bytes,
                file_name='stuff.html',
                mime='text/html'
            )
    if 'players_list' in st.session_state:
        st.button('Clear', on_click=clear_list)

with teams:
    with st.form('form'):
        sel_column = st.multiselect('Select column', fbref_table.columns,
                                    help='Select a column to form a new dataframe. Press submit when done.',
                                    default=['Club', 'Points', 'Goals', 'Goals_against',
                                             'Possession'])
        submitted = st.form_submit_button("Submit")

    if not submitted or sel_column == []:
        st.dataframe(fbref_table.iloc[:, :6], use_container_width=True, height=400)

    elif submitted:
        dfnew = fbref_table[sel_column]

        st.write('New dataframe')
        dfnew_style = dfnew.style.format(precision=2, na_rep='MISSING', thousands=",", formatter={('A'): "{:.0f}"})
        st.dataframe(dfnew_style, use_container_width=True, height=400)

    tab1, tab2 = st.tabs(["Bar-plot", "Scatter-plot"])

    with tab1:
        with st.container():
            bar_feature = st.selectbox('Select column', fbref_table.columns[1:],
                                       help='Select a column to create a plot.', index=5)

        fig = px.bar(fbref_table, bar_feature, 'Club', orientation='h', color='Club', color_discrete_map=colours)
        fig.update_layout(
            autosize=False,
            width=700,
            height=550,
        )
        fig.update_yaxes(
            title_standoff=5,
            automargin=True)
        st.plotly_chart(fig)
        mybuff = StringIO()
        fig.write_html(mybuff, include_plotlyjs='cdn')
        html_bytes = mybuff.getvalue().encode()

        st.download_button(
            label='Download as HTML',
            data=html_bytes,
            file_name='stuff.html',
            mime='text/html'
        )
    with tab2:
        with st.container():
            scatter_feature1 = st.selectbox('Select X-axis', fbref_table.columns[1:],
                                            help='Select a column that you want to represent horizontal axis.',
                                            index=20)
            scatter_feature2 = st.selectbox('Select Y-axis', fbref_table.columns[1:],
                                            help='Select a column that you want to represent vertical axis.',
                                            index=96)
            scatter_feature3 = st.selectbox('Select Point Sizes', fbref_table.columns[1:],
                                            help='Select a column that you want to represent point sizes.',
                                            index=12)
        fig = px.scatter(fbref_table, scatter_feature1, scatter_feature2, text='Club', color='Club',
                         color_discrete_map=colours,
                         size=scatter_feature3)
        fig.update_traces(textposition="top center")
        fig.update_layout(
            autosize=False,
            width=700,
            height=550,
            legend={'itemsizing': 'constant'},
            legend_title_text=f'Point Size: {scatter_feature3}'
        )
        fig.update_yaxes(
            title_standoff=15,
            automargin=True)
        st.plotly_chart(fig)
        mybuff = StringIO()
        fig.write_html(mybuff, include_plotlyjs='cdn')
        html_bytes = mybuff.getvalue().encode()

        st.download_button(
            label='Download as HTML',
            data=html_bytes,
            file_name='stuff.html',
            mime='text/html'
        )
