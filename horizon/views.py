import logging
from pprint import pprint
from django.contrib.gis.geoip2 import GeoIP2
import cleantext
import requests
from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from email_validator import validate_email, EmailNotValidError
from ipware import get_client_ip
from mailchimp3 import MailChimp

# Get an instance of a logger
logger = logging.getLogger(__name__)

if settings.MAILCHIMP_API_KEY == "" or settings.MAILCHIMP_USERNAME == "":
    mailchimp_client = ""
else:
    mailchimp_client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY, mc_user=settings.MAILCHIMP_USERNAME)

g = GeoIP2()

def affiliates(request):
    if request.method == 'GET':
        target_url = 'affiliate-program.html'
        try:
            ip = visitor_ip_address(request)
            # print("IP: ", ip)
            country_info = g.country(ip)
            country_code = country_info['country_code']
            # print(country_code)
        except Exception as e:
            country_code = "XX"
            print(e)

        if country_code == "XX":
            return render(request, target_url, {})
        else:
            if country_code in settings.SOFT_BLOCK_COUNTRIES:
                return render(request, 'coming_soon_to_your_country.html', {})
            elif country_code in settings.HARD_BLOCK_COUNTRIES:
                return HttpResponseNotFound("Page not found.")
            else:
                return render(request, target_url, {})
            
    if request.method == 'POST':

        affiliate_type = request.POST['affiliate_type']
        f_name = request.POST['first_name']
        l_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        company_name = request.POST['company_name']
        business_number = request.POST['business_number']
        address = request.POST['address']
        country = request.POST['country']
        website = request.POST['website']
        linkedin = request.POST['linkedin']
        agreement = request.POST['agreement']

        context = {}

        try:
            mailchimp_client.lists.members.create('96e59e2a2b', {
                'email_address': email,
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': f_name,
                    'LNAME': l_name,
                    'AFFILIATE_TYPE': affiliate_type,
                    'COMPANY': company_name,
                    'BUSINESS_NUMBER': business_number,
                    'PHONE': phone,
                    'COUNTRY': country,
                    'ADDRESS': address,
                    'WEBSITE': website,
                    'LINKEDIN': linkedin,
                    'AGREEMENT': agreement
                },
            })
            context['result_mailchimp'] = "success"

        except Exception as e:
            diagnostic_message = "Mail chimp API call error: " + str(e)
            context['result_mailchimp'] = "fail"
            print(diagnostic_message)

        return render(request, 'affiliate-program.html', context)


