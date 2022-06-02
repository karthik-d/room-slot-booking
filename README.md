# Room Slot Booking with Intra-Website Messaging Service - Django Application

Deployed at Blazing Hoops '18 - a state-level baskeball tournament - for scheduling and monitoring match slots and visitor facilities.  

Django based web-application to book time/room slots for events.    
Three user interface types:
- Owner: To create and manage rooms/slots
- Manager: To manage rooms/slots and bookings
- Customer: To make room/slot bookings

## Procedure to Execute

### Getting the project
- The repository can be cloned to another GitHub account or Donwloaded
- The virtual folder details the virtual environment in which the project is built
- The roomBookingManager folder contains the project file system, in a specific hierarchy that must not be disturbed
- One can either use the same, which already has all the required dependencies or get only the prohect from here and install all dependencies as detailed in "requirements.txt"
- The instructions listed below are for Linux Based Systems 

### Setting up the environment
- It is advisable to run the project from a dedicated virtual environment
- One can use the "virtual" included in the repository or create one and install all dependencies listed in "requirements.txt"
- Activate the environment
- The listed information is for using the same environment i.e "virtual", included hin this repository
  * Open a linux terminal
  * Naviagate to the folder where roomBookingManager and viirtual folders are located
  * Use this command to activate the environment (called 'virtual')
    
    ``` $ source virtual/bin/activate ```
  * This should enter the environment
  * Navigate into the roomBookingManager folder
  
### Executing the project
- Continue the steps here after "Setting up the environment"
  * You should now be in the roomBookingManager folder (Note that this folder contains a sub-folder with the same name. You must be located in the outer one. Hence, currently folders like api, users, customer_iface, etc in your present working directory)
  * Execute the following commands in order
  
  ``` 
  (virtual) $ sudo python3 manage.py makemigrations
  (virtual) $ sudo python3 manage.py migrate
  (virtual) $ sudo python3 manage.py runserver
  ```
  
  * On some systems, this might cause Import Errors as it may attempt to execute from outside the environment. In tat case, do this instead
    
  ``` 
  (virtual) $ sudo ../virtual/bin/python3 manage.py makemigrations
  (virtual) $ sudo ../virtual/bin/python3 manage.py migrate
  (virtual) $ sudo ../virtual/bin/python3 manage.py runserver
  ```
  
  * This should get the server running. The address to the website will be displayed in the terminal
  * Open the http- web address in a browser (preferably Mozilla Firefox)
  * The website can be navigated from here on
  * Hit (ctr+C) in the teminal to stop the server
  
### Running the TestCases
  - Continue the steps here after "Setting up the environment"
  ``` 
  (virtual) $ sudo python3 manage.py test
  ```
  OR
  ``` 
  (virtual) $ sudo ../virtual/bin/python3 manage.py test 
  ```
### Closing the environment
- To exit the virtual environmnet, from any directory
 ``` 
  (virtual) $ deactivate
  ```
  
## Features  

### User Authentication
- The application uses customised User Model with a rebuilt User Manager class to implement user management
  It features login with email (ceasing the need for a dedicated username)
- A login page is used to authenticate registered users
- Registration pages are dependent on the user-type to create new users

### Users Architecture

#### User Groups
There are three User Grops deisgned in this application to handle user permissions with ease
- AdminPrivilege
- ManagerPrivilege
- CustomerPrivilege
The detailed explanation is mentioned in the user-types below

#### User Types
There are 3 types of users presently with an easily extensible model to accomodate more types of employees
##### Admin
This user is the django "superuser"
He is given the "AdminPrivilege" group
An admin can
- Create and delete Employee IDs
- One admin (ref. as BASE_ADMIN - see users/constants.py) is created during the application initialization, having login details
  * Email : karthikdesingu2000@gmail.com
  * Password : admin123
  * Employee ID : ADM001
