# Flask Application for JD Sports Sales Data Integration with Verkada Helix API

Hello John! I hope you are doing well. I have completed the coding challenge. Here are some thoughts and notes about the project.

## Approach
1. As the position I am Interviewing for involves a lot of database work, I started out by creating a schema enclosed in `schema.sql` file to help understand the problem. I also created a `Schema.jpg` file to help visualize the schema. (`schema.sql` is mysql compatible). I have also included a `example_actions.sql` file to demonstarte some sample raw sql queries that can be run on the DB to perform various CRUD operations.
2. For the purpose of simplicity and ease of testing, I decided to use a SQLite database. It is located in  `instance/jdsports.db`.
3. But I have included the code to setup and spin up a MySQL database. The code is located in `mysql_db` folder and `mysql-connector` setup in `setup folder`. You will need to use docker for that. But its very easy to setup and get going.
4. In terms of the application, I have used `SQLAlchemy` to create the database tables and `Flask` to create the application. The application is in `app.py` file. The reason I used `SQLAlchemy` here was for the sake of simplicity and to meet the deadline. I would use a language like `Typescript` or the one most commonly used in the team if it were a real project being used in the company.
5. I have also included a `requirements.txt` file to help install the required packages.
6. The `setup_cron.sh` file includes the crontab and its setup.
7. **Note**:The Code works in a scenario where there is real apis involved and might need some minor tweaking. As I did not have access to real API Endpoints or a test environment, I had to make some assumptions about the data format and the API endpoints. I have included the assumptions below and in comments wherever necessary in the code.


## Features
1. Retrieve transaction data from the JD Sports Sales API endpoint for the last hour.
2. Retrieve additional data from Inventory, Camera, Point of Sale, and Store APIs. (Optional Feature I added)
3. Fill relevant tables in the database.
4. Extract transactions data and store it in the database.
5. Store camera event data in the database.
6. Post the camera event data to the Verkada Helix API.


## API Endpoints and Data Format assumptions

The application will communicate with the following APIs and retrieve data in the specified format:

### Sales API
```
{
    transaction_id: 123,
    transaction_date: 2020-01-01 12:00:00,
    transaction_amount: 100,
    item_id: 123,
    camera_id: 123,
}
```
### Inventory API (Optional Feature I added)
```
{
    item_id: 123,
    item_name: "Nike Shoes",
    item_price: 100,
    item_quantity: 10,
}
```
### Camera API (Optional Feature I added)
```
{
    camera_id: 123,
    camera_name: "Camera 1",
    camera_location: "London",
    camera_status: "Active",
    camera_model: "Camera Model 1",
    pos_id: 123,
}
```
### Point of Sale API (Optional Feature I added)
```
{
    camera_id: 123,
    pos_id: 123,
    pos_name: "Front Door POS",
    store_id : 123,
}
```
### Store API (Optional Feature I added)
```
{
    store_id: 123,
    store_name: "London Store",
    store_address: "London",
    store_phone: "1234567890",
    store_email: "store@jdsports.com"
}
```
## Database Tables

The application will create and populate the following tables in the database:

1. stores
2. cameras
3. points_of_service
4. transactions
5. camera_events_uid

## Verkada Helix API Integration
The application will post the camera event data to the Verkada Helix API. A brief version of the process is given below:

1. Create a Verkada Public API Key Token. (I assume you have already created a Verkada account and have access to the Verkada Helix API.)
2. Create an Event Type. ("Sales Transaction","Warehouse Loading" etc)
3. Create Events. (Eg: From a regular sale at a POS)

Detailed instructions for each step can be found in the original instructions. https://apidocs.verkada.com/reference/getting-started

## How to run the application

TLDR: Run `python app.py` after creating a virtual environment and installing the required packages.

1. Create a virual environment `python3 -m venv venv and source venv/bin/activate` and install the required packages using `pip install -r requirements.txt`
2. Please do note that if you want to use MySQL, you will need to install the `mysql-connector` package. You can do so by running `pip install mysql-connector-python` and for that to work you have install `mysql_config` and details on which are in setup file in scripts.
3. The application is defaulted to use sqlite. If you want to use MySQL, please change the line 11 and `db_type` default to MySQL in `app.py` file.
4. I have avoided using environment variables for the sake of simplicity. If you want to use environment variables, please change the line 12 and 13 in `app.py` file.
5. Run the application using `python app.py` and the server should start up
6. You can now test the application using Postman or any other API testing tool or by just running `curl http://localhost:5000/fetch_and_store_transactions`
7. This might not work if you are not using a real API endpoint. I have made some assumptions about the data format and the API endpoints. You can update the code to make it work with real API endpoints on line 27 in `app.py` file under the section `# API Endpoints and Keys`


## How the code works (A breif summary)
1. The code initializes a Flask application and configures it to connect to either a SQLite or MySQL database based on environment variables.
2. It defines several database models to store information related to stores, cameras, POS, transactions, and items.
3. Utility functions are implemented to fetch data from various APIs, get footage and thumbnail links from Verkada's camera API, store data in the database, create and post Verkada events, and interact with the Verkada Helix API.
4. API endpoints are defined to fetch and store transactions, list transactions, get sales information for specific stores, and list all the stores with at least one transaction.
5. The main section of the code initializes the database tables and starts the Flask server, making the application ready to receive requests.

In summary, this Flask application fetches sales transaction data from external APIs, stores it in a local database, and creates Verkada events for each transaction. The application provides API endpoints for users to interact with the stored data and view transaction information.

## Additional Considerations and future improvements
I could not improve the code as much as I would have liked to due to time constraints. However, I have listed some of the improvements that I would have liked to make if I had more time:


1. Error handling: Improve error handling throughout the code to handle edge cases, API failures, or unexpected data formats more gracefully. This could involve using more try-except blocks and implementing proper error logging.

2. Code modularity: Separate the code into different modules to improve code organization and maintainability. For example, create separate files for utility functions, database models, and API routes.

3. Authentication and security: Implement authentication and authorization to protect API endpoints and ensure that only authorized users can access the data.

4. Pagination: Add support for pagination to API endpoints that return large amounts of data, making it easier for clients to fetch and process the data.

5. Caching: Implement caching mechanisms to reduce the number of API calls to external services and improve the application's performance.

6. Dynamic event types: Enhance the application to support various event types such as warehouse events, customer check-in/check-out events, etc. This could involve making the event type creation and posting process more flexible.

7. Asynchronous processing: Introduce asynchronous processing for fetching data from external APIs and processing it. This can help improve the performance and responsiveness of the application.

8. Automated testing: Develop a test suite with unit tests and integration tests to ensure the code's functionality and maintainability.

9. Containerization: Containerize the application using Docker or a similar technology to simplify deployment, improve scalability, and ensure consistent runtime environments.

