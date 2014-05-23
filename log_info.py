from datetime import datetime

def log_info(operation_name, log_client):
    tm = datetime.now()
    info = {
        'operation_name': operation_name,
        'time': str(tm),
        
    }
    
    print 'operation: ' + operation_name + ' time: ' + str(tm)
    log_client.insert(info)