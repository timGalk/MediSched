class Doctor:
    def __init__(self, name: str, doc_id:int, spec_id:int, description:str, price:int):
        self.name = name
        self.doc_id = doc_id
        self.spec_id = spec_id
        self.description = description

class User:
    def __init__(self, fname: str, lname: str, user_id:int, phone:int, basket:list[Doctor], order_history:list[Doctor]):
        self.fname = fname
        self.lname = lname
        self.user_id = user_id
        self.phone = phone
        self.basket = basket

# class Specialization:
#     def __init__(self, spec_id:int, desc:str ):
#         self.spec_id = spec_id

class Order:
    def __init__(self, doctor_id:int, user_id:int, date:str, time:str, status:bool):
        self.doctor_id = doctor_id
        self.user_id = user_id
        self.date = date
        self.time = time
        self.status = status


class Slot :
    def __init__(self, doctor_id :int, date:str, time:str):
        self.doctor_id = doctor_id
        self.date = date
        self.time = time


