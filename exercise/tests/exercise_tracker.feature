Feature: Exercise Tracker

  Scenario: Create User
    # I can create a user by posting form data username to /api/exercise/new-user and returned will be an object with username and _id.
    Given the API endpoint /api/exercise
    When I send a POST request with form data Chopin to /new-user
    Then a user with username Chopin should exist in the database
    And the username and _id of Chopin will be returned
