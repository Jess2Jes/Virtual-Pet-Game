import pytest
from features.user import User, BcryptAuthService

"""
program_testing/test_user.py

Unit tests for the User entity's core business logic.

This module validates the primary behaviors of the User class, ensuring that:
- Users are initialized with safe default values.
- Currency operations obey logical constraints (non-negative, limits).
- Passwords are automatically hashed and validated against security rules.
- Inventory management handles addition, checking, and consumption correctly.
"""

class TestUser:
    """
    Test suite for User entity properties and methods.
    
    Covers:
    - Initialization state.
    - Property setters/getters (currency, password).
    - Authentication integration.
    - Inventory transaction logic.
    """

    def test_initialization(self, user: User):
        """
        Verify that a User instance is initialized with the correct default values.
        
        Checks:
        - Username assignment.
        - Currency bounds (0 to 25000).
        - Dependencies (AuthService).
        - Empty collections (pets, music, food).
        - Default inventory categories (food, soap, potion).
        """

        assert user.username == 'jessica29'
        assert 0 <= user.currency <= 25000
        assert isinstance(user.auth_service, BcryptAuthService)
        assert user.pets == []
        assert user.music == {}
        assert user.food == {}
        assert "food" in user.inventory
        assert "soap" in user.inventory
        assert "potion" in user.inventory
    
    def test_currency_setter(self, user: User):
        """
        Test setting a valid positive integer value for currency.
        """

        user.currency = 1000
        assert user.currency == 1000
    
    def test_currency_setter_negative(self, user: User):
        """
        Test that setting a negative currency value raises a ValueError.
        
        Currency logic must enforce non-negative balances to prevent accounting errors.
        """

        with pytest.raises(ValueError, 
            match='Currency cannot be negative.'):
            user.currency = -100
    
    def test_limit_currency(self, user: User):
        """
        Test the limit_currency method clamps values to a maximum integer limit.
        
        This prevents integer overflow issues or unrealistically high values
        that might break UI or storage.
        """

        user.currency = 2_147_483_648
        user.limit_currency()
        assert user.currency == 2_147_483_647
    
    def test_password_setter(self, user: User):
        """
        Verify that setting a password automatically hashes it.
        
        The stored `password` property should never match the plain text input.
        """

        password = '29.September.2006'
        user.password = password
        assert user.password != password
    
    def test_password_verification(self, user: User):
        """
        Test the authentication verification flow.
        
        Ensures:
        - Correct passwords return True.
        - Incorrect passwords return False.
        """

        user.password = 'StrongP@ss1'
        assert user.auth_service.verify('StrongP@ss1', user.password) is True
        assert user.auth_service.verify('WrongPass', user.password) is False
    
    def test_weak_password_setter(self, user: User):
        """
        Test that weak passwords are rejected by the validation logic.
        
        Password must meet complexity requirements:
        - Minimum 8 characters
        - At least 1 Uppercase
        - At least 1 Lowercase
        - At least 1 Digit
        - At least 1 Symbol
        """

        weak_password = 'helloworld'
        with pytest.raises(ValueError,
            match=r'Password is too weak! Must contain 8\+ chars, 1 upper, 1 lower, 1 digit, 1 symbol\.'):
            user.password = weak_password
    
    def test_inventory_flow(self, user: User):
        """
        Test the complete inventory item lifecycle.
        
        Steps:
        1. Check initial quantity of a known item.
        2. Add items and verify the total increases correctly.
        3. Consume items and verify the total decreases correctly.
        4. Check for specific item inside inventory with certain amount.
        """

        category = 'food'
        item = 'Mozarella Nugget'
        initial_qty = user.inventory[category].get(item, 0)

        user.add_item(category, item, 5)
        assert user.inventory[category][item] == initial_qty + 5

        result = user.consume_item(category, item, 1)
        assert result is True
        assert user.inventory[category][item] == initial_qty + 4

        assert user.has_item(category, item, 3)
    
    def test_consume_unavailable_item(self, user: User):
        """
        Test consuming items that are unavailable or insufficient in quantity.
        
        - Should return False if the item name doesn't exist.
        - Should return False if the quantity requested exceeds available stock.
        """

        assert user.consume_item('food', 'Cupcake', 1) is False
        assert user.consume_item('food', 'Kentucky Fried Chicken', 99999) is False