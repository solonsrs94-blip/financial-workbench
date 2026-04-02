"""Yahoo Finance → Damodaran industry name mapping.

Pure data — no imports, no logic, no Streamlit.
Keys: Yahoo Finance industry names (lowercase).
Values: Damodaran industry names (exact case from spreadsheet).

This table is checked FIRST before fuzzy matching.
Add new entries as mismatches are discovered.
"""

YAHOO_TO_DAMODARAN = {
    # ── Banks ─────────────────────────────────────────────────
    "banks - diversified": "Bank (Money Center)",
    "banks - regional": "Banks (Regional)",
    # ── Utilities ─────────────────────────────────────────────
    "utilities - regulated electric": "Utility (General)",
    "utilities - regulated gas": "Utility (General)",
    "utilities - regulated water": "Utility (Water)",
    "utilities - diversified": "Utility (General)",
    "utilities - renewable": "Power",
    "utilities - independent power producers": "Power",
    # ── REITs ─────────────────────────────────────────────────
    "reit - specialty": "R.E.I.T.",
    "reit - residential": "R.E.I.T.",
    "reit - industrial": "R.E.I.T.",
    "reit - retail": "R.E.I.T.",
    "reit - office": "R.E.I.T.",
    "reit - healthcare facilities": "R.E.I.T.",
    "reit - diversified": "R.E.I.T.",
    "reit - hotel & motel": "R.E.I.T.",
    "reit - mortgage": "R.E.I.T.",
    # ── Software ──────────────────────────────────────────────
    "software - infrastructure": "Software (System & Application)",
    "software - application": "Software (System & Application)",
    "electronic gaming & multimedia": "Software (Entertainment)",
    # ── Drugs / Pharma ────────────────────────────────────────
    "drug manufacturers - general": "Drugs (Pharmaceutical)",
    "drug manufacturers - specialty & generic": "Drugs (Pharmaceutical)",
    "biotechnology": "Drugs (Biotechnology)",
    "pharmaceutical retailers": "Retail (Special Lines)",
    # ── Healthcare ────────────────────────────────────────────
    "healthcare plans": "Insurance (General)",
    "medical devices": "Healthcare Products",
    "medical instruments & supplies": "Healthcare Products",
    "diagnostics & research": "Healthcare Products",
    "medical care facilities": "Hospitals/Healthcare Facilities",
    "medical distribution": "Healthcare Support Services",
    "health information services": "Heathcare Information and Technology",
    # ── Retail ────────────────────────────────────────────────
    "internet retail": "Retail (General)",
    "specialty retail": "Retail (Special Lines)",
    "grocery stores": "Retail (Grocery and Food)",
    "home improvement retail": "Retail (Building Supply)",
    "apparel retail": "Retail (Special Lines)",
    "luxury goods": "Retail (Special Lines)",
    "department stores": "Retail (General)",
    "discount stores": "Retail (General)",
    "auto & truck dealerships": "Retail (Automotive)",
    # ── Transport / Logistics ─────────────────────────────────
    "integrated freight & logistics": "Transportation",
    "marine shipping": "Shipbuilding & Marine",
    "railroads": "Transportation (Railroads)",
    "airlines": "Air Transport",
    "trucking": "Trucking",
    "airports & air services": "Air Transport",
    # ── Consumer ──────────────────────────────────────────────
    "footwear & accessories": "Shoe",
    "consumer electronics": "Electronics (Consumer & Office)",
    "beverages - non-alcoholic": "Beverage (Soft)",
    "beverages - wineries & distilleries": "Beverage (Alcoholic)",
    "beverages - brewers": "Beverage (Alcoholic)",
    "tobacco": "Tobacco",
    "packaged foods": "Food Processing",
    "confectioners": "Food Processing",
    "farm products": "Farming/Agriculture",
    "household & personal products": "Household Products",
    "restaurants": "Restaurant/Dining",
    "apparel manufacturing": "Apparel",
    "lodging": "Hotel/Gaming",
    "resorts & casinos": "Hotel/Gaming",
    "leisure": "Recreation",
    "travel services": "Recreation",
    "gambling": "Hotel/Gaming",
    # ── Industrials ───────────────────────────────────────────
    "building products & equipment": "Building Materials",
    "residential construction": "Homebuilding",
    "farm & heavy construction machinery": "Machinery",
    "specialty industrial machinery": "Machinery",
    "industrial distribution": "Retail (Distributors)",
    "waste management": "Environmental & Waste Services",
    "engineering & construction": "Engineering/Construction",
    "conglomerates": "Diversified",
    "rental & leasing services": "Financial Svcs. (Non-bank & Insurance)",
    "pollution & treatment controls": "Environmental & Waste Services",
    "tools & accessories": "Machinery",
    # ── Insurance ─────────────────────────────────────────────
    "insurance - life": "Insurance (Life)",
    "insurance - property & casualty": "Insurance (Prop/Cas.)",
    "insurance - diversified": "Insurance (General)",
    "insurance - reinsurance": "Reinsurance",
    "insurance - specialty": "Insurance (General)",
    "insurance brokers": "Insurance (General)",
    # ── Financial Services ────────────────────────────────────
    "asset management": "Investments & Asset Management",
    "capital markets": "Brokerage & Investment Banking",
    "financial data & stock exchanges": "Financial Svcs. (Non-bank & Insurance)",
    "financial conglomerates": "Financial Svcs. (Non-bank & Insurance)",
    "credit services": "Financial Svcs. (Non-bank & Insurance)",
    "mortgage finance": "Financial Svcs. (Non-bank & Insurance)",
    # ── Energy ────────────────────────────────────────────────
    "oil & gas integrated": "Oil/Gas (Integrated)",
    "oil & gas e&p": "Oil/Gas (Production and Exploration)",
    "oil & gas equipment & services": "Oilfield Svcs/Equip.",
    "oil & gas midstream": "Oil/Gas Distribution",
    "oil & gas refining & marketing": "Oil/Gas Distribution",
    "thermal coal": "Coal & Related Energy",
    "uranium": "Power",
    "solar": "Green & Renewable Energy",
    # ── Tech / Semis ──────────────────────────────────────────
    "semiconductors": "Semiconductor",
    "semiconductor equipment & materials": "Semiconductor Equip",
    "scientific & technical instruments": "Electronics (General)",
    "electronic components": "Electronics (General)",
    "communication equipment": "Telecom. Equipment",
    "computer hardware": "Computers/Peripherals",
    "information technology services": "Information Services",
    "internet content & information": "Software (Internet)",
    # ── Telecom ───────────────────────────────────────────────
    "telecom services": "Telecom. Services",
    "pay tv": "Cable TV",
    # ── Aerospace / Defense ───────────────────────────────────
    "aerospace & defense": "Aerospace/Defense",
    # ── Auto ──────────────────────────────────────────────────
    "auto manufacturers": "Auto & Truck",
    "auto parts": "Auto Parts",
    # ── Media ─────────────────────────────────────────────────
    "advertising agencies": "Advertising",
    "broadcasting": "Broadcasting",
    "publishing": "Publishing & Newspapers",
    "entertainment": "Entertainment",
    # ── Materials ─────────────────────────────────────────────
    "specialty chemicals": "Chemical (Specialty)",
    "chemicals": "Chemical (Diversified)",
    "steel": "Steel",
    "gold": "Precious Metals",
    "silver": "Precious Metals",
    "copper": "Metals & Mining",
    "other industrial metals & mining": "Metals & Mining",
    "other precious metals & mining": "Precious Metals",
    "aluminum": "Metals & Mining",
    "lumber & wood production": "Paper/Forest Products",
    "paper & paper products": "Paper/Forest Products",
    "packaging & containers": "Packaging & Container",
    # ── Real Estate (non-REIT) ────────────────────────────────
    "real estate services": "Real Estate (Operations & Services)",
    "real estate - development": "Real Estate (Development)",
    "real estate - diversified": "Real Estate (General/Diversified)",
    # ── Education ─────────────────────────────────────────────
    "education & training services": "Education",
    # ── Staffing ──────────────────────────────────────────────
    "staffing & employment services": "Business & Consumer Services",
    "consulting services": "Business & Consumer Services",
    "security & protection services": "Business & Consumer Services",
    "specialty business services": "Business & Consumer Services",
    "personal services": "Business & Consumer Services",
    # ── Agriculture ───────────────────────────────────────────
    "agricultural inputs": "Farming/Agriculture",
    # ── Food ──────────────────────────────────────────────────
    "food distribution": "Food Wholesalers",
    # ── Electrical ────────────────────────────────────────────
    "electrical equipment & parts": "Electrical Equipment",
}
