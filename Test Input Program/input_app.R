library(shiny)
library(googlesheets4)
library(shinymaterial)
library(tidyverse)

# Function to get the highest Game_ID from the Google Sheet
get_highest_game_id <- function(sheet_id) {
  sheet <- gs4_find(sheet_id)
  df <- as_tibble(gs4_read_sheet(sheet))
  max_game_id <- max(df$Game_ID, na.rm = TRUE)
  
  if (is.na(max_game_id)) {
    max_game_id <- 0
  }
  
  return(max_game_id)
}

# Function to add a new entry to the Google Sheet
add_new_entry <- function(sheet_id, game_id, date, players, commanders, colors) {
  sheet <- gs4_find(sheet_id)
  df <- as_tibble(gs4_read_sheet(sheet))
  new_entry <- tibble(
    Game_ID = game_id,
    Date = date,
    Players = players,
    Commanders = commanders,
    Color_Identity = colors
  )
  
  df <- bind_rows(df, new_entry)
  gs4_write_sheet(sheet, df, overwrite = TRUE)
}

# Define UI
ui <- material_page(
  title = "New Game Entry",
  navbar = NA,
  sidebar_panel(
    textInput("sheet_id", "Google Sheet ID:", placeholder = "Enter your sheet ID"),
    actionButton("load_sheet_btn", "Load Sheet"),
    br(),
    conditionalPanel(
      condition = "input.load_sheet_btn > 0",
      numericInput("game_id", "Game ID:", value = 0, min = 0, step = 1),
      dateInput("date", "Date:", value = Sys.Date(), format = "yyyy-mm-dd"),
      textInput("players", "Players:", placeholder = "Enter players' names"),
      textInput("commanders", "Commanders:", placeholder = "Enter commanders' names"),
      textInput("colors", "Color Identity:", placeholder = "Enter color identities"),
      actionButton("add_entry_btn", "Add Entry")
    )
  ),
  main_panel(
    h3("Game Entry Confirmation"),
    verbatimTextOutput("confirmation")
  )
)

# Define server
server <- function(input, output, session) {
  sheet_loaded <- reactiveVal(FALSE)
  
  observeEvent(input$load_sheet_btn, {
    validate(need(input$sheet_id != "", "Please enter your Google Sheet ID."))
    
    # Load the Google Sheet
    sheet_id <- input$sheet_id
    sheet <- gs4_find(sheet_id)
    validate(
      need(!is.null(sheet), "Google Sheet not found. Please check your ID and make sure it's accessible.")
    )
    
    sheet_loaded(TRUE)
  })
  
  observeEvent(input$add_entry_btn, {
    validate(
      need(input$game_id >= 0, "Game ID must be a non-negative number."),
      need(input$players != "", "Please enter players' names."),
      need(input$commanders != "", "Please enter commanders' names."),
      need(input$colors != "", "Please enter color identities.")
    )
    
    # Add a new entry to the Google Sheet
    if (sheet_loaded()) {
      game_id <- input$game_id + 1
      date <- as.character(input$date)
      players <- input$players
      commanders <- input$commanders
      colors <- input$colors
      
      add_new_entry(input$sheet_id, max_game_id + 1, date, players, commanders, colors)
      
      # Display confirmation message
      output$confirmation <- renderText({
        paste("New entry added to Google Sheet:",
              "\nGame ID:", max_game_id + 1,
              "\nDate:", date,
              "\nPlayers:", players,
              "\nCommanders:", commanders,
              "\nColor Identity:", colors)
      })
      
      # Reset input values
      updateNumericInput(session, "game_id", value = max_game_id + 1)
      updateDateInput(session, "date", value = Sys.Date())
      updateTextInput(session, "players", value = "")
      updateTextInput(session, "commanders", value = "")
      updateTextInput(session, "colors", value = "")
    }
  })
}

# Run the app
shinyApp(ui, server)