from passlib.hash import bcrypt

def encrypt(password):
    encrypted_password = bcrypt.encrypt(password)
    
    return encrypted_password
    
def match(true_password, offer_password):
    if bcrypt.verify(offer_password, true_password):
        return True
        
    else:
        return False