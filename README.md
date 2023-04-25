# cmdr stats
Author: Guy Schnidrig
Date: 26 April, 2023

This repository contains code and data for analyzing statistics of games played with Commander decks.

##Requirements
This project requires the following R packages:

tidyverse
plotly
readxl
flextable
shiny
flexdashboard
scryr
jsonlite
httr
data.table
dtplyr
lubridate
Data
The data used for this analysis is stored in cmdr.xlsx file. The data is read into R using read_excel() function from readxl package.

The data is preprocessed in the following ways:

A deck ID is assigned to each deck based on the deck link.
Some columns are converted to factors for better visualizations.
The Date column is converted to a date format.
Deck links are extracted from Deck_Link column and modified to add the right API path and ending.
API calls are made to extract the deck lists from Archidekt website.
The deck lists are joined with Scryfall data to get more information about the cards.
Dashboard
The dashboard for this project is created using flexdashboard package. It contains the following components:

Games played: A bar chart showing the number of games played by each player.
Statistics: A table showing some basic statistics about the games played.
Top Commanders: A table showing the top 5 commanders based on the number of games played.
Mana Value Distribution: A histogram showing the distribution of mana values in the decks.
Usage
To run the dashboard, open cmdr_stats.Rmd file and click Run Document. The dashboard will open in the viewer pane.

Notes
The code is designed to work with the specific data file and may need to be modified to work with other data.
Some of the API calls may take some time to execute depending on the size of the data.
This project is for educational purposes only and is not intended for commercial use.
