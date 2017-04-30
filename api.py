import os
from flask import Flask, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

basedir = os.path.abspath(os.path.abspath(__file__))
db_path = os.path.join(basedir, '../data.sqlite')

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}'.format(db_path)

Swagger(app)
db = SQLAlchemy(app)


class ValidationError(ValueError):
    pass


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    def get_url(self):
        return url_for('get_customer', id=self.id, _external=True)

    def export_data(self):
        return {
            'self_url': self.get_url(),
            'name': self.name
        }

    def import_data(self, data):
        try:
            self.name = data['name']
        except KeyError as e:
            raise ValidationError('Invalid Customer: missing {0}'.format(e.args[0]))
        return self


@app.route('/customers/', methods=['GET'])
def get_customers():
    """
    This is get customers API
    Call this API as a resource
    ---
    tags:
        - Customers List API
    """
    return jsonify({'customers': [customer.get_url() for customer in Customer.query.all()]})


@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    """
    This is customer instance API
    ---
    tags:
        - Customer Instance API
    parameters:
        - name: id
          in: path
          type: integer
          required: true
          description: ID of the customer
    """
    return jsonify(Customer.query.get_or_404(id).export_data())


@app.route('/customers', methods=['POST'])
def new_customer():
    """
    This is create customer API
    ---
    tags:
        - Create Customer API
    parameters:
        - name: body
          in: body
          required: true
          schema: 
            properties:
              name:
                type: string
    """
    customer = Customer()
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({}), 201, {'Location': customer.get_url()}


@app.route('/customers/<int:id>', methods=['PUT'])
def edit_customer(id):
    """
    This is update customer API
    ---
    tags:
        - Update Customer API
    parameters:
        - name: id
          in: path
          type: integer
          required: true
        - name: body
          in: body
          required: true
          schema: 
            properties:
              name:
                type: string
    """

    customer = Customer.query.get_or_404(id)
    customer.import_data(request.json)
    db.session.add(customer)
    db.session.commit()
    return jsonify({})


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)


