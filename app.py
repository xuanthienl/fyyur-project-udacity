#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for,
    abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
import pandas as pd

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

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

#  Home
#  ----------------------------------------------------------------
@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues List
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    data = []
    venues = Venue.query.all()
    for venue in venues:
        num_upcoming_shows = 0
        for show in venue.shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": [
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming_shows,
                }
            ]
        })

    if len(data):
        df = pd.DataFrame(data)
        data = df.groupby(["city", "state"])["venues"].sum().reset_index()
        data = data.to_dict(orient="records")

    return render_template('pages/venues.html', areas=data)

#  Venues Search
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search_results = Venue.query.filter((Venue.name.ilike(f"%{search_term}%"))).all()
    
    data = []
    for value in search_results:
        num_upcoming_shows = 0
        for show in value.shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

        data.append({
            "id": value.id,
            "name": value.name,
            "num_upcoming_shows": num_upcoming_shows,
        })

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)

#  Detail Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)

    past_shows = []
    upcoming_shows = []

    for show in venue.shows:
        temp_show = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # object class to dict
    data = vars(venue)
    data['website'] = data['website_link']

    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    error = False

    if form.validate() == False:
        error = True
    else:
        try:
            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(venue)
            db.session.commit()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()

    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        return render_template('forms/new_venue.html', form=form)

    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)

    data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'genres': venue.genres,
        'image_link': venue.image_link,
        'facebook_link': venue.facebook_link,
        'website_link': venue.website_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description
    }

    form = VenueForm(formdata=None, data=data)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    error = False

    venue = Venue.query.get_or_404(venue_id)

    if form.validate() == False:
        error = True
    else:
        try:
            venue.name=form.name.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.address=form.address.data
            venue.phone=form.phone.data
            venue.genres=form.genres.data
            venue.image_link=form.image_link.data
            venue.facebook_link=form.facebook_link.data
            venue.website_link=form.website_link.data
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=form.seeking_description.data
            db.session.commit()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()

    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
        return render_template('forms/edit_venue.html', form=form, venue=venue)

    flash('Venue ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        flash('Venue ID:' + venue_id + ' not found.')
        abort(404)

    error = False
    try:
        for show in venue.shows:
            db.session.delete(show)
        
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
        abort(500)

    flash('Venue ' + venue.name + ' was successfully deleted!')
    return '', 200   

#  Artists List
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)

#  Artists Search
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search_results = Artist.query.filter((Artist.name.ilike(f"%{search_term}%"))).all()
    
    data = []
    for value in search_results:
        num_upcoming_shows = 0
        for show in value.shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

        data.append({
            "id": value.id,
            "name": value.name,
            "num_upcoming_shows": num_upcoming_shows,
        })

    response = {
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=search_term)

#  Detail Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)

    past_shows = []
    upcoming_shows = []

    for show in artist.shows:
        temp_show = {
            'venue_id': show.artist_id,
            'venue_name': show.artist.name,
            'venue_image_link': show.artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    # object class to dict
    data = vars(artist)
    data['website'] = data['website_link']

    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    error = False

    if form.validate() == False:
        error = True
    else:
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )
            db.session.add(artist)
            db.session.commit()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()

    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        return render_template('forms/new_artist.html', form=form)

    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        return abort(404)

    form = ArtistForm()
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.image_link.data = artist.image_link
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    error = False

    artist = Artist.query.get(artist_id)
    if artist is None:
        return abort(404)

    if form.validate() == False:
        error = True
    else:
        try:
            artist.name=form.name.data
            artist.city=form.city.data
            artist.state=form.state.data
            artist.phone=form.phone.data
            artist.genres=form.genres.data
            artist.image_link=form.image_link.data
            artist.facebook_link=form.facebook_link.data
            artist.website_link=form.website_link.data
            artist.seeking_venue=form.seeking_venue.data
            artist.seeking_description=form.seeking_description.data
            db.session.commit()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()

    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
        return render_template('forms/edit_artist.html', form=form, artist=artist)

    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

#  Shows List
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    data = []
    shows = Show.query.all()
    if shows is not None:
        for show in shows:
            venue_info = Venue.query.get(show.venue_id)
            artist_info = Artist.query.get(show.artist_id)

            temp_show = {
                'venue_id': show.venue_id,
                'venue_name': venue_info.name,
                'artist_id': show.artist_id,
                'artist_name': artist_info.name,
                'artist_image_link': artist_info.image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            }
        
            data.append(temp_show)

    return render_template('pages/shows.html', shows=data)

#  Create Show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    error = False

    if form.validate() == False:
        error = True
    else:
        venue = Venue.query.get(form.venue_id.data)
        artist = Artist.query.get(form.artist_id.data)
        show = Show.query.filter_by(artist_id=form.artist_id.data, venue_id=form.venue_id.data, start_time=form.start_time.data).first()
        if venue is None or artist is None or show is not None:
            error = True
        else:
            try:
                show = Show(
                    artist_id=form.artist_id.data,
                    venue_id=form.venue_id.data,
                    start_time=form.start_time.data,
                )
                db.session.add(show)
                db.session.commit()
            except:
                db.session.rollback()
                error = True
            finally:
                db.session.close()

    if error:
        flash('An error occurred. Show could not be listed.')
        return render_template('forms/new_show.html', form=form)

    flash('Show was successfully listed!')
    return redirect(url_for('index'))

#  Error
#  ----------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

#----------------------------------------------------------------------------#
# Debug.
#----------------------------------------------------------------------------#

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
