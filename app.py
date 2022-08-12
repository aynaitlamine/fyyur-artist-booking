#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ✅ TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent =  db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="venue")
    created_at = db.Column(db.DateTime(), nullable=True)
    # ✅ TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue =  db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="artist")
    created_at = db.Column(db.DateTime(), nullable=True)

    # ✅ TODO: implement any missing fields, as a database migration using Flask-Migrate

# ✅ TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False);
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  all_cities = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
  data = []
  for item in all_cities:
    venues_list = []
    venues_query = Venue.query.filter_by(city=item.city).filter_by(state=item.state).all()
    for venue in venues_query:
        venues_list.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len([])
        })
    data.append({
        "city": item.city,
        "state": item.state,
        "venues": venues_list
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  term = request.form.get('search_term')
  term = "%{}%".format(term)
  query_data = Venue.query.filter(Venue.name.ilike(term) | Venue.city.ilike(term) | Venue.state.ilike(term)).all()
  data = []
  for item in query_data:
      data.append({
          "id": item.id,
          "name": item.name,
          "num_upcoming_shows": 0
      })
  response={
      "count": len(query_data),
      "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter_by(id=venue_id).first()
  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
    show_data = {
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    if datetime.now() > show.start_time:
        past_shows.append(show_data)
    else:
        upcoming_shows.append(show_data)

  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "city": venue.city,
      "state": venue.state,
      "address": venue.address,
      "phone": venue.phone,
      "website": venue.website,
      "image_link": venue.image_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "past_shows": past_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash an error.
    flash('An error occurred.')
  if not error:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error=False
  try:
      venue = Venue.query.get(venue_id)
      # TODO: delete related shows before deleting the venue
      db.session.delete(venue)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
      flash(f'An error occurred.')
  if not error:
      flash('Venue was successfully deleted.')
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  query_data = Artist.query.all()
  data = []
  for item in query_data:
      data.append({
        "id": item.id,
        "name": item.name,
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  term = request.form.get('search_term')
  term = "%{}%".format(term)
  query_data = Artist.query.filter(Artist.name.ilike(term)|Artist.city.ilike(term)|Artist.state.ilike(term)).all()
  data = []
  for item in query_data:
      data.append({
        "id": item.id,
        "name": item.name,
        "num_upcoming_shows": 0
      })
  response={
    "count": len(query_data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id=artist_id).first()
  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    show_data = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    if datetime.now() > show.start_time:
        past_shows.append(show_data)
    else:
        upcoming_shows.append(show_data)

  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "image_link": artist.image_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "past_shows": past_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()

  form.seeking_venue.default = artist.seeking_venue
  form.process()

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.genres.data = artist.genres
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)
  error = False
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.genres = request.form.getlist('genres')
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue = json.loads(request.form['seeking_venue'].lower())
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
      db.session.close()
  # on successful db insert, flash success
  if error:
      flash('An error occurred.')
  if not error:
      flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()

  form.seeking_talent.default = venue.seeking_talent
  form.process()

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@artist_blueprint.route('/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  error=False
  try:
      artist = Artist.query.get(artist_id)
      # TODO: delete related shows before deleting the artist
      db.session.delete(artist)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
      flash(f'An error occurred.')
  if not error:
      flash('Artist was successfully deleted.')

  return redirect(url_for('home.index'))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  error = False
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.genres = request.form.getlist('genres')
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = json.loads(request.form['seeking_talent'].lower())
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  # on successful db insert, flash success
  if error:
      flash('An error occurred.')
  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error= False
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    genres = request.form.getlist('genres')
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_venue = json.loads(request.form['seeking_venue'].lower())
    seeking_description = request.form['seeking_description']
    created_at = datetime.now()
    artist = Artist(name=name, city=city, state=state, phone=phone,
                genres=genres,facebook_link=facebook_link, image_link=image_link,
                website=website, seeking_venue=seeking_venue, seeking_description=seeking_description,
                created_at=created_at)
    db.session.add(artist)
    db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()

  if error:
      # on unsuccessful db insert, flash an error.
      flash('An error occurred.')
  if not error:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # displays list of shows at /shows
  query_data = Show.query.all()
  data = []
  for item in query_data:
    data.append({
      "venue_id": item.venue_id,
      "venue_name": item.venue.name,
      "artist_id": item.artist_id,
      "artist_name": item.artist.name,
      "artist_image_link": item.artist.image_link,
      "start_time": item.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
