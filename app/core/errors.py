from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError

def error_structure(code, message, details):
    return {
        'error': {
            'code': code, 
            'message': message, 
            'details': details
            }
        }
    
def status_to_code(status_code):
    match status_code:
        case 400: code = 'bad_request'
        case 401: code = 'unauthorized'
        case 403: code = 'forbidden'
        case 404: code = 'not_found'
        case 422: code = 'validation_error'
        case 500: code = 'internal_error'
        case _: code = 'http_error'
    return code
        

def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    code = status_to_code(exc.status_code)
    payload = error_structure(code, str(exc.detail), None)
    return JSONResponse(status_code=exc.status_code, content=payload)

def request_validation_error_handler(request: Request, exc: RequestValidationError):
    code = status_to_code(422)
    detail = exc.errors()
    payload = error_structure(code, message='Validation error', details=detail)
    return JSONResponse(status_code=422, content=payload)

def exception_handler(request: Request, exc: Exception):
    code = status_to_code(500)
    payload = error_structure(code, message = "Internal server error", details = None)
    return JSONResponse(status_code=500, content=payload)