- Only an admin can generate employee IDs (for both other admins and managers)
- Only an admin can unassign an employee ID, thereby deleting the corresponding employee, retaining the employee ID for reassignment
- Only an admin can view all employee IDs, so as to share it with newly appointed Managers, Admins or other employee types (if and when created), so that they can signup and use the interface
- A person can signup as an Admin, only using a generated Admin Employee ID, which is expected to be given to the person by an existing admin (hence, the need for an initially existing admin)
- An admin can access the entire database of the application through API Queries (discussed separately in APIs)
- The API is protected using a token based authentication system which can be generated only for an admin user, with his/her password (discussed separately in APIs)
- An admin can send messages and view basic profile information of any type of user

##### Manager (an Employee)
- Currently the only type of Employee
- A manager can signup a user account on the portal, only using a valid employee ID given to him/her by an Admin
- A manager can create his own rooms supplying details about
  * Room Number
  * Advance Reservation Period - Max. number of days beofre which a room can be booked (Eg. If it is 10 and today is 16th of March, any slot in that room can only be booked only upto 26th of March. That is, booking opens only 10 days in advance)
  * Description about the room 
- A manager can add any number of valid slots for each of his rooms (Room and Reservation detailed later in Document)
- A manager can view all reservations, including those of other managers
- A manager has permission to send messages to a Customer and Admin, as well as view basic profile information

##### Customer 
- A customer can can signup to the portal simply by filling a simplem form
- A customer can  view and book any room-slot that is within the Reservation Period 
- A customer can view all his bookings so far i.e. the past, future and cancelled ones
- A customer can, however, delete only bookings in the future
- A customer has permissions to send messages to a Manager and view basic profile information.
- A customer cannot initiate a message conversation with an Admin, but can respond and continue if the admin has started it

### Manager User
As per the task description
- A manager can define the number and details of rooms in his control (as mentioned above)
- A manager can define the slots for each room 
- The defined slots are recurring constantly
- A manager can modify the room slots as follows:
  * Change the slot timings, in which case the reservations made for those slots on all days in future are modified
    - The relevant customers are notified about the same, via email, when changed
  * Manager can delete a slot, in which case the reservations made for those slots on all days in future are deleted
    - The relevant customer are notified about the same via email, when deleted
- A manager can also delete a room, in which case the reservations made for that room on all days in future are deleted
  *  The relevant customer are notified about the same via email, when deleted
- A manager can view all bookings of rooms of all managers in the portal, view customer details and occupancy status


### Customer User
As per the task requirements
- A customer can book an availbale room, listed to him on the page, only if it is available for booking
- Duplicate reservations of the same room cannot be made
- A customer can view his reservations and also delete them - only in which case the room can be booked by other customers
- Customer is shown only those rooms for booking, which are within the reservation period. This period (as mentioned before) is defined by the manager during room creation
- A customer can view all types of reervations of his own - past, future, cancelled. He can further view the relevant manager's profile details

### Test Cases
Test cases testing the functioning and integrity of models, forms, signals and views have been included for all applications of the website in their respective "tests.py" file

### API Endpoints
Token authenticated API endpoints have been designed for the website, detailed ahead in the documentation
Accessible only by an admin user after token generation


## Additional Features
### Practical User Hierarchy
- Allow logins based on Email ID
- As mentioned above, the hierarchy of users is an easily extensible implementation enabling easy addition of employee types
- Separate maintenance of Employee IDs
- Need for generation of ID by admin to ensure only verified persons can signup as Manager or Admin
### Site Local MESSAGING Service
- Allows Customer to contact relevant managers through site, using their mail ID
- Managers and Admins can also easily notify users about changes, updates, etc through messages
- Display of number of unread messages during login
### RESTful API Endpoints
- API endpoints for accessing and deleting records in all databases
- Addtionally, can handle user creation - all three types
- Authentication using tokens, allowing only admins to access and modify complete site data
- (NOTE: Authentication is removed for User Management, Employee ID APIs for ease of simulation of POST requests, these can be added during actual deployment by simply mentioning the authentication class in Views)
### Email Based Notifications
- Email notification to admin during employee ID generation
- Email notification to customers about changes or deltions in bookings
### Isolated Reservation Database
- An additional database to store reservation data in simple data format
- Not linked to any other database through foreign-keys, etc. 
- Used to permanently store user reservation history
- Destroyed only when the customer is deleted
### View Profile Feature
- Users can view relevant user profiles
- This enables access to contact information like phone number, email ID apart from messaging service
- User Hierarchy is respected here
- Admin can view all
- Manager can view all
- Customer can view only Managers and only respond (not initiate) conversations with an admin
### Change Password Feature
- Users are allowed to chane their user account password   

