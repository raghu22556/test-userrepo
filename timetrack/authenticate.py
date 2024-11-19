import jwt

SECRET_KEY = 'Aspyr12345'

def authenticate_request(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload  # Payload will contain the decoded data (e.g., user info)
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

# Example usage