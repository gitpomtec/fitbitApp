# fitbitApp
fitbit WEB API wrapper
## Preparation
### Creating a Fitbit Application
1. Access the developer page. (See reference URL)
    - If you don't have a FitBit account, create one first!
1. Application Creation
    - Create it by entering the required information from the developer page “REGISTER AN APP”. If you just want to get your own data, you can do the following.
        - Application Name ... Enter an appropriate name
        - Description ... Enter an appropriate description
        - Application Website URL ... http://localhost
        - Organization ... none
        - Organization Website URL ... http://localhost
        - Terms of Service URL ... http://localhost
        - Privacy Policy URL ... http://localhost
        - OAuth 2.0 Application Type ... Personal
        - Redirect URL ... http://localhost:8000
        - Default Access Type ... Read Only
### Obtaining an access token
1. access the Fitbit OAuth 2.0 Tutorial page
    - On the “MANAGE MY APPS” tab of the developer page, click the application you created in the Create Application section and click the OAuth 2.0 Tutorial link. 1.
Enter the following in the App Settings
    1. Client ID
        - OAuth 2.0 Client ID for the application you created. 
    1. Application Type
        - Select Client.
1. Enter the following in Getting an Access Token
    1. Step 1: Generate PKCE and State Values
        - Click GENERATE for PKCE Code Verifie
        - Click on GENERATE in State
1. Step 2: Display Authorization Page
    1. Click the URL of Authorization URL
        - On the Authorization page, select “Allow all” and click “Allow“
        - Depending on your browser, you may see “localhost connection denied. but leave it as it is to be used in the next step.
1. Step 3: Handle the Redirect
    1. in the Authorization Code, enter “localhost connection denied” as the URL of the page << Enter the value of the http://localhost:8000/?code=<here>&state=~ code= part of the URL of the page “localhost connection denied” in the Authorization Code field.
    1. In the State field, enter the value of “localhost connection denied. Enter the value of the http://localhost:8000/?code=~&state=<here> state= part of the URL on the page
1. Step 4: Get Tokens
    1. Click SUBMIT REQUEST.
        - The response should show the tokens without any errors.
        - Save the Response to a text file named Token.json (or whatever file name you want)
1. Access User Data
    1. Click SUBMIT REQUEST
        - Response should show your profile data with no errors.
### Create Config file
Create a file named Config.json with the following contents
```json:Config.json
{
    "CLIENT_ID":"Your OAuth 2.0 Client ID for the created application",
    "CLIENT_SECRET":"Your Client Secret for the created application"
}
```

## Reference URL
- Developer Page https://dev.fitbit.com/apps
- Reference https://dev.fitbit.com/build/reference/web-api/
