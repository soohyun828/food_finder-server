import json
import requests

latitude = '37.2432629'
longitude = '127.0801557'

def test_signup(base_url):
    print('////////////Sign Up////////////')
    username = input('Enter username:')

    # Check for duplicate ID
    check_url = f'{base_url}/check_username/{username}'
    check_response = requests.get(check_url)

    if check_response.status_code == 200:
        check_result = check_response.json()
        if check_result['success']:
            print(check_result['message'])

            # If ID is available, enter pw and phoneNumber
            phone_number = input('Enter phone number:')
            password = input('Enter password:')
            print('/////////////////////////////////')

            signup_url = f'{base_url}/signup'
            data = {
                'username': username,
                'phoneNumber': phone_number,
                'password': password,
            }

            try:
                response = requests.post(
                    signup_url,
                    headers={'Content-Type': 'application/json'},
                    json=data
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f'Signup Result: {result}')
                else:
                    print(f'Failed to sign up. Status code: {response.status_code}')
            except Exception as e:
                print(f'Error: {e}')
        else:
            print('이미 사용중인 ID 입니다.')
    else:
        print(f'Failed to check username. Status code: {check_response.status_code}')


def test_login(base_url):
    print('////////////Login////////////')
    username = input('Enter username:')
    password = input('Enter password:')
    print('/////////////////////////////')

    login_url = f'{base_url}/login'
    data = {
        'username': username,
        'password': password,
    }

    try:
        response = requests.post(
            login_url,
            headers={'Content-Type': 'application/json'},
            json=data
        )

        print(f"Response status code: {response.status_code}")
        # print(f"Response JSON: {response.json()}")

        if response.status_code == 200:
            result = response.json()
            print(f'Login Result: {result}')
        else:
            print(f'Login failed. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')


    # print('////////////Login////////////')
    # username = input('Enter username:')
    # password = input('Enter password:')
    # print('/////////////////////////////////')

    # login_url = f'{base_url}/login'
    # data = {
    #     'username': username,
    #     'password': password,
    # }

    # try:
    #     response = requests.post(
    #         login_url,
    #         headers={'Content-Type': 'application/json'},
    #         json=data
    #     )

    #     if response.status_code == 200:
    #         result = response.json()
    #         print(f'Login Result: {result}')
    #     else:
    #         print(f'Login failed. Status code: {response.status_code}')
    # except Exception as e:
    #     print(f'Error: {e}')


def test_restaurant_list(base_url):
    print('////////////RestaurantListUp////////////')
    category = input('Enter category:')
    menu = input('Enter menu:')
    username = input('Enter username:')
    # latitude = input('Enter latitude:')
    # longitude = input('Enter longitude:')
    print('/////////////////////////////////////////')

    restaurant_list_url = f'{base_url}/{category}/{menu}/{username}/{latitude}/{longitude}'
    try:
        response = requests.get(restaurant_list_url)

        if response.status_code == 200:
            result = response.json()
            print(f'Restaurant List Result: {result}')
        else:
            print(f'Failed to get restaurant list. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')


def test_search(base_url):
    print('////////////Search////////////')
    menu = input('Enter Search Keyword (menu):')
    latitude = input('Enter latitude:')
    longitude = input('Enter longitude:')
    print('/////////////////////////////////////////')

    search_url = f'{base_url}/home/search/{latitude}/{longitude}'
    data = {'menu': menu}
    try:
        response = requests.post(
            search_url,
            headers={'Content-Type': 'application/json'},
            json=data
        )

        if response.status_code == 200:
            result = response.json()
            print('Search Result:')
            for restaurant in result:
                print(f"Resnum: {restaurant['resnum']}")
                print(f"Resname: {restaurant['resname']}")
                print(f"Menu: {restaurant['menu']}")
                print(f"Address: {restaurant['address']}")
                print(f"Image URL: {restaurant['imageURL']}")
                print(f"Category: {restaurant['category']}")
                print(f"Distance: {restaurant['distance']} meters")
                print('-----------------------------')
        else:
            print(f'Failed to search. Status code: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    base_url = 'http://127.0.0.1:5000/home'
    
    # Test signup
    #test_signup(base_url)

    # Test login
    test_login(base_url)

    # # Test restaurant listing
    test_restaurant_list(base_url)
