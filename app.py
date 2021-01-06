
import os

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from datetime import date

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt



import psycopg2 as pg





# PAGE CONFIG

st.set_page_config(
	page_title = "Spotter Operantar XXXIX",
	page_icon = 'logo_MB.png',
	layout = 'centered',
	)




# STYLE PAGE

st.markdown(
    """
<style>


.overlayBtn {
    display: none;
}


body {
    color: #fff;
    background-color: #111;
    text-align: center;
}


.reportview-container .markdown-text-container{
	font-family: Arial, Helvetica sans-serif;
}



# .streamlit-button {
# 	color: rgb(218, 165, 32);
# }


.st-dx {
	background-color: #555555
}

.Widget>label {
	color: #fafafa
}



# .st-c2 {
# 	background-color: transparent;
# }


# .st-cm {
# 	background-color: transparent;
# }

# .st-cn {
# 	color: #DAA520;
# }

# .st-ck {
# 	color: rgb(218, 165, 32);
# }

# .st-cl {
# 	background-color: transparent;
# }

# .st-bg{
#     color: rgb(218, 165, 32);
# }


.st-bd{
    color: rgb(218, 165, 32);
}

.st-cr{
    color: rgb(218, 165, 32);
}


.st-ag{
	font-weight: bold;
}


# .st-dh:focus {
#     background-color: rgba(120, 160, 160, 0.5);
# }

# .st-dk:focus {
#     color: rgb(0, 0, 128);
# }

# .st-di:focus {
#     border-color: rgb(0, 0, 128);
# }

# .st-dj:focus {
#     box-shadow: rgba(0, 0, 128, 0.5) 0px 0px 0px 0.2rem;
# }




.btn-outline-secondary {
	border-color: #333333;
	color: #FFFF00;
}



canvas {
max-width: 100%!important;
height: auto!important;
}

# .sidebar .sidebar-content {
#     background-image: linear-gradient(#372066,#111111);
#     font-color: #fff;
# }





.st-ci {
	color: #DAA520;
	font-weight: bold;
	font-family: Times New Roman, sans-serif;
}


#MainMenu {
	visibility: hidden;
}


footer {
	visibility: hidden;
	}

# footer:after {
# 	content:'Centro de Hidrografia da Marinha \A Diretoria de Hidrografia e Navegação \A Marinha do Brasil';
# 	white-space: pre;
# 	visibility: visible;
# 	display: block;
# 	position: relative;
# 	#background-color: red;
# 	padding: 5px;
# 	top: 2px;

}







</style>
""",
    unsafe_allow_html=True,
)



# configs_plot plotly
config = {'displaylogo': False}


plot_height = 450
plot_width = 1000


# Layout of box:
bn_width = 500
bn_height = 800








# SIDEBAR - MENU

# st.sidebar.image("logo_MB.png")
# st.sidebar.title("Menu")
# st.sidebar.subheader("Spotter Operantar XXXIX")
# st.sidebar.markdown("---")





st.title('SPOTTER - OPERANTAR XXXIX')

# Mapa MapBox:

token_mapbox = os.environ['MB_TOKEN']






### STATUS ####

@st.cache(allow_output_mutation = True)
def get_last_values_spotter():



	with pg.connect(user=os.environ['USER_RAW'],
                      password=os.environ['PASSWORD_RAW'],
                      host=os.environ['HOST_RAW'],
                      database=os.environ['DATABASE_RAW']) as conn:

		query = "SELECT * FROM spotter_status ORDER BY date_time DESC LIMIT 2"

		df_status = pd.read_sql_query(query, conn)
		
		

	return df_status

df_status = get_last_values_spotter()


def meters_to_knots(df):

	df['Wspd'] = (df['Wspd']/0.5144).round(1)

	return df




@st.cache(allow_output_mutation = True)
def get_last_values_spotter_general():



	with pg.connect(user=os.environ['USER_QC'],
                      password=os.environ['PASSWORD_QC'],
                      host=os.environ['HOST_QC'],
                      database=os.environ['DATABASE_QC']) as conn:

		query = """SELECT date_time, 
				 lat as "Lat",
				 lon as "Lon", 
				 sst, swvht1 as "Hs", 
				 tp1 as "Tp", 
				 mean_tp as "Mean_Tp", 
				 pk_dir as "Peak_Dir",
				 wvdir1 as "Wave_Dir", 
				 pk_wvspread as "Peak_Spread", 
				 wvspread1 as "Wave_Spread",
				 wspd as "Wspd",
				 wdir as "Wdir"
				 FROM data_buoys
		         WHERE date_time = (SELECT max(date_time)
		         FROM data_buoys where buoy_id = 3)"""


		df_general = pd.read_sql_query(query, conn)
		df_general = meters_to_knots(df_general)
		
		

	return df_general

