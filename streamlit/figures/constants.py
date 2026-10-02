"""Reference data shared by the queries, the charts and the filters.

Years, lines of coverage, plan size bands, NAICS sectors, state names and the patterns that tag
Schedule C providers to a national broker firm.
"""

YEARS = list(range(2019, 2025))
FIRST, LAST = YEARS[0], YEARS[-1]

LINES = [
    "Medical",
    "Stop-loss",
    "Dental",
    "Vision",
    "Life & AD&D",
    "Disability",
    "Multi-line bundle",
    "Voluntary & other",
]

SELF_FUNDING_BANDS = [
    "100-249",
    "250-499",
    "500-999",
    "1,000-2,499",
    "2,500-4,999",
    "5,000+",
]
VOLUNTARY_BANDS = ["100-249", "250-499", "500-999", "1,000-4,999", "5,000+"]

NAICS_SECTORS = {
    "11": "Agriculture",
    "21": "Mining, Oil & Gas",
    "22": "Utilities",
    "23": "Construction",
    "31": "Manufacturing",
    "32": "Manufacturing",
    "33": "Manufacturing",
    "42": "Wholesale Trade",
    "44": "Retail Trade",
    "45": "Retail Trade",
    "48": "Transportation & Warehousing",
    "49": "Transportation & Warehousing",
    "51": "Information",
    "52": "Finance & Insurance",
    "53": "Real Estate",
    "54": "Professional & Technical Services",
    "55": "Management of Companies",
    "56": "Admin & Support Services",
    "61": "Educational Services",
    "62": "Health Care & Social Assistance",
    "71": "Arts & Recreation",
    "72": "Accommodation & Food Services",
    "81": "Other Services",
    "92": "Public Administration",
}
SECTORS = sorted(set(NAICS_SECTORS.values()))

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia",
    "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}  # fmt: skip

# Order matters: a provider name takes the first firm whose pattern matches (as np.select does).
# Each firm has a pattern the name must match and, optionally, a pattern that rules it out
# (investment arms, law firms, look-alike names). \b is a word boundary, so ALERA no longer
# matches SALERA. Keep in sync with the notebook; rules and examples are in docs/name-matching.md.
BROKER_FIRMS = {
    "WTW": (r"\bWILLIS\b|\bTOWERS WATSON\b|^WTW\b|WILLISTOWERSWATSON", r"INVESTMENT"),
    "Mercer": (r"\bMERCER\b", r"INVESTMENT|\bMERCER (?:COUNTY|ISLAND|UNIVERSITY)\b"),
    "Aon": (r"^AON\b|^AONHEWITT|\bAON (?:CONSULTING|RISK|HEWITT)\b", r"INVESTMENT"),
    "Gallagher": (
        r"^GALLAGHER\b|\bARTHUR (?:J\.? )?GALLAGHER\b|\bA\.? ?J\.? GALLAGHER\b"
        r"|\bGALLAGHER BENEFIT|, A GALLAGHER\b",
        r"FIDUCIARY|INVESTMENT",
    ),
    "Marsh McLennan Agency": (r"\bMARSH (?:&|AND) ?MC|\bMARSH MC|\bMARSH USA\b", None),
    "Lockton": (r"LOCKTON", None),
    "HUB International": (r"^HUB\b|\bHUB INT", None),
    "USI": (r"^USI\b|\bUSI (?:INSURANCE|CONSULTING)\b", None),
    "Brown & Brown": (r"\bBROWN (?:&|AND) BROWN\b", None),
    "OneDigital": (r"\bONE ?DIGITAL\b|\bDIGITAL INSURANCE\b", r"INVESTMENT"),
    "AssuredPartners": (r"\bASSURED ?PARTNERS\b", None),
    "Alliant": (r"\bALLIANT (?:INS|EMPLOYEE|BEN)", None),
    "NFP": (r"^NFP|\bNATIONAL FINANCIAL PARTNERS\b", None),
    "CBIZ": (r"CBIZ", r"\bCPAS?\b"),
    "Segal": (r"\bSEGAL\b", r"\bMARCO\b"),
    "McGriff": (r"\bMCGRIFF\b|\bTRUIST INSURANCE\b", None),
    "Acrisure": (r"\bACRISURE\b", None),
    "Alera": (r"\bALERA\b", None),
    "EPIC": (r"\bEDGEWOOD PARTNERS\b|^EPIC ", None),
    "Holmes Murphy": (r"\bHOLMES MURPHY\b", None),
    "IMA": (r"^IMA\b|\bIMA FINANCIAL\b", None),
    "Hylant": (r"\bHYLANT\b", None),
}
