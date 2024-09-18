from tkinter import *
import phonenumbers
from phonenumbers import timezone, geocoder, carrier
from phonenumbers.phonenumberutil import NumberParseException
import requests
from datetime import datetime
import pytz

OPEN_CAGE_API_KEY = '{Add your own my guy}'

def move_caret_to_end(event):
    
    phone_number_entry.icursor("end")
    return "break"

def get_lat_long_opencage(location):

    geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={OPEN_CAGE_API_KEY}"
    response = requests.get(geocode_url)
    result = response.json()
    
    print(f"OpenCage Geocode Response: {result}") 
    
    if result['results']:

        if len(result['results']) > 0:
            lat = result['results'][0]['geometry']['lat']
            lon = result['results'][0]['geometry']['lng']
            return lat, lon
    print("Geocoding failed or returned no results.")
    return None, None

def reverse_geocode_opencage(lat, lon):

    reverse_geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={lat},{lon}&key={OPEN_CAGE_API_KEY}"
    response = requests.get(reverse_geocode_url)
    result = response.json()
    
    print(f"OpenCage Reverse Geocode Response: {result}")
    
    if result['results']:
        address = result['results'][0]['formatted']
        return address
    print("Reverse geocoding failed.") 
    return "Unknown Address"

def get_local_time(timezones):

    if timezones:
        tz = pytz.timezone(timezones[0])
        local_time = datetime.now(tz)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")
    return "Unknown"

def lookup_phone_number():

    result_label.config(text="", fg="red")  
    time_label.config(text="")
    location_label.config(text="")
    lat_lng_label.config(text="")
    address_label.config(text="")
    service_label.config(text="")

    number = phone_number_entry.get()
    try:
        phoneNumber = phonenumbers.parse(number)
        
        if not phonenumbers.is_valid_number(phoneNumber):
            result_label.config(text="Invalid phone number.")
        else:
            timezones = timezone.time_zones_for_number(phoneNumber)
            local_time = get_local_time(timezones)
            time_label.config(text="Current Time: " + local_time)
            
            geolocation = geocoder.description_for_number(phoneNumber, "en")
            
            if geolocation and geolocation != "United Kingdom":
                location_label.config(text="Location: " + geolocation)
                
                lat, lng = get_lat_long_opencage(geolocation)
                
                if lat and lng:
                    lat_lng_label.config(text=f"Latitude: {lat}, Longitude: {lng}")
                    address = reverse_geocode_opencage(lat, lng)
                    
                    if address.startswith("Unnamed Road") or "Unknown" in address:
                        address_label.config(text="Address: Not specific or unknown.")
                        result_label.config(text="Address not specific or unknown.")
                    else:
                        address_label.config(text=f"Address: {address}")
                        window.clipboard_clear()
                        window.clipboard_append(address)
                        window.update()  
                        result_label.config(text="Address copied to clipboard!",fg="purple")
                else:
                    lat_lng_label.config(text="Latitude/Longitude: Unknown")
                    address_label.config(text="Address: Unknown")
                    result_label.config(text="Latitude/Longitude or Address is unknown.")
            else:
                location_label.config(text="Location: Unknown or too vague (e.g., United Kingdom).")
                lat_lng_label.config(text="Latitude/Longitude: Unknown")
                address_label.config(text="Address: Unknown")
                result_label.config(text="Address information is not available.")
            
            service = carrier.name_for_number(phoneNumber, "en")
            service_label.config(text="Service provider: " + (service if service else "Unknown"))
    
    except NumberParseException as e:
        result_label.config(text=f"Error parsing number: {e}")
    except Exception as e:
        result_label.config(text=f"An error occurred: {e}")


def update_screen():

    label.place_forget()  

    button = Button(window, text="Who's in trouble?", font=('Futura', 30), fg='blue', bg='black')
    button.place(relx=0.5, rely=0.2, anchor='center')

    info_label = Label(window, text="Enter phone number:", font=('Futura', 20), fg='green', bg='black')
    info_label.place(relx=0.5, rely=0.3, anchor='center')

    global phone_number_entry
    phone_number_entry = Entry(window, font=('Futura', 20), fg='black', bg='white', insertbackground="black", insertwidth=2)
    phone_number_entry.place(relx=0.5, rely=0.4, anchor='center')
    phone_number_entry.focus_set()  
    phone_number_entry.bind("<Return>", move_caret_to_end)

    lookup_button = Button(window, text="Lookup Phone Number", font=('Futura', 20), fg='blue', bg='black', command=lookup_phone_number)
    lookup_button.place(relx=0.5, rely=0.5, anchor='center')

    global time_label, location_label, service_label, result_label, lat_lng_label, address_label
    time_label = Label(window, font=('Futura', 16), fg='green', bg='black')
    time_label.place(relx=0.5, rely=0.6, anchor='center')

    location_label = Label(window, font=('Futura', 16), fg='green', bg='black')
    location_label.place(relx=0.5, rely=0.65, anchor='center')

    lat_lng_label = Label(window, font=('Futura', 16), fg='green', bg='black')
    lat_lng_label.place(relx=0.5, rely=0.7, anchor='center')

    address_label = Label(window, font=('Futura', 16), fg='green', bg='black')
    address_label.place(relx=0.5, rely=0.75, anchor='center')

    service_label = Label(window, font=('Futura', 16), fg='green', bg='black')
    service_label.place(relx=0.5, rely=0.8, anchor='center')

    result_label = Label(window, font=('Futura', 16), fg='red', bg='black')
    result_label.place(relx=0.5, rely=0.85, anchor='center')

window = Tk()
window.title("CLIP TRACK")
window.geometry("800x600")
window.config(background="black")

label = Label(window,
              text="SPARROW 🦅",
              font=('Digital-7', 40), 
              fg='green',
              bg='black',
              relief=RAISED,
              bd=10,
              padx=20,
              pady=20)


window.after(500, lambda: label.place(relx=0.5, rely=0.5, anchor='center'))

window.after(2000, update_screen)


window.mainloop()