df_general = get_last_values_spotter_general()

df_general = df_general.fillna(value=np.nan)





last_data = pd.Timestamp(df_status.date_time.values[0])
lat = abs(df_status.latitude.values[0].round(4))
lon = abs(df_status.longitude.values[0].round(4))

temp = df_general.sst.values[0]
humidity = df_status.humidity.values[0]
wind_dir = df_general.Wdir.values[0]
wind_spe = df_general.Wspd.values[0]
swvht = df_general.Hs.values[0].round(2)
tp = df_general.Tp.values[0].round(1)
dir_wave = df_general.Wave_Dir.values[0].round(1)
dir_peak = df_general.Peak_Dir.values[0].round(1)
solar_v = df_status.solar_voltage.values[0]

battery_p = df_status.battery_power.values[0]
battery_v = df_status.battery_voltage.values[0]



st.markdown("---")
st.subheader("ÚLTIMO DADO")
st.markdown(last_data)



big_n = go.Figure()


# Order of lines in dash

row_params = 0
row_waves_1 = 1
row_waves_2 = 2
row_coords_fundeio = 3
row_coords_boia = 4


col_1_pos = 0
col_2_pos = 2
col_3_pos = 4
n_cols = 5

#row_params_2 = 2


##################

# COORDS FUNDEIO

big_n.add_trace(go.Indicator(
    mode = "number",
    value = lat,
    title = {'text':'LAT FUNDEIO', 'font':{'size':12, 'color':'white'}},
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
              'suffix': '° S',
              'valueformat':'0'},
    domain = {'row': row_coords_fundeio, 'column': col_1_pos}))


big_n.add_trace(go.Indicator(
    mode = "number",
    value = lon,
    title = {'text':'LON FUNDEIO', 'font':{'size':12, 'color':'white'}},
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
              'suffix': '° W',
              'valueformat':'0'},
    domain = {'row': row_coords_fundeio, 'column': col_3_pos}))


# COORDS BOIA

big_n.add_trace(go.Indicator(
    mode = "number",
    value = lat,
    title = {'text':'LAT ÚLTIMA POSICÃO', 'font':{'size':12, 'color':'white'}},
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
              'suffix': '° S',
              'valueformat':'0'},
    domain = {'row': row_coords_boia, 'column': col_1_pos}))


big_n.add_trace(go.Indicator(
    mode = "number",
    value = lon,
    title = {'text':'LON  ÚLTIMA POSICÃO', 'font':{'size':12, 'color':'white'}},
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
              'suffix': '° W',
              'valueformat':'0'},
    domain = {'row': row_coords_boia, 'column': col_3_pos}))




# TEMP-  DIR VENTO  - VEL VENTO

# 1
big_n.add_trace(go.Indicator(
    mode = "number",
    title = {'text':'TEMP', 'font':{'size':12, 'color':'white'}},
    value = temp,
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
               'suffix': '°C'},
    domain = {'row': row_params, 'column': col_1_pos}))

# 2
# big_n.add_trace(go.Indicator(
#     mode = "number",
#     title = {'text':'U.R.', 'font':{'size':12, 'color':'white'}},
#     value = umidade,
#     number = {'font':{'color':'white',
#                       'size': 32,
#                       'family': 'Times New Roman'},
#                'suffix': '%'},
#     domain = {'row': row_params, 'column': 1}))

# 3
big_n.add_trace(go.Indicator(
    mode = "number",
    title = {'text':'DIR.VENTO', 'font':{'size':12, 'color':'white'}},
    value = wind_dir,
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
               'suffix': '°'},
    domain = {'row': row_params, 'column': col_2_pos}))

# 4
big_n.add_trace(go.Indicator(
    mode = "number",
    title = {'text':'VEL.VENTO', 'font':{'size':12, 'color':'white'}},
    value = wind_spe,
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
               'suffix': ' kn'},
    domain = {'row': row_params, 'column': col_3_pos}))

# TERCEIRA ROW - WAVES








big_n.add_trace(go.Indicator(
    mode = "number",
    title = {'text':'DIR MÉDIA ONDA', 'font':{'size':12, 'color':'white'}},
    value = dir_wave,
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
               'suffix': '°'},
    domain = {'row': row_waves_1, 'column': col_1_pos}))

