import bcrypt
from features.user import User

class TestUserInitialization:
    """Tests for User initialization and basic properties."""

    def test_user_initialization(self, sample_user: User):
        """Test that a User instance is properly initialized."""
        user = sample_user

        assert user.username == 'jessica29'
        assert user.pets == []
        assert user.music == {}
        assert user.food == {}
        assert 0 <= user.currency <= 25000

        assert set(["food", "soap", "potion"]).issubset(user.inventory)

        assert user.password.startswith('$2b$')
        assert user.password != '29.September.2006'

    def test_user_with_password_hash(self):
        """Test initialization with an already hashed password."""

        hash = bcrypt.hashpw('29.September.2006'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User('jessica29', hash)
        assert user.password == hash
        assert user.password.startswith('$2b$')

class TestUserCurrency:
    """Tests for currency-related functionality."""

    def test_currency_property(self, sample_user: User):
        """Test currency getter and setter with valid values."""

        user = sample_user
        user.currency = 1000
        assert user.currency == 1000

    def test_negative_currency(self, sample_user: User):
        """Test that negative currency is prevented."""

        user = sample_user
        original_currency = user.currency
        user.currency = -100
        assert user.currency == original_currency