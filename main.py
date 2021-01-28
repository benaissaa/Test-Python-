from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource,fields, marshal_with
from sqlalchemy.orm import relationship
from flask_rest_paginate import Pagination
from faker import Faker
from flask_restplus import Api, Resource ,fields
app = Flask(__name__)

# __BD__
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paginate-test.db' 
db = SQLAlchemy(app) 
pagination = Pagination(app, db)
ma = Marshmallow(app)
api = Api(app=app, title='Test Python Backend', description='', validate=True)






# __Model Account__

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    malls = db.relationship('Mall', backref='account', lazy=True)  # Many to one 

    
    def __repr__(self):
        return '<Accountt %s>' % self.name


class AccountSchema(ma.Schema):
    class Meta:
        fields = ("id", "name")
        model = Account


account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)

# __Model Mall__

class Mall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    account_id=db.Column(db.Integer, db.ForeignKey('account.id'))
    
    unit = relationship("Unit", uselist=False, back_populates="mall") # one to one 
    

    def __repr__(self):
        return '<Mall %s>' % self.name

class MallSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "account_id")
        model = Mall 

mall_schema = MallSchema()
malls_schema = MallSchema(many=True)              


# __Model Unit__

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    mall_id=db.Column(db.Integer, db.ForeignKey('mall.id'))
    mall = relationship("Mall", back_populates="unit")  # one to one 

    def __repr__(self):
        return '<Unit %s>' % self.name

class UnitSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "mall_id")
        model = Unit 

unit_schema = UnitSchema()
units_schema = UnitSchema(many=True)  


#__ Fileds__

mall_fields = {
    'name': fields.String,
    
    'account_id': fields.Integer
}


account_fields = {
    'name': fields.String,
    'malls': fields.List(fields.Nested(mall_fields))
}

unit_fields = {
    'name': fields.String,
    
    'mall_id': fields.Integer
}


# __API Account__

account_definition = api.model('account Informations', {
    'name': fields.String(required=True)})


@api.route("/accounts")
class AccountListResource(Resource):
    def get(self):

        """
        returns a list of account with pagination
        """
        return pagination.paginate( Account,account_fields)

    @api.expect(account_definition)	
    def post(self):
        """
        Add a new account
        """
        new_account = Account(
            name=request.json['name'],
            
        )
        db.session.add(new_account)
        db.session.commit()
        return account_schema.dump(new_account)


       

@api.route("/accounts/<int:account_id>")
class AccountResource(Resource):
    def get(self, account_id):
        """
        fetch an account with the given id + pagination
        """
        return pagination.paginate(Account.query.filter_by(id=account_id), account_fields)

    @api.expect(account_definition)
    def patch(self, account_id):
        """
        update an account 
        """

        account = Account.query.get_or_404(account_id)
        
        if 'name' in request.json:
            account.name = request.json['name']
        
        db.session.commit()
        return account_schema.dump(account)
       
    def delete(self, account_id):
        """
        delete an account
        """

        account = Account.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()
        return '', 204


# __API Mall__

mall_definition = api.model('mall Informations', {
    'name': fields.String(required=True),
    'account_id': fields.Integer(required=True)
    })

@api.route("/malls")
class MallListResource(Resource):

    def get(self):
        
        return pagination.paginate( Mall,mall_fields)


    @api.expect(mall_definition)
    def post(self):
        new_mall = Mall(
            name=request.json['name'],
            account_id=request.json['account_id'],
            
        )
        db.session.add(new_mall)
        db.session.commit()
        return mall_schema.dump(new_mall) 


@api.route("/malls/<int:mall_id>")
class MallResource(Resource):

    def get(self, mall_id):
        mall = Mall.query.get_or_404(mall_id)
        return mall_schema.dump(mall)

    @api.expect(mall_definition)
    def patch(self, mall_id):
        mall = Mall.query.get_or_404(mall_id)

        if 'name' in request.json:
            mall.name = request.json['name']
        if 'account_id' in request.json:
            mall.account_id  = request.json['account_id']


        db.session.commit()
        return mall_schema.dump(mall)

    def delete(self, mall_id):
        mall = Mall.query.get_or_404(mall_id)
        db.session.delete(mall)
        db.session.commit()
        return '', 204

# __Api Unit__ 

unit_definition = api.model('unit Informations', {
    'name': fields.String(required=True),
    'mall_id': fields.Integer(required=True)
    })


@api.route("/units")
class UnitListResource(Resource):

    def get(self):
        
        return pagination.paginate( Unit,unit_fields)


    @api.expect(unit_definition)
    def post(self):
        new_unit = Unit(
            name=request.json['name'],
            mall_id=request.json['mall_id'],
            
        )
        db.session.add(new_unit)
        db.session.commit()
        return unit_schema.dump(new_unit)


       
@api.route("/units/<int:unit_id>")
class UnitResource(Resource):

    def get(self, unit_id):
        unit = Unit.query.get_or_404(unit_id)
        return unit_schema.dump(unit)

    @api.expect(unit_definition)
    def patch(self, unit_id):
        unit = Unit.query.get_or_404(unit_id)

        if 'name' in request.json:
            unit.name = request.json['name']
        if 'mall_id' in request.json:
            unit.mall_id  = request.json['mall_id']

        db.session.commit()
        return unit_schema.dump(unit)

    def delete(self, unit_id):
        unit = Unit.query.get_or_404(unit_id)
        db.session.delete(unit)
        db.session.commit()
        return '', 204



"""
Seed database
"""
def seed():
    fake = Faker()
    for i in range(100):
        db.session.add(Account(name=fake.name()))
        for j in range(10):
            db.session.add(Mall(name=fake.name(), account_id=i))
            db.session.add(Unit(name=fake.name(), mall_id=j))
    db.session.commit()


"""
Recreate the DB
"""
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()



"""
Run the app
"""
if __name__ == '__main__':
    recreate_db()
    seed()
    app.run(debug=True)