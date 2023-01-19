import streamlit as st
import numpy as np
import requests
import pandas as pd
import plotly.express as px


@st.experimental_memo(experimental_allow_widgets=True)
def get_data():
    with st.container():
        st.header('Select season to be displayed')
        season = st.radio("Select the season",
                          ('2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019', '2017-2018'))
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

data_attack = team_data[2]
data_defense = team_data[3]
data_standard = team_data[0]


def create_team_table(data_standard, data_attack, data_defense):
    def create_standard_table(team):
        if 'Last 5' in team.columns:
            team.drop('Last 5', axis=1, inplace=True)

        team.columns = ['Standing', 'Club', 'Matches', 'Won', 'Draw', 'Lost',
                        'Goals', 'Goals_Against', 'Goal_difference', 'Points', 'Points_Per_Match', 'xG', 'xGA',
                        'xGD', 'xGDP90', 'Attendance', 'TopScorer', 'Goalie', 'Notes']
        team.drop(['Goals', 'Goals_Against', 'Goal_difference', 'Points_Per_Match',
                   'xG', 'xGD', 'xGA', 'xGDP90',
                   'TopScorer', 'Attendance', 'Goalie', 'Notes'], axis=1, inplace=True)
        return team

    def create_attack_table(team):
        team.columns = ['Club', 'NumberOfPlayers', 'Age', 'Possesion', 'MatchesPlayed', 'NumberOfStarts',
                        'MinutesPlayed', 'MinutesPlayedP90', 'Goals', 'Assists', 'NPGoals', 'PenaltyGoals',
                        'Penalties', 'YellowCards', 'RedCards', 'GoalsP90', 'AssistsP90', 'Goals+AssistsP90',
                        'NPGoalsP90', 'NPGoals+AssistsP90', 'xG', 'NPxG', 'xA', 'NPxG+xA', 'xGP90', 'xAP90',
                        'xG+xAP90', 'NPxGP90', 'NPxG+xAP90']
        team.drop(['NumberOfStarts', 'MinutesPlayed', 'MinutesPlayedP90',
                   'Assists', 'AssistsP90', 'Goals+AssistsP90', 'NPGoals+AssistsP90',
                   'xA', 'NPxG+xA', 'xAP90', 'xG+xAP90', 'NPxG+xAP90'], axis=1, inplace=True)
        return team

    def create_defense_table(team):
        team.columns = ['Club', 'NumberOfPlayers', 'Age', 'Possesion', 'MatchesPlayed', 'NumberOfStarts',
                        'MinutesPlayed', 'MinutesPlayedP90', 'Goals_Against', 'Assists', 'NPGoals_Against',
                        'PenaltyGoals_Against', 'Penalties_Against', 'YellowCards_Against', 'RedCards_Against',
                        'GoalsP90_Against', 'AssistsP90_Against',
                        'Goals+AssistsP90_Against',
                        'NPGoalsP90_Against', 'NPGoals+AssistsP90_Against', 'xG_Against', 'NPxG_Against',
                        'xA_Against', 'NPxG+xA_Against', 'xGP90_Against', 'xAP90_Against',
                        'xG+xAP90_Against', 'NPxGP90_Against', 'NPxG+xAP90_Against']

        team.drop(['NumberOfStarts', 'MinutesPlayed', 'MinutesPlayedP90',
                   'Assists', 'NumberOfPlayers', 'Age', 'Possesion', 'MatchesPlayed',
                   'AssistsP90_Against', 'Goals+AssistsP90_Against', 'NPGoals+AssistsP90_Against',
                   'xA_Against', 'NPxG+xA_Against', 'xAP90_Against', 'xG+xAP90_Against', 'NPxG+xAP90_Against'
                   ], axis=1, inplace=True)
        team['Club'] = team['Club'].str.slice_replace(0, 3, '')
        return team

    table_defense = create_defense_table(data_defense)
    table_attack = create_attack_table(data_attack)
    table_standard = create_standard_table(data_standard)

    merged = pd.merge(table_attack, table_defense, on='Club')
    return pd.merge(table_standard, merged, on='Club')


fbref_table = create_team_table(data_standard, data_attack, data_defense)
fbref_table.update(fbref_table.select_dtypes(include=np.number).applymap('{:,g}'.format))
for column in fbref_table.columns:
    fbref_table[column] = pd.to_numeric(fbref_table[column], errors='ignore')
fbref_table = fbref_table.iloc[:, 1:]
fbref_table.index += 1

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
                             'Starts', 'Minutes/90', 'Full Matches', 'Goals', 'Assists', 'NPGoals',
                             'Penalty Goals', 'Penalty Attempts', 'Yellow Cards', 'Red Cards', 'GoalsP90',
                             'AssistsP90', 'Goals+AssistsP90', 'NPGoalsP90', 'NPGoals+AssistsP90', 'xG', 'NPxG',
                             'xAG', 'NPxG+xAG', 'xGP90', 'xAGP90', 'xG+xAGP90', 'NPxGP90', 'NPxG+xAGP90']
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
                             'Live-ball Touches', 'Successful Dribbles', 'Dribbles Attempted', 'Dribbles Success%',
                             'Miscontrols', 'Dispossessed', 'Passes Received', 'Progressive Passes Received']
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
                                          help='Select a column to form a new dataframe. Press submit when done.')


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
    if 'players_list' in st.session_state:
        st.button('Clear', on_click=clear_list)

with teams:
    with st.form('form'):
        sel_column = st.multiselect('Select column', fbref_table.columns,
                                    help='Select a column to form a new dataframe. Press submit when done.',
                                    default=['Club', 'Points', 'Goals', 'Goals_Against'])
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
                                       help='Select a column to create a plot. Press submit when done.', index=4)

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
    with tab2:
        with st.container():
            scatter_feature1 = st.selectbox('Select X-axis', fbref_table.columns[1:],
                                            help='Select a column that you want to represent horizontal axis.',
                                            index=17)
            scatter_feature2 = st.selectbox('Select Y-axis', fbref_table.columns[1:],
                                            help='Select a column that you want to represent vertical axis.',
                                            index=7)
            scatter_feature3 = st.selectbox('Select Point Sizes', fbref_table.columns[1:],
                                            help='Select a column that you want to represent point sizes.',
                                            index=29)
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
