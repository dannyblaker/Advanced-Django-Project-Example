![django logo](django-logo.svg)

# About this repository

## Summary

Welcome! 

This repository is a website I built which showcases how you can use python to accomplish more advanced features in a Django project including:

- geo-blocking by country (both hard-block and soft-block)
- require users to use their company email adress when signing up (no free email addresses such as gmail, yahoo etc.)
- mailchimp integration
- signup form:
  - Robust Email validation, including domain blacklisting.
  - Google Recaptcha check on form submission
  - Phone number validation with country code selection
  - Form submission to an API endpoint of your choice, including useful error handling
- logging

I invite you to use this project as a source of inspiration for your own advanced Django projects.

**You are most welcome to use this code in your commercial projects, all that I ask in return is that you credit my work by providing a link back to this repository. Thank you & Enjoy!**

## Background

I originally built this project for a client, therefore I have deleted and / or anonymized all sensitive content. I have replaced the original product name with the mock name "Horizon" throughout. 

The original website was intended for the user to learn about the product, then either:

- sign up as a user 
- sign up as an affiliate who can refer users.

The user sign up process was handled by an existing external system, therefore instead of using Django models, user signup information had to be sent to an API endpoint hosted by the external system.

This project accounts for the following requirements requested by the client:
- The product was to be initially released in Australia and New Zealand only. Therefore customers outside those countries...
  - should be re-directed to a "Coming soon" page (after detecting their region by IP address)
  - should be able to sign up to a "notify me" mailing list (mailchimp)
- If a user happens to be traveling in those countries (AUS or NZ), but intends to return to their home country, this scenario should be handled by the sign up form to prevent them from signing up.
- Prevent employees of competitors from registering by blocking email addresses using their company domain names
- Sign up form must use Google Recaptcha to prevent bots signing up
- The user must be informed if sign up fails by providing them with human readable error messages, such as: if an email address has already been registered, if the API is currently offline, etc.


## Local Setup

