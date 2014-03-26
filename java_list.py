def get_str_list(java_json_list):
    str_without_square = java_json_list[1: -1]
    str_list = str_without_square.split(', ')
    
    return str_list