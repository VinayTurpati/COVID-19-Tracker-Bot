import os
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import locale
import traceback
from matplotlib import dates
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
sns.set_style("darkgrid")

import os
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import locale
import traceback
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
sns.set_style("darkgrid")


class COVID_Tracker():
    
    def __init__(self):
        self.COVID19_API_URL_HISTORY = "https://api.covid19api.com"
        self.COVID19_API_LIVE = "https://corona.lmao.ninja/v2"
        self.PLOT_OUTPUT_DIR = "../flask_server/static/img"
        self.IMG_API_URL = "http://ec2-13-126-127-146.ap-south-1.compute.amazonaws.com:5020/img/"
        
    def convert_timestamp(self, time_str, time_format):
        if not time_str:
            return None
        time_str = time_str.split("T")[0]
        try:
            return datetime.strptime(time_str, "%Y-%m-%d").strftime(time_format)
        except Exception as e:
            pass
        return None

    def add_day_end_hour(self, time_str, time_format):
        if not time_str:
            return None
        time_str = time_str
        try:
            date_Obj = datetime.strptime(time_str, time_format)
            date_Obj = date_Obj + timedelta(hours=23,minutes=59)
            return date_Obj.strftime(time_format)
        except Exception as e: 
            print(e)
        return None

    def is_todays_date(self, to_date_str, time_format):
        if not to_date_str:
            return False
        to_date = datetime.strptime(to_date_str, time_format).strftime("%y-%m-%d")
        today_date = datetime.now().strftime("%y-%m-%d")    
        if to_date == today_date:
            return True
        return False

    def generate_api_url_using_entites(self, slots, entities):
        url = ""
        from_date, to_date = "", ""
        url_type = []
        status = False
        api_url = []
        country_name = [ent["value"] for ent in entities if ent['entity']=="GPE"]
        corono_status = slots["corono_status"]
        TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
        if "time" in slots and slots["time"]:
            time_values = slots["time"]
            if time_values:

                if time_values == str and time_values != "":
                    to_date = self.convert_timestamp(time_values, TIME_FORMAT)

                if "from" in time_values and time_values["from"]:
                    from_date = time_values["from"]            
                    from_date = self.convert_timestamp(from_date, TIME_FORMAT)
                if "to" in time_values and time_values["to"]:
                    to_date = time_values["to"]
                    to_date = self.convert_timestamp(to_date, TIME_FORMAT)
                
                if from_date == "" and not self.is_todays_date(to_date, TIME_FORMAT):
                    from_date = to_date
                    to_date = self.add_day_end_hour(to_date, TIME_FORMAT)    

        if from_date and len(country_name) == 1:
            api_url.append(f"{self.COVID19_API_URL_HISTORY}/country/{country_name[0]}?from={from_date}&to={to_date}")
            url_type.append("API1")
            status = True
        elif len(country_name) == 1:
            ## get today's live covid cases
            api_url.append(f"{self.COVID19_API_LIVE}/countries/{country_name[0]}")
            url_type.append("API2")
            status = True
        elif len(country_name) > 1:
            ## comparision of two country
            for country in country_name:
                api_url.append(f"{self.COVID19_API_LIVE}/countries/{country}")        
                url_type.append("API2")
            status = True
        return {"status":status, "url":api_url, "corono_status":corono_status, "url_type":url_type, "from_date":from_date,
               "to_date":to_date, "country":country_name, "spread_level":slots["spread_level"]}
    
    def get_covid_cases_by_api(self, api_endpoint):
        status = False
        data = {}
        try:
            response = requests.get(api_endpoint,timeout=5)
            data = response.json()    
            status = True
        except Exception as e:
            status = False

        return {"status":status, "data":data}

    def validate_api_response_for_date(self, url_type, api_response, from_date, to_date):
        covid_df = None
        if "API1" == url_type:
            df = pd.DataFrame.from_dict(api_response["data"])
            df["Date"] = df["Date"].str.split("T").str[0]
            df["Date"] = pd.to_datetime(df["Date"])
            
            if from_date != "" and to_date != "":
                from_date = from_date.split("T")[0]
                to_date = to_date.split("T")[0]
                df = df[(df['Date'] >= from_date) & (df['Date'] <= to_date)]
            
            covid_df = df
        elif "API2" == url_type:
            data = {"updated": api_response["data"]["updated"],                
                    "Confirmed": api_response["data"]["cases"],
                    "Active": api_response["data"]["active"],
                    "Deaths": api_response["data"]["deaths"],
                    "Recovered": api_response["data"]["recovered"],
                    "todayCases": api_response["data"]["todayCases"],
                    "todayDeaths": api_response["data"]["todayDeaths"],
                    "todayRecovered": api_response["data"]["todayRecovered"]}
            df = pd.DataFrame.from_dict([data])
            covid_df = df
        
        return covid_df
    
    def create_plot_for_covid_cases(self, data, country_name, corono_status):
        fig, ax = plt.subplots()
        today_date = datetime.now().strftime("%d%m%Y_%H%M%S")        
        sns.set(rc={'figure.figsize':(11.7,8.27)})        
        updated_info = ""
        bot_msg = ""
        country_names = "".join(country_name)
        updated_date = "today"
        #print(data.shape, data.columns, country_name)
        if len(data) == 1:
            if "todayCases" in data:
                today_cases_info = data[["todayCases","todayDeaths", "todayRecovered"]]
                updated_info = data["updated"][0]                
                updated_date = datetime.fromtimestamp(int(updated_info)/1000)  # using the local timezone
                updated_date = updated_date.strftime("%Y-%m-%d %H:%M:%S")
                data.drop(["todayCases","todayDeaths", "todayRecovered","updated"], axis=1, inplace=True)
            else:
                data = data[["Active","Confirmed","Deaths","Recovered"]]
            data = data / 1000            
            ## get current corono status                     
            chart = sns.barplot(data=data.head(1))
            chart.set_title(f'COVID-19 Cases Status - {country_name[0].upper()}')
            for index, row in enumerate(data.values.tolist()[0]):    
                chart.text(index ,row+0.7, locale.format("%d", int(row*1000), grouping=True), color='black', ha="center")
            chart.set(ylabel='No of COVID cases (per 1K)', xlabel=f'Status updated on {updated_date}')
            #print(data, corono_status.title())
            if corono_status:
                if corono_status.title() in data:                    
                    spread_level_cases = int(data[corono_status.title()][0] * 1000)
                    bot_msg = f"*{corono_status.title()} cases: {spread_level_cases}*. The below is the COVID-19 Cases updates for *{country_name[0].upper()}*"
                else:
                    bot_msg = f"The below is the COVID-19 Cases updates for *{country_name[0].upper()}*"
            else:
                bot_msg = f"The below is the COVID-19 Cases updates for *{country_name[0].upper()}*"
            #bot_msg = f"The below is the COVID-19 Cases updates for {country_name[0].upper()}"
            #plt.show()            
        elif len(data) > 1 and len(country_name) == 1:
            df_grp = data.groupby(["Date"]).agg(sum)            
            df_grp = df_grp / 1000
            df_grp.reset_index(inplace=True)
            df_grp.index = pd.to_datetime(df_grp["Date"])
            df_grp.drop(["Date"], inplace=True, axis=1)
            print(df_grp.head())
            chart = sns.lineplot(data=df_grp, ax=ax, markers=True, dashes=False, style='label')
            #print(df_grp)
            chart.set_title(f'COVID-19 Cases Status - {country_name[0].upper()}')
            chart.set(ylabel='No of COVID cases (per 1K)', xlabel='Status')
            #ax.set(xticks=df_grp.index.values)
            ax.xaxis.set_major_formatter(dates.DateFormatter("%d-%b"))
            #bot_msg = f"The below is the COVID-19 Cases updates for {country_name[0].upper()}"
            if corono_status:
                if corono_status.title() in df_grp:
                    spread_level_cases = int(df_grp[corono_status.title()][0] * 1000)
                    bot_msg = f"*{corono_status.title()} cases: {spread_level_cases}*. The below is the COVID-19 Cases updates for *{country_name[0].upper()}*"
                else:
                    bot_msg = f"The below is the COVID-19 Cases updates for *{country_name[0].upper()}*"
            else:
                bot_msg = f"The below is the COVID-19 Cases updates for *{country_name[0].upper()}*"
            #plt.show()
        elif len(country_name) == 2:
            
            data["cases"] = data["cases"] / 10000
            updated_info = data["updated"][0]        
            updated_date = datetime.fromtimestamp(int(updated_info)/1000)  # using the local timezone
            updated_date = updated_date.strftime("%Y-%m-%d %H:%M:%S")            
            chart = sns.barplot(data=data,  x="status", y="cases", hue="country")
            country_names = " Vs ".join(country_name)
            chart.set_title(f'COVID-19 Cases Status - {country_names.upper()}')
            """
            for index, row in enumerate(data["cases"].tolist()):  
                print(index, row)
                chart.text(index ,row+0.7, locale.format("%d", int(row*10000), grouping=True), color='black', ha="center")
            """
            chart.set(ylabel='No of COVID cases (per 10K)', xlabel=f'Status updated on {updated_date}')
            #bot_msg = f"The below is the COVID-19 Cases comparision for {country_names.upper()}"
            if corono_status:
                if corono_status.title() in data:
                    spread_level_cases = int(data[corono_status.title()][0] * 100000)
                    bot_msg = f"*{corono_status.title()} cases: {spread_level_cases}*. The below is the COVID-19 Cases comparision for {country_names.upper()}*"
                else:                
                    bot_msg = f"The below is the COVID-19 Cases comparision for *{country_names.upper()}*"
            else:                
                bot_msg = f"The below is the COVID-19 Cases comparision for *{country_names.upper()}*"
            #plt.show()
            country_names = "_".join(country_name)
        img_file_name = os.path.join(self.PLOT_OUTPUT_DIR, f'{country_names.upper()}_COVID_Cases_plot_{today_date}.png')
        fig.savefig(img_file_name)
        img_file_name = f"{self.IMG_API_URL}{country_names.upper()}_COVID_Cases_plot_{today_date}.png"
        return img_file_name, bot_msg
            
    
    def get_bot_response(self, slots, entities):
        img_file_name, bot_msg = "", ""
        status = False
        try:
            print(slots, entities)
            api_info = self.generate_api_url_using_entites(slots, entities)
            print(api_info)

            if api_info["status"]:
                if len(api_info["url"]) == 1:
                    ## single country api url found
                    api_response = self.get_covid_cases_by_api(api_info["url"][0])                    
                    #print(api_response)
                    if not api_response["status"]:                        
                        return {"status":False, "bot_msg":"COVID-19 API is unreachable. Please try after some time.!!!"}
                    if "code=404" in api_response["data"] or "message" in  api_response["data"]:                        
                        if type(api_response["data"]) == str:
                            return {"status":False, "bot_msg":api_response["data"], img_file_name : f"{self.IMG_API_URL}minion-oops.jpg"}
                            #return                         
                        elif type(api_response["data"]) == dict:
                            #return api_response["data"]["message"]
                            return {"status":False, bot_msg:api_response["data"]["message"], img_file_name : f"{self.IMG_API_URL}minion-oops.jpg"}                    
                    df = self.validate_api_response_for_date(api_info["url_type"][0], api_response, api_info["from_date"], 
                                                             api_info["to_date"])
                    
                    img_file_name, bot_msg = self.create_plot_for_covid_cases(df, api_info["country"], slots["corono_status"])
                    status = True
                elif len(api_info["url"]) == 2:
                    ## comparing two contry of corono
                    ## single country api url found                    
                    api_response_country_1 = self.get_covid_cases_by_api(api_info["url"][0])                     
                    api_response_country_2 = self.get_covid_cases_by_api(api_info["url"][1]) 
                    if not api_response_country_1["status"] or not api_response_country_2["status"]:                        
                        return "COVID-19 API is unreachable. Please try after some time.!!!"
                    if "code=404" in api_response_country_1["data"] or "message" in  api_response_country_1["data"] or \
                        "code=404" in api_response_country_2["data"] or "message" in  api_response_country_2["data"]:                        
                        if type(api_response_country_1["data"]) == str:                            
                            return {"status":False, "bot_msg":api_response_country_1["data"], img_file_name : f"{self.IMG_API_URL}minion-oops.jpg"}                        
                        elif type(api_response_country_1["data"]) == dict:                            
                            return {"status":False, "bot_msg":api_response_country_1["data"]["message"], img_file_name : f"{self.IMG_API_URL}minion-oops.jpg"}
                        if type(api_response_country_2["data"]) == str:
                            return {"status":False, "bot_msg":api_response_country_2["data"], img_file_name : f"{self.IMG_API_URL}minion-oops.jpg"}                      
                        elif type(api_response_country_2["data"]) == dict:
                            return {"status":False, "bot_msg":api_response_country_2["data"]["message"], img_file_name : f"{self.IMG_API_URL}minion-oops.jpg"}
                    
                    #print(api_response_country_1, api_response_country_2)
                    df_country_1 = self.validate_api_response_for_date(api_info["url_type"][0], api_response_country_1, api_info["from_date"], 
                                                             api_info["to_date"])
                    
                    df_country_2 = self.validate_api_response_for_date(api_info["url_type"][1], api_response_country_2, api_info["from_date"], 
                                                             api_info["to_date"])
                    
                    df_country_1["country"] = api_info["country"][0]
                    df_country_2["country"] = api_info["country"][1]
                    df_country_1 = df_country_1.append(df_country_2)
                    df_country_1 = df_country_1.melt( id_vars=["country","updated","todayCases","todayDeaths","todayRecovered"],
                                        var_name="status", 
                                        value_name="cases")
                    img_file_name, bot_msg = self.create_plot_for_covid_cases(df_country_1, api_info["country"], slots["corono_status"])
                    status = True
                    
        except Exception as e:
            print(traceback.print_exc())
            status = False
            bot_msg = "Results not found. Please rephrase the question."
            img_file_name = f"{self.IMG_API_URL}minion-oops.jpg"
        return {"status":status, "file_name":img_file_name, "bot_msg":bot_msg}
