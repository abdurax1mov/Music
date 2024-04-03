from flask import *
from flask_migrate import Migrate
from flask_sqlalchemy import *
from sqlalchemy import *
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = Flask
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123')
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
DB_NAME = os.getenv('DB_NAME', 'music')
database_path = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = database_path
app.config['SECRET_KEY'] = "F4qwqw"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    name = Column(String)
    surname = Column(String)
    password = Column(String)
    role = Column(String)
    save = db.relationship("Music", backref="saves", secondary="save", order_by="Music.id")
    like = relationship("Music", backref="like_by", secondary="like", order_by="Music.id")
    music = relationship("Music", backref="user", order_by="Music.id")


db.Table('save',
         db.Column('music_id', db.Integer, db.ForeignKey('music.id')),
         db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class File(db.Model):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    img = Column(String)
    music = db.relationship('Music', backref="file", order_by="Music.id")


class Music(db.Model):
    __tablename__ = "music"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    img = Column(String)
    music = Column(String)
    time = Column(String)
    date = Column(String)
    like_count = Column(Integer, default=0)
    artist = Column(Integer, ForeignKey("user.id"))
    file_id = Column(Integer, ForeignKey('file.id'))
    genre_id = Column(Integer, ForeignKey('genre.id'))


db.Table('like',
         db.Column('music_id', db.Integer, db.ForeignKey('music.id')),
         db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class Genre(db.Model):
    __tablename__ = "genre"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('user.id'))
    name = Column(String)
    img = Column(String)
    music = db.relationship('Music', backref="genre", order_by="Music.id")


def online_user():
    get = None
    if "username" in session:
        user = User.query.filter(User.username == session["username"]).first()
        get = user
    return get


@app.route('/get_artists')
def get_artists():
    artists = User.query.all()
    artist = []
    for i in artists:
        artist.append({
            'photo': i.name
        })
    return jsonify(artist)


@app.route('/xit_genre', methods=["POST", "GET"])
def xit_genre():
    genre = Genre.query.filter(Genre.id == 5).first()
    print(genre.music)
    user = online_user()
    genre = Genre.query.all()
    return render_template("genre.html", user=user, genre=genre)


@app.route('/genre_music/<int:genre_id>', methods=["POST", "GET"])
def genre_music(genre_id):
    user = online_user()
    genre = Genre.query.filter(Genre.id == genre_id).first()
    musics = Music.query.filter(Music.genre_id == genre_id).all()
    for music in musics:
        print(music.artist)
    lens = len(musics)
    music_id = []
    for music_like in user.like:
        music_id.append(music_like.id)
    return render_template("genre_musics.html", genre=genre, lens=lens, user=user, music_id=music_id)


@app.route('/add_like_genre/<int:music_id>/<int:genre_id>', methods=["POST", "GET"])
def add_like_genre(music_id, genre_id):
    music_name = Music.query.filter(Music.id == music_id).first()
    user_num = online_user()
    music_ids = []
    if user_num.like:
        for musics in user_num.like:
            music_ids.append(musics.id)
        if music_name.id in music_ids:
            user_num.like.remove(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count - 1
            })
            db.session.commit()
        else:
            user_num.like.append(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count + 1
            })
            db.session.commit()
    else:
        user_num.like.append(music_name)
        db.session.commit()
        Music.query.filter(Music.id == music_id).update({
            "like_count": music_name.like_count + 1
        })
        db.session.commit()
    like_id = []
    for post_like in user_num.like:
        like_id.append(post_like.id)
    return redirect(url_for('genre_music', genre_id=genre_id))


