import http.client
import json
import urllib.parse

def get_user_info(screen_name):
    conn = http.client.HTTPSConnection("api.apidance.pro")
    
    headers = {
        'apikey': 'socsapueb0mjukcjc2gv1nwwiw3n6m'
    }
    
    params = urllib.parse.urlencode({
        'screen_name': screen_name.replace('@', '')
    })
    
    conn.request("GET", f"/1.1/users/show.json?{params}", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return json.loads(data.decode("utf-8"))

def get_user_following(screen_name):
    conn = http.client.HTTPSConnection("api.apidance.pro")
    
    headers = {
        'apikey': 'socsapueb0mjukcjc2gv1nwwiw3n6m'
    }
    
    params = urllib.parse.urlencode({
        'screen_name': screen_name.replace('@', ''),
        'count': 200  # Maximum allowed by Twitter API
    })
    
    conn.request("GET", f"/1.1/friends/list.json?{params}", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return json.loads(data.decode("utf-8"))

if __name__ == "__main__":
    # Test with one of our target users
    test_user = "@cz_binance"
    
    print(f"Getting user info for {test_user}...")
    user_info = get_user_info(test_user)
    print(f"User ID: {user_info.get('id', 'Not found')}")
    print(f"Name: {user_info.get('name', 'Not found')}")
    print(f"Following count: {user_info.get('friends_count', 'Not found')}")
    
    print(f"\nGetting following list for {test_user}...")
    following_data = get_user_following(test_user)
    
    if 'users' in following_data:
        print(f"Retrieved {len(following_data['users'])} users that {test_user} follows")
        print("Sample of first 5 following:")
        for i, user in enumerate(following_data['users'][:5]):
            print(f"{i+1}. @{user['screen_name']} - {user['name']}")
    else:
        print("Error retrieving following list")
        print(following_data)
