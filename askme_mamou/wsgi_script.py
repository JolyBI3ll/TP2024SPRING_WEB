def application(environ, start_response):
    # Получение параметров запроса GET
    query_string = environ.get('QUERY_STRING', '')
    get_params = query_string.split('&')
    get_params_dict = {k: v for k, v in (x.split('=') for x in get_params if '=' in x)}

    # Получение параметров запроса POST
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
    post_params = request_body.split('&')
    post_params_dict = {k: v for k, v in (x.split('=') for x in post_params if '=' in x)}

    # Формирование ответа
    response_body = (
        f"GET parameters: {get_params_dict}\n\n"
        f"POST parameters: {post_params_dict}\n"
    )
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]

    # Вывод для отладки
    print(f"Request method: {environ.get('REQUEST_METHOD')}")
    print(f"GET parameters: {get_params_dict}")
    print(f"POST parameters: {post_params_dict}")

    start_response(status, headers)
    return [response_body.encode('utf-8')]


if __name__ == '__main__':
    from waitress import serve

    print("Serving on port 8081.")
    serve(application, host='localhost', port=8081)