def signup(request):
    if request.method == 'GET':

        context = {}
        context['recaptcha'] = settings.RECAPTCHA_SITE_KEY

        try:
            ip = visitor_ip_address(request)
            # print("IP: ", ip)
            country_info = g.country(ip)
            country_code = country_info['country_code']
            # print(country_code)
        except Exception as e:
            country_code = "XX"
            print(e)

        if country_code == "XX":
            return render(request, 'signup.html', context)
        else:
            if country_code in settings.SOFT_BLOCK_COUNTRIES:
                return render(request, 'coming_soon_to_your_country.html', {})
            elif country_code in settings.HARD_BLOCK_COUNTRIES:
                return HttpResponseNotFound("Page not found.")
            else:
                return render(request, 'signup.html', context)

    if request.method == 'POST':

        key = settings.USER_REGISTRATION_API_KEY
        f_name = request.POST['first_name']
        l_name = request.POST['last_name']
        email = request.POST['email']
        mobile_phone = request.POST['phone_number_for_request']
        company_name = request.POST['company_name']
        business_number = request.POST['business_number']
        other_country = request.POST['your_other_country']
        industry = request.POST['industry']
        other_industry = request.POST['your_other_industry']

        if other_industry:
            industry = other_industry

        try:
            referrer = request.headers.get("Referer")
        except:
            referrer = ""

        if settings.ENABLE_RECAPTCHA:
            try:
                recaptcha_response = request.POST['g-recaptcha-response']
            except:
                recaptcha_response = ""

            recaptcha_passed = False

            if recaptcha_response:
                params = {
                    'secret': settings.RECAPTCHA_SECRET,
                    'response': recaptcha_response,
                }
                recaptcha_result = requests.post('https://www.google.com/recaptcha/api/siteverify', params=params)
                recaptcha_response_data = recaptcha_result.json()

                if recaptcha_response_data['success'] == True:
                    recaptcha_passed = True

            if not recaptcha_passed:
                context = {}
                context['result_validation'] = "recaptcha_error"
                logger.error('recaptcha failed. Email address used to sign up: ', email)
                return render(request, 'signup.html', context)

        data = request.POST.dict()

        email_valid = validate_user_email(data.get("email"))

        if not email_valid:
            context = {}
            context['result_validation'] = "not_valid"
            logger.error('email validation error: ', email)
            return render(request, 'signup.html', context)

        blacklist = check_blacklisted_domains(data.get("email"))

        if blacklist:
            context = {}
            context['result_validation'] = "server_error"
            logger.error('email blacklist blocked: ', email)
            return render(request, 'signup.html', context)

        free_email_domain = check_free_domains(data.get("email"))

        if free_email_domain:
            context = {}
            context['result_validation'] = "free_email"
            logger.error('free email blocked: ', email)
            return render(request, 'signup.html', context)

        other_country_exists = data.get("your_other_country")

        if other_country_exists:
            context = {}

            try:
                mailchimp_client.lists.members.create('51af483b0e', {
                    'email_address': email,
                    'status': 'subscribed',
                    'merge_fields': {
                        'FNAME': f_name,
                        'LNAME': l_name,
                        'COMPANY': company_name,
                        'COUNTRY': other_country,
                        'INDUSTRY': industry
                    },
                })
                context['result_mailchimp'] = "success"

            except Exception as e:
                diagnostic_message = "Mail chimp API call error: " + str(e)
                logger.error('mailchimp fail: ', email)
                context['result_mailchimp'] = "fail"
                print(diagnostic_message)

            return render(request, 'signup.html', context)

        else:

            data = {
                "key": key,
                "first_name": f_name,
                "last_name": l_name,
                "email": email,
                "company_name": company_name,
                "business_number": business_number,
                "mobile_phone": mobile_phone,
                "industry": industry,
                "referral_url": referrer
            }

            try:
                result = requests.post(url=settings.USER_REGISTER_ENDPOINT, data=data, timeout=15)
                diagnostic_message = "Request passed."
                request_success = True
                # print(diagnostic_message)

            except requests.exceptions.Timeout:
                result = None
                diagnostic_message = "Request time out. Check that server IP is white-listed / server has access to the horizon api endpoint."
                logger.error('request timeout - could be API issue: email: ', email)
                print(diagnostic_message)
                request_success = False

            except requests.exceptions.TooManyRedirects:
                result = None
                diagnostic_message = "Too many redirects - Check api endpoint url is correct."
                logger.error('request timeout - could be API issue: email: ', email)
                print(diagnostic_message)
                request_success = False

            except requests.exceptions.RequestException as e:
                result = None
                diagnostic_message = "Catastrophic error: " + str(e)
                logger.error('Catastrophic error - could be API issue: ', diagnostic_message)
                print(diagnostic_message)
                request_success = False

            context = {}

            if request_success:
                context['result'] = result.status_code

                if result.status_code == 409:
                    email_already_reg_message = "Hi, I would like to sign up for Horizon, however, I am unable to sign up via the Horizon website as I have an existing Horizon account. Can you please assist me in accessing Horizon? Thanks!"
                    complete_message_url = "https://horizontest.com/contact/?message=" + email_already_reg_message
                    logger.error('horizon account with email already exists. cant signup automatically.', email)
                    return (redirect(complete_message_url))
            return render(request, 'signup.html', context)


