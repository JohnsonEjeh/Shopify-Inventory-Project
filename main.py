import configparser
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

##############
version = '0.1'
##############

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///inventory.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

config = configparser.ConfigParser()
config.read('config.ini')
config.set('systemsettings', 'version', version)

column_header = ('Name',
                 'Description',
                 'Location',
                 'Amount',
                 'Data Sheet',
                 'Entry Date',
                 'Updated Date',
                 'Remark')


class AddForm(FlaskForm):
    name = StringField("Component Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    amount = StringField("Amount", validators=[DataRequired()])
    datasheet = StringField("Data sheet", validators=[DataRequired()])
    remark = StringField("Remark", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditForm(FlaskForm):
    name = StringField("Component Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    amount = StringField("Amount", validators=[DataRequired()])
    datasheet = StringField("Datasheet", validators=[DataRequired()])
    remark = StringField("Remark", validators=[DataRequired()])
    submit = SubmitField("Submit")


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    entry_date = db.Column(db.String(250), nullable=False)
    updated_date = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    amount = db.Column(db.String(250), nullable=True)
    location = db.Column(db.String(250), nullable=True)
    remark = db.Column(db.String(250), nullable=True)
    data_sheet = db.Column(db.String(250), nullable=True)


db.create_all()


# i = Inventory(
#     name='Johnson',
#     description='it',
#     location='here',
#     entry_date=2022,
#     amount=1,
#     updated_date=2022,
#     remark='good',
#     data_sheet='N/A'
# )
# db.session.add(i)
# db.session.commit()


@app.route('/')
def home():

    form = EditForm()
    get_components = Inventory.query.all()
    return render_template('index.html', config=config, table_components=get_components,
                           column_header=column_header, form=form
                           )


@app.route('/add_to_db', methods=['POST', 'GET'])
def add_to_db():
    form = AddForm()
    date = datetime.datetime
    if form.validate_on_submit():
        components_to_add = Inventory(
            name=form.name.data,
            description=form.description.data,
            location=form.location.data,
            amount=form.amount.data,
            data_sheet=form.datasheet.data,
            entry_date=str(date.today().strftime("%B %d, %Y")),
            updated_date='N/A',
            remark=form.remark.data
        )
        db.session.add(components_to_add)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


@app.route('/delete')
def delete():

    inventory_id = request.args.get('id')
    inventory_to_remove = Inventory.query.get(inventory_id)
    deleted_name = inventory_to_remove.name
    deleted_description = inventory_to_remove.description
    deleted_location = inventory_to_remove.location
    deleted_amount = inventory_to_remove.amount
    deleted_data_sheet = inventory_to_remove.data_sheet
    deleted_entry_date = inventory_to_remove.entry_date
    deleted_updated_date = inventory_to_remove.updated_date
    deleted_remark = inventory_to_remove.remark
    db.session.delete(inventory_to_remove)
    db.session.commit()
    flash(f'{deleted_name} has been deleted. Click Undelete to add the item back,  Otherwise Click view component to see Inventory')

    return render_template('delete.html', deleted_name=deleted_name, deleted_description=deleted_description,
                           deleted_location=deleted_location, deleted_amount=deleted_amount,
                           deleted_data_sheet=deleted_data_sheet, deleted_entry_date=deleted_entry_date,
                           deleted_updated_date=deleted_updated_date, deleted_remark=deleted_remark,)


@app.route('/undelete', methods=['GET', 'POST'])
def undelete():
    deleted_name = request.args.get('deleted_name')
    deleted_description = request.args.get('deleted_description')
    deleted_location = request.args.get('deleted_location')
    deleted_amount = request.args.get('deleted_amount')
    deleted_data_sheet = request.args.get('deleted_data_sheet')
    deleted_entry_date = request.args.get('deleted_entry_date')
    deleted_updated_date = request.args.get('deleted_updated_date')
    deleted_remark = request.args.get('deleted_remark')
    if request.method == 'GET' or request.method == 'POST':
        components_to_add = Inventory(
            name=deleted_name,
            description=deleted_description,
            location=deleted_location,
            amount=deleted_amount,
            data_sheet=deleted_data_sheet,
            entry_date=deleted_entry_date,
            updated_date=deleted_updated_date,
            remark=deleted_remark
        )
        db.session.add(components_to_add)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    date = datetime.datetime
    inventory_id = request.args.get('id')
    get_component = Inventory.query.get(inventory_id)
    form = EditForm(
        name=get_component.name,
        description=get_component.description,
        location=get_component.location,
        amount=get_component.amount,
        remark=get_component.remark,
        datasheet=get_component.data_sheet
    )

    if form.validate_on_submit():
        get_component.name = form.name.data
        get_component.description = form.description.data
        get_component.location = form.location.data
        get_component.amount = form.amount.data
        get_component.remark = form.remark.data
        get_component.data_sheet = form.datasheet.data
        get_component.updated_date = str(date.today().strftime("%B %d, %Y"))
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', config=config, get_component=get_component,
                           column_header=column_header, form=form)


if __name__ == '__main__':
    app.run(debug=True)
