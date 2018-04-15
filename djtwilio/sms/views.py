import json
import urllib
import image
import pprint
import requests
import apiai
from rapidconnect import RapidConnect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from twilio.twiml.messaging_response import MessagingResponse


@csrf_exempt
def sms_response(request):
    query = request.POST.get('Body','')
    print(query)
    # print(request.__dict__)
    term,location = diagflowapi(query)

    print(term,location)
    name,rating,phone,latitude,longitude = yelpapi(term,location)
    print(name,rating,phone,latitude,longitude)
    # define a series of location markers and their styles
    # syntax:  markers=markerStyles|markerLocation1|markerLocation2|... etc.
    marker_list = []
    # marker_list.append("markers=color:blue|label:S|11211|11206|11222")  # blue S at several zip code's centers
    marker_list.append("markers=|label:B|color:0xFFFF00|"+str(latitude)+","+str(longitude)+"|")  # tiny yellow B at lat/long B ko resturnt name dena hai
    # marker_list.append(
    #     "markers=size:mid|color:red|label:6|Brooklyn+Bridge,New+York,NY")  # mid-sized red 6 at search location
    # see http://code.google.com/apis/maps/documentation/staticmaps/#Markers
    googleUrl = get_static_google_map("google_map_example3", center=location, imgsize=(400, 400), imgformat="png", markers=marker_list)
    # Start our TwiML response
    resp = MessagingResponse()
    # Add a text message
    msg = resp.message("Check out this sweet owl!")

    # Add a picture message
    f = open(r'C:\Users\Harsh\Documents\GitHub\YelpONTHEGO\djtwilio\djtwilio\static\images\staticmap.png','wb')
    f.write(requests.get(googleUrl).content)
    f.close()
    msg.media("/static/images/staticmap.png")
    return HttpResponse(str(resp))

def get_static_google_map(filename_wo_extension, center=None, zoom=None, imgsize="500x500", imgformat="jpeg",
                          maptype="roadmap", markers=None ):


    """retrieve a map (image) from the static google maps server 

     See: http://code.google.com/apis/maps/documentation/staticmaps/

        Creates a request string with a URL like this:
        http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512&maptype=roadmap
&markers=color:blue|label:S|40.702147,-74.015794&sensor=false"""

    # assemble the URL
    requestg = "http://maps.google.com/maps/api/staticmap?"  # base URL, append query params, separated by &
    # if center and zoom  are not given, the map will show all marker locations

    if center != None:
        requestg += "center=%s&" % center
        # request += "center=%s&" % "40.714728, -73.998672"   # latitude and longitude (up to 6-digits)
    # if center != None:
    #     requestg += "zoom=%i&" % zoom  # zoom 0 (all of the world scale ) to 22 (single buildings scale)

    requestg += "size=%ix%i&" % (imgsize)
    requestg += "format=%s&" % imgformat
    requestg += "maptype=%s&" % maptype
    # add markers (location and style)

    if markers != None:
        for marker in markers:
            requestg += "%s&" % marker
    requestg += "mobile=true&"  # optional: mobile=true will assume the image is shown on a small screen (mobile device)
    requestg += "sensor=false&"  # must be given, deals with getting loction from mobile device
    print(requestg.replace(" ","%20"))
    return (requestg.replace(" ","%20"))
    # a = urllib.request.urlretrieve(requestg, filename_wo_extension + "." + imgformat)  # Option 1: save image directly to disk
    # print(a)

def yelpapi(term,location):
    # BASE_YELP = 'https://api.yelp.com/v3/businesses/search?term='+term+'&location='+location+'&limit=3'
    rapid = RapidConnect("default-application_5a246d92e4b0218e3e35f338", "c756cc4b-19a6-4574-b215-0f2c604d5960")

    result = rapid.call('YelpAPI', 'getBusinesses', {
        'term': term,
        'limit': '3',
        # 'categories': 'italian',
        'accessToken': 'BO0AYqJQdXB7nrSehYzcOxBbAAGieshsFgPK1_clBWY_-fesovCVPiklv_CGOXVM0hJHGf9_b'
                       'i32r-Gro3JFtdhzakOOXeQWFyzBREzKwJUlmCN3xOYzmcK_TmwkWnYx',
        'location': location
    })
    # result = json.loads(result.getresponse().read().decode('utf-8'))
    # pprint.pprint(result)
    # print(result["businesses"][0]["name"],result["businesses"][0]["rating"],result["businesses"][0]["phone"],
    #       result["businesses"][0]["coordinates"]["latitude"],result["businesses"][0]["coordinates"]["longitude"])
    return (result["businesses"][0]["name"],result["businesses"][0]["rating"],result["businesses"][0]["phone"],
          result["businesses"][0]["coordinates"]["latitude"],result["businesses"][0]["coordinates"]["longitude"])


def diagflowapi(query):
    CLIENT_ACCESS_TOKEN = '95619c30bfbd46088f39b5f813a82bde'
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()

    request.lang = 'en'  # optional, default value equal 'en'

    request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"

    request.query = query

    # response = request.getresponse()
    # pprint.pprint(response)
    response = json.loads(request.getresponse().read().decode('utf-8'))
    # message = response['result']['parameter']['location']
    # pprint.pprint(response)
    message1 = response['result']['parameters']['Restaurant'][0]
    message2 = response['result']['parameters']['location']['city']
    # print(message1)
    # print(message2)
    return message1,message2
    # print (response.read())