def not_available_in_your_country(request):
    if request.method == 'GET':
        context = {}
        context['recaptcha'] = settings.RECAPTCHA_SITE_KEY
        return render(request, 'coming_soon_to_your_country.html', context)

    if request.method == 'POST':

        f_name = request.POST['first_name']
        l_name = request.POST['last_name']
        email = request.POST['email']
        mobile_phone = request.POST['phone']
        company_name = request.POST['company_name']
        other_country = request.POST['your_other_country']

        if settings.ENABLE_RECAPTCHA:
            try:
                recaptcha_response = request.POST['g-recaptcha-response']
            except:
                recaptcha_response = ""

            recaptcha_passed = False

            if recaptcha_response:
                params = {
                    'secret': settings.RECAPTCHA_SECRET,
                    'response': recaptcha_response,
                }
                recaptcha_result = requests.post('https://www.google.com/recaptcha/api/siteverify', params=params)
                recaptcha_response_data = recaptcha_result.json()

                if recaptcha_response_data['success'] == True:
                    recaptcha_passed = True

            if not recaptcha_passed:
                context = {}
                context['result_validation'] = "recaptcha_error"
                return render(request, 'coming_soon_to_your_country.html', context)

        data = request.POST.dict()

        email_valid = validate_user_email(data.get("email"))

        if not email_valid:
            context = {}
            context['result_validation'] = "not_valid"
            logger.error('email validation error: ', email)
            return render(request, 'coming_soon_to_your_country.html', context)

        blacklist = check_blacklisted_domains(data.get("email"))

        if blacklist:
            context = {}
            context['result_validation'] = "server_error"
            logger.error('black-listed email blocked: ', email)
            return render(request, 'coming_soon_to_your_country.html', context)

        free_email_domain = check_free_domains(data.get("email"))

        if free_email_domain:
            context = {}
            context['result_validation'] = "free_email"
            logger.error('free-domain email blocked: ', email)
            return render(request, 'coming_soon_to_your_country.html', context)

        other_country_exists = data.get("your_other_country")

        if other_country_exists:

            context = {}

            try:
                mailchimp_client.lists.members.create('51af483b0e', {
                    'email_address': email,
                    'status': 'subscribed',
                    'merge_fields': {
                        'FNAME': f_name,
                        'LNAME': l_name,
                        'COMPANY': company_name,
                        'PHONE': mobile_phone,
                        'COUNTRY': other_country,
                    },
                })
                context['result_mailchimp'] = "success"

            except Exception as e:
                diagnostic_message = "Mail chimp API call error: " + str(e)
                context['result_mailchimp'] = "fail"
                logger.error('mailchimp failed: ', email)
                print(diagnostic_message)

            return render(request, 'coming_soon_to_your_country.html', context)
        else:
            return render(request, 'coming_soon_to_your_country.html', {})


def clean_name(name):
    cleaned_name = cleantext.clean(
        str(name),
        extra_spaces=True,
        lowercase=True,
        numbers=True,
        punct=True
    )

    return cleaned_name


def validate_user_email(email):
    try:
        # Validate email
        valid = validate_email(
            email,
            allow_smtputf8=True,
            allow_empty_local=False,
            check_deliverability=False,
        )

        email = valid.ascii_email

    except EmailNotValidError as e:
        print(str(e))
        email = None

    return email


def check_blacklisted_domains(email):
    blacklisted = False

    for domain in settings.BLACKLISTED_DOMAINS:
        if domain in email:
            blacklisted = True
            break

    return blacklisted


def check_free_domains(email):
    free_domain = False

    for domain in settings.FREE_DOMAINS:
        if domain in email:
            free_domain = True
            break

    return free_domain

def visitor_ip_address(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip is None:
        # Unable to get the client's IP address
        return client_ip
    else:
        # We got the client's IP address
        if is_routable:
            return client_ip
        # The client's IP address is publicly routable on the Internet
        else:
            return client_ip


