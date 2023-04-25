# Load libraries
library(data.table)
library(jsonlite)

# Misc
Sys.setenv(LANG = "en")
rm(list=ls())
gc()

# attempt to set the working directory to the primary file path
dir_path_primary <- "G:/Meine Ablage/MTG/cmdr_stats"
dir_path_fallback <- "G:/My Drive/MTG/cmdr_stats"

tryCatch(
  {
    setwd(dir_path_primary)
  },
  error = function(e) {
    # if an error occurs, set the working directory to the fallback file path
    message("An error occurred while setting the primary working directory: ", conditionMessage(e))
    message("Setting the fallback working directory instead.")
    setwd(dir_path_fallback)
  }
)

# Get all Scryfall data
name_of_json <- Sys.glob("*.json")
srcyfall_data <- fromJSON(name_of_json, flatten = TRUE)

# Filter data
vec <- c("id", "name", "type_line", "cmc", "mana_cost", "colors", "color_identity", "power", "toughness", "keywords")
srcyfall_data_reduced <- srcyfall_data %>%
  select(id, name, type_line, cmc, mana_cost, color_identity, power, toughness) %>%
  as.data.table()

# Export Data Frame
fwrite(srcyfall_data_reduced, "srcyfall_data.csv", bom = T)
