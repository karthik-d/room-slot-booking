# Slot Booking with Intra-Website Messaging Service: A Django Application

> Deployed as a web service at [Blazing Hoops '17](https://d2c99kev9mr0qi.cloudfront.net/), a state-level inter-school basketball tournament, to schedule and **manage game slots and visitor facilities** on a **resource-constrained campus**.

A Python Django -based web-application to **manage time/room slots** for events centrally, with hierarchical user permissions.    
It features three user-ends (interfaces and permission-levels):
- **Owner**: To create and manage rooms/slots. Admin access, with managerial rights. 
- **Manager**: To manage rooms/slots and bookings. 
- **Customer**: To request room/slot bookings. 

## Key Features

> Each feature is **independently pluggable** into any Django project, with minimal adaptations. For instance, the **intra-website messaging service** can be plugged into any Django project that conceptualizes user management.

### Practical User Hierarchy
- Allow logins based on Email ID.
- As mentioned above, the hierarchy of users is an easily extensible implementation enabling easy addition of employee types.
- Separate maintenance of Employee IDs.
- Need for generation of ID by admin to ensure only verified persons can signup as Manager or Admin.

### Site-local Messaging Service
- Allows Customer to contact relevant managers through site, using their mail ID
- Managers and Admins can also easily notify users about changes, updates, etc through messages.
- Display of number of unread messages during login.

### RESTful API Endpoints, in addition to the Web-Application
- API endpoints for accessing and deleting records in all databases.
- Addtionally, can handle user creation - all three types.
- Authentication using tokens, allowing only admins to access and modify complete site data.
> Note that authentication is removed for User Management, Employee ID APIs for ease of simulation of POST requests, these can be added during actual deployment by simply mentioning the authentication class in Views.

### Email Notifications
- Email notification to admin during employee ID generation.
- Email notification to customers about changes or deltions in bookings.

### Isolated Reservation Database
- An additional database to store reservation data in simple data format
- Not linked to any other database through foreign-keys, etc. 
- Used to permanently store user reservation history.
- Destroyed only when the customer is deleted.

## Improvizations and Atomic Features Used
- Built multi-layer wrapped decorators to accept additional arguments.
- Created custom decorators for permissions management.
- Used signals to initially populate database.
- Used signals to auto-update isolated data models.
- Used signals to send email updates to Cutsomer User.
- Custom defined user model to enable email based login.
- Redefined User Manager class to handle custome user model.
- Created user groups to streamline and control user access.
- Used SMTP protocol for emailing notifications to customers.


## Run your own instance!

**Get the whole project and build atop ([`fork`](./fork)), or simply plug in the features you need ([`clone`](https://github.com/karthik-d/room-slot-booking.git)).**

### Getting the project
- [`Clone`](https://github.com/karthik-d/room-slot-booking.git) or [`fork`](./fork) the repository, based on what you need.
- The [`virtual`](./virtual) folder details the environment sandbox for the project.
- The [`roomBookingManager`](./roomBookingManager) folder contains the project file system.
- Either reuse the environment, or install all dependencies as specified in [requirements.txt](./requirements.txt).
- The instructions listed below are for *nix systems.

### Setting up the environment
- It is recommended that the project us run in a dedicated virtual environment.
- Once the environment is set up, activate the environment.
- The listed information is for using the same environment i.e **virtual**, included hin this repository.
  * Open a linux terminal.
  * Navigate to the folder where roomBookingManager and viirtual folders are located.
  * Use this command to activate the environment.    
    ``` $ source virtual/bin/activate ```
  * This should enter the environment.
  * Navigate to the [`roomBookingManager`](./roomBookingManager) folder.
  
### Executing the project
  * You should now be in the [`roomBookingManager`](./roomBookingManager) folder.   
  **Note** that this folder contains a sub-folder with the same name. You must be located in the outer one.
  * Execute the following commands in order  
  ``` 
  (virtual) $ sudo python3 manage.py makemigrations
  (virtual) $ sudo python3 manage.py migrate
  (virtual) $ sudo python3 manage.py runserver
  ```
  
  * On some systems, this might cause import errors as it may attempt to execute from outside the environment. Here's a workaround,   
  ``` 
  (virtual) $ sudo ../virtual/bin/python3 manage.py makemigrations
  (virtual) $ sudo ../virtual/bin/python3 manage.py migrate
  (virtual) $ sudo ../virtual/bin/python3 manage.py runserver
  ```
  
  * This should get the server running. The address to the website will be displayed in the terminal.
  * Open the HTTP web address in a browser.
  * Hit `ctrl+c` in the teminal to stop the server.
  
### Running the TestCases
  To run the automated test cases,
  ``` 
  (virtual) $ sudo python3 manage.py test
  ```
  **Or**
  ``` 
  (virtual) $ sudo ../virtual/bin/python3 manage.py test 
  ```
### Closing the environment
- To exit the virtual environmnent, from any directory,
 ``` 
  (virtual) $ deactivate
  ```
  
## Features  

### User Authentication
- The application uses a customised user model with a tailored `UserManager` class to implement user management, featuring email authentication.
- A login page is used to authenticate registered users.
- Registration pages are dependent on the user type.

### Users Architecture

#### User Groups
There are three user groupes deisgned in this application to handle user permissions with ease.
- `AdminPrivilege`
- `ManagerPrivilege`
- `CustomerPrivilege`

A detailed explanation follows.

#### User Types
There are 3 types of users presently with an easily extensible model to retrofit with more employee types.

##### Admin
- This user is the Django *superuser*.   
- This user type is given the **AdminPrivilege** group.   
   
An admin can
- Create and delete Employee IDs
- One admin (referred to as BASE_ADMIN - see [users/constants.py](./roomBookingManager/users/constants.py)) is created during the application initialization, with the following credentials,
  * **Email** : karthikdesingu2000@gmail.com
  * **Password** : admin123
  * **Employee ID** : ADM001
- Only an admin can generate employee IDs (for both other admins and managers).
- Only an admin can unassign an employee ID, thereby deleting the corresponding employee, retaining the employee ID for reassignment.
- Only an admin can view all employee IDs, so as to share it with newly appointed Managers, Admins or other employee types (if and when created), so that they can signup and use the interface.
- A person can sign up as an Admin, only using a generated Admin Employee ID, which is expected to be given to the person by an existing admin (hence, the need to initialize an admin).
- An admin can access the entire database of the application through API Queries (discussed separately in APIs).
- The API is protected using a token based authentication system which can be generated only for an admin user, with his/her password (discussed separately in APIs).
- An admin can send messages and view basic profile information of any type of user.

##### Manager (an Employee)
- Currently, the only type of Employee.
- A manager can signup a user account on the portal, only using a valid employee ID given to him/her by an `admin`.
- A manager can create his own rooms supplying details about.
  * Room Number
  * Advance Reservation Period - Max. number of days beofre which a room can be booked (Eg. If it is 10 and today is 16th of March, any slot in that room can only be booked only upto 26th of March. That is, booking opens only 10 days in advance)
  * Description about the room 
- A manager can add any number of valid slots for each of his rooms (*Room* and *Reservation* are detailed later in this document).
- A manager can view all reservations, including those of other managers.
- A manager has permission to send messages to a Customer and Admin, as well as view basic profile information.

##### Customer 
- A customer can can signup to the portal simply by filling a simplem form.
- A customer can  view and book any room-slot that is within the Reservation Period.
- A customer can view all his bookings so far i.e. the past, future and cancelled ones.
- A customer can, however, delete only bookings in the future.
- A customer has permissions to send messages to a Manager and view basic profile information.
- A customer cannot initiate a message conversation with an Admin, but can respond and continue if the admin has started it.

### Manager User
- A manager can define the number and details of rooms in his control (as mentioned above).
- A manager can define the slots for each room.
- The defined slots are recurring constantly.
- A manager can modify the room slots as follows:
  * Change the slot timings, in which case the reservations made for those slots on all days in future are modified.
   - The relevant customers are notified about the same, via email, when changed.
  * Manager can delete a slot, in which case the reservations made for those slots on all days in future are deleted.
   - The relevant customer are notified about the same via email, when deleted.
- A manager can also delete a room, in which case the reservations made for that room on all days in future are deleted.
  *  The relevant customer are notified about the same via email, when deleted.
- A manager can view all bookings of rooms of all managers in the portal, view customer details and occupancy status.

### Customer User
- A customer can book an availbale room, listed to him on the page, only if it is available for booking.
- Duplicate reservations of the same room cannot be made.
- A customer can view his reservations and also delete them - only in which case the room can be booked by other customers.
- Customer is shown only those rooms for booking, which are within the reservation period. This period (as mentioned before) is defined by the manager during room creation.
- A customer can view all types of reervations of his own - past, future, cancelled. He can further view the relevant manager's profile details.

### Test Cases
Test cases testing the functioning and integrity of models, forms, signals and views have been included for all applications of the website in their respective "tests.py" file.

### API Endpoints
Token authenticated API endpoints have been designed for the website. These are accessible only to an `admin` user after token generation.

## API Endpoints: In Detail

> Note that Token Authentication is removed for user management to enable easy simulation of GET, POST and DELETE methods and the Authentication can be added before deployment with just a single line of code.

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

> Note that all URLs mentioned here are *relative*. THE HOST and DOMAIN depend on the Address on which the test-server runs
- Eg. For a relative URL `/api/get-token/`, 
- If my server runs on http://127.0.0.1:8000/
- The absolute URL will be http://127.0.0.1:8000/api/get-token/ 
- Hence, send requests to the absolute URLs after combining.

Following are the APIs and their relative URLs,
### Generating Token for Admins (**No Authentication**)
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

### User Details (**No Authentication**)
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


### Customer Details (**No Authentication**)
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
 
 - The following `curl` command can be used (OR) URL can be used in a browser directly
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
 - The following `curl` command can be used (OR) URL can be used in a browser directly
 ```
 curl -X DELETE http://127.0.0.1:8000/api/cust-detail/2/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to DELETE the record with a button click


### Manager Details (**No Authentication**)
 ### Relative URLs
 - **URL 1**: For Listing All (GET) Manager and Creating Manager (POST)
 ```
 /api/manager-handler/
 ```
 - **URL 2**: To view a specific Manager (GET) and Deleting a Manager (DELETE)
 - The id for manager can be found in the JSON data returned by the Listing URL
 - The URL to specific user can be found in the JSON data returned by the Listing URL
 ```
 /api/manager-detail/id/
 ``` 
 
 #### GET Request Examples
 
 - The following `curl` command can be used (OR) URL can be used in a browser directly
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
 - The following `curl` command can be used (OR) URL can be used in a browser directly
 ```
 curl -X DELETE http://127.0.0.1:8000/api/manager-detail/2/
```
- This request can be made on a browser directly as the Django Rest Framework (DRF) provides an interface to DELETE the record with a button click


### Admin Details (**No Authentication**)
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
 
 - The following `curl` command can be used (OR) URL can be used in a browser directly
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


### Employee ID Details (**No Authentication**)
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
 
 - The following `curl` command can be used (OR) URL can be used in a browser directly
 ```
 curl -X GET http://127.0.0.1:8000/api/empid-handler/
 curl -X GET http://127.0.0.1:8000/api/empid-detail/MAN002/
 ```
 #### POST Request Example
 
 - Used to CREATE an Employee ID
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


### Room Details (**No Authentication**)
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

   - `get-token/`, GenerateAuthToken
   - `user-handler/`, UserHandler.
   - `user-detail/<int:id>/`, UserDetail	
   - `cust-handler/`, CustomerHandler
   - `cust-detail/<int:id>/`, CustomerDetail
   - `manager-handler/`, ManagerHandler
   - `manager-detail/<int:id>/`, ManagerDetail
   - `admin-handler/`, AdminHandler.as_view()
   - `admin-detail/<int:id>/`, AdminDetail
   - `empid-handler/`, EmpidHandler
   - `empid-detail/<str:emp_id>/`
   - `room-handler/`, RoomHandler
   - `slot-handler/`, SlotHandler
   - `room-detail/<str:room_no>/`, RoomDetail
   - `slot-detail/<int:id>/`, SlotDetail
   - `all-reserves/`, AllReservations
   - `past-reserves/`, PastReservations
   - `future-reserves/`, FutureReservations
   - `occupied-reserves/`, OngoingReservations.
   - `cancelled-reserves/`, CancelledReservations
   - `reserve-detail/<int:id>/`, InactiveReservationDetail
   - `reserve-manage/<int:id>/`, ActiveReservationManage       
     
> Complete implementation details can be found in the [`api`](./roomBookingManager/api) folder of the project.

## Regulations

- Followed PEP8 Recommendations.
