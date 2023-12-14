import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

void main() async {
  final baseUrl = 'http://127.0.0.1:5000/home';

  // Test signup
  await testSignup(baseUrl);

  // Test login
  await testLogin(baseUrl);

  // Test restaurant listing
  await testRestaurantList(baseUrl);
}

Future<void> testSignup(String baseUrl) async {
  print('////////////Sign Up////////////');
  print('Enter username:');
  final username = stdin.readLineSync();

  // id 중복 확인
  final checkUrl = '$baseUrl/check_username/$username';
  final checkResponse = await http.get(Uri.parse(checkUrl));

  if (checkResponse.statusCode == 200) {
    final checkResult = jsonDecode(checkResponse.body);
    if (checkResult['available']) {
      print('사용가능한 ID 입니다.');

      // id 사용가능하면 pw, phoneNumber 입력
      print('Enter phone number:');
      final phoneNumber = stdin.readLineSync();

      print('Enter password:');
      final password = stdin.readLineSync();
      print('/////////////////////////////////');

      final signupUrl = '$baseUrl/signup';
      final data = {
        'username': username,
        'phoneNumber': phoneNumber,
        'password': password,
      };

      try {
        final response = await http.post(
          Uri.parse(signupUrl),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(data),
        );

        if (response.statusCode == 200) {
          final result = jsonDecode(response.body);
          print('Signup Result: $result');
        } else {
          print('Failed to sign up. Status code: ${response.statusCode}');
        }
      } catch (e) {
        print('Error: $e');
      }
    } else {
      print('Username is already taken. Choose another username.');
    }
  } else {
    print('Failed to check username. Status code: ${checkResponse.statusCode}');
  }
}

Future<void> testLogin(String baseUrl) async {
  print('////////////Login////////////');
  print('Enter username:');
  final username = stdin.readLineSync();

  print('Enter password:');
  final password = stdin.readLineSync();
  print('/////////////////////////////////');

  final loginUrl = '$baseUrl/login';
  final data = {
    'username': username,
    'password': password,
  };

  try {
    final response = await http.post(
      Uri.parse(loginUrl),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );

    if (response.statusCode == 200) {
      final result = jsonDecode(response.body);
      print('Login Result: $result');
    } else {
      print('Login failed. Status code: ${response.statusCode}');
    }
  } catch (e) {
    print('Error: $e');
  }
}

Future<void> testRestaurantList(String baseUrl) async {
  print('////////////RestaurantListUp////////////');
  print('Enter category:');
  final category = stdin.readLineSync();

  print('Enter menu:');
  final menu = stdin.readLineSync();

  print('Enter username:');
  final username = stdin.readLineSync();

  print('Enter latitude:');
  final latitude = stdin.readLineSync();

  print('Enter longitude:');
  final longitude = stdin.readLineSync();
  print('/////////////////////////////////////////');

  final restaurantListUrl = '$baseUrl/$category/$menu/$username/$latitude/$longitude';
  try {
    final response = await http.get(Uri.parse(restaurantListUrl));

    if (response.statusCode == 200) {
      final result = jsonDecode(response.body);
      print('Restaurant List Result: $result');
    } else {
      print('Failed to get restaurant list. Status code: ${response.statusCode}');
    }
  } catch (e) {
    print('Error: $e');
  }
}


Future<void> testSearch(String baseUrl) async {
  print('////////////Search////////////');

  print('Enter Search Keyword (menu):');
  final menu = stdin.readLineSync();

  print('Enter latitude:');
  final latitude = stdin.readLineSync();

  print('Enter longitude:');
  final longitude = stdin.readLineSync();
  print('/////////////////////////////////////////');

  final searchUrl = '$baseUrl/home/search/$latitude/$longitude';
  final data = {'menu': menu};
  try {
    final response = await http.post(
      Uri.parse(searchUrl),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );

    if (response.statusCode == 200) {
      final result = jsonDecode(response.body);
      print('Search Result:');
      for (var restaurant in result) {
        print('Resnum: ${restaurant['resnum']}');
        print('Resname: ${restaurant['resname']}');
        print('Menu: ${restaurant['menu']}');
        print('Address: ${restaurant['address']}');
        print('Image URL: ${restaurant['imageURL']}');
        print('Category: ${restaurant['category']}');
        print('Distance: ${restaurant['distance']} meters');
        print('-----------------------------');
      }
    } else {
      print('Failed to search. Status code: ${response.statusCode}');
    }
  } catch (e) {
    print('Error: $e');
  }
}
