from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.sql import func, insert
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os, csv

app = Flask(__name__)
app.secret_user = os.getenv('user', 'admin')
app.secret_key = os.getenv('SECRET', 'Grand2025')
database_uri = os.getenv('DATABASE_URI', 'postgresql://user:password@db/grand') 
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 

def create_user():
    db.create_all()  # Create tables
    # Check if user exists
    user = User.query.filter_by(username=app.secret_user).first()
    if user:
        # update
        user.password = app.secret_key  
        db.session.commit()  
    else:
        # create
        user = User(username=app.secret_user, password=app.secret_key) 
        db.session.add(user)
        db.session.commit()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modèle FEB
class Feb(db.Model):
    feb_id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    target_du_id = db.Column(db.Integer, nullable=True) 


# Modèle Antenna
class Antenna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    du_id = db.Column(db.Integer, unique=True, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # Remplacez ceci par un hachage sécurisé
            login_user(user)
            get_flashed_messages()
            return redirect(url_for('index'))  # Rediriger vers la page d'index après connexion
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required  
def logout():
    logout_user()  # Déconnexion de l'utilisateur
    return redirect(url_for('login'))  # Redirige vers la page de connexion


# Routes pour FEB
@app.route('/')
@login_required
def index():
    febs = Feb.query.all()
    return render_template('index_feb.html', febs=febs)

@app.route('/index_feb')
@login_required
def index_feb():
    febs = Feb.query.all()
    return render_template('index_feb.html', febs=febs)
@app.route('/add_feb', methods=['GET', 'POST'])
@login_required
def add_feb():
    try:
       if request.method == 'POST':

           feb_id=request.form['feb_id'],
           mac_address=request.form['mac_address'],
           ip_address=request.form['ip_address'],
           target_du_id=request.form.get('target_du_id')
           # Convert target_du_id to None if not provided
           if target_du_id == '':
                target_du_id = None  # Default to None if not specified

           new_feb = Feb(
                feb_id=feb_id,
                mac_address=mac_address,
                ip_address=ip_address,
                target_du_id=target_du_id
           )
           db.session.add(new_feb)
           db.session.commit()
           return redirect(url_for('index'))
       return render_template('add_feb.html')
    except Exception as e:
       flash(f'Error: {str(e)} </li><li><strong>The record was not added !</strong> </li>')
       return render_template('add_feb.html')

#@app.route('/edit_feb/<int:feb_id>', methods=['GET', 'POST'])
#@login_required
#def edit_feb(feb_id):
#    try:
#      feb = Feb.query.get_or_404(feb_id)
#      if request.method == 'POST':
#          feb.mac_address = request.form['mac_address']
#          feb.ip_address = request.form['ip_address']
#          feb.target_du_id = request.form.get('target_du_id')
#          db.session.commit()
#          return redirect(url_for('index'))
#      return render_template('edit_feb.html', feb=feb)
#    except Exception as e:
#         flash(f'Error: {str(e)} </li><li><strong>The record was not updated !</strong> </li>')
#         return redirect(url_for('index'))

@app.route('/edit_feb/<int:feb_id>', methods=['POST'])
@login_required
def edit_feb(feb_id):
    try:
        feb = Feb.query.get_or_404(feb_id)
        feb.mac_address = request.form['mac_address']
        feb.ip_address = request.form['ip_address']
        feb.target_du_id = request.form.get('target_du_id')
        if feb.target_du_id == '':
                feb.target_du_id = None  # Default to None if not specified
        db.session.commit()
        flash('FEB record updated successfully!')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error: {str(e)}. The record was not updated!')
        return redirect(url_for('index'))


@app.route('/delete_feb/<int:feb_id>', methods=['POST'])
@login_required
def delete_feb(feb_id):
    feb = Feb.query.get_or_404(feb_id)
    db.session.delete(feb)
    db.session.commit()
    return redirect(url_for('index'))

# Routes pour Antennas
@app.route('/antennas')
@login_required
def index_antenna():
    antennas_febs = db.session.execute(
            text("""
            SELECT *
            FROM get_antennas_with_febs();
            """),
       ).fetchall()
    return render_template('index_antenna.html', antennas_febs=antennas_febs)

#def index_antenna():
#    antennas = Antenna.query.all()
#    return render_template('index_antenna.html', antennas=antennas)

@app.route('/add_antenna', methods=['GET', 'POST'])
@login_required
def add_antenna():
    try:
       if request.method == 'POST':
           new_antenna = Antenna(
               longitude=request.form['longitude'],
               latitude=request.form['latitude'],
               du_id=request.form['du_id']
           )
           db.session.add(new_antenna)
           db.session.commit()
           return redirect(url_for('index_antenna'))
       return render_template('add_antenna.html')
    except Exception as e:
       flash(f'Error: {str(e)} </li><li><strong>The record was not added !</strong> </li>')
       return render_template('add_antenna.html')


@app.route('/edit_antenna/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_antenna(id):
    try:
       antenna = Antenna.query.get_or_404(id)
       if request.method == 'POST':
           antenna.longitude = request.form['longitude']
           antenna.latitude = request.form['latitude']
           antenna.du_id = request.form['du_id']
           db.session.commit()
           flash('Antenna updated successfully!')
           return redirect(url_for('index_antenna'))
       return render_template('edit_antenna.html', antenna=antenna)
    except Exception as e:
       flash(f'Error: {str(e)} </li><li><strong>The record was not updated !</strong> </li>')
       return redirect(url_for('index_antenna'))

#@app.route('/edit_antenna/<int:id>', methods=['POST'])
#@login_required
#def edit_antenna(id):
#    try:
#        antenna = Antenna.query.get_or_404(id)
#        antenna.longitude = request.form['longitude']
#        antenna.latitude = request.form['latitude']
#        antenna.du_id = request.form['du_id']
#        db.session.commit()
#        flash('Antenna updated successfully!')
#        return redirect(url_for('index_antenna'))
#    except Exception as e:
#        flash(f'Error: {str(e)}. The record was not updated!')
#        return redirect(url_for('index_antenna'))


@app.route('/delete_antenna/<int:id>', methods=['POST'])
@login_required
def delete_antenna(id):
    antenna = Antenna.query.get_or_404(id)
    db.session.delete(antenna)
    db.session.commit()
    return redirect(url_for('index_antenna'))

@app.route('/get_du_id', methods=['POST'])
def get_du_id():
    longitude = float(request.form.get('long'))
    latitude = float(request.form.get('lat'))
#    data = request.get_json()
#    longitude = data.get('longitude')
#    latitude = data.get('latitude')
    if longitude is None or latitude is None:
       longitude = 0
       latitude = 0
    if longitude != 0 and latitude != 0 :
       result = db.session.execute(
            text("""
            SELECT du_id, id
            FROM antenna
            ORDER BY ST_Distance(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
            LIMIT 1;
            """),
            {"lon": longitude, "lat": latitude}
       ).fetchone()

       if result is not None:
          du_id = result[0]
          antenna_id = result[1]
          client_ip = request.remote_addr
          feb = Feb.query.filter_by(ip_address=client_ip).first()
          if feb is not None:
             now=func.current_timestamp()
             try:
                 # Attempt to insert using feb_id
                 resupd = db.session.execute(
                     text("""
                                         INSERT INTO feb_antenna (feb_id, antenna_id, last_seen, last_test) 
                                         VALUES (:feb_id, :antenna_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
                                         ON CONFLICT(feb_id) DO UPDATE 
                                         SET antenna_id = EXCLUDED.antenna_id, 
                                             last_seen = EXCLUDED.last_seen, 
                                             last_test = EXCLUDED.last_test;
                                     """),
                     {"feb_id": feb.feb_id, "antenna_id": antenna_id}
                 )
                 db.session.commit()
             except Exception as e:
                 # If there was an integrity error, handle conflict by attempting to insert with antenna_id
                 db.session.rollback()  # Rollback the previous transaction
                 resupd = db.session.execute(
                     text("""
                                         INSERT INTO feb_antenna (feb_id, antenna_id, last_seen, last_test) 
                                         VALUES (:feb_id, :antenna_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
                                         ON CONFLICT(antenna_id) DO UPDATE 
                                         SET feb_id = EXCLUDED.feb_id, 
                                             last_seen = EXCLUDED.last_seen, 
                                             last_test = EXCLUDED.last_test;
                                     """),
                     {"feb_id": feb.feb_id, "antenna_id": antenna_id}
                 )
                 db.session.commit()

                
       else:
          du_id = 0
    else:
       du_id = 0
    
    return str(du_id)


@app.route('/map')
@login_required
def map_view():
    antennas = Antenna.query.all()  # Récupérer toutes les antennes
    febs = Feb.query.all()
    antennas_febs = db.session.execute(
            text("""
            SELECT *
            FROM get_antennas_with_febs();
            """),
       ).fetchall()
    return render_template('map.html', antennas=antennas, febs=febs, antennas_febs=antennas_febs)

#-----------

app.config['UPLOAD_FOLDER'] = 'uploads/'  # Dir to store updated files
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/upload_antenna', methods=['GET', 'POST'])
def upload_antenna():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Check and secure file
        if file and file.filename.endswith('.csv'):
            # Save file
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Process CSV
            res=process_csv_antenna(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if res:
                flash('File successfully processed!')
            else:
                flash('<strong>File processed with errors!</strong>')
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index_antenna'))  # Redirect to antennas

    return render_template('upload_antenna.html')

@app.route('/upload_feb', methods=['GET', 'POST'])
def upload_feb():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Check and secure file
        if file and file.filename.endswith('.csv'):
            # Save file
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Process CSV
            res=process_csv_feb(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if res:
                flash('<strong>File successfully processed!</strong>')
            else:
                flash('<strong>File processed with errors!</strong>')
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index_feb'))  # Redirect to feb

    return render_template('upload_feb.html')

def process_csv_antenna(file_path):
    res=True
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        line=2
        next(reader)  # Ignore the header row if there is one
        for row in reader:
            # Read csv with columns : longitude, latitude, du_id
            if len(row) != 3:
                continue  # Ignore invalid lines
            longitude, latitude, du_id = row
            if latitude != "" and longitude != "" and du_id != "":
                # Check if the antenna already exists in the database
                try:
                    existing_antenna = Antenna.query.filter_by(du_id=int(du_id)).first()
                except Exception as e:
                    flash(f'Error on line {line}: {str(e)} </li><li><strong></strong> </li>')
                    res=False
                    break
                if existing_antenna is None:
                    # Add to database
                    try:
                        new_antenna = Antenna(longitude=float(longitude), latitude=float(latitude), du_id=int(du_id))
                        db.session.add(new_antenna)
                        flash(f'Antenna {du_id} added')
                    except Exception as e:
                        #db.session.rollback()
                        flash(f'Error: {str(e)} </li><li><strong></strong> </li>')
                        res=False
                else:
                    # Update existing record
                    existing_antenna.longitude = longitude
                    existing_antenna.latitude = latitude

                line+=1

        db.session.commit()
    return res

def process_csv_feb(file_path):
    res=True
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Ignore the header row if there is one
        for row in reader:
            # Read csv with columns : longitude, latitude, du_id
            if len(row) != 3:
                continue  # Ignore invalid lines
            feb_id, mac_address, ip_address = row
            if feb_id != "" and mac_address != "" and ip_address != "":
                # Check if the antenna already exists in the database
                try:
                    existing_feb = Feb.query.filter_by(feb_id=int(feb_id)).first()
                except Exception as e:
                    flash(f'Error: {str(e)} </li><li><strong></strong> </li>')
                    res=False
                    break
                if existing_feb is None:
                    # Add to database
                    try:
                        new_feb = Feb(feb_id=int(feb_id), mac_address=str(mac_address), ip_address=str(ip_address))
                        db.session.add(new_feb)
                        flash(f'Feb {feb_id} added')
                    except Exception as e:
                        flash(f'Error: {str(e)} </li><li><strong></strong> </li>')
                        res = False
                else:
                    # Update feb
                    #flash(f'Warning: Feb {feb_id} already exists (skipped)')
                    existing_feb.mac_address = mac_address
                    existing_feb.ip_address = ip_address

        db.session.commit()
    return res

#-----------
if __name__ == '__main__':
    with app.app_context():  # Création du contexte d'application
        db.create_all()  # Crée les tables si elles n'existent pas déjà
        create_user()
    app.run(host='0.0.0.0', debug=True)  # À exposer à l'extérieur du conteneur