@app.route('/edit_music_genre/<int:music_edit>/<int:genre_id>', methods=["POST", "GET"])
def edit_music_genre(music_edit, genre_id):
    genres = Genre.query.all()
    albo = Genre.query.filter(Genre.id == genre_id).first()
    users = User.query.all()
    edi_music = Music.query.filter(Music.id == music_edit).first()
    user = online_user()
    if request.method == "POST":
        genre_name = request.form.get("file_name")
        artist = request.form.get("artist")
        name = request.form.get("name")
        times = request.form.get("time")
        date = request.form.get("date")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        Music.query.filter(Music.id == music_edit).update({
            "genre_id": genre_name,
            "artist": artist,
            "name": name,
            "time": times,
            "date": date,
            "img": photo_url
        })
        db.session.commit()
        return redirect(url_for("genre_music", genre_id=genre_id))
    return render_template("edit_music_genre.html", user=user, edi_music=edi_music, genre_id=genre_id, users=users,
                           genres=genres, albo=albo)


@app.route('/delete_genre/<int:genre_id>', methods=["POST", "GET"])
def delete_genre(genre_id):
    gen = Genre.query.filter(Genre.id == genre_id).first()
    db.session.delete(gen)
    db.session.commit()
    return redirect(url_for("xit_genre", genre_id=genre_id))


@app.route('/music_delete_genre<int:music_edit>/<int:genre_id>', methods=["POST", "GET"])
def music_delete_genre(music_edit, genre_id):
    musics = Music.query.filter(Music.id == music_edit).first()
    db.session.delete(musics)
    db.session.commit()
    return redirect(url_for("genre_music", genre_id=genre_id))


@app.route('/genre/', methods=["POST", "GET"])
def genre():
    if request.method == 'POST':
        name = request.form.get("genre_name")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        add = Genre(name=name, img=photo_url)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for("add_music"))


@app.route('/genre_edit/<int:genre_id>', methods=["POST", "GET"])
def genre_edit(genre_id):
    genre = Genre.query.filter(Genre.id == genre_id).first()
    user = online_user()
    if request.method == 'POST':
        name = request.form.get("file_name")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        Genre.query.filter(Genre.id == genre_id).update({
            "name": name,
            "img": photo_url
        })
        db.session.commit()
        return redirect(url_for("genre_music", genre_id=genre_id))
    return render_template("genre_edit.html", genre=genre, user=user)


@app.route('/albom', methods=["POST", "GET"])
def albom():
    user = online_user()
    albom = File.query.all()
    return render_template("albom.html", online_user=user, albom=albom)


@app.route('/download/<int:music_id>', methods=["POST", "GET"])
def download(music_id):
    user = online_user()
    filters = Music.query.filter(Music.id == music_id).first()
    save_ids = []
    if user.save:
        for musics in user.save:
            save_ids.append(musics.id)
        if filters.id in save_ids:
            user.save.remove(filters)
            db.session.commit()
        else:
            user.save.append(filters)
            db.session.commit()
    else:
        user.save.append(filters)
        db.session.commit()
    path = filters.music
    corrected_url = path.lstrip('/')
    print(corrected_url)
    return send_file(corrected_url, as_attachment=True, environ=request.environ)


@app.route('/an_save/<int:music_id>', methods=["POST", "GET"])
def an_save(music_id):
    user = online_user()
    filters = Music.query.filter(Music.id == music_id).first()
    save_ids = []
    if user.save:
        for musics in user.save:
            save_ids.append(musics.id)
        if filters.id in save_ids:
            user.save.remove(filters)
            db.session.commit()
        else:
            user.save.append(filters)
            db.session.commit()
    else:
        user.save.append(filters)
        db.session.commit()
    return redirect(url_for('save'))


@app.route('/save', methods=["POST", "GET"])
def save():
    user = online_user()
    save_music = user.save
    music_ids = []
    for music_like in user.like:
        music_ids.append(music_like.id)
    return render_template("save.html", user=user, save_music=save_music, music_ids=music_ids)


@app.route('/like', methods=["POST", "GET"])
def like():
    user = online_user()
    likes = user.like
    like_id = []
    for post_like in user.like:
        like_id.append(post_like.id)
    return render_template("like.html", user=user, likes=likes, like_id=like_id)


