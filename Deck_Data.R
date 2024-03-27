# Deck Data Script

# Load Libraries
library(tidyverse)
library(plotly)
library(readxl)
library(flextable)
library(shiny)
library(flexdashboard)
library(jsonlite)
library(httr)
library(data.table)
library(dtplyr)
library(googlesheets4)


# Misc
Sys.setenv(LANG = "en")
rm(list=ls())
gc()
set.seed(42)
options(scipen = 999,
        dplyr.summarise.inform = FALSE)

# Authenticate using token. 
gs4_auth(cache = ".secrets", email = "g.schnidu@gmail.com")

# Game Data
data <- read_sheet("https://docs.google.com/spreadsheets/d/1yMb2ijZfeAcAVHBNJGTcnORYu4GPSBTlDTioDQkoB1c/edit#gid=1318392544")

color_list <- hcl.colors(length(unique(data$Player)), "Set 2")

data$color <- leaflet::colorFactor(
  palette = color_list, domain = unique(data$Player)
)(data$Player)

player_color_mapping <- data %>% 
  group_by(Player) %>%
  reframe(color = color) %>% 
  distinct(Player, .keep_all = T) %>% 
  ungroup()

# Set Deck ID
data <- data %>%
  group_by(Deck_Link) %>%
  mutate(Deck_ID = cur_group_id()) %>%
  ungroup()

# Set Date
data$Date <- lubridate::dmy(data$Date)

# Get Deck links
deck_list <- data %>%
  filter(grepl("archidekt", Deck_Link)) %>%
  select(Deck_Link, Deck_ID) %>%
  distinct(Deck_Link, Deck_ID)

# Add right api path and ending
deck_list <- deck_list %>%
  mutate(Deck_Link = gsub("https?://(www\\.)?archidekt\\.com/(decks/\\d+).*", "https://archidekt.com/api/\\2", Deck_Link))


deck_list <- deck_list %>%
  mutate(Deck_Link_clean = paste0(Deck_Link,"/")) %>%
  select(-Deck_Link) %>% 
  distinct()

data <- left_join(data, deck_list, by = "Deck_ID") 


# Get Deck lists
res_list <- lapply(deck_list$Deck_Link_clean, httr::GET)
json_text_list <- lapply(res_list, content, as = "text", encoding = "UTF-8") 
json_data_list <- lapply(json_text_list, fromJSON)

names(json_data_list) <- deck_list$Deck_Link_clean

counter <- 0
quantity_list <- lapply(json_data_list, function(i) {
  counter <<- counter + 1
  x = i$cards$quantity 
  z = i$cards$card$oracleCard$cmc
  g = i$cards$card$oracleCard$salt
  p = i$cards$card$prices$tcg
  n = i$cards$card$oracleCard$name
  c = i$cards$card$oracleCard$defaultCategory
  t = i$cards$card$oracleCard$types
  s = i$cards$card$oracleCard$superTypes
  d = i$name
  m = as.character(i$cards$categories)
  id = deck_list$Deck_Link_clean[counter]
  col = i$cards$card$oracleCard$colorIdentity
  
  result <- tibble(deck_name = d,
                   card_name = n,
                   Quantity = x,
                   cmc = z,
                   color = col,
                   salt = g,
                   price = p,
                   type = t,
                   super_type = s,
                   category = c,
                   cmdr_tag = m,
                   Deck_Link_clean = id) %>%
    filter(!str_detect(m, "Maybeboard")) 
})

commander_decks <- quantity_list

# Create data frame with all decks
all_decks <- data.table::rbindlist(commander_decks)

all_decks <- all_decks %>% 
  mutate(cmdr_tag = case_when(cmdr_tag == "Commander" ~ 1,
                              TRUE ~ 0))

deck_infos <- data %>%
  select(Deck_Link_clean, Commander, Player, Deck_ID) %>% 
  distinct() %>% 
  drop_na()

all_decks_join <- left_join(all_decks, deck_infos, by = "Deck_Link_clean")

all_decks_join <- all_decks_join %>%
  group_by(Player) %>%
  mutate(Number_of_decks = length(unique(Deck_ID))) %>% 
  ungroup()


# Handle Types
all_decks_join <- all_decks_join %>% 
  mutate(basic_land = case_when(super_type == "Basic" & type == "Land" ~ 1 ,
                                TRUE ~ 0))
# Split types
all_decks_join <- all_decks_join %>%
  separate(type, into = c("type_1", "type_2"), sep = " ", fill = "right")

# Define the pattern you want to remove
pattern_1 = 'c\\("'
pattern_2 = '\",'
pattern_3 = '\"'
pattern_4 = '\\)'

# Remove the pattern 
all_decks_join$type_1 <- gsub(pattern_1, '', all_decks_join$type_1)
all_decks_join$type_1 <- gsub(pattern_2, '', all_decks_join$type_1)
all_decks_join$type_2 <- gsub(pattern_3, '', all_decks_join$type_2)
all_decks_join$type_2 <- gsub(pattern_4, '', all_decks_join$type_2)

# Make regression data frame
deck_summary <- all_decks_join %>% 
  group_by(Deck_ID, Player) %>% 
  summarise(Average_cmc = mean(cmc[cmc != 0], na.rm = T),
            Salt_Score = sum(salt, na.rm = T),
            Artifacts = sum(Quantity[type_1 == "Artifact" | type_2  == "Artifact"], na.rm = T),
            Creatures = sum(Quantity[type_1 == "Creature" | type_2  == "Creature"], na.rm = T),
            Ramp = sum(Quantity[category == "Ramp"], na.rm = T),
            Draw = sum(Quantity[category == "Draw"], na.rm = T),
            Removal = sum(Quantity[category == "Removal"], na.rm = T),
            Protection = sum(Quantity[category == "Protection"], na.rm = T),
            Tutor = sum(Quantity[category == "Tutor"], na.rm = T),
            Finisher = sum(Quantity[category == "Finisher"], na.rm = T),
            Basic_lands = sum(Quantity[basic_land == 1], na.rm = T),
            Deck_price = sum(price, na.rm = T))

# Join deck summary
data <- left_join(data, deck_summary, by = join_by(Player, Deck_ID))

# Fill up Win turn
data <- data %>% 
  group_by(Game_ID) %>% 
  fill(Win_Turn, .direction = "updown") %>% 
  ungroup()

write_rds(data, "G:/My Drive/MTG/cmdr_stats/deck_data.rds")
write_rds(all_decks_join, "G:/My Drive/MTG/cmdr_stats/all_decks_join.rds")
