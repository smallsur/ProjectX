
def get_log_format(process_info=False, thread_info=False):

    _format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s'

    if thread_info:
        _format = 'thread(%(threadName)s-%(thread)d)'+ ' - ' + _format
    if process_info:
        _format = 'process(%(process)d)'+ ' - ' + _format
    
    return _format


