from app.extensions import db

class EmployeeBasicInfo(db.Model):
    __tablename__ = 'employee_basic_info'

    id = db.Column(db.Integer, primary_key= True)
    employee_id = db.Column(db.String, unique= True, nullable= False)
    first_name = db.Column(db.String(100), nullable= False)
    date_of_joining = db.Column(db.Date, nullable= False)

    salary_info = db.relationship('EmployeeSalaryInfo', backref='employee', uselist=False, cascade="all, delete-orphan")
    contact_info = db.relationship('EmployeeContactInfo', backref='employee', uselist=False, cascade="all, delete-orphan")


class EmployeeSalaryInfo(db.Model):
    __tablename__ = 'employee_salary_info'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employee_basic_info.employee_id'), nullable=False)
    salary = db.Column(db.Float)
    pay_grade = db.Column(db.String(50))


class EmployeeContactInfo(db.Model):
    __tablename__ = 'employee_contact_info'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employee_basic_info.employee_id'), nullable=False)
    phone_number = db.Column(db.String(40))
    city = db.Column(db.String(100))

