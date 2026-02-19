import streamlit as st
import numpy as np
import pandas as pd
import base64
from joblib import load
from pathlib import Path
import requests


#########################################################################################################
st.set_page_config(layout="wide", page_icon="🍁", page_title="EstimAI : Property Price Estimator in British Columbia - Canada")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem;
        }
        
        .element-container:first-child {
            margin-top: -1rem;
        }
        
        header[data-testid="stHeader"] {
            display: none;
        }
        
        [data-testid="stAppViewContainer"] > .main {
            padding-top: 0rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        html, body, [data-testid="stApp"] {
            background-color: #0e1117;
            color: #e6e6e6;
        }

        .block-container {
            background-color: #0E111C;
        }

        h1, h2, h3, h4 {
            color: #ffffff;
        }
        

    </style>
    """,
    unsafe_allow_html=True
)


BASE_DIR = Path(__file__).resolve().parent

def get_base64_image(path):
    image_path = BASE_DIR / path
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

banner = get_base64_image("sunny.jpg")
logo = get_base64_image("estimlogo.png")

st.markdown(
    f"""
    <div style="text-align: center; padding: 10px 0;">
        <img src="data:image/png;base64,{logo}" alt="Logo" style="width: 200px; cursor: pointer;">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <style>
    .header {{
        position: relative;
        width: 100%;
        height: 500px;
        background-image: url("data:image/jpeg;base64,{banner}");
        background-size: cover;
        background-position: center;
        border-radius: 12px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 30px;
        margin-top: 10px;
    }}

    .header-overlay {{
        position: absolute;
        inset: 0;
        background: linear-gradient(
            rgba(0,0,0,0.45),
            rgba(0,0,0,0.15)
        );
        border-radius: 12px;
    }}

    .header-title {{
        position: absolute;
        bottom: 240px;
        left: 30px;
        color: white;
        font-family: 'Playfair Display', 'Serif';
        font-size: 80px;
        font-weight: 500;
        text-shadow: 2px 2px 12px rgba(0,0,0,0.6);
        z-index: 2;
        line-height: 1.1;
    }}

    .header-subtitle {{
        position: absolute;
        bottom: 160px;
        left: 40px;
        font-family: 'Sans-Serif';
        color: #f0f0f0;
        font-size: 18px;
        z-index: 2;
        line-height: 1.5;
    }}

    @media (max-width: 768px) {{
        .header {{
            height: 400px;
        }}
        
        .header-title {{
            font-size: 48px;
            bottom: 160px;
            left: 20px;
            right: 20px;
        }}
        
        .header-subtitle {{
            font-size: 14px;
            bottom: 100px;
            left: 20px;
            right: 20px;
        }}
    }}

    @media (max-width: 480px) {{
        .header {{
            height: 310px;
        }}
        
        .header-title {{
            font-size: 36px;
            bottom: 150px;
            left: 15px;
            right: 15px;
        }}
        
        .header-subtitle {{
            font-size: 13px;
            bottom: 100px;
            left: 15px;
            right: 15px;
        }}
    }}
    </style>

    <div class="header">
        <div class="header-overlay"></div>
        <div class="header-title">EstimAI</div>
        <div class="header-subtitle">
            Estimate your property's market value in British Columbia<br/>
            using AI models trained on BC real estate data.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


#################### Location #####################


import requests

@st.cache_data(ttl=3600)
def geocode_geoapify(address):
    """
    Geocoding with Geoapify API
    It returns (latitude, longitude, country, province) or (None, None, None, None) if an error occured
    """
    
    api_key = st.secrets.get("GEOAPIFY_API_KEY", "")
    
    if not api_key:
        st.error("Geoapify API key not configured") # Test if the api key is configured
        return None, None, None, None
    
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": address,
        "filter": "countrycode:ca",  # Restriction area to Canada
        "apiKey": api_key,
        "limit": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("features") and len(data["features"]) > 0:
            feature = data["features"][0]
            coords = feature["geometry"]["coordinates"]
            props = feature["properties"]
            
            latitude = coords[1]
            longitude = coords[0]
            country = props.get("country", "")
            province = props.get("state", "")
            
            return latitude, longitude, country, province
        
        return None, None, None, None
        
    except requests.exceptions.Timeout:
        st.error("Request timeout. Please try again.")
        return None, None, None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error. Please check your internet connection.")
        return None, None, None, None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None, None, None, None


st.title("📍Location")


col1, col2 = st.columns([0.70, 0.30], vertical_alignment="bottom")

with col1: 
    address = st.text_input("Enter your address : ", placeholder="Type your address here")

with col2: 
    search = st.button("Search", icon=":material/search:")


# Latitude and longitude are in the session state dictionary

if "address_valid" not in st.session_state:
    st.session_state.address_valid = False

if "latitude" not in st.session_state:
    st.session_state.latitude = None

if "longitude" not in st.session_state:
    st.session_state.longitude = None

if search:
    st.session_state.address_valid = False
    st.session_state.longitude = None
    st.session_state.latitude = None
    
    if not address: 
        st.warning("Please enter an address.")
        st.session_state.address_valid = False
    else:
        with st.spinner("🔍 Searching address..."):
            latitude, longitude, country, province = geocode_geoapify(address)
            
            if latitude is None:
                st.error("Address not found. Please enter a valid address.")
                st.session_state.address_valid = False
            else:
                if not country or not province:
                    st.error("Incomplete address. Please enter a full address in British Columbia.")
                    st.session_state.address_valid = False
                
                elif country != "Canada":
                    st.error("The address is not in Canada.")
                    st.session_state.address_valid = False
                
                elif province != "British Columbia":
                    st.error("The address is not in British Columbia.")
                    st.session_state.address_valid = False
                
                else:
                    st.session_state.longitude = longitude
                    st.session_state.latitude = latitude
                    st.session_state.address_valid = True

if st.session_state.address_valid: 
    st.success("Your address has been found", icon="✅")
    df_map = pd.DataFrame({"LAT": [st.session_state.latitude], "LON": [st.session_state.longitude]})
    st.map(df_map, zoom=5, size=3, color="#EE4B2B")


#################### Property type #####################

st.space(size="small")
st.title("🏠 Property type")


if "property_type" not in st.session_state:
    st.session_state.property_type = None
    
st.session_state.property_type = st.selectbox(
    "Select the type of the property :",
    index=None,
    placeholder="Select a property type",
    options=("Condo", "Townhome", "Condo/Townhome", "Duplex", "Manufactured House", "Single Family", "Multi Family"),
    
)


#################### Surface & Acreage #####################

st.space(size="small")
st.title("📐 Square footage & Acreage")
square_footage = st.number_input("Enter the square footage of the property : ", min_value = 96, value=96)

answer = st.radio(
    "Do you know the acreage of the property ?",
    horizontal=True,
    index = 0,
    options = ["Yes", "No"]
)

missing_acreage = 0
acreage = 0
if answer != "No":
    acreage = st.number_input("Enter the Acreage of the property :", min_value = 0.01, step=0.1, value=0.15)
else :
    missing_acreage = 1




#################### Property Tax #####################
st.space(size="small")
st.title("🧾 Property Tax")

answer2 = st.radio(
    "Do you know the annual property tax amount ?",
    horizontal=True,
    index = 0,
    options = ["Yes", "No"]
)

missing_property_tax = 0
property_tax = 0
if answer2 != "No":
    property_tax = st.number_input("Enter the annual tax amount ($) :", min_value = 0, value=2500, step = 50)
else:
    missing_property_tax = 1




#################### Beds & baths & Heating distrib & Energy #####################

st.space(size="small")
st.title("🚪 Interior & Features")

col1, col2  = st.columns([0.5, 0.5], vertical_alignment="bottom")
with col1:
    nb_beds = st.number_input("Enter the number of bedrooms :", min_value = 1, value="min")
with col2:
    nb_baths = st.number_input("Enter the number of bathrooms :", min_value = 1, value="min")


st.space(size="small")

# Heatin distrib. system

has_heating = 1
missing_distrib = 0
heating_distrib = []
missing_energy = 0
energy_types = []


answer4 = "No"
answer5 = "No"

answer3 = st.radio(
    "Do you have one or more Heating Distribution System ?",
    horizontal=True,
    index = 0,
    options = ["Yes", "No"]
)

# If the answer3 != No, it means that the property has a distrib system. And answer3 == yes means the opposite.
if answer3 != "No":
    
    answer4 = st.radio(
        "Do you know the type of your Heating Distribution System(s) ?",
        horizontal=True,
        index = 0,
        options = ["Yes", "No"]
    )

    if answer4 != "No":
        heating_distrib = st.multiselect(
            "Select all your Heating distribution systems",
            ["Forced Air", "Baseboard", "Radiant", "Hydronic", "Heat Pump", "Overhead", "Space heater"]
        )

    else : 
        # if answer4 == yes, it means that the user doesn't know the heating distrib type of his property and can continue
        missing_distrib = 1

    
    answer5 = st.radio(
        "Do you know the energy source used by the heating system ?",
        horizontal=True,
        index = 0,
        options = ["Yes", "No"]
    )
    
    if answer5 != "No":
        energy_types = st.multiselect(
                "Select all your energy sources used by the heating system(s)",
                ["Electric", "Geothermal", "Natural Gas", "Oil", "Propane", "Biomass", "Solar"]
        )
    else : 
        missing_energy = 1
    
else : 
    has_heating = 0






#################### Parking #####################

st.space("small")
st.title("🅿️ Parking")

missing_parking = 0
parking_closed = 1  # If it's a garage or a parking box
multi_car = 0
premium_parking = 0


answer6 = st.radio(
    "Do you know if the property has one or more parking spaces ?",
    horizontal=True,
    index = 0,
    options = ["Yes", "No"]
)

if answer6 != "No":

    # Number of parking space
    nb_parking = st.number_input("Enter the number of parking spaces :", min_value = 1, value="min")
    if nb_parking > 1 :
        multi_car = 1

    # Closed parking ?
    answer7 = st.radio(
        "Do you have a closed parking space ?",
        horizontal=True,
        index = 0,
        options = ["Yes", "No"]
    )

    if answer7 != "Yes":
        parking_closed = 0

    other_infos = st.pills(
        "Select extra features if needed :",
        selection_mode = "multi",
        options = ["Heated Garage", "Oversized Garage", "Recreational Vehicule Access"],
        )

    if len(other_infos) > 0:
        premium_parking = 1
else : 
    missing_parking = 1



##############################################################################
# Checking if every mandatory inputs are filled with a value #################
##############################################################################

#################### Prediction Button #####################

result_placeholder = st.empty()

st.space("medium")
_, _, mid, _, _ = st.columns(5)
with mid:
    get_pred = st.button("**Get a Price estimate ↓**", icon=":material/sell:", type="primary", width=300)

st.space("xsmall")

st.session_state.unfilled = []

if get_pred:
    with result_placeholder.container(): 
        if (not address) & ("Location" not in st.session_state.unfilled):
            st.session_state.unfilled.append("Location")
    
        if (st.session_state.property_type == None) & ("Property type" not in st.session_state.unfilled):
            st.session_state.unfilled.append("Property type")
            
        if (answer4 == "Yes") & (len(heating_distrib) == 0) & ("Heating Distribution System" not in st.session_state.unfilled):
            st.session_state.unfilled.append("Heating Distribution System")
    
        if (answer5 == "Yes") & (len(energy_types) == 0) & ("Energy source" not in st.session_state.unfilled):
            st.session_state.unfilled.append("Energy source")
    
        
        if len(st.session_state.unfilled) > 0:
            # display the unfilled fields
            st.space("small")
            st.warning(
                "Please complete the following fields : \n" + "\n".join([f"- {unfilled}" for  unfilled in st.session_state.unfilled])
            )
        
        else :  
    
            ####################### Filling the Dataframe X_pred with all the user's infos ########################
            ### The user's features that we'll give to our trained model to get a price prediction
            X_pred = pd.DataFrame()
            
            dict_features = {
                'latitude' : st.session_state.latitude, 
                'longitude': st.session_state.longitude,      
                'property-beds' : nb_beds,
                'property-baths' : nb_baths,
                'Acreage' : acreage,
                'Property Tax' : property_tax,
                'Square Footage' : square_footage,
                'Missing Acreage' : missing_acreage,
                'Missing Property Tax' : missing_property_tax,
                'Missing Parking' : missing_parking,
                "parking_closed" : parking_closed,
                "multi_car" : multi_car,
                "premium_parking" : premium_parking,
                'has_heating' : has_heating,
                'missing_energy' : missing_energy,         
                'missing_distrib' : missing_distrib,
                
                
            }
    
            properties_dict = {
                'Condo':'Property Type_Condo',
                'Condo/Townhome' : 'Property Type_Condo/Townhome',
                'Duplex' : 'Property Type_Duplex',
                'Manufactured House' : 'Property Type_Manufactured Home',
                'Multi Family' : 'Property Type_MultiFamily',
                'Single Family' : 'Property Type_Single Family',
                'Townhome' : 'Property Type_Townhome'
            }
    
            distrib_dict = {
                "Baseboard" : "baseboard", 
                "Forced Air" : "forced_air", 
                "Radiant" : "radiant", 
                "Hydronic" : "hydronic", 
                "Heat Pump" : "heat_pump", 
                "Overhead" : "overhead", 
                "Space heater" : "space_heater"
            }
    
            energy_dict = {
                "Electric" : "electric", 
                "Geothermal" : "geothermal",
                "Natural Gas" : "natural_gas", 
                "Oil" : "oil", 
                "Propane" : "propane", 
                "Biomass" : "biomass", 
                "Solar" : "solar"
            }
    
            #### This order counts ####
    
            for key, val in dict_features.items():
                X_pred[key] = [val]
    
            
            # Initialization for energy_type
            for key, val in energy_dict.items():
                X_pred[val] = [0]
                if key in energy_types:
                    X_pred[val] = [1]
    
            # Initialization for distrib_type
            for key, val in distrib_dict.items():
                X_pred[val] = [0]
                if key in heating_distrib:
                    X_pred[val] = [1]
                    
            # Initialization for property_type
            for key, val in properties_dict.items():
                X_pred[val] = [0]
                if key == st.session_state.property_type:
                    X_pred[val] = [1]
                    
    
            BASE_DIR_MODEL = Path(__file__).resolve().parent.parent
    
            ARTIFACTS_DIR = BASE_DIR_MODEL / "artifacts"
            model = load(ARTIFACTS_DIR / "gdb_final_model.pkl")
            price = model.predict(X_pred)
            price = np.expm1(price)[0]
            price_ranges = load(ARTIFACTS_DIR / "gdb_mape_dict.pkl")
    
            for interval, percentage in price_ranges.items():
                min_interv, max_interv = interval
                if (min_interv < price) & (price < max_interv):
                    st.session_state.min_price = price * (1 - percentage)
                    st.session_state.max_price = price * (1 + percentage)
                    
    
            
            st.session_state.pred_price = price
            
            if "pred_price" in st.session_state:
                price = st.session_state.pred_price
    
                if ("min_price" in st.session_state) & ("max_price" in st.session_state):
                    min_price = st.session_state.min_price
                    max_price = st.session_state.max_price
    
                    st.markdown(f"""
                        <div class="price-card">
                            <div class="price-title">Estimated Property Value</div>
                            <div class="price-value">${price:,.0f}</div>
                            <div class="range-container">
                                <div class="range-box">
                                    <div class="range-label">Low estimate</div>
                                    <div class="range-value">${min_price:,.0f}</div>
                                </div>
                                <div class="range-box">
                                    <div class="range-label">High estimate</div>
                                    <div class="range-value">${max_price:,.0f}</div>
                                </div>
                            </div>
                            <div class="price-sub">
    This estimate is generated by an AI model using historical
    sales data. </br>
    It is provided for informational purposes only. It is not a professional appraisal and actual prices may vary.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    
                else : 
                    st.markdown(f"""
                        <div class="price-card">
                            <div class="price-title">Estimated Property Value</div>
                            <div class="price-value">${price:,.0f}</div>
                            <div class="price-sub">
                                Based on British Columbia market trends
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    
                    
            st.markdown("""
                <style>
                .price-card {
                    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                    border-radius: 16px;
                    padding: 40px;
                    text-align: center;
                    color: white;
                    box-shadow: 0px 15px 40px rgba(0,0,0,0.35);
                    margin-top: 40px;
                }
                
                .price-title {
                    font-size: 22px;
                    font-weight: 500;
                    opacity: 0.85;
                }
                
                .price-value {
                    font-size: 45px;
                    font-weight: 800;
                    margin: 12px 0 20px 0;
                    letter-spacing: 1px;
                }
                
                .range-container {
                    display: flex;
                    justify-content: space-between;
                    margin-top: 10px;
                }
                
                .range-box {
                    width: 45%;
                    background: rgba(255,255,255,0.12);
                    border-radius: 12px;
                    padding: 14px;
                }
                
                .range-label {
                    font-size: 13px;
                    opacity: 0.75;
                }
                
                .range-value {
                    font-size: 20px;
                    font-weight: 600;
                    margin-top: 4px;
                }
                
                .price-sub {
                    font-size: 15px;
                    opacity: 0.75;
                    margin-top: 20px;
                }
                </style>
                """, unsafe_allow_html=True)
                
        

    