Rest API documentation
======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

REST API repository Contacts
============================

.. automodule:: src.repository.contacts
   :members:
   :undoc-members:
   :show-inheritance:

REST API repository Users
=========================

.. automodule:: src.repository.users
   :members:
   :undoc-members:
   :show-inheritance:

Authentication Routes
=====================

Documentation for the FastAPI authentication routes.

Functions:
-----------

.. autofunction:: src.api.auth.register_user

.. autofunction:: src.api.auth.login_user

.. autofunction:: src.api.auth.confirmed_email

.. autofunction:: src.api.auth.request_email

Contacts Routes
===============

Documentation for the FastAPI contacts routes.

Functions:
-----------

.. autofunction:: src.api.contacts.read_contacts

.. autofunction:: src.api.contacts.read_contact

.. autofunction:: src.api.contacts.create_contact

.. autofunction:: src.api.contacts.update_contact

.. autofunction:: src.api.contacts.remove_contact

.. autofunction:: src.api.contacts.upcoming_birthdays

Users Routes
============

Documentation for the FastAPI users routes.

Functions:
-----------

.. autofunction:: src.api.users.me

.. autofunction:: src.api.users.update_avatar_user

Utils Routes
============

Documentation for the FastAPI utils routes.

Functions:
-----------

.. autofunction:: src.api.utils.healthchecker

Contact and User Models Documentation
=====================================

.. automodule:: src.database.models
   :members: Contact, User
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
