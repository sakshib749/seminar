import re
import socket
import requests
import whois
import urllib
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# 1. Having IP address
def having_ip_address(url):
    match = re.search(
        r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])', url
    )
    return 1 if match else 0


# 2. Having @ symbol
def have_at_sign(url):
    return 1 if "@" in url else 0


# 3. URL Length
def get_length(url):
    return 1 if len(url) >= 54 else 0


# 4. URL Depth
def get_depth(url):
    s = urlparse(url).path.split('/')
    depth = sum([1 for j in s if j])
    return depth


# 5. Redirection (// in URL)
def redirection(url):
    return 1 if '//' in url[7:] else 0


# 6. https in domain part
def https_domain(url):
    domain = urlparse(url).netloc
    return 1 if 'https' in domain else 0


# 7. TinyURL
def tinyURL(url):
    shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|" \
                          r"ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|" \
                          r"cli\.gs|yfrog\.com|migre\.me|ff\.im|tiny\.cc|" \
                          r"url4\.eu|twit\.ac|su\.pr|twurl\.nl|" \
                          r"snipurl\.com|short\.to|BudURL\.com|ping\.fm|" \
                          r"post\.ly|Just\.as|bkite\.com|snipr\.com|" \
                          r"fic\.kr|loopt\.us|doiop\.com|short\.ie|" \
                          r"kl\.am|wp\.me|rubyurl\.com|om\.ly|" \
                          r"to\.ly|bit\.do|lnkd\.in|db\.tt|qr\.ae|" \
                          r"adf\.ly|goo\.gl|cur\.lv|tinyurl\.com|ow\.ly|" \
                          r"bit\.ly|ity\.im|q\.gs|is\.gd|po\.st|" \
                          r"bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|" \
                          r"cutt\.us|u\.bb|yourls\.org|x\.co|" \
                          r"prettylinkpro\.com|scrnch\.me|filoops\.info|" \
                          r"vzturl\.com|qr\.net|1url\.com|tweez\.me|" \
                          r"v\.gd|tr\.im|link\.zip\.net"
    match = re.search(shortening_services, url)
    return 1 if match else 0


# 8. Prefix/Suffix in domain
def prefix_suffix(url):
    return 1 if '-' in urlparse(url).netloc else 0


# 9. DNS Record
def dns_record(url):
    try:
        domain = urlparse(url).netloc
        socket.gethostbyname(domain)
        return 0
    except:
        return 1


# 10. Web Traffic (Alexa API is shut down → return 0 always)
def web_traffic(url):
    return 0


# 11. Domain Age
def domain_age(domain_name):
    try:
        creation_date = domain_name.creation_date
        expiration_date = domain_name.expiration_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        ageofdomain = abs((expiration_date - creation_date).days)
        return 0 if ageofdomain >= 365 else 1
    except:
        return 1


# 12. Domain End
def domain_end(domain_name):
    try:
        expiration_date = domain_name.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        today = datetime.datetime.now()
        end = abs((expiration_date - today).days)
        return 0 if end >= 365 else 1
    except:
        return 1


# 13. iFrame
def iframe(response):
    if response == "" or response is None:
        return 1
    # look for actual iframe/frame tags (case-insensitive)
    try:
        text = response.text
    except Exception:
        return 1
    if re.search(r"<iframe\b", text, re.I) or re.search(r"<frame\b", text, re.I):
        return 1
    return 0


# 14. Mouse Over
def mouse_over(response):
    if response == "" or response is None:
        return 1
    # detect uses of onmouseover (attribute or in scripts). Case-insensitive.
    try:
        text = response.text
    except Exception:
        return 1
    if re.search(r"onmouseover\s*=", text, re.I) or re.search(r"onmouseover\s*\(|onmouseover\b", text, re.I):
        return 1
    return 0


# 15. Right Click
def right_click(response):
    if response == "" or response is None:
        return 1
    # look for common patterns that disable right-click: event.button==2 or oncontextmenu handlers
    try:
        text = response.text
    except Exception:
        return 1
    if re.search(r"event\.button\s*==\s*2", text, re.I) or re.search(r"oncontextmenu\s*=", text, re.I):
        return 1
    return 0


# 16. Web Forwards
def forwarding(response):
    if response == "" or response is None:
        return 1
    if len(response.history) <= 2:
        return 0
    else:
        return 1


# MAIN FUNCTION - extract all features
def featureExtraction(url):
    features = []

    # Address bar features
    features.append(having_ip_address(url))
    features.append(have_at_sign(url))
    features.append(get_length(url))
    features.append(get_depth(url))
    features.append(redirection(url))
    features.append(https_domain(url))
    features.append(tinyURL(url))
    features.append(prefix_suffix(url))

    # Domain-based features
    dns = dns_record(url)
    features.append(dns)
    try:
        domain_name = whois.whois(urlparse(url).netloc)
    except:
        domain_name = ""
    features.append(domain_age(domain_name))
    features.append(domain_end(domain_name))

    # Web traffic
    features.append(web_traffic(url))

    # HTML & JS based features
    try:
        # add a short timeout to avoid hanging on slow/unresponsive sites
        response = requests.get(url, timeout=5)
    except requests.exceptions.SSLError:
        # SSL issues — treat as no response
        response = ""
    except requests.exceptions.RequestException:
        # network/connection/timeouts etc.
        response = ""
    features.append(iframe(response))
    features.append(mouse_over(response))
    features.append(right_click(response))
    features.append(forwarding(response))

    return features


# Feature names (16 only – fixed)
feature_names = [
    'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth', 'Redirection',
    'https_Domain', 'TinyURL', 'Prefix/Suffix', 'DNS_Record', 'Web_Traffic',
    'Domain_Age', 'Domain_End', 'iFrame', 'Mouse_Over', 'Right_Click',
    'Web_Forwards'
]