## API Endpoints - Details

**NOTE that Token Authenticatio is removed for user management to enable EASY SIMULATION Of GET, POST and DELETE methods
and the Authentication can be added before deployment with just a single line of code***

- The authentication is enabled for all API endpoints except Token Generation, User, Customer, Manager and Admin Management
- The API interface for this webiste is isolated from the rest of the HTTP HTML request rendering, being kept in a separate application called "api"
- Only an Admin User can access the API through URLs
- Authentication is performed using Admin specific tokens
- **All requests (except token generation and user management) need a Authentication Token header to send requests**
- The GET, POST, DELETE requests can be made using any browser if it allows adding URL Authentication Header
- The suggested method is using 'curl' from the terminal for authenticated views. Other third-party GUI softwares are available to send tailored HHTP requests as well
- For non-authenticated APIs i.e USER MANAGEMENT, browser can be directly used.
- DRF Provides an interface to directly supply POST data. Authentication is not included for POST request for **ease of simulation** of POST requests. They can be added with just a single-line before deployment 
- Python based scripts using 'requests' module can also be used to send requests and get back data
- The mentioned methods use curl

**NOTE THAT ALL URLs HERE ARE ONLY ONLY RELATIVE. THE HOST and DOMAIN depend on the Address on which the test-server runs**
- Eg. For a relative URL "/api/get-token/", 
- If my server runs on http://127.0.0.1:8000/
- The absolute URL will be http://127.0.0.1:8000/api/get-token/ 
- Hence, send requests to the absoilute URLs after combining

Below are the APIs and their relative URLs
### Generating Token for Admins (NO AUTHENTICATION)
- This is the only request that can be made without a Token based autentication
```
api/get-token
```
- A GET request to this URL, specifies the format for POST request to get a Authentication Token for the admin user
- POST request should be sent in that format to the same URL
- The JSON format for POST is
```
{"email":"admin@gmail.com", "password":"secret"}
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to type in POST JSON data and send a request 

### User Details (NO AUTHENTICATION)
 ### Relative URLs
 - **URL 1**: For Listing All Users (GET) 
 ```
 /api/user-handler/
 ```
 - **URL 2**: For Viewing Specific User (GET) and deleting a user (DELETE)
 - The id for user can be found in the JSON data returned by the Listing URL
 - The URL to specific user can be found in the JSON data returned by the Listing URL
 ```
/api/user-detail/<int:id>/
 ``` 
 
 #### GET Request Examples
 
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X GET http://127.0.0.1:8000/api/user-handler/
 curl -X GET http://127.0.0.1:8000/api/user-detail/2/
 ```
 
#### DELETE Request Example

