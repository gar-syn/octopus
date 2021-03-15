"""
This file (test_models.py) contains the unit tests for the models/model.py file.
"""
import pytest
from werkzeug.security import generate_password_hash
import uuid

from app.models.model import User, Projects, Experiments
from app.views.forms import stringdate, stringdatetime

@pytest.fixture(scope='module')
def new_user():
    user = User('lastname@proivder.tld', 'SuperStrongPassword', 'Name', 'Site', 'Building', 'Room')
    return user

@pytest.fixture(scope='module')
def new_project():
    date = stringdate()
    project = Projects('Project Title', 'Project Description', date)
    return project

def test_new_user(new_user):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password, name, site, building and room
    """
    
    assert new_user.email == 'lastname@proivder.tld'
    assert new_user.password != generate_password_hash('SuperStrongPassword')
    assert new_user.name == 'Name'
    assert new_user.site == 'Site'
    assert new_user.building == 'Building'
    assert new_user.room == 'Room'

def test_user_id(new_user):
    """
    GIVEN an existing User
    WHEN the ID of the user is defined to a value
    THEN check the user ID returns a string (and not an integer) as needed by Flask-WTF
    """
    new_user.id = 17
    assert isinstance(new_user.get_id(), str)
    assert not isinstance(new_user.get_id(), int)
    assert new_user.get_id() == '17'
    
def test_new_project(new_project):
    """
    GIVEN a Project model
    WHEN a new Project is created
    THEN check the guid, title, description and creation date
    """    
    assert new_project.title == 'Project Title'
    assert new_project.description == 'Project Description'
    assert new_project.created_date == new_project.created_date
    
def test_new_experiment(new_user, new_project):
    """
    GIVEN a Experiment model
    WHEN a new Experiment is created
    THEN check the guid, eln, title, description, site, building, room, user, creation date, last edited date and project guid
    """

    date = stringdate()
    last_changed_date = stringdatetime()
    
    experiment = Experiments('ELN-NUMBER-00', 'Experiment Title', 'Experiment Description', new_user.site, new_user.building, new_user.room, new_user.name, date, last_changed_date, new_project.id)
    assert experiment.eln == 'ELN-NUMBER-00'
    assert experiment.title == 'Experiment Title'
    assert experiment.description == 'Experiment Description'
    assert experiment.site == 'Site'
    assert experiment.building == 'Building'
    assert experiment.room == 'Room'
    assert experiment.user_id == 'Name'
    assert experiment.created_date == date
    assert experiment.last_modified_date == last_changed_date
    assert experiment.project_id == new_project.id