big_n.add_trace(go.Indicator(
    mode = "number",
    title = {'text':'DIR. PICO ONDA', 'font':{'size':12, 'color':'white'}},
    value = dir_peak,
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
               'suffix': '°'},
    domain = {'row': row_waves_1, 'column': col_3_pos}))



big_n.add_trace(go.Indicator(
    mode = "number",
    title = {'text':'TP', 'font':{'size':12, 'color':'white'}},
    value = tp,
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
               'suffix': ' s'},
    domain = {'row': row_waves_2, 'column': col_1_pos}))

big_n.add_trace(go.Indicator(
    mode = "number",
    title = {'text':'HS', 'font':{'size':12, 'color':'white'}},
    value = swvht,
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
               'suffix': ' m'},
    domain = {'row': row_waves_2, 'column': col_3_pos}))




### Layout Graph
big_n.update_layout(
    grid = {'rows': 6, 'columns': n_cols, 'pattern': "independent"},
    template = {'data' : {'indicator': [{
    #    'title': {'text': "Bateria"},
        'mode' : "number",
        'delta' : {'reference': 12}}]
                         }},
                         paper_bgcolor = '#111',
                         plot_bgcolor = '#111',
                         height = bn_height,
                         width = bn_width)

# Plot
st.plotly_chart(big_n, config = config, use_container_width = False)



st.markdown("---")
st.subheader("SISTEMA BOIA")
#st.markdown("2020-06-05 12:42:00")


big_n_2 = go.Figure()


row_system = 1


if len(df_status) == 2:
  last_battery_v = df_status.battery_voltage.values[1]
  last_solar_v = df_status.solar_voltage.values[1]

elif len(df_status) == 1:
  last_battery_v = np.nan
  last_solar_v = np.nan






big_n_2.add_trace(go.Indicator(
    mode = "number + delta",
    title = {'text':'BATERIA V', 'font':{'size':12, 'color':'white'}},
    value = battery_v,
    number = {'font':{'color':'white',
                      'size': 30,
                      'family': 'Times New Roman'},
              'suffix': ' V'},
    domain = {'row': row_system, 'column': col_1_pos},
    delta = {'reference': last_battery_v, 'decreasing':{'color':'red'}},
                    )
                )

big_n_2.add_trace(go.Indicator(
    mode = "number + delta",
    title = {'text':'BATERIA SOLAR', 'font':{'size':12, 'color':'white'}},
    value = solar_v,
    number = {'font':{'color':'white',
                      'size': 30,
                      'family': 'Times New Roman'},
              'suffix': ' V'},
    domain = {'row': row_system, 'column': col_2_pos},
    delta = {'reference': last_solar_v, 'decreasing':{'color':'red'}},
                    )
                )



big_n_2.add_trace(go.Indicator(
    mode = "number",
    value = humidity,
    title = {'text':'UMIDADE INTERNA', 'font':{'size':12, 'color':'white'}},
    number = {'font':{'color':'white',
                      'size': 32,
                      'family': 'Times New Roman'},
              'suffix': '%',
              'valueformat':'0'},
    domain = {'row': row_system, 'column': col_3_pos}))






### Layout Graph

bn_2_height = 200

big_n_2.update_layout(
    grid = {'rows': 1, 'columns': n_cols, 'pattern': "independent"},
    template = {'data' : {'indicator': [{
    #    'title': {'text': "Bateria"},
        'mode' : "number+delta+gauge",
        }]
                         }},
                         paper_bgcolor = '#111',
                         plot_bgcolor = '#111',
                         height = bn_2_height,
                         width = bn_width)



st.plotly_chart(big_n_2, config = config, use_container_width = False)







st.markdown("---")






st.markdown("---")



namesp = ['SPOT-0731']
pointsLat = df_status.latitude.values[0]
pointsLon = df_status.longitude.values[0]




teste_df = pd.DataFrame({'name': namesp,
                         'lat': pointsLat,
                         'lon': pointsLon})


map_location = px.scatter_mapbox(teste_df, lat="lat", lon="lon", hover_name="name",
                            hover_data=["name"], zoom=9)
map_location.update_layout(mapbox_style="dark", mapbox_accesstoken=token_mapbox)
map_location.update_layout(margin={"r":0,"t":0,"l":0,"b":0})





st.header("LOCALIZAÇÃO")



st.plotly_chart(map_location, config = config, use_container_width = True)




########
######## ONDA





st.markdown('---')
st.title("Consulta de Dados")
#st.sidebar.subheader("Dados de Onda")


start_date = st.date_input("Início", date.today() - timedelta(days = 3))
end_date = st.date_input("Fim", date.today())



