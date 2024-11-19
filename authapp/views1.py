# from django.shortcuts import render
from django.http import JsonResponse
# from rest_framework.views import APIView
# from rest_framework.response import Response
import psycopg
from configparser import ConfigParser
# from config import config
import jwt
# import datetime

# Get user login and password input
usr_login, usr_pass = input().split()
secret_key = 'Aspyr123'

# response = {
#     'message' : '',
#     'status' : 0,
#     'token': ''
# }


def config(filename = 'database.ini', section = 'postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} is not found in the {1} file'.format(section, filename))
    
    return db


def generate_jwt(usr_login):
    payload = {'login': usr_login}
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


# class AuthenticateView(APIView):
    
def post(usr_login, usr_pass):
    
    # usr_login = request.data.get('login')
    # usr_pass = request.data.get('password')

    try:
        connection = None
        params = config()
        print('Connecting to the PostgreSQL database...')
        connection = psycopg.connect(**params)

        # Create a cursor to interact with the database
        crsr = connection.cursor()

        # Use parameterized queries to prevent SQL injection
        crsr.execute("""
            SELECT password
            FROM credentials
            WHERE login = %s
        """, (usr_login,))

        # Fetch the result (which should be the password stored in the DB)
        password = crsr.fetchone()

        # Check if password matchesabc
        if password and password[0] == usr_pass:
            print('Authenticated')
            token = generate_jwt(usr_login)
            # return JsonResponse({'message': 'Logged in successfully', 'token':token}, status=200)
                    
        else:
            print('Wrong password or username')
            return JsonResponse({'error':'Invalid login or password'}, status=401)
            
        crsr.close()

    except (Exception, psycopg.DatabaseError) as error:
        print(f"Error: {error}")
        print("status = 500, server unreachable")
        
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated.')

    # print(response)

# Call the function with user login and password
post(usr_login, usr_pass)