@app.route('/add_like/<int:music_id>', methods=["POST", "GET"])
def like_s(music_id):
    music_name = Music.query.filter(Music.id == music_id).first()
    user_num = online_user()
    music_ids = []
    if user_num.like:
        for musics in user_num.like:
            music_ids.append(musics.id)
        if music_name.id in music_ids:
            user_num.like.remove(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count - 1
            })
            db.session.commit()
        else:
            user_num.like.append(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count + 1
            })
            db.session.commit()
    else:
        user_num.like.append(music_name)
        db.session.commit()
        Music.query.filter(Music.id == music_id).update({
            "like_count": music_name.like_count + 1
        })
        db.session.commit()
    like_id = []
    for post_like in user_num.like:
        like_id.append(post_like.id)
    return redirect(url_for('like'))


@app.route('/artist_music/<int:artists_id>', methods=["POST", "GET"])
def artist_music(artists_id):
    user = online_user()
    artist = User.query.filter(User.id == artists_id).first()
    musics = Music.query.filter(Music.artist == artists_id).all()
    lens = len(musics)
    like_id = []
    for post_like in user.like:
        like_id.append(post_like.id)
    return render_template("artist_music.html", user=user, lens=lens, artist=artist, like_id=like_id)


@app.route('/add_like/<int:music_id>/<int:file_id>', methods=["POST", "GET"])
def add_like(music_id, file_id):
    music_name = Music.query.filter(Music.id == music_id).first()
    user_num = online_user()
    music_ids = []
    if user_num.like:
        for musics in user_num.like:
            music_ids.append(musics.id)
        if music_name.id in music_ids:
            user_num.like.remove(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count - 1
            })
            db.session.commit()
        else:
            user_num.like.append(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count + 1
            })
            db.session.commit()
    else:
        user_num.like.append(music_name)
        db.session.commit()
        Music.query.filter(Music.id == music_id).update({
            "like_count": music_name.like_count + 1
        })
        db.session.commit()
    like_id = []
    for post_like in user_num.like:
        like_id.append(post_like.id)
    return redirect(url_for('music_album', file_id=file_id))


@app.route('/add_like_home/<int:music_id>', methods=["POST", "GET"])
def add_like_home(music_id):
    music_name = Music.query.filter(Music.id == music_id).first()
    user_num = online_user()
    music_ids = []
    if user_num.like:
        for musics in user_num.like:
            music_ids.append(musics.id)
        if music_name.id in music_ids:
            user_num.like.remove(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count - 1
            })
            db.session.commit()
        else:
            user_num.like.append(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count + 1
            })
            db.session.commit()
    else:
        user_num.like.append(music_name)
        db.session.commit()
        Music.query.filter(Music.id == music_id).update({
            "like_count": music_name.like_count + 1
        })
        db.session.commit()
    like_id = []
    for post_like in user_num.like:
        like_id.append(post_like.id)
    return redirect(url_for('music'))


@app.route('/get_like', methods=["POST", "GET"])
def get_like():
    music_id = request.json["music_id"]
    music_name = Music.query.filter(Music.id == music_id).first()
    user_num = online_user()
    music = []
    if user_num.like:
        for musics in user_num.like:
            music.append(musics.id)
        if music_name.id in music:
            user_num.like.remove(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count - 1
            })
            db.session.commit()
        else:
            user_num.like.append(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count + 1
            })
            db.session.commit()
    else:
        user_num.like.append(music_name)
        db.session.commit()
        Music.query.filter(Music.id == music_id).update({
            "like_count": music_name.like_count + 1
        })
        db.session.commit()

    like_red = []
    for music_like in user_num.like:
        music_id.append(music_like.id)
    return jsonify({
        "like_red": like_red
    })


@app.route('/add_artist_music/<int:music_id>/<int:artists_id>', methods=["POST", "GET"])
def add_artist_music(music_id, artists_id):
    music_name = Music.query.filter(Music.id == music_id).order_by().first()
    user_num = online_user()
    music_ids = []
    if user_num.like:
        for musics in user_num.like:
            music_ids.append(musics.id)
        if music_name.id in music_ids:
            user_num.like.remove(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count - 1
            })
            db.session.commit()
        else:
            user_num.like.append(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count + 1
            })
            db.session.commit()
    else:
        user_num.like.append(music_name)
        db.session.commit()
        Music.query.filter(Music.id == music_id).update({
            "like_count": music_name.like_count + 1
        })
        db.session.commit()
    like_id = []
    for post_like in user_num.like:
        like_id.append(post_like.id)
    return redirect(url_for('artist_music', artists_id=artists_id))