@st.cache
def get_waves_data(start_date, end_date):



  with pg.connect(user=os.environ['USER_QC'],
                      password=os.environ['PASSWORD_QC'],
                      host=os.environ['HOST_QC'],
                      database=os.environ['DATABASE_QC']) as conn:
                     
                     

    query = """SELECT date_time, 
         lat as "Lat",
         lon as "Lon", 
         sst, swvht1 as "Hs", 
         tp1 as "Tp", 
         mean_tp as "Mean_Tp", 
         pk_dir as "Peak_Dir",
         wvdir1 as "Wave_Dir", 
         pk_wvspread as "Peak_Spread", 
         wvspread1 as "Wave_Spread",
         wspd as "Wspd",
         wdir as "Wdir"
         FROM data_buoys
             WHERE date_time >= '{}' and date_time <= '{}' and buoy_id = 3""".format(start_date, end_date)

   	
    df_waves = pd.read_sql_query(query, conn)
    df_waves['Date'] = [day.date() for day in df_waves['date_time']]
    df_waves['Hour'] = [day.time() for day in df_waves['date_time']]

  	

  return df_waves


@st.cache(allow_output_mutation=True)
def get_wind_data(start_date, end_date):

  with pg.connect(user=os.environ['USER_QC'],
		      password=os.environ['PASSWORD_QC'],
		      host=os.environ['HOST_QC'],
		      database=os.environ['DATABASE_QC']) as conn:

    query = f"""SELECT date_time, \
		 lat as "Lat", lon as "Lon", \
		TRUNC(wspd,2) as "Wspd", \
		 wdir as "Wind_Dir" \
		 FROM data_buoys \
		WHERE date_time >='{start_date}' and \
	       date_time <= '{end_date}' \
	      AND buoy_id = 3"""

		
    df_wind = pd.read_sql_query(query, conn)
    df_wind['Date'] = [day.date() for day in df_wind['date_time']]
    df_wind['Hour'] = [day.time() for day in df_wind['date_time']]
    df_wind = meters_to_knots(df_wind)

   	

  return df_wind






button_sql = st.button("Get Data")

if button_sql:
	df_waves = get_waves_data(start_date, end_date)
	df_wind = get_wind_data(start_date, end_date)




	if not df_waves.empty:

		st.title("Dados de Onda")
		st.write(df_waves)
	

		ht_plot = px.line(df_waves, x = 'date_time', y = 'Hs', template = 'plotly_dark',
		                    title = '<b>Altura Significativa</b>',
		                    labels = {'date_time': '<b>DATA HORA</b>', 'Hs': '<b>METROS</b>'},
		                    height = plot_height,
		                    width = plot_width)
		#layout
		ht_plot.update_traces(line = dict(color = 'Blue', width = 1), mode = 'markers+lines')

		st.plotly_chart(ht_plot, config = config, use_container_width = True)



	#### GRAFICO PERIODO

	#if st.sidebar.checkbox("Período"):
		pk_plot = px.line(df_waves, x = 'date_time', y = 'Tp', template = 'plotly_dark',
		                    title = '<b>Período</b>',
		                    labels = {
		                    'Tp': '<b>SEGUNDOS</b>',
		                    'date_time': '<b>DATA HORA</b>',
		                     'value': '<b>SEGUNDOS</b>'},
		                    height = plot_height,
		                    width = plot_width)
		#layout
		pk_plot.update_traces(line = dict(width = 2, color = 'yellow'), mode = 'markers+lines')
		pk_plot.update_layout(legend=dict(
		    orientation="h",
		    yanchor="bottom",
		    y=1.02,
		    xanchor="right",
		    x=1
		))
		st.plotly_chart(pk_plot, config = config, use_container_width = True)



	else:
		st.markdown("### Sem dados para o período selecionado.")



	if not df_wind.empty:

		st.title("Dados de Vento")
		st.write(df_wind.astype('object'))


		wind_fig = px.bar_polar(df_wind, r = 'Wspd', theta = 'Wind_Dir', template = 'plotly_dark',
		                    color_discrete_sequence = px.colors.sequential.Plasma_r,
		                    )

		wind_fig.update_layout(
		    height = plot_height+100,
		    width = plot_width,
		    title = dict(
		            text = '<b>Velocidade (nós) e Direção Média para o Período Selecionado</b>',
		            font = dict(family = 'Times New Roman',
		                        size = 18
		            )
		    )
		)

		
		st.plotly_chart(wind_fig, config = config, use_container_width = True)




	st.markdown("---")




