## get_covid_status
* get_covid_status
  - action_get_covid_status

## get_state_level_analysis
* get_state_level_analysis
  - action_get_state_level_analysis

## get_country_level_comparision
* get_country_level_comparision
  - action_get_country_level_comparision

## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot
