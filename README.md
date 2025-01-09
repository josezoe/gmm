Custom User Model:
•	CustomUser Model:
o	Extends Django's AbstractUser model to include additional fields specific to our platform.
o	Includes a user_type field to differentiate between admin, vendor, and customer roles.
o	Fields like country, state, and city are included to handle geographical data, supporting location-based features.

Geographical Data Management:
•	Country Model:
o	Stores information about countries, including name, code, and associated currency.
•	State Model:
o	Related to the Country model, storing states or provinces, with a name and code.
•	City Model:
o	Linked to the State model, allowing for city-level specificity in user profiles or listings.
•	TimeZone Model:
o	Manages time zones to handle time-sensitive operations across different geographical locations.

Fiscal and Administrative Settings:
•	TaxSetting Model:
o	Manages tax rates that can be applied based on country and optionally state, aiding in
Implemented Features:
User Authentication and Authorization:
•	Vendor Signup: 
o	Vendors can sign up with basic information like business name, phone, and basic user credentials. 
o	Upon signup, vendors are not immediately approved; they require admin approval.
•	Vendor Login:
o	Vendors can log in with their credentials, but login is only successful if their account has been approved by an admin.
•	Vendor Logout:
o	A logout feature is implemented for vendors to end their session.

Vendor Management:
•	Vendor Approval:
o	Admins can approve or reject new vendor applications through the Django admin interface.
•	Vendor Profile:
o	Vendors can view and update their profile information, including business details like name, phone, and address.
•	Vendor Settings:
o	A settings page for vendors to toggle features like gift card sales, party bookings, and event bookings
