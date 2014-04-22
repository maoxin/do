from datetime import datetime

def log_info(operation_name, client):
    tm = datetime.now()
    info = {
        'operation_name': operation_name,
        'time': tm,
        
    }
    
    print 'operation: ' + operation_name + ' time: ' + tm
    client.server_log.operation_log.insert(info)