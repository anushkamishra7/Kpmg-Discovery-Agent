"""
Seed the DB with known IndiGo campaign data pulled from public search results.
Use this instead of scraping when the live site blocks requests.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.database import init_db, upsert_campaign

CAMPAIGNS = [
    {
        "id": "destinations-of-the-week",
        "name": "Destinations of the Week",
        "url": "https://www.goindigo.in/campaigns/destinations-of-the-week-offers.html",
        "offer_text": (
            "Get up to 10% discount on base fare to select international flights. "
            "Destinations include Bangkok, Phuket and Krabi. "
            "Apply coupon code FLYMORE at the time of payment to avail the discount. "
            "Valid for bookings made on goIndiGo.in, IndiGo mobile app, Android and iOS. "
            "Offer valid for one week only. Cannot be clubbed with other offers. "
            "Non-transferable, non-refundable, non-redeemable for cash."
        ),
        "promo_codes": "FLYMORE",
    },
    {
        "id": "family-and-friends-offer",
        "name": "Family and Friends Offer",
        "url": "https://www.goindigo.in/campaigns/family-and-friends-offer.html",
        "offer_text": (
            "IndiGo is offering discounted fare to passengers who select Family and Friends Fare. "
            "Applicable for bookings with minimum 4 and maximum 9 passengers per PNR. "
            "Discount up to INR 400 per passenger on base fare. "
            "Additionally up to 30% discount on ancillaries including Fast Forward, "
            "standard seat selection, and meal selections. "
            "Valid on domestic and international IndiGo flights booked on goindigo.in or mobile app. "
            "Cannot be clubbed with other offers. Not valid on group bookings."
        ),
        "promo_codes": "",
    },
    {
        "id": "indigo-stretch-offers",
        "name": "IndiGoStretch Business Cabin Offer",
        "url": "https://www.goindigo.in/campaigns/indigo-stretch-offers.html",
        "offer_text": (
            "IndiGo offers up to 15% discount on base fare of Stretch and Business class "
            "for selected domestic flight bookings. "
            "Valid on flights scheduled for departure on Tuesday, Wednesday and Thursday "
            "from 21:00 hours up to 05:00 hours. "
            "Applicable for non-stop domestic flights booked at least 7 days in advance. "
            "Valid on Stretch and Stretch+ fare only. Not applicable on Economy fares. "
            "Book via goindigo.in, IndiGo mobile app, or 6ESkai WhatsApp."
        ),
        "promo_codes": "",
    },
    {
        "id": "payzapp-offer",
        "name": "HDFC PayZapp Cashback Offer",
        "url": "https://www.goindigo.in/campaigns/indigo-offers/payzapp-offer.html",
        "offer_text": (
            "HDFC Bank PayZapp offers 15% cashback up to INR 1000 per month on IndiGo flight bookings. "
            "Minimum booking amount of INR 4000 required. "
            "Valid on bookings made on goindigo.in or IndiGo mobile app using HDFC Bank PayZapp. "
            "Cashback credited to PayZapp Prepaid Card within 15 working days after transaction. "
            "Valid for Indian residents only. Not applicable on EMI transactions or group bookings. "
            "Cannot be clubbed with other IndiGo offers."
        ),
        "promo_codes": "",
    },
    {
        "id": "6e-social-offer",
        "name": "6E Social Flight Booking Offer",
        "url": "https://www.goindigo.in/campaigns/6e-social-offer-terms-and-conditions.html",
        "offer_text": (
            "IndiGo 6E Social offer allows customers to book flights through social channels. "
            "Exclusive fares available through IndiGo social media platforms. "
            "Non-transferable, non-exchangeable, non-refundable and non-redeemable for cash. "
            "Subject to IndiGo conditions of carriage and government rules and regulations."
        ),
        "promo_codes": "",
    },
    {
        "id": "indigo-citi-offer",
        "name": "IndiGo Citibank Cashback Offer",
        "url": "https://www.goindigo.in/content/indigo/airlines/en/campaigns/indigo-citi.html",
        "offer_text": (
            "Citibank offers flat cashback of INR 1500 on minimum flight booking of INR 7500 on IndiGo. "
            "Valid on bookings through IndiGo website or mobile app using Citi Credit and Debit Cards. "
            "Excludes Citi Corporate cards. Valid for one transaction per card during offer period. "
            "Cashback processed within 15 working days. "
            "Not applicable on hold bookings, group bookings, or bookings through travel agents."
        ),
        "promo_codes": "",
    },
    {
        "id": "early-bird-offer",
        "name": "Early Bird Discount",
        "url": "https://www.goindigo.in/campaigns/indigo-offers.html",
        "offer_text": (
            "Book IndiGo flights early and save more. "
            "Early bird discounts available on domestic and international routes. "
            "Greater savings when booking 30 to 60 days in advance. "
            "Valid on Economy, Flexi and Stretch fare classes. "
            "Book directly on goindigo.in or IndiGo mobile app for best fares."
        ),
        "promo_codes": "",
    },
    {
        "id": "monsoon-sale",
        "name": "Monsoon Sale - Discounted Fares",
        "url": "https://www.goindigo.in/campaigns/indigo-offers.html",
        "offer_text": (
            "IndiGo monsoon sale offers discounted fares on domestic routes across India. "
            "Save up to 20% on base fares to popular destinations including Mumbai, Delhi, "
            "Bengaluru, Hyderabad, Chennai, Kolkata, Goa and more. "
            "Limited seats available at sale prices. "
            "Book now on goindigo.in and travel during the monsoon season."
        ),
        "promo_codes": "MONSOON",
    },
    {
        "id": "student-discount",
        "name": "Student Discount on Flights",
        "url": "https://www.goindigo.in/campaigns/indigo-offers.html",
        "offer_text": (
            "IndiGo offers special student fares on domestic and select international routes. "
            "Students with valid student ID can avail discounted base fares. "
            "Additional baggage allowance of 10kg included for students. "
            "Valid on Economy class bookings made through goindigo.in or IndiGo mobile app. "
            "Student ID must be presented at check-in."
        ),
        "promo_codes": "STUDENT",
    },
    {
        "id": "web-checkin-offer",
        "name": "Web Check-in Offer",
        "url": "https://www.goindigo.in/campaigns/indigo-offers.html",
        "offer_text": (
            "Save on seat selection fees by completing web check-in on IndiGo. "
            "Web check-in opens 48 hours before departure. "
            "Select preferred seats at discounted rates when checking in online. "
            "Available on goindigo.in and IndiGo mobile app. "
            "Avoid airport queues and get your boarding pass instantly."
        ),
        "promo_codes": "",
    },
]


def main():
    print("Initialising database...")
    init_db()

    print(f"\nSeeding {len(CAMPAIGNS)} campaigns...")
    for c in CAMPAIGNS:
        upsert_campaign(c)
        print(f"  saved: {c['name']}")

    print(f"\nDone. {len(CAMPAIGNS)} campaigns in DB.")
    print("Run scripts/embed_campaigns.py next.")


if __name__ == "__main__":
    main()