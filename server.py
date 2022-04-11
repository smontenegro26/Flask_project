from flask import Flask, json, jsonify, request, render_template
import csv

DATA_FILE = 'data.csv'

def load_data(DATA_FILE):
  with open(DATA_FILE, 'r', newline='') as csv_file:
    reader = csv.DictReader(csv_file,  delimiter=',')
    csv_data = []
    csv_data = [row for row in reader] 
  return csv_data

def append_data(DATA_FILE, new_data):
  row = new_data
  with open(DATA_FILE, 'a', newline='') as csv_file:
    writer = csv.DictWriter (csv_file,list(reversed(new_data.keys())))
    writer.writerow(row)

def rewrite_data(DATA_FILE, new_data):
  with open(DATA_FILE, 'w', newline='') as csv_file:
    writer = csv.DictWriter (csv_file,list(new_data[0].keys()))
    writer.writeheader()
    {writer.writerow(row) for row in new_data}
    
def validate_data (data):
    if_error = True
    error_key = [] 
    for key, val in  data.items():
      if key in ["catchphrase" , "first companion"]:
          if_error = isinstance(val, str)
      elif key in ["regeneration" , "year"]:
          if_error =  isinstance(val, int)
      if not if_error:
          error_key = key
          break
    return if_error, error_key

app = Flask(__name__)

@app.route('/doctors')
def doctor_index():
  doctors = load_data(DATA_FILE)
  return render_template('index.html', doctors = doctors)

# @app.route('/doctors/new')
# def load_new_data_form():
#     return render_template('add.html')

@app.route('/doctors/<doctor_id>')
def doctors_show(doctor_id):
  doctors = load_data(DATA_FILE)
  for doctor in doctors:
    if doctor['regeneration'] == doctor_id:
      return render_template('show.html', doctor=doctor)
  return { 'error': 'Not Found' }, 404

@app.route('/doctors', methods=['POST'])
def doctors_create():
  doctors = load_data(DATA_FILE)
  new_doctor = request.get_json()
  if_error, key = validate_data (dict(new_doctor))
  if if_error:
    new_doctor['regeneration'] = str(len(doctors) + 1)
    append_data(DATA_FILE, dict(new_doctor))
    return { 'message': 'Doctor regenerated successfully'}, 201
  return { 'message': '{} data could not be validated'.format(key)}, 422

@app.route('/doctors/<doctor_id>', methods=['PATCH'])
def doctors_update(doctor_id):
  doctors = load_data(DATA_FILE)
  updates = request.get_json()
  if_error, key = validate_data (dict(updates))
  if if_error:
    done =  {doctors[i].update(updates) for i in range(len(doctors)) if doctors[i]['regeneration'] == doctor_id}
    if done:
      rewrite_data(DATA_FILE, doctors)
      return { 'message': 'Doctor updated successfully' }, 201
    return { 'error': 'Not Found' }, 404
  return { 'message': '{} data could not be validated'.format(key)}, 422

@app.route('/doctors/<doctor_id>', methods=['DELETE'])
def doctor_delete(doctor_id):
  doctors = load_data(DATA_FILE)
  found_doctor_idx = None
  found_doctor_idx = next(i for i in range(len(doctors)) if doctors[i]['regeneration'] == doctor_id)

  if found_doctor_idx != None:
    doctors.pop(found_doctor_idx)
    rewrite_data(DATA_FILE, doctors)
    return { 'message': 'Doctor deleted successfully' }
  return { 'error': 'Not Found' }, 404

app.run()
