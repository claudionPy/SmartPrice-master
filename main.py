# Importing the modules
from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import re
import logging
import config
import logging_config
import json
import eventlet

# Initializing eventlet
eventlet.monkey_patch()

# Initializing the logging configuration from logging_config.py file
logging_config.setup_logging()

# Initializing Flask App and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Initializing RGB MATRIX options from config.py file
options = RGBMatrixOptions()
for key, value in config.LED_OPTIONS.items():
    setattr(options, key, value)
matrix = RGBMatrix(options=options)

# Setting fonts and color
font_large = graphics.Font()
font_large.LoadFont("/home/raspberry/SmartPrice/fonts/custom.bdf")

font_small = graphics.Font()
font_small.LoadFont("/home/raspberry/SmartPrice/fonts/custom_small.bdf")

text_color = graphics.Color(255, 255, 255)

# Defining background functions:

# This function is a must to prevent injections into the web server
# It validates the price that comes from the user
# Returns a boolean value if the price respects the criteria (e.g [0.000])
# Notice that there is another protection level written in JavaScript.
def validate_price(price):
    return bool(re.match(r'^\d\.\d{3}$', price))

# This function splits the price in 2 parts 
# Displaying the price with the first 3 numbers at regular size and the last a little smaller
# Usually fuel prices are written like this to help customers read the valuable part of the price (0.00)
def split_price(price):
    return price[:-1], price[-1]

# This function saves the price recived from the user into a Json file
def save_json(fiprice, seprice, namefile="logprice.json"):
    logprice = {"fiprice": fiprice, "seprice": seprice}
    try:
        with open(namefile, 'w') as file:
            json.dump(logprice, file, indent=4)
        logging.info("Prices saved to JSON successfully.")
    except IOError as e:
        logging.error(f"Failed to save prices to JSON: {e}")

# This function reads the price from the previous created Json file
def read_json(namefile="logprice.json"):
    try:
        with open(namefile, 'r') as file:
            prices = json.load(file)
            return prices.get("fiprice"), prices.get("seprice")
    except FileNotFoundError:
        logging.warning(f"File {namefile} not found")
    except json.JSONDecodeError:
        logging.error("Decoding JSON failed")
    return None, None

# This function simply displays the prices that will come from the user
def display_prices(price1, price2):
    try:
        # Clears the matrix from other texts (there shouldn't be any text, but it's common practice to clear everything)
        matrix.Clear()

        # Sets the returning result of the split_price function on 2 variables ({first 3 numbers}, {last number})
        price1_main, price1_last = split_price(price1)
        price2_main, price2_last = split_price(price2)

        # Here we use the splitted prices to display in normal size the first 2 numbers
        graphics.DrawText(matrix, font_large, 64, 31, text_color, price1_main)
        graphics.DrawText(matrix, font_large, 0, 31, text_color, price2_main)

        # Sets the offset space to display the last small number in the right position
        offset_large = graphics.DrawText(matrix, font_large, 64, 31, text_color, price1_main)
        graphics.DrawText(matrix, font_small, 64 + offset_large, 21, text_color, price1_last)

        offset_large = graphics.DrawText(matrix, font_large, 0, 31, text_color, price2_main)
        graphics.DrawText(matrix, font_small, 0 + offset_large, 21, text_color, price2_last)

    except Exception as e:
        logging.error(f"error, couldn't update the matrix: {e}")
        raise

# Here we can find the part of the script that runs at first boot or at every reboot
# This is made to prevent the panel to lose the prices if he gets rebooted or the script break and restart
def get_prices_at_start():
    fiprice, seprice = read_json()
    if fiprice and seprice:
        display_prices(fiprice, seprice)
    else:
        logging.error("Couldn't find prices in logprice.json")

# Defining the route to get the prices from the user
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        price1 = request.form.get('price1')
        price2 = request.form.get('price2')

        # Calling the validate_price function
        if validate_price(price1) and validate_price(price2):
            try:
                display_prices(price1, price2)
                save_json(price1, price2)

                # The socket emit process shares the prices to a possible slave devices
                socketio.emit('update_prices', {'price1': price1, 'price2': price2})
                logging.info(f"Emitted price update: {price1}, {price2}")
            except Exception as e:
                logging.error(f"Couldn't display prices correctly: {e}")
        else:
            logging.warning(f"Validation failed: {price1}, {price2}")
    return render_template('index.html')

# This route recives the differentials that sends to the slave device
# The slave device then computes the differentials and modifies the final price displayed
@app.route('/differ', methods=['GET', 'POST'])
def differ():
    if request.method == 'POST':
        differ_price1 = request.form.get('differ_price1')
        differ_price2 = request.form.get('differ_price2')

        if validate_price(differ_price1) and validate_price(differ_price2):
            try:
                socketio.emit('update_differ', {'differ_price1': differ_price1, 'differ_price2': differ_price2})
                logging.info(f"Emitted differential update: {differ_price1}, {differ_price2}")
                
                # Rendering the main page when sending the differentials
                return render_template('index.html')
            except Exception as e:
                logging.error(f"Couldn't display prices correctly: {e}")
        else:
            logging.warning(f"Validation failed: {differ_price1}, {differ_price2}")
    return render_template('differ.html')

# This route serves the manifest.json that contains a few settings that makes the PWA
@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')

# The line commented below should be uncommented if the script runs without a production server (Gunicorn is used)

if __name__ == '__main__':
    get_prices_at_start()
    #socketio.run(app, host='127.0.0.1', port=5000, use_reloader=False)
