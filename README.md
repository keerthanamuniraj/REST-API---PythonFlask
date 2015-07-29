# REST-API---PythonFlask


“This REST API is meant to be a system designed to feed and retrieve the weekly PPPs, meaning the Progress Problem Plan ,which are submitted to the user's respective manager. The submission and retrieval of the PPP records happens via a REST API which interacts with the database storing the user and their respective PPPs along with the date of submission. “


Retrieval of PPP records:

Any authenticated employee can retrieve a user's Progress, Problem and Plan information provided the user is registered in the Employee Database.
The user being the manager can retrieve the record in order to review it or the user being the team member can retrieve their records to either edit or read it.

How is the authentication carried out?
 The authentication is done when the user tries to log in using their credentials- username and password token which can be accessed using the REST API. This token is verified with the  hashed password stored in the database.

Submission of PPP records:

The team members need to be authenticated before submitting their records.

Once they are authenticated they can submit their PPP information using the REST API service.