- Used to DELETE a Room
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X DELETE http://127.0.0.1:8000/api/user-detail/2/
```


### Customer Details (NO AUTHENTICATION)
 ### Relative URLs
 - **URL 1**: For Listing All (GET) Customer and Creating Customer (POST)
 ```
 /api/cust-handler/
 ```
 - **URL 2**: For Viewing Specific Customer(GET) and Deleting a Customer (DELETE)
 - The id for customer can be found in the JSON data returned by the Listing URL
 - The URL to specific user can be found in the JSON data returned by the Listing URL
 ```
 /api/cust-detail/id/
 ``` 
 
 #### GET Request Examples
 
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X GET http://127.0.0.1:8000/api/cust-handler/
 curl -X GET http://127.0.0.1:8000/api/cust-detail/2/
 ```
 #### POST Request Example
 
 - Used to CREATE a Customer
 - JSON Data required - email, name, password, gender, phone
 - It is recommended to make POST requests directly through browser to avoid loss or incorrect formatting of data
 - The DRF provides an interface to directly supply RAW JSON data
 - A sample JSON and URL are provided below 
 ```
{"email":"abc@example.com","name":"ABC", "password":"secret", "gender":"M", "phone":"9980006526"}'
http://127.0.0.1:8000/api/cust-handler/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to type in POST JSON data and send a request 

#### DELETE Request Example

- Used to DELETE a Customer
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X DELETE http://127.0.0.1:8000/api/cust-detail/2/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to DELETE the record with a button click


### Manager Details (NO AUTHENTICATION)
 ### Relative URLs
 - **URL 1**: For Listing All (GET) Manager and Creating Manager (POST)
 ```
 /api/manager-handler/
 ```
 - **URL 2**: For Viewing Specific Manager(GET) and Deleting a Manager (DELETE)
 - The id for manager can be found in the JSON data returned by the Listing URL
 - The URL to specific user can be found in the JSON data returned by the Listing URL
 ```
 /api/manager-detail/id/
 ``` 
 
 #### GET Request Examples
 
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X GET http://127.0.0.1:8000/api/manager-handler/
 curl -X GET http://127.0.0.1:8000/api/manager-detail/2/
 ```
 #### POST Request Example
 
 - Used to CREATE a manager
 - JSON Data required - email, name, password, gender, phone, emp_id (a valid employee ID already generated by an admin)
 - It is recommended to make POST requests directly through browser to avoid loss or incorrect formatting of data
 - The DRF provides an interface to directly supply RAW JSON data
 - A sample JSON and URL are provided below 
 ```
{"email":"abc@example.com","name":"ABC", "password":"secret", "emp_id":"MAN002", "gender":"M", "phone":"9980006526"}'
http://127.0.0.1:8000/api/manager-handler/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to type in POST JSON data and send a request 

#### DELETE Request Example

- Used to DELETE a Manager
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X DELETE http://127.0.0.1:8000/api/manager-detail/2/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to DELETE the record with a button click


### Admin Details (NO AUTHENTICATION)
 ### Relative URLs
 - **URL 1**: For Listing All (GET) Admins and Creating Admins (POST)
 ```
 /api/admin-handler/
 ```
 - **URL 2**: For Viewing Specific Admins(GET) and Deleting a Admin (DELETE)
 - The id for admin can be found in the JSON data returned by the Listing URL
 - The URL to specific user can be found in the JSON data returned by the Listing URL
 ```
 /api/admin-detail/id/
 ``` 
 
 #### GET Request Examples
 
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X GET http://127.0.0.1:8000/api/admin-handler/
 curl -X GET http://127.0.0.1:8000/api/admin-detail/2/
 ```
 #### POST Request Example
 
 - Used to CREATE an Admin
 - JSON Data required - email, name, password, gender, phone, emp_id (a valid employee ID already generated by an admin)
 - It is recommended to make POST requests directly through browser to avoid loss or incorrect formatting of data
 - The DRF provides an interface to directly supply RAW JSON data
 - A sample JSON and URL are provided below 
 ```
{"email":"abc@example.com","name":"ABC", "password":"secret", "emp_id":"ADM002", "gender":"M", "phone":"9980006526"}'
http://127.0.0.1:8000/api/admin-handler/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to type in POST JSON data and send a request 

#### DELETE Request Example

- Used to DELETE an Admin
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X DELETE http://127.0.0.1:8000/api/admin-detail/2/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to DELETE the record with a button click


### Employee ID Details (NO AUTHENTICATION)
 ### Relative URLs
 - **URL 1**: For Listing All (GET) IDs and Creating IDs (POST)
 ```
 /api/empid-handler/
 ```
 - **URL 2**: For Viewing Specific ID (GET) and unassigning ID and Deleting corresponding employee (DELETE)
 - The emp_id can be found in the JSON data returned by the Listing URL
 - The URL to specific user can be found in the JSON data returned by the Listing URL
 ```
