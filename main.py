from flask import Flask, request, jsonify, send_file
import mysql.connector
from flask_cors import CORS
import math
from fpdf import FPDF

app = Flask(__name__)
CORS(app)  # Allows frontend access to API

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'michaelkhuri@gmail.com'
EMAIL_PASSWORD = 'nkfv bdut pjud kenv'

def send_email(to_emails, subject, body, filename):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    with open(filename, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_emails, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# MySQL Database Configuration
# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "1234",
#     "database": "Local_Pump_Info"
# }

db_config = {
    "host": "132.148.249.113",
    "user": "quote",
    "password": ".2zKuI]4#n@V",
    "database": "Quotes_Database_3_13_25"
}

def get_flange_size_id(psi):
    if psi < 290:
        return 150
    elif 290 <= psi < 750:
        return 300
    elif 750 <= psi < 1000:
        return 400
    elif 1000 <= psi < 1500:
        return 600
    elif 1500 <= psi <= 2250:
        return 900
    else:
        return None  # Handle cases where PSI is out of range

ball_size_mapping = {
    "1/8\"": "1",
    "3/16\"": "2",
    "1/4\"": "3",
    "3/8\"": "4",
    "1/2\"": "5",
    "5/8\"": "6",
    "3/4\"": "7",
    "7/8\"": "8",
    "1\"": "9",
    "1-1/4\"": "A",
    "1-1/2\"": "B",
    "1-3/4\"": "C",
    "2\"": "D",
    "2-1/4\"": "E",
    "2-1/2\"": "F",
    "3\"": "G",
    "3-1/2\"": "H",
    "1/2\" Double Ball": "V",
    "7/8\" Double Ball": "W",
    "1/2\" Suction and 3/8\" Discharge": "X",
    "3/8\" Double Ball": "Z"
}

# Flange Pricing Tables
flange_pricing_tables = {
    150: {
        "1/2\"": {"316SS": 24.75, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 7.56, "PVDF": "C/F"},
        "3/4\"": {"316SS": 26.75, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 8.86, "PVDF": "C/F"},
        "1\"": {"316SS": 29.5, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 9.7, "PVDF": "C/F"},
        "1-1/4\"": {"316SS": 40.55, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 12.16, "PVDF": "C/F"},
        "1-1/2\"": {"316SS": 42.8, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 13.27, "PVDF": "C/F"},
        "2\"": {"316SS": 53.25, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 13.57, "PVDF": "C/F"},
        "2-1/2\"": {"316SS": 83.65, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 26.41, "PVDF": "C/F"},
        "3\"": {"316SS": 69.7, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 27.18, "PVDF": "C/F"},
        "4\"": {"316SS": 114, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 51.07, "PVDF": "C/F"}
    },
    300: {
        "1/2\"": {"316SS": 33.15, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3/4\"": {"316SS": 37.1, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1\"": {"316SS": 39.95, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/4\"": {"316SS": 58.95, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/2\"": {"316SS": 62.75, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2\"": {"316SS": 72.25, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2-1/2\"": {"316SS": 135, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3\"": {"316SS": 138, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "4\"": {"316SS": 225, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0}
    },
    400: {
        "1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3/4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0}
    },
    600: {
        "1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3/4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0}
    },
    900: {
        "1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3/4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0}
    }
}

# Flange Adaptor Pricing Tables
flange_adaptor_pricing_tables = {
    "psi_lt_1000": {
        "1/2\"": {"316SS": 8.16, "Alloy 20": 62.74, "Hast. C": "C/F", "PVC": 1.2, "PVDF": "C/F"},
        "3/4\"": {"316SS": 11.88, "Alloy 20": 84.51, "Hast. C": "C/F", "PVC": 1.53, "PVDF": "C/F"},
        "1\"": {"316SS": 14.85, "Alloy 20": 91.87, "Hast. C": "C/F", "PVC": 2.47, "PVDF": "C/F"},
        "1-1/4\"": {"316SS": 25.4, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 3.29, "PVDF": "C/F"},
        "1-1/2\"": {"316SS": 33.89, "Alloy 20": 123.5, "Hast. C": "C/F", "PVC": 3.53, "PVDF": "C/F"},
        "2\"": {"316SS": 42.84, "Alloy 20": 167.19, "Hast. C": "C/F", "PVC": 4.27, "PVDF": "C/F"},
        "2-1/2\"": {"316SS": 101.55, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 9.83, "PVDF": "C/F"},
        "3\"": {"316SS": 129.27, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 11.21, "PVDF": "C/F"},
        "4\"": {"316SS": 168.20, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 14.96, "PVDF": "C/F"}
    },
    "psi_gt_1000": {
        "1/2\"": {"316SS": 24.31, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "3/4\"": {"316SS": 36.19, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1\"": {"316SS": 61.56, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/4\"": {"316SS": 84.74, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "1-1/2\"": {"316SS": 125.87, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2\"": {"316SS": 175.24, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 0, "PVDF": 0},
        "2-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": "C/F", "PVDF": "C/F"},
        "3\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": "C/F", "PVDF": "C/F"},
        "4\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": "C/F", "PVDF": "C/F"}
    },
    "all": {
        "1/2\"": {"316SS": 9.53, "Alloy 20": 40.23, "Hast. C": "C/F", "PVC": 1, "PVDF": "C/F"},
        "3/4\"": {"316SS": 12, "Alloy 20": 47.58, "Hast. C": "C/F", "PVC": 1, "PVDF": "C/F"},
        "1\"": {"316SS": 18.5, "Alloy 20": 82.74, "Hast. C": "C/F", "PVC": 1.5, "PVDF": "C/F"},
        "1-1/4\"": {"316SS": 31.56, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 2.2, "PVDF": "C/F"},
        "1-1/2\"": {"316SS": 35.53, "Alloy 20": 99.55, "Hast. C": "C/F", "PVC": 2.5, "PVDF": "C/F"},
        "2\"": {"316SS": 56.26, "Alloy 20": 189.91, "Hast. C": "C/F", "PVC": 3.5, "PVDF": "C/F"},
        "2-1/2\"": {"316SS": "C/F", "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 5.5, "PVDF": "C/F"},
        "3\"": {"316SS": 109.26, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 6.5, "PVDF": "C/F"},
        "4\"": {"316SS": 230, "Alloy 20": "C/F", "Hast. C": "C/F", "PVC": 9.5, "PVDF": "C/F"}
    }
}

def calculate_flange_adaptor_price(psi, suction_flange_size, discharge_flange_size, liquid_end_material, simplex_duplex):
    # Determine which table to use based on PSI
    if psi < 1000:
        table = flange_adaptor_pricing_tables["psi_lt_1000"]
    else:
        table = flange_adaptor_pricing_tables["psi_gt_1000"]

    # Get the prices for suction and discharge flanges from the first table
    suction_price = table.get(suction_flange_size, {}).get(liquid_end_material, 0)
    discharge_price = table.get(discharge_flange_size, {}).get(liquid_end_material, 0)

    # Get the prices for suction and discharge flanges from the "all" table
    suction_price_all = flange_adaptor_pricing_tables["all"].get(suction_flange_size, {}).get(liquid_end_material, 0)
    discharge_price_all = flange_adaptor_pricing_tables["all"].get(discharge_flange_size, {}).get(liquid_end_material, 0)

    # Handle "C/F" and "0" values
    if suction_price == "C/F" or discharge_price == "C/F" or suction_price_all == "C/F" or discharge_price_all == "C/F":
        return {"total_flange_adaptor_price": "C/F (Flange Adaptor)"}  # Return C/F message
    if suction_price == 0 or discharge_price == 0 or suction_price_all == 0 or discharge_price_all == 0:
        return {"total_flange_adaptor_price": "Unavailable (Flange Adaptor)"}  # Return Unavailable message

    # Calculate total flange adaptor price
    total_price = (suction_price + discharge_price + suction_price_all + discharge_price_all) * (5 if simplex_duplex.lower() == "simplex" else 10)
    return {"total_flange_adaptor_price": total_price}

def get_flange_price(flange_size_id, flange_size, liquid_end_material):
    if flange_size_id not in flange_pricing_tables:
        return None  # Invalid Flange Size ID

    if flange_size not in flange_pricing_tables[flange_size_id]:
        return None  # Invalid Flange Size

    price = flange_pricing_tables[flange_size_id][flange_size][liquid_end_material]
    return price

def calculate_flange_price(psi, suction_flange_size, discharge_flange_size, liquid_end_material):
    # Get the flange size ID based on PSI
    flange_size_id = get_flange_size_id(psi)
    if flange_size_id is None:
        return {"error": "Invalid PSI value for flange size calculation"}

    # Validate suction and discharge flange sizes
    if suction_flange_size not in flange_pricing_tables[flange_size_id]:
        return {"error": f"Invalid suction flange size: {suction_flange_size}"}
    if discharge_flange_size not in flange_pricing_tables[flange_size_id]:
        return {"error": f"Invalid discharge flange size: {discharge_flange_size}"}

    # Get the prices for suction and discharge flanges
    suction_price = get_flange_price(flange_size_id, suction_flange_size, liquid_end_material)
    discharge_price = get_flange_price(flange_size_id, discharge_flange_size, liquid_end_material)

    # Handle "C/F" and "0" values
    if suction_price == "C/F" or discharge_price == "C/F":
        return {"total_flange_price": "C/F (Flange)"}  # Return C/F message
    if suction_price == 0 or discharge_price == 0:
        return {"total_flange_price": "Unavailable (Flange)"}  # Return Unavailable message

    # Calculate total flange price
    total_price = (suction_price * 1.6 + discharge_price * 1.6) * 3
    return {"total_flange_price": total_price}

def replace_last_letter(model, ball_size):
    """
    Replace the last letter of the model name based on the ball size.
    Skip if ball_size is "Standard".
    """
    if ball_size.lower() == "standard":
        return model  # Do not replace if ball_size is "Standard"

    # Get the replacement letter from the mapping
    replacement = ball_size_mapping.get(ball_size, "")

    if replacement:
        # Replace the last letter of the model name
        model = model[:-1] + replacement

    return model

def replace_model_letters(model, liquid_end_material, balls_type):
    """
    Replace the two letters after the dash in the model name based on liquid end material and ball type.
    """
    # Define the replacement table
    replacement_table = {
        "316SS": {"Std.": "04", "Ceramic": "74", "Tungsten": "84"},
        "Alloy 20": {"Std.": "05", "Ceramic": "75", "Tungsten": "85"},
        "Hast. C": {"Std.": "06", "Ceramic": "76", "Tungsten": "86"},
        "PVC": {"Std.": "08", "Ceramic": "08", "Tungsten": "88"},
        "PVDF": {"Std.": "0A", "Ceramic": "0A", "Tungsten": "8A"},
    }

    # Get the replacement letters
    replacement = replacement_table.get(liquid_end_material, {}).get(balls_type, "00")

    # Replace the two letters after the dash
    if "-" in model:
        parts = model.split("-")
        if len(parts) > 1:
            # Replace the two letters after the dash
            parts[1] = replacement + parts[1][2:]  # Keep the rest of the string after the two letters
            model = "-".join(parts)

    return model

def calculate_suction_lift_price(series, liquid_end_material, suction_lift):
    """
    Calculate the suction lift price based on the series and liquid end material.
    Only add the price if suction_lift is "yes".
    """
    if suction_lift.lower() != "yes":
        return 0  # Do not add suction lift price if customer selects "no"

    if series == "Series 1000":
        if liquid_end_material in ["316SS", "Alloy 20", "Hast. C", "PVC", "PVDF"]:
            return 844  # All materials in Series 1000 add $844
    elif series == "Series 2000":
        if liquid_end_material == "316SS":
            return "C/F"
        elif liquid_end_material == "Alloy 20":
            return 2860
        elif liquid_end_material in ["Hast. C", "PVC", "PVDF"]:
            return "C/F"
    return 0

def find_best_pump(gph=None, lph=None, psi=None, bar=None, hz=None, 
                   simplex_duplex=None, want_motor=None, motor_type=None, 
                   motor_power=None, spm=None, diaphragm=None, liquid_end_material=None, 
                   leak_detection=None, phase=None, degassing=None, flange=None, 
                   balls_type=None, suction_lift=None, ball_size=None, suction_flange_size=None, 
                   discharge_flange_size=None, food_graded_oil=None):
    # Ensure either GPH or LPH is provided
    if gph is None and lph is None:
        return {"error": "Either GPH or LPH is required. Please provide one."}

    # Ensure either PSI or Bar is provided
    if psi is None and bar is None:
        return {"error": "Either PSI or Bar is required. Please provide one."}

    # Ensure Hz is required and valid
    if hz not in [50, 60]:
        return {"error": "Hz is required and must be either 50 or 60."}

    # Ensure Simplex/Duplex is required
    if not simplex_duplex:
        return {"error": "Simplex/Duplex is required. Please provide either 'Simplex', 'Duplex', or 'Both'."}

    # Ensure want_motor is provided and is either "yes" or "no"
    if want_motor.lower() not in ["yes", "no"]:
        return {"error": "Want motor is required and must be either 'yes' or 'no'."}

    # If motor is required, ensure motor_type (TEFC/XPFC) and motor_power (AC/DC) are provided
    if want_motor == "yes" and (motor_type is None or motor_power is None):
        return {"error": "Motor type (TEFC/XPFC) and motor power (AC/DC) must be provided when selecting a motor."}

    # Ensure SPM is provided and is one of the valid options
    valid_spm_options = [29, 44, 58, 88, 97, 117, 140, 170, 191]
    if spm is None or spm not in valid_spm_options:
        return {"error": "SPM is required and must be one of the following: 29, 44, 58, 88, 97, 117, 140, 170, 191."}

    # Ensure diaphragm is provided and is one of the valid options
    valid_diaphragm_options = ["ptfe", "viton", "hypalon", "epdm"]
    if diaphragm is None or diaphragm.lower() not in valid_diaphragm_options:
        return {"error": "Diaphragm is required and must be one of the following: PTFE, Viton, Hypalon, EPDM."}

    # Ensure liquid end material is provided and is one of the valid options
    valid_liquid_end_material = ["316SS", "Alloy 20", "Hast. C", "PVC", "PVDF"]
    if liquid_end_material is None or liquid_end_material not in valid_liquid_end_material:
        return {"error": "Liquid End Material is required and must be one of the following: 316SS, Alloy 20, Hast. C, PVC, PVDF."}

    # Ensure leak detection is provided and is one of the valid options
    valid_leak_detection_options = ["no", "conductive", "vacuum"]
    if leak_detection is None or leak_detection.lower() not in valid_leak_detection_options:
        return {"error": "Leak Detection is required and must be one of the following: No, Conductive, Vacuum."}

    # Ensure phase is provided and is one of the valid options
    valid_phase_options = ["1 Ph", "3 Ph"]
    if phase is None or phase not in valid_phase_options:
        return {"error": "Phase is required and must be one of the following: 1 Ph, 3 Ph."}

    # Ensure degassing is provided and is either "yes" or "no"
    if degassing.lower() not in ["yes", "no"]:
        return {"error": "Degassing is required and must be either 'yes' or 'no'."}

    # Ensure flange is provided and is either "yes" or "no"
    if flange.lower() not in ["yes", "no"]:
        return {"error": "Flange is required and must be either 'yes' or 'no'."}

    # Ensure balls type is provided and is one of the valid options
    valid_balls_type_options = ["Std.", "Tungsten", "Ceramic"]
    if balls_type is None or balls_type not in valid_balls_type_options:
        return {"error": "Balls Type is required and must be one of the following: Std., Tungsten, Ceramic."}

    # Ensure suction_lift is provided and is either "yes" or "no"
    if suction_lift.lower() not in ["yes", "no"]:
        return {"error": "Suction Lift is required and must be either 'yes' or 'no'."}

    # Ensure ball_size is provided and is one of the valid options
    if balls_type in ["Tungsten", "Ceramic"]:
        valid_ball_size_options = ["Standard", "1/4\"", "3/8\"", "1/2\"", "7/8\"", "1-1/4\"", "1-1/2\""]
    else:
        valid_ball_size_options = [
            "1/8\"", "3/16\"", "1/4\"", "3/8\"", "1/2\"", "5/8\"", "3/4\"", "7/8\"", 
            "1\"", "1-1/4\"", "1-1/2\"", "1-3/4\"", "2\"", "2-1/4\"", "2-1/2\"", 
            "3\"", "3-1/2\"", "1/2\" Double Ball", "7/8\" Double Ball", 
            "1/2\" Suction and 3/8\" Discharge", "3/8\" Double Ball", "Standard"
        ]

    # Normalize the ball_size input to handle cases like "2-1/4""
    if ball_size:
        ball_size = ball_size.replace("%26quot%3B", "\"")  # Replace URL-encoded quotes
        ball_size = ball_size.replace("&quot;", "\"")  # Replace HTML-encoded quotes
        ball_size = ball_size.strip()  # Remove any leading/trailing whitespace

    if ball_size is None or ball_size not in valid_ball_size_options:
        return {"error": f"Ball Size is required and must be one of the following: {', '.join(valid_ball_size_options)}."}

    # Ensure flange sizes are provided only if flange is "Yes"
    if flange and flange.lower() == "yes":
        print(f"Suction Flange Size: {suction_flange_size}")
        print(f"Discharge Flange Size: {discharge_flange_size}")
        if not suction_flange_size or not discharge_flange_size:
            return {"error": "Suction and Discharge flange sizes are required when selecting flanges."}
    else:
        # If flange is "No", ignore flange sizes
        suction_flange_size = None
        discharge_flange_size = None

    # Ensure Food_Graded_Oil is provided and is either "yes" or "no"
    if food_graded_oil.lower() not in ["yes", "no"]:
        return {"error": "Food Graded Oil is required and must be either 'yes' or 'no'."}

    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM pumps"
    cursor.execute(query)
    pumps = cursor.fetchall()
    cursor.close()
    conn.close()

    filtered_pumps = []
    for pump in pumps:
        # Ensure Liquid End Material matches
        if pump["Liquid_End_Material"] != liquid_end_material:
            continue

        # Select the correct column for GPH/LPH based on Hz
        if gph is not None:
            pump_flow = float(pump["GPH_60Hz"]) if hz == 60 else float(pump["GPH_50Hz"])
            input_flow = gph
        else:
            pump_flow = float(pump["LPH_60Hz"]) if hz == 60 else float(pump["LPH_50Hz"])
            input_flow = lph

        # Ensure input flow is always ≤ database values
        if pump_flow is None or input_flow > pump_flow:
            continue

        # Convert Bar to PSI if Bar is provided
        if bar is not None:
            psi = float(bar) * 14.5038  # 1 Bar = 14.5038 PSI

        # Select the correct column for PSI/Bar
        if psi is not None:
            max_pressure = float(pump["Max_Pressure_PSI"])
            high_pressure = float(pump["Max_Pressure_PSI_High_Pressure_Adder"])
        else:
            max_pressure = float(pump["Max_Pressure_Bar"])
            high_pressure = float(pump["Max_Pressure_Bar_High_Pressure_Adder"])

        use_hp = psi > max_pressure if psi is not None else bar > max_pressure
        if (psi is not None and psi > max_pressure and (not high_pressure or psi > high_pressure)) or \
           (bar is not None and bar > max_pressure and (not high_pressure or bar > high_pressure)):
            continue  # Skip if pressure exceeds even high-pressure max

        # Ensure pump's Max_SPM is <= user-input SPM
        max_spm = float(pump["Max_SPM"]) if pump["Max_SPM"] is not None else 0
        if max_spm > spm:
            continue  # Skip if pump's Max_SPM exceeds user-input SPM

        final_model = pump["Model"]

        if diaphragm.lower() == "ptfe":
            if leak_detection.lower() == "no":
                final_model = final_model[:3] + "T" + final_model[4:]
            elif leak_detection.lower() == "conductive":
                final_model = final_model[:3] + "W" + final_model[4:]
            elif leak_detection.lower() == "vacuum":
                final_model = final_model[:3] + "K" + final_model[4:]
        elif diaphragm.lower() == "viton":
            if leak_detection.lower() == "no":
                final_model = final_model[:3] + "B" + final_model[4:]
            elif leak_detection.lower() == "conductive":
                final_model = final_model[:3] + "R" + final_model[4:]
        elif diaphragm.lower() == "hypalon":
            if leak_detection.lower() == "no":
                final_model = final_model[:3] + "A" + final_model[4:]
            elif leak_detection.lower() == "conductive":
                final_model = final_model[:3] + "M" + final_model[4:]
        elif diaphragm.lower() == "epdm":
            if leak_detection.lower() == "no":
                final_model = final_model[:3] + "C" + final_model[4:]

        # Replace the last letter based on ball_size (if not "Standard")
        final_model = replace_last_letter(final_model, ball_size)
        
        if flange.lower() == "yes":
            final_model += "F"

        if degassing.lower() == "yes":
            final_model += "D"

        if use_hp:
            final_model += "HP"

        final_model = replace_model_letters(final_model, liquid_end_material, balls_type)

        # Handle Ball Size Pricing
        ball_size_price = 0
        ball_size_display = ball_size  # Default to the selected ball size

        if balls_type == "Std.":
            # Handle special ball sizes (Z, V, W) for Standard balls
            if ball_size == "3/8\" Double Ball":
                ball_size_price = 250
            elif ball_size == "1/2\" Double Ball":
                ball_size_price = 350
            elif ball_size == "7/8\" Double Ball":
                ball_size_price = 450

            # Fetch the Ball_Size from the database if the option is "Standard"
            if ball_size == "Standard":
                ball_size_display = f"Standard ({pump['Ball_Size']})"
        elif balls_type in ["Tungsten", "Ceramic"]:
            # Handle Standard option for Tungsten and Ceramic balls
            if ball_size == "Standard":
                ball_size_display = f"Standard ({pump['Ball_Size']})"
                # Define base prices for ball sizes
                if balls_type == "Tungsten":
                    ball_size_prices = {
                        "1/4\"": 4.00,
                        "3/8\"": 7.67,
                        "1/2\"": 17.22,
                        "7/8\"": 49.54,
                        "1-1/4\"": 102.15,
                        "1-1/2\"": 144.30
                    }
                elif balls_type == "Ceramic":
                    ball_size_prices = {
                        "1/4\"": 4.60,
                        "3/8\"": 3.00,
                        "1/2\"": 4.60,
                        "7/8\"": 28.95,
                        "1-1/4\"": 60.05,
                        "1-1/2\"": 70.55
                    }

                # Apply the base price for the selected ball size
                if pump['Ball_Size'] in ball_size_prices:
                    base_price = ball_size_prices[pump['Ball_Size']]
                    if balls_type == "Tungsten":
                        ball_size_price = base_price * 2.89  # Multiply by 2.89 for Tungsten
                    elif balls_type == "Ceramic":
                        ball_size_price = base_price * 1.7  # Multiply by 1.7 for Ceramic

        # Ensure Simplex/Duplex matches or allow "both"
        if simplex_duplex.lower() != "both" and pump["Simplex_Duplex"].lower() != simplex_duplex.lower():
            continue

        # Start total price calculation (without suction lift)
        pump_price = float(pump["Pump_Price"]) if pump["Pump_Price"] is not None else 0
        motor_price = 0
        diaphragm_price = 0
        leak_detection_price = 0
        flange_price = 0

        # Determine correct motor price column
        if want_motor == "yes":
            if motor_type == "TEFC" and motor_power == "AC":
                motor_price_column = "TEFC_AC_Price"
            elif motor_type == "XPFC" and motor_power == "AC":
                motor_price_column = "XPFC_AC_Price"
            elif motor_type == "TEFC" and motor_power == "DC":
                motor_price_column = "TEFC_DC_Price"
            elif motor_type == "XPFC" and motor_power == "DC":
                motor_price_column = "XPFC_DC_Price"
            else:
                return {"error": "Invalid motor type or power. Choose TEFC/XPFC and AC/DC correctly."}

            motor_price_value = pump[motor_price_column]

            # Skip this pump if motor price is 0 for DC motor
            if motor_power == "DC" and motor_price_value == "0":
                continue

            # Handle "C/F" values
            if motor_price_value == "C/F":
                motor_price = "C/F"
            else:
                motor_price = float(motor_price_value) if motor_price_value is not None else 0

        # Determine diaphragm price
        if diaphragm.lower() == "viton":
            diaphragm_price = float(pump["Viton"]) if pump["Viton"] is not None else 0
        elif diaphragm.lower() == "hypalon":
            diaphragm_price = float(pump["Hypalon"]) if pump["Hypalon"] is not None else 0
        elif diaphragm.lower() == "epdm":
            diaphragm_price = float(pump["EPDM"]) if pump["EPDM"] is not None else 0
        elif diaphragm.lower() != "ptfe":
            continue

        # Determine leak detection price
        if leak_detection.lower() == "conductive":
            leak_detection_price = float(pump["Conductive_Leak_Detection_Price_Adder"]) if pump["Conductive_Leak_Detection_Price_Adder"] is not None else 0
        elif leak_detection.lower() == "vacuum":
            leak_detection_price = float(pump["Vacuum_Leak_Detection_Price_Adder"]) if pump["Vacuum_Leak_Detection_Price_Adder"] is not None else 0
        else:
            leak_detection_price = 0

        # Calculate Food Graded Oil price
        food_graded_oil_price = 0
        if food_graded_oil.lower() == "yes":
            if pump["Series"] == "Series 1000":
                food_graded_oil_price = 140
            elif pump["Series"] == "Series 2000":
                food_graded_oil_price = 280
            elif pump["Series"] == "Series 3000":
                food_graded_oil_price = 840
            elif pump["Series"] == "Series 4000":
                food_graded_oil_price = 2200
            elif pump["Series"] == "Series 900":
                food_graded_oil_price = 44

        # Updated total price calculation
        total_price = pump_price  # Always include the pump price

        # Add degassing price if applicable
        if degassing.lower() == "yes":
            total_price += 450

        # Add ball size price if applicable
        total_price += ball_size_price

        # Round up the total price
        if isinstance(total_price, (int, float)):
            total_price_rounded = math.ceil(total_price)
        else:
            total_price_rounded = total_price  # Handle "C/F" case

        annotations = []

        # Add motor price if it's not "C/F"
        if motor_price != "C/F":
            total_price += motor_price
        else:
            annotations.append("C/F (Motor)")

        if flange_price != "C/F":
            total_price += flange_price
        else:
            annotations.append("C/F (Flange)")

        # Add diaphragm price if not "ptfe"
        total_price += diaphragm_price

        # Add leak detection price
        total_price += leak_detection_price

        # Add HP adder price if it's not "C/F"
        if use_hp and pump["High_Pressure_Adder_Price"] is not None and pump["High_Pressure_Adder_Price"] != "C/F":
            total_price += float(pump["High_Pressure_Adder_Price"])
        elif use_hp and pump["High_Pressure_Adder_Price"] == "C/F":
            annotations.append("C/F (HP)")

        # Add ball size price if applicable
        total_price += ball_size_price

        # Add Food Graded Oil price if applicable
        total_price += food_graded_oil_price

        # Round up the total price to the nearest whole number
        if isinstance(total_price, (int, float)):
            total_price_rounded = math.ceil(total_price)
        else:
            total_price_rounded = total_price  # Handle "C/F" case

        # Add annotations for "C/F" cases
        if annotations:
            total_price_rounded = f"{total_price_rounded} + {' + '.join(annotations)}"

        # print("PUMPS")
        # print(final_model)
        # print(total_price_rounded)

        filtered_pumps.append({
            "model": final_model,
            "series": pump["Series"],
            "simplex_duplex": pump["Simplex_Duplex"],
            "gph": float(pump["GPH_60Hz"]) if hz == 60 else float(pump["GPH_50Hz"]),
            "lph": float(pump["LPH_60Hz"]) if hz == 60 else float(pump["LPH_50Hz"]),
            "psi": float(pump["Max_Pressure_PSI"]),
            "bar": float(pump["Max_Pressure_Bar"]),
            "high_pressure_psi": float(pump["Max_Pressure_PSI_High_Pressure_Adder"]),
            "high_pressure_bar": float(pump["Max_Pressure_Bar_High_Pressure_Adder"]),
            "max_spm": float(pump["Max_SPM"]),
            "liquid_end_material": pump["Liquid_End_Material"],
            "pump_price": pump_price,
            "motor_price": motor_price,
            "diaphragm_price": diaphragm_price,
            "leak_detection_price": leak_detection_price,
            "flange_price": flange_price,
            "total_price": total_price_rounded,
            "phase": phase,
            "ball_size_price": ball_size_price,
            "ball_size_display": ball_size_display,
            "Motor_HP_AC": pump.get("Motor_HP_AC", "N/A"),
            "Motor_HP_AC_High_Pressure": pump.get("Motor_HP_AC_High_Pressure", "N/A"),
            "Motor_HP_DC_TEFC": pump.get("Motor_HP_DC_TEFC", "N/A"),
            "Motor_HP_DC_XPFC": pump.get("Motor_HP_DC_XPFC", "N/A"),
            "food_graded_oil_price": food_graded_oil_price,
        })

    # Inside the `find_best_pump` function, after selecting the best pump
    if filtered_pumps:
        # Sort pumps by total_price, GPH, SPM, and PSI
        filtered_pumps.sort(key=lambda x: (
            float('inf') if isinstance(x["total_price"], str) else x["total_price"],  # Sort by price
            x["gph"],  # Sort by GPH (ascending)
            x["max_spm"],  # Sort by SPM (ascending)
            x["psi"]  # Sort by PSI (ascending)
        ))

        best_pump = filtered_pumps[0]
        # Add additional details to the best_pump dictionary
        best_pump["want_motor"] = want_motor
        best_pump["motor_type"] = motor_type
        best_pump["motor_power"] = motor_power
        best_pump["use_hp"] = use_hp
        best_pump["Liq_Inlet"] = pump["Liq_Inlet"]
        best_pump["Liq_Outlet"] = pump["Liq_Outlet"]
        best_pump["suction_flange_size"] = suction_flange_size
        best_pump["discharge_flange_size"] = discharge_flange_size
        best_pump["food_graded_oil"] = food_graded_oil
        best_pump["food_graded_oil_price"] = food_graded_oil_price

        # Add flange price AFTER choosing the cheapest pump
        flange_price = 0
        flange_message = None
        if flange and flange.lower() == "yes":
            flange_price_result = calculate_flange_price(psi, suction_flange_size, discharge_flange_size, liquid_end_material)
            if "error" in flange_price_result:
                return flange_price_result  # Return the error if any

            flange_price = flange_price_result["total_flange_price"]
            print(f"Total Flange Price: {flange_price}")  # Debug: Print total flange price

            # Update total price with flange price (if applicable)
            if isinstance(flange_price, str):  # Handle "C/F" or "Unavailable" cases
                if isinstance(best_pump["total_price"], str):
                    # If total price is already a string (e.g., "C/F"), append the flange price message
                    best_pump["total_price"] = f"{best_pump['total_price']} + {flange_price}"
                else:
                    # If total price is a number, convert it to a string and append the flange price message
                    best_pump["total_price"] = f"{best_pump['total_price']} + {flange_price}"
            else:
                # If flange price is a number, add it to the total price
                if isinstance(best_pump["total_price"], str):
                    # If total price is already a string (e.g., "C/F"), append the flange price
                    best_pump["total_price"] = f"{best_pump['total_price']} + ${flange_price}"
                else:
                    best_pump["total_price"] += flange_price
        else:
            # If flange is "No", set flange_price to 0
            flange_price = 0
            flange_message = "Flange not selected"

        # Add flange details to the best pump
        best_pump["flange_price"] = flange_price
        best_pump["flange_message"] = flange_message

        # Add suction lift price AFTER choosing the cheapest pump
        suction_lift_price = 0
        suction_lift_message = None
        if suction_lift.lower() == "yes":
            suction_lift_price = calculate_suction_lift_price(best_pump["series"], liquid_end_material, suction_lift)
            if suction_lift_price == 0:  # Suction lift is not available for this series
                suction_lift_message = "Suction lift is not available"

        # Update total price with suction lift price (if applicable)
        if suction_lift_price != "C/F" and suction_lift_price != 0:
            if isinstance(best_pump["total_price"], str):
                # If total price is already a string (e.g., "C/F"), append the suction lift price
                best_pump["total_price"] = f"{best_pump['total_price']} + ${suction_lift_price}"
            else:
                best_pump["total_price"] += suction_lift_price
        elif suction_lift_price == "C/F":
            best_pump["total_price"] = f"{best_pump['total_price']} + C/F (Suction Lift)"

        # Add suction lift details to the best pump
        best_pump["suction_lift_price"] = suction_lift_price
        best_pump["suction_lift_message"] = suction_lift_message

        # Add flange adaptor price AFTER choosing the cheapest pump
        flange_adaptor_price = 0
        flange_adaptor_message = None
        if flange and flange.lower() == "yes":
            flange_adaptor_price_result = calculate_flange_adaptor_price(psi, suction_flange_size, discharge_flange_size, liquid_end_material, simplex_duplex)
            if "error" in flange_adaptor_price_result:
                return flange_adaptor_price_result  # Return the error if any

            flange_adaptor_price = flange_adaptor_price_result["total_flange_adaptor_price"]
            print(f"Total Flange Adaptor Price: {flange_adaptor_price}")  # Debug: Print total flange adaptor price

            # Update total price with flange adaptor price (if applicable)
            if isinstance(flange_adaptor_price, str):  # Handle "C/F" or "Unavailable" cases
                if isinstance(best_pump["total_price"], str):
                    # If total price is already a string (e.g., "C/F"), append the flange adaptor price message
                    best_pump["total_price"] = f"{best_pump['total_price']} + {flange_adaptor_price}"
                else:
                    # If total price is a number, convert it to a string and append the flange adaptor price message
                    best_pump["total_price"] = f"{best_pump['total_price']} + {flange_adaptor_price}"
            else:
                # If flange adaptor price is a number, add it to the total price
                if isinstance(best_pump["total_price"], str):
                    # If total price is already a string (e.g., "C/F"), append the flange adaptor price
                    best_pump["total_price"] = f"{best_pump['total_price']} + ${flange_adaptor_price}"
                else:
                    best_pump["total_price"] += flange_adaptor_price
        else:
            # If flange is "No", set flange_adaptor_price to 0
            flange_adaptor_price = 0
            flange_adaptor_message = "Flange Adaptor not selected"

        # Add flange adaptor details to the best pump
        best_pump["flange_adaptor_price"] = flange_adaptor_price
        best_pump["flange_adaptor_message"] = flange_adaptor_message

        return best_pump
    else:
        return {"error": "No suitable pump found for the given specifications."}

def generate_pdf(pump_data, filename="pump_quote.pdf"):
    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()

    # Set font for the entire document
    pdf.set_font("Arial", size=12)

    # Add a header with a logo
    pdf.image("logo.png", x=10, y=8, w=30)  # Ensure the logo path is correct
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt="Pump Quote", ln=True, align="C")
    pdf.ln(10)  # Add some space

    # Initialize the dynamic description string
    dynamic_description = ""

    # Add the base description
    ball_type = pump_data.get("balls_type", "N/A")
    diaphragm = pump_data.get("diaphragm", "N/A")

    # Check if suction lift is "yes" and add "High Suction Lift" to the description
    suction_lift_text = "High Suction Lift " if pump_data.get("suction_lift", "").lower() == "yes" else ""

    if pump_data.get("flange", "").lower() == "yes":
        # Get the flange size ID based on PSI
        psi = pump_data.get("psi", 0)
        flange_size_id = get_flange_size_id(psi)  # Use the function from the top of the code

        # Build the flange-specific sentence
        if ball_type.lower() == "tungsten":
            dynamic_description += (
                f"Aquflow {pump_data.get('series', 'N/A')} ({pump_data.get('simplex_duplex', 'N/A')}) "
                f"hydraulic diaphragm metering pump with {suction_lift_text}liquid end in {pump_data.get('liquid_end_material', 'N/A')} "
                f"with {ball_type} Carbid balls and {diaphragm} Diaphragm with {pump_data.get('suction_flange_size', 'N/A')} "
                f"ANSI RF Type #{flange_size_id} Suction and {pump_data.get('discharge_flange_size', 'N/A')} "
                f"ANSI RF Type #{flange_size_id} Discharge Flanges."
                f"The pump has a maximum flow capacity of {pump_data.get('gph', 'N/A')} GPH at {pump_data.get('hz', 'N/A')} Hz "
                f"and design pressure of {pump_data.get('psi', 'N/A')} PSI."
            )
        elif ball_type.lower() == "ceramic":
            dynamic_description += (
                f"Aquflow {pump_data.get('series', 'N/A')} ({pump_data.get('simplex_duplex', 'N/A')}) "
                f"hydraulic diaphragm metering pump with {suction_lift_text}liquid end in {pump_data.get('liquid_end_material', 'N/A')} "
                f"with {ball_type} balls and {diaphragm} Diaphragm with {pump_data.get('suction_flange_size', 'N/A')} "
                f"ANSI RF Type #{flange_size_id} Suction and {pump_data.get('discharge_flange_size', 'N/A')} "
                f"ANSI RF Type #{flange_size_id} Discharge Flanges."
                f"The pump has a maximum flow capacity of {pump_data.get('gph', 'N/A')} GPH at {pump_data.get('hz', 'N/A')} Hz "
                f"and design pressure of {pump_data.get('psi', 'N/A')} PSI."
            )
        else:
            dynamic_description += (
                f"Aquflow {pump_data.get('series', 'N/A')} ({pump_data.get('simplex_duplex', 'N/A')}) "
                f"hydraulic diaphragm metering pump with {suction_lift_text}liquid end in {pump_data.get('liquid_end_material', 'N/A')} "
                f"and {diaphragm} Diaphragm with {pump_data.get('suction_flange_size', 'N/A')} "
                f"ANSI RF Type #{flange_size_id} Suction and {pump_data.get('discharge_flange_size', 'N/A')} "
                f"ANSI RF Type #{flange_size_id} Discharge. The pump has a maximum flow capacity of "
                f"{pump_data.get('gph', 'N/A')} GPH at {pump_data.get('hz', 'N/A')} Hz and design pressure of "
                f"{pump_data.get('psi', 'N/A')} PSI."
            )
    else:
        # Use the default sentence for non-flange connections
        if ball_type.lower() == "tungsten":
            dynamic_description += (
                f"Aquflow {pump_data.get('series', 'N/A')} ({pump_data.get('simplex_duplex', 'N/A')}) "
                f"hydraulic diaphragm metering pump with {suction_lift_text}liquid end in {pump_data.get('liquid_end_material', 'N/A')} "
                f"with {ball_type} Carbid balls and {diaphragm} Diaphragm with {pump_data.get('Liq_Inlet', 'N/A')} suction "
                f"and {pump_data.get('Liq_Outlet', 'N/A')} discharge check valve connections. "
                f"The pump has a maximum flow capacity of {pump_data.get('gph', 'N/A')} GPH at {pump_data.get('hz', 'N/A')} Hz "
                f"and design pressure of {pump_data.get('psi', 'N/A')} PSI."
            )
        elif ball_type.lower() == "ceramic":
            dynamic_description += (
                f"Aquflow {pump_data.get('series', 'N/A')} ({pump_data.get('simplex_duplex', 'N/A')}) "
                f"hydraulic diaphragm metering pump with {suction_lift_text}liquid end in {pump_data.get('liquid_end_material', 'N/A')} "
                f"with {ball_type} balls and {diaphragm} Diaphragm with {pump_data.get('Liq_Inlet', 'N/A')} suction "
                f"and {pump_data.get('Liq_Outlet', 'N/A')} discharge check valve connections. "
                f"The pump has a maximum flow capacity of {pump_data.get('gph', 'N/A')} GPH at {pump_data.get('hz', 'N/A')} Hz "
                f"and design pressure of {pump_data.get('psi', 'N/A')} PSI."
            )
        else:
            dynamic_description += (
                f"Aquflow {pump_data.get('series', 'N/A')} ({pump_data.get('simplex_duplex', 'N/A')}) "
                f"hydraulic diaphragm metering pump with {suction_lift_text}liquid end in {pump_data.get('liquid_end_material', 'N/A')} "
                f"and {diaphragm} Diaphragm with {pump_data.get('Liq_Inlet', 'N/A')} suction "
                f"and {pump_data.get('Liq_Outlet', 'N/A')} discharge check valve connections. The pump has a maximum "
                f"flow capacity of {pump_data.get('gph', 'N/A')} GPH at {pump_data.get('hz', 'N/A')} Hz and design "
                f"pressure of {pump_data.get('psi', 'N/A')} PSI."
            )

    # Add motor description if want_motor is "yes"
    if pump_data.get("want_motor", "").lower() == "yes":
        # Determine motor input voltage based on motor_power, hz, and phase
        motor_power = pump_data.get("motor_power", "").upper()
        hz = pump_data.get("hz", 60)  # Default to 60 Hz if not provided
        phase = pump_data.get("phase", "1 Ph")  # Default to 1 Ph if not provided

        if motor_power == "AC":
            if hz == 60:
                if phase == "1 Ph":
                    input_voltage = "115/230 VAC"
                elif phase == "3 Ph":
                    input_voltage = "230/460 VAC"
            elif hz == 50:
                if phase == "1 Ph":
                    input_voltage = "110/220 VAC"
                elif phase == "3 Ph":
                    input_voltage = "230/400 VAC"
        elif motor_power == "DC":
            input_voltage = "90 VDC"
            phase = ""  # Remove phase for DC motors

        # Get motor_hp from pump_data
        motor_hp = pump_data.get("Motor_HP_AC", "N/A")  # Default to N/A if not provided

        # Add the motor description sentence
        if motor_power == "DC":
            dynamic_description += f" The pump comes with {motor_hp} HP, {input_voltage}, {pump_data.get('motor_type', 'N/A')} Motor."
        else:
            dynamic_description += f" The pump comes with {motor_hp} HP, {input_voltage}, {phase}, {pump_data.get('motor_type', 'N/A')} Motor."

    # Add degassing description if degassing is "yes"
    if pump_data.get("degassing", "").lower() == "yes":
        dynamic_description += " The pump comes with a degassing valve."

    # Add food graded oil description if food_graded_oil is "yes"
    if pump_data.get("food_graded_oil", "").lower() == "yes":
        dynamic_description += " The pump comes with food graded oil."

    # Add suction lift description if suction_lift is "yes"
    if pump_data.get("suction_lift", "").lower() == "yes":
        dynamic_description += " The pump comes with suction lift."

    # Add the combined description to the PDF
    pdf.multi_cell(0, 10, txt=dynamic_description)

    # Add pump details section (unchanged)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Pump Specifications", ln=True)
    pdf.set_font("Arial", size=12)

    # Add Model
    pdf.cell(0, 10, txt=f"Model: {pump_data.get('model', 'N/A')}", ln=True)

    # Add Series
    pdf.cell(0, 10, txt=f"Series: {pump_data.get('series', 'N/A')}", ln=True)

    # Add GPH/LPH
    if "gph" in pump_data:
        pdf.cell(0, 10, txt=f"Flow Rate (GPH): {pump_data['gph']}", ln=True)
    elif "lph" in pump_data:
        pdf.cell(0, 10, txt=f"Flow Rate (LPH): {pump_data['lph']}", ln=True)

    # Add PSI/Bar
    if "psi" in pump_data:
        pdf.cell(0, 10, txt=f"Pressure (PSI): {pump_data['psi']}", ln=True)
    elif "bar" in pump_data:
        pdf.cell(0, 10, txt=f"Pressure (Bar): {pump_data['bar']}", ln=True)

    # Add Hz
    pdf.cell(0, 10, txt=f"Frequency (Hz): {pump_data.get('hz', 'N/A')}", ln=True)

    # Add Simplex/Duplex
    pdf.cell(0, 10, txt=f"Simplex/Duplex: {pump_data.get('simplex_duplex', 'N/A')}", ln=True)

    # Add Motor Type and Motor Power (if applicable)
    if pump_data.get("want_motor", "").lower() == "yes":
        pdf.cell(0, 10, txt=f"Motor Type: {pump_data.get('motor_type', 'N/A')}", ln=True)
        pdf.cell(0, 10, txt=f"Motor Power: {pump_data.get('motor_power', 'N/A')}", ln=True)

        # Add Motor Horsepower (HP)
        motor_hp = "N/A"  # Default value
        if pump_data.get("motor_power", "") == "AC":
            if pump_data.get("use_hp", False):  # Check if high pressure is needed
                motor_hp = pump_data.get("Motor_HP_AC_High_Pressure", "N/A")
            else:
                motor_hp = pump_data.get("Motor_HP_AC", "N/A")
        elif pump_data.get("motor_power", "") == "DC":
            if pump_data.get("motor_type", "") == "TEFC":
                motor_hp = pump_data.get("Motor_HP_DC_TEFC", "N/A")
            elif pump_data.get("motor_type", "") == "XPFC":
                motor_hp = pump_data.get("Motor_HP_DC_XPFC", "N/A")

        pdf.cell(0, 10, txt=f"Motor Horsepower (HP): {motor_hp}", ln=True)

    # Add Diaphragm
    pdf.cell(0, 10, txt=f"Diaphragm Material: {pump_data.get('diaphragm', 'N/A')}", ln=True)

    # Add Liquid End Material
    pdf.cell(0, 10, txt=f"Liquid End Material: {pump_data.get('liquid_end_material', 'N/A')}", ln=True)

    # Add Leak Detection (if not "no")
    if pump_data.get("leak_detection", "").lower() != "no":
        pdf.cell(0, 10, txt=f"Leak Detection: {pump_data.get('leak_detection', 'N/A')}", ln=True)

    # Add Phase
    pdf.cell(0, 10, txt=f"Phase: {pump_data.get('phase', 'N/A')}", ln=True)

    # Add Degassing (if "yes")
    if pump_data.get("degassing", "").lower() == "yes":
        pdf.cell(0, 10, txt=f"Add Degassing: Yes", ln=True)
    else:
        pdf.cell(0, 10, txt=f"Add Degassing: No", ln=True)

    # Add Flange (if "yes")
    if pump_data.get("flange", "").lower() == "yes":
        pdf.cell(0, 10, txt=f"Add Flange: Yes", ln=True)
    else:
        pdf.cell(0, 10, txt=f"Add Flange: No", ln=True)

    # Add Balls Type
    pdf.cell(0, 10, txt=f"Balls Type: {pump_data.get('balls_type', 'N/A')}", ln=True)

    # Add Ball Size
    pdf.cell(0, 10, txt=f"Ball Size: {pump_data.get('ball_size_display', 'N/A')}", ln=True)

    # Add Suction Lift (if "yes")
    if pump_data.get("suction_lift", "").lower() == "yes":
        pdf.cell(0, 10, txt=f"Add Suction Lift: Yes", ln=True)
        if pump_data.get("suction_lift_message"):  # Display message if suction lift is not available
            pdf.cell(0, 10, txt=f"Note: {pump_data['suction_lift_message']}", ln=True)
    else:
        pdf.cell(0, 10, txt=f"Add Suction Lift: No", ln=True)

    # Add Food Graded Oil (if "yes")
    if pump_data.get("food_graded_oil", "").lower() == "yes":
        pdf.cell(0, 10, txt=f"Add Food Graded Oil: Yes", ln=True)
    else:
        pdf.cell(0, 10, txt=f"Add Food Graded Oil: No", ln=True)

    pdf.ln(10)  # Add some space

    # Add pricing details (unchanged)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Pricing Details", ln=True)
    pdf.set_font("Arial", size=12)

    # Add Pump Price
    pdf.cell(100, 10, txt="Pump Price", border=1)
    pdf.cell(80, 10, txt=f"${pump_data['pump_price']}", border=1, ln=True)

    # Add Motor Price
    pdf.cell(100, 10, txt="Motor Price", border=1)
    if isinstance(pump_data.get("motor_price"), str):  # Handle "C/F" case
        pdf.cell(80, 10, txt=f"{pump_data['motor_price']}", border=1, ln=True)
    else:
        pdf.cell(80, 10, txt=f"${pump_data.get('motor_price', 0)}", border=1, ln=True)

    # Add Flange Price (if applicable)
    if pump_data.get("flange_price", 0) != 0:
        pdf.cell(100, 10, txt="Flange Price", border=1)
        if isinstance(pump_data.get("flange_price"), str):  # Handle "C/F" or "Unavailable" cases
            pdf.cell(80, 10, txt=f"{pump_data['flange_price']}", border=1, ln=True)
        else:
            pdf.cell(80, 10, txt=f"${pump_data.get('flange_price', 0)}", border=1, ln=True)

    # Add Flange Adaptor Price (if applicable)
    if pump_data.get("flange_adaptor_price", 0) != 0:
        pdf.cell(100, 10, txt="Flange Adaptor Price", border=1)
        if isinstance(pump_data.get("flange_adaptor_price"), str):  # Handle "C/F" or "Unavailable" cases
            pdf.cell(80, 10, txt=f"{pump_data['flange_adaptor_price']}", border=1, ln=True)
        else:
            pdf.cell(80, 10, txt=f"${pump_data.get('flange_adaptor_price', 0)}", border=1, ln=True)

    # Add Diaphragm Price
    if pump_data['diaphragm_price'] != 0:
        pdf.cell(100, 10, txt="Diaphragm Price", border=1)
        pdf.cell(80, 10, txt=f"${pump_data['diaphragm_price']}", border=1, ln=True)

    # Add Leak Detection Price
    if pump_data['leak_detection_price'] != 0:
        pdf.cell(100, 10, txt="Leak Detection Price", border=1)
        pdf.cell(80, 10, txt=f"${pump_data['leak_detection_price']}", border=1, ln=True)

    # Add Degassing Price
    if pump_data.get("degassing", "").lower() == "yes":
        pdf.cell(100, 10, txt="Degassing Price", border=1)
        pdf.cell(80, 10, txt="$450", border=1, ln=True)

    # Add Suction Lift Price (if available)
    if pump_data.get("suction_lift_price", 0) != 0:
        pdf.cell(100, 10, txt="Suction Lift Price", border=1)
        if isinstance(pump_data.get("suction_lift_price"), str):  # Handle "C/F" case
            pdf.cell(80, 10, txt=f"{pump_data['suction_lift_price']}", border=1, ln=True)
        else:
            pdf.cell(80, 10, txt=f"${pump_data.get('suction_lift_price', 0)}", border=1, ln=True)

    # Add Ball Size Price (if applicable)
    if pump_data.get("ball_size_price", 0) != 0:
        pdf.cell(100, 10, txt="Ball Size Price", border=1)
        pdf.cell(80, 10, txt=f"${pump_data.get('ball_size_price', 0)}", border=1, ln=True)

    # Add Food Graded Oil Price (if applicable)
    if pump_data.get("food_graded_oil", "").lower() == "yes":
        pdf.cell(100, 10, txt="Food Graded Oil Price", border=1)
        pdf.cell(80, 10, txt=f"${pump_data.get('food_graded_oil_price', 0)}", border=1, ln=True)

    # Add Pump + Motor Price
    pump_motor_price = pump_data['pump_price'] + pump_data['motor_price']
    pdf.cell(100, 10, txt="Pump + Motor Price", border=1)
    pdf.cell(80, 10, txt=f"{pump_motor_price}", border=1, ln=True)

    # Add Total Price
    pdf.cell(100, 10, txt="Total Price", border=1)
    if isinstance(pump_data.get("total_price"), str):  # Handle "C/F" case
        pdf.cell(80, 10, txt=f"{pump_data['total_price']}", border=1, ln=True)
    else:
        pdf.cell(80, 10, txt=f"${pump_data.get('total_price', 0)}", border=1, ln=True)

    pdf.ln(10)  # Add some space

    # Add a footer
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, txt="Thank you for choosing us!", ln=True, align="C")
    pdf.cell(0, 10, txt="Terms and conditions apply.", ln=True, align="C")

    # Save the PDF
    pdf.output(filename)
    return filename

@app.route('/get_pump', methods=['GET'])
def get_pump():
    try:
        # Log the incoming request parameters
        print("Request Args:", request.args)

        # Get parameters from the request
        gph = request.args.get('gph', type=float)
        psi = request.args.get('psi', type=float)
        hz = request.args.get('hz', type=int)
        simplex_duplex = request.args.get('simplex_duplex', type=str)
        want_motor = request.args.get('want_motor', type=str)
        motor_type = request.args.get('motor_type', type=str)
        motor_power = request.args.get('motor_power', type=str)
        spm = request.args.get('spm', type=int)
        diaphragm = request.args.get('diaphragm', type=str)
        liquid_end_material = request.args.get('liquid_end_material', type=str)
        leak_detection = request.args.get('leak_detection', type=str)
        phase = request.args.get('phase', type=str)
        degassing = request.args.get('degassing', type=str)
        flange = request.args.get('flange', type=str)
        balls_type = request.args.get('balls_type', type=str)
        suction_lift = request.args.get('suction_lift', type=str)
        ball_size = request.args.get('ball_size', type=str)
        suction_flange_size = request.args.get('suction_flange_size', type=str)
        discharge_flange_size = request.args.get('discharge_flange_size', type=str)
        food_graded_oil = request.args.get('food_graded_oil', type=str)
        user_email = request.args.get('user_email', type=str)

        # Log the parsed parameters
        print("Parsed Parameters:", {
            "gph": gph,
            "psi": psi,
            "hz": hz,
            "simplex_duplex": simplex_duplex,
            "want_motor": want_motor,
            "motor_type": motor_type,
            "motor_power": motor_power,
            "spm": spm,
            "diaphragm": diaphragm,
            "liquid_end_material": liquid_end_material,
            "leak_detection": leak_detection,
            "phase": phase,
            "degassing": degassing,
            "flange": flange,
            "balls_type": balls_type,
            "suction_lift": suction_lift,
            "ball_size": ball_size,
            "suction_flange_size": suction_flange_size,
            "discharge_flange_size": discharge_flange_size,
            "food_graded_oil": food_graded_oil,
            "user_email": user_email
        })

        # Find the best pump
        result = find_best_pump(
            gph, None, psi, None, hz, simplex_duplex, want_motor, motor_type, 
            motor_power, spm, diaphragm, liquid_end_material, leak_detection, 
            phase, degassing, flange, balls_type, suction_lift, ball_size, 
            suction_flange_size, discharge_flange_size, food_graded_oil
        )

        # Log the result
        print("Result:", result)

        # Generate PDF
        if "error" not in result:
            # Include additional details in the result for the PDF
            result["hz"] = hz
            result["diaphragm"] = diaphragm
            result["psi"] = psi
            result["degassing"] = degassing
            result["flange"] = flange
            result["balls_type"] = balls_type
            result["suction_lift"] = suction_lift
            result["ball_size"] = ball_size
            pdf_filename = generate_pdf(result)
            # result["pdf_url"] = f"/download_pdf/{pdf_filename}"

            # Send the PDF via email
            email_subject = "Your Pump Quote"
            email_body = "Please find attached the pump quote."
            to_emails = [user_email, "michaelkhoury744@gmail.com"]
            if send_email(to_emails, email_subject, email_body, pdf_filename):
                result["email_status"] = "Email sent successfully"
            else:
                result["email_status"] = "Failed to send email"

        return jsonify(result)

    except Exception as e:
        print(f"Error in /get_pump: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download_pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "PDF not found"}), 404

@app.route('/test_db')
def test_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Database connection successful!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Heroku's $PORT or default to 5000
    app.run(host="0.0.0.0", port=port, debug=False)  # Disable debug mode for production