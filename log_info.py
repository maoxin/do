from datetime import datetime

def log_info(operation_name, client):
    tm = datetime.now()
    info = {
        'operation_name': operation_name,
        'time': str(tm),
        
    }
    
    print 'operation: ' + operation_name + ' time: ' + str(tm)
    client.server_log.operation_log.insert(info)