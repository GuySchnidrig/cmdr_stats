# Read the configuration settings from the file
USER_CREDENTIALS = exec(open("user_credentials").read())

# Now you can access USER_CREDENTIALS dictionary
print(USER_CREDENTIALS)