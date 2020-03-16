# Room Slot Booking - Django Application
## Account Details
### yaksh.fossee.in 
- Registered Email : me.karthikd@gmail.com
- Profile Name : Karthik D
(Registered using Google Account, no username registered)

### courses.fossee.in 
- Username : me_karthikd
- Email : me.karthikd@gmail.com

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

## Task Requirements Met

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


## Key Features

- Followed PEP8 Recommendations

## Improvisations and Atomic Features Used
- Created custom decorators for permissions management
- Used signals to initially populate database 
- Used signals to auto-update isolated data models
- Used signals to send email updates to Cutsomer User
- Custom defined user model to enable email based login
- Redefined User Manager class to handle custome user model
- Created user groups to streamline and control user access
