class Authentication:
    def __init__(self):
        self.email = None
        self.password = None
    
    def set_user(self, email, password):
        self.email = email
        self.password = password

    def get_user_email(self):
        return self.email

    def logout(self):
        self.email = None
        self.password = None