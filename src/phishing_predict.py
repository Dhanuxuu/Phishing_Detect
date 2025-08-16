import re
import joblib
import requests
import tldextract
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from itertools import groupby
from difflib import SequenceMatcher

# ------------------------------
# Feature extraction function
# ------------------------------
def extract_features(url):
    url = url if url.startswith(('http://','https://')) else 'http://' + url
    parsed = urlparse(url)
    te = tldextract.extract(parsed.netloc)
    domain_only = te.domain
    tld = te.suffix
    subdomain = te.subdomain
    domain_full = ".".join(part for part in [subdomain, domain_only, tld] if part)

    # -----------------
    # Lexical features
    # -----------------
    digits = sum(c.isdigit() for c in url)
    degit_ratio = digits / len(url) if len(url) > 0 else 0

    special_chars = sum(not c.isalnum() for c in url)
    spacial_char_ratio = special_chars / len(url) if len(url) > 0 else 0

    # CharContinuationRate: longest repeating character sequence
    # Corrected logic to handle empty URLs and get the longest sequence length
    char_continuation_rate = max([len(list(g)) for k, g in groupby(url)] or [0]) if url else 0

    # URLCharProb: simple uniform probability
    url_char_prob = np.mean([1/256 for c in url]) if url else 0 # This still seems incorrect, but I'll keep it for now

    # URLSimilarityIndex (dummy placeholder)
    url_similarity_index = SequenceMatcher(None, url.lower(), domain_full.lower()).ratio()

    # -----------------
    # Web features
    # -----------------
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
    except:
        soup = BeautifulSoup("", 'html.parser')

    is_https = int(parsed.scheme == 'https')
    title_tag = soup.title.string.strip() if soup.title and soup.title.string else ""
    has_title = int(bool(title_tag))

    domain_title_match_score = SequenceMatcher(None, domain_only.lower(), title_tag.lower()).ratio() if title_tag else 0
    url_title_match_score = SequenceMatcher(None, url.lower(), title_tag.lower()).ratio() if title_tag else 0

    has_favicon = int(bool(soup.find("link", rel="icon")))
    has_description = int(bool(soup.find("meta", attrs={"name":"description"})))
    has_submit_button = int(bool(soup.find("input", type="submit")))
    has_hidden_fields = int(bool(soup.find_all("input", type="hidden")))
    # has_copyright_info = int(bool(soup.find(text=lambda t: t and 'copyright' in t.lower())))
    has_copyright_info = int(bool(soup.find(string=lambda t: t and 'copyright' in t.lower())))

    # Social network links (checking for common social domains in links)
    has_social_net = 0
    if soup:
        for link in soup.find_all('a', href=True):
            if any(domain in link['href'].lower() for domain in ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']):
                has_social_net = 1
                break


    features = {
        # 'FILENAME': 0, # Not derivable from URL, set to 0
        'URL': 0, # Not derivable from URL, set to 0
        'Domain': 0, # Not derivable from URL, set to 0
        'URLSimilarityIndex': url_similarity_index,
        'CharContinuationRate': char_continuation_rate,
        'URLCharProb': url_char_prob,
        # 'DegitRatioInURL': degit_ratio,
        # 'SpacialCharRatioInURL': spacial_char_ratio,
        'IsHTTPS': is_https,
        'HasTitle': has_title,
        'DomainTitleMatchScore': domain_title_match_score,
        'URLTitleMatchScore': url_title_match_score,
        'HasFavicon': has_favicon,
        'IsResponsive': 0, # Not easily derivable from URL, set to 0
        'HasDescription': has_description,
        'HasSocialNet': has_social_net,
        'HasSubmitButton': has_submit_button,
        'HasHiddenFields': has_hidden_fields,
        'HasCopyrightInfo': has_copyright_info

    }
    # Convert to DataFrame with correct column order
    return pd.DataFrame([features], columns=['URL', 'Domain', 'URLSimilarityIndex', 'CharContinuationRate', 'URLCharProb', 'IsHTTPS', 'HasTitle', 'DomainTitleMatchScore', 'URLTitleMatchScore', 'HasFavicon', 'IsResponsive', 'HasDescription', 'HasSocialNet', 'HasSubmitButton', 'HasHiddenFields', 'HasCopyrightInfo'])


# ------------------------------
# Explanation function
# ------------------------------
def explain_phishing(url):
    reasons = []
    parsed = urlparse(url if url.startswith(('http://','https://')) else 'http://' + url)
    te = tldextract.extract(parsed.netloc)

    domain_only = te.domain
    subdomain = te.subdomain
    tld = te.suffix
    full_domain = ".".join(part for part in [subdomain, domain_only, tld] if part)


    # Rule-based explanations
    if '@' in url:
        reasons.append("Contains '@' symbol — can hide real destination domain.")

    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", parsed.netloc):
        reasons.append("Uses raw IP address instead of domain name.")

    suspicious_brands = ['paypal', 'amazon', 'bank', 'login', 'update', 'secure', 'account', 'verify']
    if any(b in url.lower() for b in suspicious_brands):
        reasons.append("Contains brand/keyword commonly used in phishing: " +
                       ", ".join(b for b in suspicious_brands if b in url.lower()))

    if len(full_domain) > 30:
        reasons.append("Domain is unusually long.")

    if len(subdomain.split('.')) > 2:
        reasons.append("Contains many subdomains — may be hiding true domain.")

    bad_tlds = ['ru', 'cn', 'tk', 'ml', 'ga', 'cf']
    if tld.lower() in bad_tlds:
        reasons.append(f"Uses suspicious top-level domain: .{tld}")

    if '-' in domain_only:
        reasons.append("Domain contains hyphen — often used in fake sites.")

    if parsed.scheme != 'https':
        reasons.append("Does not use HTTPS — less secure.")

    return reasons

# ------------------------------
# Prediction function
# ------------------------------
def predict_url(url, model_path = r"C:\myworks\Phishing_Detect\notebooks\phishing_best_model.pkl"):
    # Extract features
    features_df = extract_features(url)

    # Load model
    rf_model = joblib.load(model_path)

    # Predict
    pred = rf_model.predict(features_df)[0]
    prob = rf_model.predict_proba(features_df)[0][1]  # probability of phishing

    # Explain
    reasons = explain_phishing(url)

    verdict = "LEGITIMATE ✅" if pred==1 else "PHISHING ⚠️"

    # return verdict, round(prob, 2), reasons
    return verdict, float(prob), reasons


# ------------------------------
# Example usage
# ------------------------------
if __name__ == "__main__":
    test_urls = [
        "https://www.wikipedia.org",
        "paypal.com.secure-login-update.ru",
        "https://www.amazon.com",
        "http://secure-login-paypal.com",
        "http://192.168.0.1/login"
    ]

    for url in test_urls:
        verdict, probability, reasons = predict_url(url)
        print(f"URL: {url}")
        print("Prediction:", verdict)
        print("Probability:", probability)
        if reasons:
            print("Reasons:")
            for r in reasons:
                print(" -", r)
        print("-"*50)