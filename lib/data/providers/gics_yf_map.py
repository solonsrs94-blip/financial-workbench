"""GICS Sub-Industry <-> yfinance industry mapping.

Auto-generated from S&P 500 data (503 tickers, 0 errors).
Used by comps_peers.py to match target yfinance industry against
S&P 500 GICS Sub-Industry classifications.

127 GICS Sub-Industries, 111 yfinance industries.
"""

# yfinance industry -> list of matching GICS Sub-Industries
YF_TO_GICS: dict[str, list[str]] = {
    "Advertising Agencies": ["Advertising", "Application Software"],
    "Aerospace & Defense": ["Aerospace & Defense"],
    "Agricultural Inputs": ["Fertilizers & Agricultural Chemicals"],
    "Airlines": ["Passenger Airlines"],
    "Apparel Manufacturing": ["Apparel, Accessories & Luxury Goods"],
    "Apparel Retail": [
        "Apparel Retail", "Apparel, Accessories & Luxury Goods",
    ],
    "Asset Management": [
        "Asset Management & Custody Banks", "Life & Health Insurance",
        "Investment Banking & Brokerage",
    ],
    "Auto & Truck Dealerships": ["Automotive Retail"],
    "Auto Manufacturers": ["Automobile Manufacturers"],
    "Auto Parts": [
        "Automotive Retail", "Automotive Parts & Equipment", "Distributors",
    ],
    "Banks - Diversified": [
        "Diversified Banks", "Asset Management & Custody Banks",
    ],
    "Banks - Regional": ["Regional Banks", "Diversified Banks"],
    "Beverages - Brewers": ["Distillers & Vintners", "Brewers"],
    "Beverages - Non-Alcoholic": [
        "Soft Drinks & Non-alcoholic Beverages",
    ],
    "Beverages - Wineries & Distilleries": ["Distillers & Vintners"],
    "Biotechnology": ["Biotechnology", "Life Sciences Tools & Services"],
    "Building Materials": ["Construction Materials"],
    "Building Products & Equipment": ["Building Products"],
    "Capital Markets": ["Investment Banking & Brokerage"],
    "Chemicals": ["Commodity Chemicals"],
    "Communication Equipment": [
        "Communications Equipment",
        "Technology Hardware, Storage & Peripherals",
        "Electronic Equipment & Instruments",
    ],
    "Computer Hardware": [
        "Technology Hardware, Storage & Peripherals",
        "Communications Equipment",
    ],
    "Confectioners": ["Packaged Foods & Meats"],
    "Conglomerates": ["Industrial Conglomerates"],
    "Consulting Services": ["Research & Consulting Services"],
    "Consumer Electronics": [
        "Technology Hardware, Storage & Peripherals",
    ],
    "Copper": ["Copper"],
    "Credit Services": [
        "Consumer Finance",
        "Transaction & Payment Processing Services",
    ],
    "Diagnostics & Research": [
        "Life Sciences Tools & Services", "Health Care Equipment",
        "Health Care Services",
    ],
    "Discount Stores": ["Consumer Staples Merchandise Retail"],
    "Drug Manufacturers - General": ["Pharmaceuticals", "Biotechnology"],
    "Drug Manufacturers - Specialty & Generic": ["Pharmaceuticals"],
    "Electrical Equipment & Parts": [
        "Industrial Machinery & Supplies & Components",
        "Electrical Components & Equipment",
    ],
    "Electronic Components": [
        "Electronic Components", "Electronic Manufacturing Services",
    ],
    "Electronic Gaming & Multimedia": ["Interactive Home Entertainment"],
    "Engineering & Construction": ["Construction & Engineering"],
    "Entertainment": [
        "Movies & Entertainment", "Broadcasting", "Publishing",
    ],
    "Farm & Heavy Construction Machinery": [
        "Construction Machinery & Heavy Transportation Equipment",
        "Agricultural & Farm Machinery",
    ],
    "Farm Products": [
        "Agricultural Products & Services", "Packaged Foods & Meats",
    ],
    "Financial Data & Stock Exchanges": ["Financial Exchanges & Data"],
    "Food Distribution": ["Food Distributors"],
    "Footwear & Accessories": [
        "Footwear", "Apparel, Accessories & Luxury Goods",
    ],
    "Gold": ["Gold"],
    "Grocery Stores": ["Food Retail"],
    "Healthcare Plans": ["Managed Health Care", "Health Care Services"],
    "Home Improvement Retail": ["Home Improvement Retail"],
    "Household & Personal Products": [
        "Household Products", "Personal Care Products",
    ],
    "Industrial Distribution": [
        "Trading Companies & Distributors", "Distributors",
        "Industrial Machinery & Supplies & Components",
    ],
    "Information Technology Services": [
        "IT Consulting & Other Services",
        "Transaction & Payment Processing Services",
        "Data Processing & Outsourced Services",
        "Technology Distributors", "Diversified Support Services",
    ],
    "Insurance - Diversified": [
        "Property & Casualty Insurance", "Multi-line Insurance",
        "Multi-Sector Holdings",
    ],
    "Insurance - Life": ["Life & Health Insurance"],
    "Insurance - Property & Casualty": [
        "Property & Casualty Insurance", "Multi-line Insurance",
    ],
    "Insurance - Reinsurance": ["Reinsurance"],
    "Insurance Brokers": ["Insurance Brokers"],
    "Integrated Freight & Logistics": [
        "Air Freight & Logistics", "Cargo Ground Transportation",
    ],
    "Internet Content & Information": ["Interactive Media & Services"],
    "Internet Retail": [
        "Broadline Retail", "Specialized Consumer Services",
    ],
    "Leisure": ["Leisure Products"],
    "Lodging": ["Hotels, Resorts & Cruise Lines"],
    "Luxury Goods": ["Apparel, Accessories & Luxury Goods"],
    "Medical Care Facilities": [
        "Health Care Facilities", "Health Care Services",
    ],
    "Medical Devices": ["Health Care Equipment"],
    "Medical Distribution": ["Health Care Distributors"],
    "Medical Instruments & Supplies": [
        "Health Care Equipment", "Health Care Supplies",
        "Health Care Technology",
    ],
    "Oil & Gas E&P": ["Oil & Gas Exploration & Production"],
    "Oil & Gas Equipment & Services": ["Oil & Gas Equipment & Services"],
    "Oil & Gas Integrated": ["Integrated Oil & Gas"],
    "Oil & Gas Midstream": ["Oil & Gas Storage & Transportation"],
    "Oil & Gas Refining & Marketing": ["Oil & Gas Refining & Marketing"],
    "Packaged Foods": ["Packaged Foods & Meats"],
    "Packaging & Containers": [
        "Paper & Plastic Packaging Products & Materials",
        "Metal, Glass & Plastic Containers",
    ],
    "Personal Services": ["Environmental & Facilities Services"],
    "Pollution & Treatment Controls": [
        "Environmental & Facilities Services",
    ],
    "REIT - Diversified": ["Hotel & Resort REITs"],
    "REIT - Healthcare Facilities": ["Health Care REITs"],
    "REIT - Hotel & Motel": ["Hotel & Resort REITs"],
    "REIT - Industrial": ["Self-Storage REITs", "Industrial REITs"],
    "REIT - Office": ["Office REITs"],
    "REIT - Residential": [
        "Multi-Family Residential REITs",
        "Single-Family Residential REITs",
    ],
    "REIT - Retail": ["Retail REITs"],
    "REIT - Specialty": [
        "Telecom Tower REITs", "Data Center REITs",
        "Other Specialized REITs", "Timber REITs",
    ],
    "Railroads": [
        "Rail Transportation",
        "Construction Machinery & Heavy Transportation Equipment",
    ],
    "Real Estate Services": ["Real Estate Services"],
    "Rental & Leasing Services": ["Trading Companies & Distributors"],
    "Residential Construction": ["Homebuilding"],
    "Resorts & Casinos": ["Casinos & Gaming"],
    "Restaurants": ["Restaurants"],
    "Scientific & Technical Instruments": [
        "Electronic Equipment & Instruments", "Electronic Components",
        "Industrial Machinery & Supplies & Components",
        "Consumer Electronics",
    ],
    "Security & Protection Services": ["Building Products"],
    "Semiconductor Equipment & Materials": [
        "Semiconductor Materials & Equipment",
    ],
    "Semiconductors": ["Semiconductors"],
    "Software - Application": [
        "Application Software",
        "Human Resource & Employment Services",
        "Electronic Equipment & Instruments",
        "Systems Software",
        "Passenger Ground Transportation",
    ],
    "Software - Infrastructure": [
        "Systems Software", "Internet Services & Infrastructure",
        "Application Software",
        "Transaction & Payment Processing Services",
        "Communications Equipment",
        "Technology Hardware, Storage & Peripherals",
    ],
    "Solar": ["Semiconductors"],
    "Specialty Business Services": [
        "Diversified Support Services",
        "Transaction & Payment Processing Services",
    ],
    "Specialty Chemicals": ["Specialty Chemicals", "Industrial Gases"],
    "Specialty Industrial Machinery": [
        "Industrial Machinery & Supplies & Components",
        "Electrical Components & Equipment", "Building Products",
        "Construction Machinery & Heavy Transportation Equipment",
        "Heavy Electrical Equipment",
    ],
    "Specialty Retail": [
        "Other Specialty Retail", "Computer & Electronics Retail",
        "Homefurnishing Retail",
    ],
    "Steel": ["Steel"],
    "Telecom Services": [
        "Integrated Telecommunication Services", "Cable & Satellite",
        "Wireless Telecommunication Services",
    ],
    "Tobacco": ["Tobacco"],
    "Tools & Accessories": [
        "Industrial Machinery & Supplies & Components",
    ],
    "Travel Services": ["Hotels, Resorts & Cruise Lines"],
    "Trucking": ["Cargo Ground Transportation"],
    "Utilities - Diversified": [
        "Independent Power Producers & Energy Traders", "Multi-Utilities",
    ],
    "Utilities - Independent Power Producers": [
        "Electric Utilities",
        "Independent Power Producers & Energy Traders",
    ],
    "Utilities - Regulated Electric": [
        "Electric Utilities", "Multi-Utilities",
    ],
    "Utilities - Regulated Gas": ["Gas Utilities", "Multi-Utilities"],
    "Utilities - Regulated Water": ["Water Utilities"],
    "Waste Management": ["Environmental & Facilities Services"],
}
