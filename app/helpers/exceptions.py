from app.helpers.response import Response
from app.helpers.logger import logger

def handle_exception(foo, *args, **kwargs):
    try: 
        result = foo(*args, **kwargs)
        logger.info(result)
        return Response.success(result)
    except Exception as e:
        return Response.error(str(e))