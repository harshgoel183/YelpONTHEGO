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
    globalCount = 0
    query = request.POST.get('Body','')
    print(query)
    # print(request.__dict__)
    term,location = diagflowapi(query)

    print(term,location)
    name, rating, phone, longitude, latitude=yelpapi(term,location)

    # name,rating,phone,latitude,longitude = yelpapi(term,location)
    print(name,rating,phone,longitude,latitude)
    # define a series of location markers and their styles
    # syntax:  markers=markerStyles|markerLocation1|markerLocation2|... etc.
    marker_list = []
    # marker_list.append("markers=color:blue|label:S|11211|11206|11222")  # blue S at several zip code's centers
    msgStr = ""
    for i in range(0,len(name)):
        marker_list.append("markers=|label:"+str(i+1)+"|color:0xFFFF00|"+str(latitude[i])+","+str(longitude[i])+"|")  # tiny yellow B at lat/long B ko resturnt name dena hai
        msgStr += "\n"+str(i+1)+") "+str(name[i]) +", Rating: " +str(rating[i]) +", Ph: "+str(phone[i])
    # marker_list.append(
    #     "markers=size:mid|color:red|label:6|Brooklyn+Bridge,New+York,NY")  # mid-sized red 6 at search location
    # see http://code.google.com/apis/maps/documentation/staticmaps/#Markers
    googleUrl = get_static_google_map("google_map_example3", center=location, imgsize=(400, 400), imgformat="png", markers=marker_list)
    # Start our TwiML response

    resp = MessagingResponse()
    # Add a text message


    msg = resp.message(msgStr)

    # Add a picture message
    f = open(r'C:\Users\Harsh\Documents\GitHub\YelpONTHEGO\djtwilio\djtwilio\static\images\staticmap'+str(globalCount)+'.png','wb')
    f.write(requests.get(googleUrl).content)
    f.close()

    msg.media("/static/images/staticmap"+str(globalCount)+".png")
    globalCount += 1
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

def yelpapi(term,location,limiter = 3):
    name = []
    rating = []
    phone = []
    latitude = []
    longitude = []
    # BASE_YELP = 'https://api.yelp.com/v3/businesses/search?term='+term+'&location='+location+'&limit=3'
    rapid = RapidConnect("default-application_5a246d92e4b0218e3e35f338", "c756cc4b-19a6-4574-b215-0f2c604d5960")

    result = rapid.call('YelpAPI', 'getBusinesses', {
        'term': term,
        'limit': limiter,
        # 'categories': 'italian',
        'accessToken': 'BO0AYqJQdXB7nrSehYzcOxBbAAGieshsFgPK1_clBWY_-fesovCVPiklv_CGOXVM0hJHGf9_b'
                       'i32r-Gro3JFtdhzakOOXeQWFyzBREzKwJUlmCN3xOYzmcK_TmwkWnYx',
        'location': location
    })
    # result = json.loads(result.getresponse().read().decode('utf-8'))
    # pprint.pprint(result)
    # print(result["businesses"][0]["name"],result["businesses"][0]["rating"],result["businesses"][0]["phone"],
    #       result["businesses"][0]["coordinates"]["latitude"],result["businesses"][0]["coordinates"]["longitude"])
    for i in range(0,limiter):
        name.append(result["businesses"][i]["name"])
        rating.append(result["businesses"][i]["rating"])
        phone.append(result["businesses"][i]["phone"])
        longitude.append(result["businesses"][i]["coordinates"]["longitude"])
        latitude.append(result["businesses"][i]["coordinates"]["latitude"])
    return (name,rating,phone,longitude,latitude)


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
    pprint.pprint(response)
    if 'restaurant' or 'hotel' in query.lower():

        rest1 = response['result']['parameters']['Restaurant'][0]
        # message2 = response['result']['parameters']['location'][0]
        rest2 = response['result']['parameters']['location'][0].values()
        rest2 = list(rest2)
        # print("harsh")
        return rest1, rest2[0]
    elif 'gas' in query.lower():
        gas1 = response['result']['parameters']['Gas'][0]
        # message2 = response['result']['parameters']['location'][0]
        gas2 = response['result']['parameters']['location'].values()
        gas2 = list(gas2)
        return gas1, gas2[0]
    # message1 = response['result']['parameters']['Restaurant'][0]
    # # message2 = response['result']['parameters']['location'][0]
    # message2 = response['result']['parameters']['location'][0].values()
    # message2 = list(message2)
    # print(v[0])

    # return message1,message2[0]
    # print (response.read())