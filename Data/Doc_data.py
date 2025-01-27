from Classes.Clinics import Doctor

list_of_doctors = []

doctor1 = Doctor('John','Brown',1, 1, 'Cardiologist '
                                      'with specialization in heart disease')

list_of_doctors.append(doctor1)
doctor2 = Doctor('Jane','Doe',2, 2, 'Pediatrician '
                                      'with specialisation')


specialisation_ids = {1: 'Cardiologist', 2: 'Pediatrician'}