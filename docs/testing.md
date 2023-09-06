# Testing Guide for ShoppingCart

The `ShoppingCart` package is equipped with a comprehensive suite of tests to ensure its functionality and reliability. Both `pytest` and `unittest` frameworks are utilized to provide a robust testing environment.

## Setting Up the Testing Environment:

### Dependencies:

   Ensure you have both `pytest` and `unittest` installed. If you're planning to run the `pytest` tests, make sure to have `pytest` installed:

   `pip install pytest`

For developers and contributors, you can install the package with all the testing requirements by running:

 `pip install .[test]`

## Running Tests:

### Using unittest:

Navigate to the uni_tests directory inside the 'tests' folder. To run all tests, use:

`python -m unittest discover`

Or you can also run it from the package directory:
`C:\FOLDER\shopping_cart_package> python -m unittest discover -s tests/uni_tests`

### Specific File:
To run a specific test file, for example, test_api_unittest.py, use:

`python -m unittest test_api_unittest.py`

## Test Descriptions:

    API Tests:
        These tests ensure that the core functionalities of the shopping cart API are working as expected.
        Operations like adding, removing, and retrieving items are tested.

    CLI Tests:
        These tests validate the command-line interface of the shopping cart.
        They simulate user commands and check the responses and effects of these commands.

    Database Tests:
        These tests ensure that the database interactions are correct.
        They validate operations like adding items to the database, removing items, and fetching items.

    GUI Tests:
        These tests validate the graphical user interface of the shopping cart.
        They simulate user interactions with the GUI and ensure that the GUI responds correctly.

## Mocking:

For some tests, especially the CLI tests, mocking is used to simulate user inputs and capture outputs. Both 'unittest.mock' and the 'monkeypatch' fixture from pytest are utilized for this purpose.
Conclusion:

Regular testing ensures the reliability and robustness of the ShoppingCart package. Whether you're a developer, contributor, or user, running these tests can provide confidence in the package's functionality.