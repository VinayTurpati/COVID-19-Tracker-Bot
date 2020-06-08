#This files contains your custom actions which can be used to run
#custom Python code.
#
#See this guide on how to implement these action:
#https://rasa.com/docs/rasa/core/actions/#custom-actions/

#This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset
from CovidTracker import COVID_Tracker

class CovidStatus(Action):

    def name(self) -> Text:
        return "action_get_covid_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("Getting COVID-19 API results!!!")        
        
        tracker_obj = COVID_Tracker()
        bot_response = tracker_obj.get_bot_response(tracker.current_slot_values(), tracker.latest_message['entities'])
        print(bot_response)
        if bot_response["status"]:
            file_path = bot_response["file_name"]
            dispatcher.utter_message(text=bot_response["bot_msg"], image=file_path)
        else:
            dispatcher.utter_message(text="Please try after some time. ", image="http://ec2-13-126-127-146.ap-south-1.compute.amazonaws.com:5020/img/minion-oops.jpg")
        return [AllSlotsReset()]


class StateLevel(Action):

    def name(self) -> Text:
        return "action_get_state_level_analysis"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:  
        print("Getting COVID-19 API results!!!")        
        
        tracker_obj = COVID_Tracker()
        bot_response = tracker_obj.get_bot_response(tracker.current_slot_values(), tracker.latest_message['entities'])
        print(bot_response)
        if bot_response["status"]:
            file_path = bot_response["file_name"]
            dispatcher.utter_message(text=bot_response["bot_msg"], image=file_path)
        else:
            dispatcher.utter_message(text="Please try after some time. ", image="http://ec2-13-126-127-146.ap-south-1.compute.amazonaws.com:5020/img/minion-oops.jpg")
        return [AllSlotsReset()]


class CovidComparision(Action):

    def name(self) -> Text:
        return "action_get_country_level_comparision"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:        
        print("Getting COVID-19 API results!!!")        
        
        tracker_obj = COVID_Tracker()
        bot_response = tracker_obj.get_bot_response(tracker.current_slot_values(), tracker.latest_message['entities'])
        print(bot_response)
        if bot_response["status"]:
            file_path = bot_response["file_name"]
            dispatcher.utter_message(text=bot_response["bot_msg"], image=file_path)
        else:
            dispatcher.utter_message(text="Please try after some time. ", image="http://ec2-13-126-127-146.ap-south-1.compute.amazonaws.com:5020/img/minion-oops.jpg")
        return [AllSlotsReset()]
