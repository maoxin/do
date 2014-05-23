from passlib.hash import bcrypt

def encrypt(meta_info):
    encrypted_info = bcrypt.encrypt(meta_info)
    
    return encrypted_info
    
def match(true_info, offer_info):
    if bcrypt.verify(offer_info, true_info):
        return True
        
    else:
        return False