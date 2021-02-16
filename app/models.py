from app import app, db
from app.search import SearchableMixin
import jwt
import datetime


class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String, primary_key=True)
    registered_on = db.Column(db.Integer)
    last_seen = db.Column(db.Integer)

    keys = db.relationship('Key', cascade='all,delete', back_populates='user')

    def generate_token(self):
        """
        Generate auth token.
        :return: token and expiration timestamp.
        """
        now = datetime.datetime.utcnow()
        payload = {
            'iat': now,
            'sub': self.username,
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    def create_key(self, description):
        token = self.generate_token()
        key = Key(token=token, description=description, created_at=datetime.datetime.utcnow())
        key.approved = True
        self.keys.append(key)
        return key

    @staticmethod
    def from_token(token):
        """
        Decode/validate an auth token.
        :param token: token to decode.
        :return: User whose token this is, or None if token invalid/no user associated
        """
        try:
            payload = jwt.decode(token, app.config.get('SECRET_KEY'), algorithms=['HS256'])
            """
            is_blacklisted = BlacklistedToken.check_blacklist(token)
            if is_blacklisted:
                # Token was blacklisted following logout
                return None
            """
            return User.query.get(payload['sub'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Signature expired, or token otherwise invalid
            return None


class Person(SearchableMixin, db.Model):
    __tablename__ = 'person'
    __searchable__ = ['first_name', 'last_name', 'netid', 'college', 'email', 'residence', 'major', 'address']
    _to_exclude = ('id')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Identifiers
    netid = db.Column(db.String)
    upi = db.Column(db.Integer)
    email = db.Column(db.String)
    mailbox = db.Column(db.String)
    phone = db.Column(db.String)

    # Naming
    title = db.Column(db.String)
    first_name = db.Column(db.String, nullable=False)
    preferred_name = db.Column(db.String)
    middle_name = db.Column(db.String)
    last_name = db.Column(db.String, nullable=False)
    suffix = db.Column(db.String)
    pronoun = db.Column(db.String)

    # Students
    school_code = db.Column(db.String)
    school = db.Column(db.String)
    year = db.Column(db.Integer)
    curriculum = db.Column(db.String)
    # Undergrads
    college = db.Column(db.String)
    college_code = db.Column(db.String)
    leave = db.Column(db.Boolean)
    eli_whitney = db.Column(db.Boolean)
    image_id = db.Column(db.Integer)
    image = db.Column(db.String)
    birthday = db.Column(db.String)
    residence = db.Column(db.String)
    building_code = db.Column(db.String)
    entryway = db.Column(db.String)
    floor = db.Column(db.Integer)
    suite = db.Column(db.Integer)
    room = db.Column(db.String)
    major = db.Column(db.String)
    address = db.Column(db.String)
    access_code = db.Column(db.String)

    # Staff
    organization_id = db.Column(db.String)
    organization = db.Column(db.String)
    unit_class = db.Column(db.String)
    unit_code = db.Column(db.String)
    unit = db.Column(db.String)
    postal_address = db.Column(db.String)
    office = db.Column(db.String)

    @staticmethod
    def search(criteria):
        print('Searching by criteria:')
        print(criteria)
        person_query = Person.query
        query = criteria.get('query')
        filters = criteria.get('filters')
        page = criteria.get('page')
        page_size = criteria.get('page_size')
        if query:
            person_query = Person.query_search(query)
        if filters:
            for category in filters:
                if category not in (
                    'netid', 'upi', 'email', 'mailbox', 'phone',
                    'title', 'first_name', 'preferred_name', 'middle_name', 'last_name', 'suffix', 'pronoun',
                    'school_code', 'school', 'year', 'curriculum', 'college', 'college_code', 'leave', 'eli_whitney',
                    'birthday', 'residence', 'building_code', 'entryway', 'floor', 'suite', 'room', 'major', 'access_code',
                    'organization_id', 'organization', 'unit_class', 'unit_code', 'unit', 'office'
                ):
                    return None
                if not isinstance(filters[category], list):
                    filters[category] = [filters[category]]
                person_query = person_query.filter(getattr(Person, category).in_(filters[category]))
        if page:
            students = person_query.paginate(page, page_size or app.config['PAGE_SIZE'], False).items
        else:
            students = person_query.all()
        return students


class Key(db.Model):
    __tablename__ = 'key'
    _to_exclude = ('uses', 'approved', 'deleted', 'user_username')
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, unique=True, nullable=False)
    uses = db.Column(db.Integer, default=0)
    description = db.Column(db.String, nullable=False)
    approved = db.Column(db.Boolean, nullable=False)
    deleted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.Integer)
    last_used = db.Column(db.Integer)

    user_username = db.Column(db.String, db.ForeignKey('users.username'))
    user = db.relationship('User', back_populates='keys')
