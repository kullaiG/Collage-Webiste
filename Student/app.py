from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

class College:
    def __init__(self):
        self.used_ids = set()  # Set to store used IDs
        self.valid_castes = ["OC", "BC", "BC-A", "OBC", "BC-B", "SC", "ST"]

    def student(self, name, age, gender, caste):
        self.Id = self.get_unique_id()
        self.Name = name
        self.Age = age
        self.Gender = gender
        self.Caste = caste

    def get_unique_id(self):
        new_id = len(self.used_ids) + 1  # Assign IDs sequentially
        self.used_ids.add(new_id)
        return new_id

    def to_excel(self, num_students, branch, filename='student_data.xlsx'):
        self.data = {'ID': [], 'Name': [], 'Age': [], 'Gender': [], 'Caste': [], 'Branch': []}  # Initialize data
        self.used_ids = set()  # Reset used IDs for each branch

            # Check if directory exists, create if not
        if not os.path.exists('data'):
            os.makedirs('data')

        filepath = os.path.join('data', filename)

        if not os.path.exists(filepath):  # Create a new file if it doesn't exist
            df = pd.DataFrame(columns=['ID', 'Name', 'Age', 'Gender', 'Caste', 'Branch'])
            df.to_excel(filepath, index=False)

        # Clear existing data for current branch
        self.data['Branch'] = [branch] * num_students  # Add branch column
        for i in range(num_students):
            name = request.form.get(f'name-{i}', '')
            age = int(request.form.get(f'age-{i}', 0))
            gender = request.form.get(f'gender-{i}', '')
            caste = request.form.get(f'caste-{i}', '')

            # Server-side validation
            if name and age and gender and caste and caste in self.valid_castes:
                self.student(name, age, gender, caste)
                self.data['ID'].append(self.Id)  # Append ID
                self.data['Name'].append(self.Name)
                self.data['Age'].append(self.Age)
                self.data['Gender'].append(self.Gender)
                self.data['Caste'].append(self.Caste)
            else:
                # Handle missing or invalid fields gracefully
                self.data['ID'].append('')
                self.data['Name'].append('')
                self.data['Age'].append('')
                self.data['Gender'].append('')
                self.data['Caste'].append('')

        df = pd.DataFrame(self.data)
        with pd.ExcelWriter(filepath, mode='a', engine='openpyxl') as writer:
            sheet_name = f'Sheet_{branch}'  # Combine branch name with 'Sheet_' prefix
            if sheet_name in writer.book.sheetnames:
                existing_index = writer.book.sheetnames.index(sheet_name)
                writer.book.remove(writer.book.worksheets[existing_index])  # Remove existing sheet
            df.to_excel(writer, index=False, sheet_name=sheet_name)

college = College()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save_data():
    try:
        num_students_branch = int(request.form['num_students'])
        branch = request.form['branch']
        college.to_excel(num_students_branch, branch)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
