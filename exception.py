
import logging
logger = logging.getLogger('common_exception_handler')

class excption_code:
    INVALID_RUN_FILE = "invalid_run_file"
    BLANK = 'blank'
    REQUIRED = 'required'
    INVALID_CODE = 'invalid_code'
    MAX_VALUE = 'max_value'

# 예외 처리 함수
def exception_handler(error_msg):
    logger.error(error_msg)
    message = None
    code = None
    detail = None
    
    try:
        if error_msg == excption_code.INVALID_RUN_FILE:
            message = "실행 파일이 존재하지 않습니다."
            code = excption_code.INVALID_RUN_FILE
        elif error_msg == excption_code.BLANK or error_msg == excption_code.REQUIRED:
            message = "필수 값이 누락되었습니다."
            code = error_msg  
        elif error_msg == excption_code.INVALID_CODE:
            message = "잘못된 코드입니다."
            code = excption_code.INVALID_CODE
        else:
            message = "알 수 없는 오류가 발생했습니다."
            code = "unknown_error"
    except Exception as exc:
        code = "internal_server_error"
        detail = str(exc)
        logger.error(detail)
        # logger.debug(traceback.format_exc())