/api/empid-detail/<str:emp_id>/
 ``` 
 
 #### GET Request Examples
 
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X GET http://127.0.0.1:8000/api/empid-handler/
 curl -X GET http://127.0.0.1:8000/api/empid-detail/MAN002/
 ```
 #### POST Request Example
 
 - Used to CREATE an Employee iD
 - JSON Data required - emp_type (the type of employee for whom to generate ID - valid values are 'manager', 'admin'
 Refer users/constants.py - The EMPLOYEE_PREFIXES dictionary's keys are the available employee types)
 - It is recommended to make POST requests directly through browser to avoid loss or incorrect formatting of data
 - The DRF provides an interface to directly supply RAW JSON data
 - A sample JSON and URL are provided below 
 ```
{"emp_type":"admin"}'
http://127.0.0.1:8000/api/empid-handler/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to type in POST JSON data and send a request 

#### DELETE Request Example

- Used to DELETE a Employee ID
 - The following curl command can be used (OR) URL can be used in a browser directly
 ```
 curl -X DELETE http://127.0.0.1:8000/api/empid-detail/MAN002/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to DELETE the record with a button click


### Room Details (AUTHENTICATION REQUIRED)
 ### Relative URLs
 - **URL 1**: For Listing All Rooms (GET) 
 ```
 /api/room-handler/
 ```
 - **URL 2**: For Viewing Specific Room (GET) and deleting a Room (DELETE)
 - The room_no for can be found in the JSON data returned by the Listing URL
 - The URL to specific user can be found in the JSON data returned by the Listing URL
 ```
/api/room-detail/<str:room_no>/
 ``` 
 
 #### GET Request Examples
 
 - The following curl command can be used 
 ```
 curl -H 'Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b' -X GET http://127.0.0.1:8000/api/room-handler/
 curl -H 'Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b' -X GET http://127.0.0.1:8000/api/room-detail/B105/
 ```
 
#### DELETE Request Example

- Used to DELETE a Room
- The following curl command can be used 
 ```
 curl -H 'Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b' -X DELETE http://127.0.0.1:8000/api/room-detail/B105/
```

### Other API Endpoints
The other API endpoints are alll authenticated and are similar to type Room Detail API:
- Past Reservations - GET (List and Specific)
- Present Reservations - GET (List and Specific)
- Ongoing Reservations - GET (List and Specific)
- Future Reservations - GET (List and Specific), DELETE

### URLs Summary
The following is the list of URL Patterns which has to be prefixed with **/api/**
 

   - get-token/', GenerateAuthToken
   - user-handler/', UserHandler.
   - user-detail/<int:id>/', UserDetail	
   - cust-handler/', CustomerHandler
   - cust-detail/<int:id>/', CustomerDetail
   - manager-handler/', ManagerHandler
   - manager-detail/<int:id>/', ManagerDetail
   - admin-handler/', AdminHandler.as_view()
   - admin-detail/<int:id>/', AdminDetail
   - empid-handler/', EmpidHandler
   - empid-detail/<str:emp_id>/'
   - room-handler/', RoomHandler
   - slot-handler/', SlotHandler
   - room-detail/<str:room_no>/', RoomDetail
   - slot-detail/<int:id>/', SlotDetail
   - all-reserves/', AllReservations
   - past-reserves/', PastReservations
   - future-reserves/', FutureReservations
   - occupied-reserves/', OngoingReservations.
   - cancelled-reserves/', CancelledReservations
   - reserve-detail/<int:id>/', InactiveReservationDetail
   - reserve-manage/<int:id>/', ActiveReservationManage   
    
     
   Complete implementation details can be found in the "api" folder of the project

## Improvisations and Atomic Features Used
- Built multi-layer wrapped decorators to accept additional arguments
- Created custom decorators for permissions management
- Used signals to initially populate database 
- Used signals to auto-update isolated data models
- Used signals to send email updates to Cutsomer User
- Custom defined user model to enable email based login
- Redefined User Manager class to handle custome user model
- Created user groups to streamline and control user access
- Used SMTP protocol for emailing notifications to customers


## Regulations

- Followed PEP8 Recommendations (as prescribed in task)

