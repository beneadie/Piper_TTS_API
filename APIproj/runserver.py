from waitress import serve

from APIproj.wsgi import application
# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html

if __name__ == '__main__':
    serve(application, host = 'localhost', port='8080', max_request_body_size=104857600)