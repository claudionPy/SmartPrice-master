#installation guide of SmartPrice
#device supported = Raspberry pi 3 model B
#HAT supported = Adafruit HAT Hub75
#Matrix supported = Led Outdoor P5 64x32px
#python version tested 3.9
#Raspberry Pi Os 32bit, debian bullseye, 0.4gb 


#FOR A CORRECT INSTALLATION, YOU MUST FOLLOW THIS FILE, DO NOT SKIP ANY STEP!

device username = raspberry
device password = smartprice-rpi
device local hostname = smartprice.local

if you didn't install SmartPrice with git, please install git: sudo apt install git
rename the entire folder from SmartPrice-Duo-master to SmartPrice: sudo mv SmartPrice-Duo-master SmartPrice
navigate into /SmartPrice
install python3-venv: sudo apt install python3-venv
create a virtual environment into /SmartPrice: python3 -m venv venv
activate it: source venv/bin/activate
install the packages into the virtual environment: pip3 install -r requirements.txt
install rpi-rgb-led-matrix library (see the file "rpi-rgb-led-matrix")
after installing rpi-rgb-led-matrix, deactivate the venv: deactivate
create the service file (see the file "service-config")
install and configure nginx reverse proxy (see the file "nginx-config")
set the network options (see the file "network-config")
check if everything works, on a web browser on the local network search for "smartprice.local"
the website it's a PWA, so by linking the web page on the home screen it should appear like a native app

IMPORTANT NOTE:
THE FOLLOWING INSTRUCTIONS ARE WRITTEN FOR SMARTPRICE-DUO(MASTER) DEVICE OF THE SMARTPRICE-DUO SOLUTION
TO COMPLETE THE INSTALLATION OF SP-DUO YOU NEED TO FOLLOW THE SMARTPRICE-DUO(SLAVE) INSTRUCTIONS
ON THE SECOND DEVICE, IF YOU NEED TO RUN SMARTPRICE ON A SINGLE DEVICE, PLEASE INSTALL 'SMARTPRICE'
NOT THE 'DUO' VERSION.

if you got any troubles on the installation and configuration feel free to ask help at our helpdesk
send an email to: lopreiatoclaudio.finnd@gmail.com
in the email, describe your problem in short, leave ur name, surname, company name and a phone number
we will contact you back to solve your problems

Thank you for trusting in us!