**Step 1:** Install [Python](https://www.python.org/) version 3.7

**Step 2:** Clone this project into a folder, open a terminal and navigate to the folder that contains the project.

**Step 3:** Create and activate a python 3.7 virtual environment

**Step 4:** Install the project dependancies
```bash
pip install -r requirements.txt
```

**Step 5:** Create a file called `config.json` in the project's root directory, then add the following, replacing credentials with your own. Note: if just testing locally, you can copy and paste the below text as is.

```json
{
    "user_registration_api_key": "",
    "user_registration_endpoint": "https://api.example.com/register",
    "mailchimp_api_key": "",
    "mailchimp_username": "",
    "recaptcha_test_site_key": "",
    "recaptcha_test_secret_key": "",
    "lockdown_password": ""
}
```

**Step 6:** Create environment variables file

in the root folder of the project create a `.env` file with the following contents:

```
ENVIRONMENT=LOCAL
SECRET_KEY="m!)4+x^d5=mtmxhkl%_4dn9m04fen9yev$s23a%x4thvcf4y3j"
```

(keep `SECRET_KEY` used in production secret!)

**Step 7:** Visit MaxMind (https://www.maxmind.com/en/home), signup for a free account then download the following files: `GeoLite2-City.mmdb` and `GeoLite2-Country.mmdb`, unzip them, then place them in the project's root directory.

**Step 8:** Start the development server

```bash
python manage.py runserver
```

The django app should be available at `http://127.0.0.1:8000/`


## General Information

A database is not required as all forms are sent to APIs.

Libraries used:

**django**: https://www.djangoproject.com/ - A security-centric, python-based web-framework

**email-validator** : https://pypi.org/project/email-validator/

**mailchimp3** : https://pypi.org/project/mailchimp3/1.0.17/ - used to store requests for interest from users in countries where the product is not yet available.

**requests** : https://requests.readthedocs.io/en/master/ - for API calls

**cleantext** : https://pypi.org/project/cleantext/ - for cleaning form inputs

**django-geoip2-extras** : https://pypi.org/project/django-geoip2-extras/ - for Geo-blocking by country

**openpyxl** : https://openpyxl.readthedocs.io/en/stable/ - for reading in the list of blocked countries

Geo Blocking: 

**django-ipware** : https://pypi.org/project/django-ipware/

**GeoIP2** : https://docs.djangoproject.com/en/3.2/ref/contrib/gis/geoip2/


## User signup form

The form has the following fields:

(all fields are required)

`First name`

`Last name`

`Email`

`Phone` (country flag dropdown)

`Business Number`

`industry` (drop down)

`Company`

`Country` (drop down)

note:

The `Country` *choice field* lists the countries in which Horizon is currently available.

### Form Scenarios

There are **two** scenarios associated with the form.

#### Scenario One

If the user selects a Country from the options available in the country drop-down menu, upon form submission the data is
sent to the following horizon endpoint
`https://horizon.com/api/auth/register` and a user account is created.

The user then receives a verification email sent via Horizon, which opens a link allowing the user to set their password.

#### Scenario Two

If the user is unable to locate their desired country in the list of available countries, they have the option of
selecting `other`.

When `other` is selected, a second `request_country` field appears prompting the user to enter in their requested
country.

(the `request_country` field also appears if the user selects a country prefix (flag), in the phone number field, that
is not currently available)

In this scenario, the form data is sent to the Mailchimp API which adds the user to a mailing list for future contact.

Data is not sent to the Horizon API in this scenario.

### Sign up form Validation

The following validation is being applied

**First & Last name:**

- removing all symbols and spaces

**Email:**

- email format
- check email delivery (DNS resolution) (currently de-activated)
- blocking competitor email addresses - see `competitor_domains.csv`
- blocking free email addresses - see `free_domains.csv`

**Phone:**

- country extention
- remove letters (allow numbers only)

**Company:**

none

**Country:**

- select from drop-down only
- remove all symbols

### Form security

A CSRF token is being passed into the form

### Sign up form responses

Once the user clicks `submit` on the create account form, a loading icon will display temporarily, then a pop-up message
will display in the bottom right-hand corner, with the following possible responses:
<br/><br/>

#### Account creation:

---
**Message:** Success! Please check your email and click on the verification link to get started!

**Cause:** Account successfully created.

**Request Response Code:** 201

---
**Message:** This email has already been registered. Please try another one. If you believe this is a mistake, please
contact support.

**Cause:** User entered an email that already exists in database.

**Request Response Code:** 409

---
**Message:** Creating accounts is currently unavailable. Our team is working top amend this issue as soon as possible!
Please try again in a little while.

**Cause:**

Either:

1. Either API server is down / inaccessible

2. The server hosting the website (django app) is being blocked and requires being having IP white-listed

**Request Response Code:** 500

<br/><br/>

#### Registering interest for a country inwhich Horizon is not yet available:

---
**Message:** Thanks for your interest! We'll notify you as soon as Horizon becomes available in your country.

**Cause:**

**Request Response Code:** Mailchimp API response 201

---
**Message:** Thanks! You are already subscribed.

**Cause:** API response 400

**Request Response Code:** API response 400

---

### API Call example

If all validation checks pass, the following API call is made:

```json
{
  "key": "key123",
  "first_name": "Laura",
  "last_name": "Jones",
  "email": "laura@test.com",
  "company_name": "test",
  "business_number": "12378634234",
  "mobile_phone": "+6104112341234",
  "industry": "legal",
  "referral_url": "https://referrer.com"
}
```

#### API Responses

**201** - Account creation successful

**409** - An account with that email has already been registered.

**500** - Either API server is down, or the server hosting the django app is being blocked (and requires having IP white-listed)

#Geo-blocking

Geo-blocking is handled in the View logic before each template is rendered.

We are using the following 2 libraries:


**django-ipware** : https://pypi.org/project/django-ipware/

**GeoIP2** : https://docs.djangoproject.com/en/3.2/ref/contrib/gis/geoip2/


For our purposes, there are 2 types of blocking:

**Soft**: Re-directs the user to a 'coming soon' page

**Hard**: Returns a `Page not found` 404 error

A list of countries and their blocking-type is loaded into memory when 
the server starts (from a CSV for convenience) via `settings.py` - 
(see: `block countries by IP - (all IPv4 Ranges).csv`)

The **MaxMind GeoIP2 database** binary file is available in the root folder 
of the project (required) (see `GeoLite2-Country.mmdb`)
(https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)

## Geo-blocking Overview

1. Fetch the IP address of the incoming request (using django-ipware)
2. Get the country code of the IP address (using GeoIP2)
3. Render appropriate template, or block request.

See complete example below:

```Python
# Example views.py (view + ip checking function):
from ipware import get_client_ip

def home(request):
    if request.method == 'GET':

        target_url = 'index.html'
        try:
            # get IP
            ip = visitor_ip_address(request)
            
            country_info = g.country(ip)
            
            # get country code
            country_code = country_info['country_code']

        except Exception as e:
            country_code = "XX"
            print(e)

        if country_code == "XX":
            return render(request, target_url, {})
        else:
            # Check list of countries and take appropriate action
            if country_code in settings.SOFT_BLOCK_COUNTRIES:
                return render(request, 'coming_soon_to_your_country.html', {})
            elif country_code in settings.HARD_BLOCK_COUNTRIES:
                return HttpResponseNotFound("Page not found.")
            else:
                return render(request, target_url, {})
                
def visitor_ip_address(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        # Unable to get the client's IP address
        return client_ip
    else:
        # client's IP address available
        if is_routable:
            return client_ip
        # The client's IP address is publicly routable on the Internet
        else:
            return client_ip
    # The client's IP address is private
```