@app.route('/add_like_save/<int:music_id>', methods=["POST", "GET"])
def add_like_save(music_id):
    music_name = Music.query.filter(Music.id == music_id).order_by().first()
    user_num = online_user()
    music_ids = []
    if user_num.like:
        for musics in user_num.like:
            music_ids.append(musics.id)
        if music_name.id in music_ids:
            user_num.like.remove(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count - 1
            })
            db.session.commit()
        else:
            user_num.like.append(music_name)
            db.session.commit()
            Music.query.filter(Music.id == music_id).update({
                "like_count": music_name.like_count + 1
            })
            db.session.commit()
    else:
        user_num.like.append(music_name)
        db.session.commit()
        Music.query.filter(Music.id == music_id).update({
            "like_count": music_name.like_count + 1
        })
        db.session.commit()
    like_id = []
    for post_like in user_num.like:
        like_id.append(post_like.id)
    return redirect(url_for('save'))


@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter(User.username == username).first()
        if user:
            if check_password_hash(user.password, password):
                session["username"] = user.username
                return redirect(url_for("music", user_id=user.id))
            else:
                return redirect(url_for("login"))
    return render_template("login.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        surname = request.form.get("surname")
        name = request.form.get("name")
        password = request.form.get("password")
        password = generate_password_hash(password, 'scrypt')
        add = User(username=username, surname=surname, name=name, password=password)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route('/music', methods=["POST", "GET"])
def music():
    music = Music.query.order_by(Music.id).all()
    user = online_user()
    music_id = []
    for music_like in user.like:
        music_id.append(music_like.id)
    return render_template("music.html", music=music, user=user, music_id=music_id)


@app.route('/genres', methods=["POST", "GET"])
def genres():
    genre = Genre.query.all()
    user = online_user()
    return render_template("genre.html", user=user, genre=genre)


@app.route('/file', methods=["POST", "GET"])
def file():
    if request.method == 'POST':
        name = request.form.get("file_name")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        add = File(name=name, img=photo_url)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for("add_music"))


@app.route('/add_music', methods=["POST", "GET"])
def add_music():
    files = File.query.all()
    genre = Genre.query.all()
    users = User.query.all()
    user = online_user()
    if request.method == "POST":
        file_name = request.form.get("file_name")
        files_name = File.query.filter(File.name == file_name).first()
        artist_name = request.form.get("artist")
        artist = User.query.filter(User.name == artist_name).first()
        gen = request.form.get("genre")
        genres = Genre.query.filter(Genre.name == gen).first()
        music_name = request.form.get("music_name")
        music = request.files["music"]
        times = request.form.get("time")
        date = request.form.get("date")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        music_url = ''
        if music:
            music_file = secure_filename(music.filename)
            music_url = '/' + 'static/img/' + music_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            music.save(os.path.join(app.config['UPLOAD_FOLDER'], music_file))
        add = Music(name=music_name, music=music_url, img=photo_url, time=times, file_id=files_name.id, date=date,
                    artist=artist.id, genre_id=genres.id)
        db.session.add(add)
        db.session.commit()
        return redirect(url_for("add_music"))
    return render_template("add_music.html", files=files, genre=genre, users=users, user=user)


@app.route('/music_album/<int:file_id>', methods=["POST", "GET"])
def music_album(file_id):
    user = online_user()
    files = File.query.filter(File.id == file_id).first()
    musics = Music.query.filter(Music.file_id == file_id).all()
    for music in musics:
        print(music.artist)
    lens = len(musics)
    music_id = []
    for music_like in user.like:
        music_id.append(music_like.id)
    return render_template("music_albom.html", files=files, lens=lens, user=user, music_id=music_id)


@app.route('/delete/<int:file_id>', methods=["POST", "GET"])
def delete(file_id):
    files = File.query.filter(File.id == file_id).first()
    db.session.delete(files)
    db.session.commit()
    return redirect(url_for("albom"))


@app.route('/music_delete<int:music_edit>/<int:file_id>', methods=["POST", "GET"])
def music_delete(music_edit, file_id):
    musics = Music.query.filter(Music.id == music_edit).first()
    db.session.delete(musics)
    db.session.commit()
    return redirect(url_for("music_album", file_id=file_id))


@app.route('/muz_delete<int:music_edit>', methods=["POST", "GET"])
def muz_delete(music_edit):
    musics = Music.query.filter(Music.id == music_edit).first()
    db.session.delete(musics)
    db.session.commit()
    return redirect(url_for("music"))


@app.route('/file_edit/<int:files_id>', methods=["POST", "GET"])
def file_edit(files_id):
    file = File.query.filter(File.id == files_id).first()
    user = online_user()
    if request.method == 'POST':
        name = request.form.get("file_name")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        File.query.filter(File.id == files_id).update({
            "name": name,
            "img": photo_url
        })
        db.session.commit()
        return redirect(url_for("albom"))
    return render_template("file_edit.html", file=file, user=user)


@app.route('/artist', methods=["POST", "GET"])
def artist():
    if request.method == "POST":
        username = request.form.get("username")
        surname = request.form.get("surname")
        name = request.form.get("name")
        password = request.form.get("password")
        password = generate_password_hash(password, 'scrypt')
        add = User(username=username, surname=surname, name=name, password=password, role="artist")
        db.session.add(add)
        db.session.commit()
        return redirect(url_for("add_music"))


@app.route('/edit_music/<int:music_edit>/<int:files_id>', methods=["POST", "GET"])
def edit_music(music_edit, files_id):
    files = File.query.all()
    albo = File.query.filter(File.id == files_id).first()
    users = User.query.all()
    edi_music = Music.query.filter(Music.id == music_edit).first()
    user = online_user()
    if request.method == "POST":
        file_name = request.form.get("file_name")
        artist = request.form.get("artist")
        name = request.form.get("name")
        times = request.form.get("time")
        date = request.form.get("date")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        Music.query.filter(Music.id == music_edit).update({
            "file_id": file_name,
            "artist": artist,
            "name": name,
            "time": times,
            "date": date,
            "img": photo_url
        })
        db.session.commit()
        return redirect(url_for("music_album", file_id=files_id))
    return render_template("edit_music.html", user=user, edi_music=edi_music, file_id=files_id, users=users,
                           files=files, albo=albo)


@app.route('/edit_music_home/<int:music_edit>', methods=["POST", "GET"])
def edit_music_home(music_edit):
    users = User.query.all()
    edi_music = Music.query.filter(Music.id == music_edit).first()
    user = online_user()
    if request.method == "POST":
        file_name = request.form.get("file_name")
        artist = request.form.get("artist")
        name = request.form.get("name")
        times = request.form.get("time")
        date = request.form.get("date")
        photo = request.files["img"]
        photo_url = ""
        if photo:
            photo_file = secure_filename(photo.filename)
            photo_url = '/' + 'static/img/' + photo_file
            app.config['UPLOAD_FOLDER'] = 'static/img'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_file))
        Music.query.filter(Music.id == music_edit).update({
            "file_id": file_name,
            "artist": artist,
            "name": name,
            "time": times,
            "date": date,
            "img": photo_url
        })
        db.session.commit()
        return redirect(url_for("music"))
    return render_template("edit_muz.html", user=user, edi_music=edi_music, users=users)


@app.route('/profile', methods=["POST", "GET"])
def profile():
    user = online_user()
    if request.method == "POST":
        username = request.form.get("username")
        name1 = request.form.get("name")
        surname2 = request.form.get("surname")
        User.query.filter(User.id == user.id).update({
            "name": name1,
            "surname": surname2,
            "username": username
        })
        db.session.commit()
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user)


if __name__ == '__main__':
    app.run()
