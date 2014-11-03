axosoft-python
================================
[![Build Status](https://travis-ci.org/ckaznocha/axosoft-python.svg?branch=master)](https://travis-ci.org/ckaznocha/axosoft-python)
[![Coverage Status](https://img.shields.io/coveralls/ckaznocha/axosoft-python.svg)](https://coveralls.io/r/ckaznocha/axosoft-python?branch=master)
[![Code Health](https://landscape.io/github/ckaznocha/axosoft-python/master/landscape.png)](https://landscape.io/github/ckaznocha/axosoft-python/master)
[![Stories in Ready](https://badge.waffle.io/ckaznocha/axosoft-python.svg?label=ready&title=stories+ready)](http://waffle.io/ckaznocha/axosoft-python)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://ckaznocha.mit-license.org)

An unofficial Python module for the Axosoft (formerly OnTime) API.

## Usage
1. Import the module into your project

    ```python
    from axosoft_api import Axosoft
    ```

1. Create a new `Axosoft` instance

    The constructor accepts 4 arguments
    1. The client ID provided to you by Axosoft
    1. The client secret provide to you by Axosoft
    1. The domain you use to access Axosoft without the protocol.
        i.e. If your domain is `https://foo.axosoft.com` you would use `foo.axosoft.com`
    1. Optionally, a token from a previous session

    ```python
    axosoft_client = Axosoft(
            'Your client ID',
            'Your client secret',
            'Your Axosoft domain'
        )
    ```

1. Authenticate

    The authentication methods return the token so it can be used for future sessions

    There are two ways to authenticate
    1. Username/Password authentication:

        ```python
            token = axosoft_client.authenticate_by_password(
                axosoft_user,
                axosoft_password,
                "read write"
            )
        ```

    1. Code based authentication:

        ```python
        """
        Pass the URL to begin_authentication_by_code() where you would like the access code sent
        """
        redirect_uri = "http://foo.bar/"
        url = self.axosoft_client.begin_authentication_by_code(
            redirect_uri,
            "read write"
        )

        """
        Send the user to the url returned by the method.

        Once they have authenticated they will be forwarded to the URL you provided.
        Exchanged to code for a token by passing the code and the redirect_uri to complete_authentication_by_code().
        """
        code = code_from_redirect_url

        token = self.axosoft_client.complete_authentication_by_code(
            code,
            redirect_uri
        )
        ```

    If you need to confirm that you're successfully authenticated, you may use the `is_authenticated` method

    ```python
        if axosoft_client.is_authenticated:
            pass
    ````

1. Start interacting with your Axosoft API resources

    ```python
        # These examples arbitrarily use the release resource

        """
        Create a new release.

        The first argument is the resource type you're creating
        The second argument is the payload which should be a dictionary containing at minimum the required fields for the resource type
        """
        r = axosoft_client.create('releases', payload={'name': 'testRelease', 'release_type': {'id': 1}})

        """
        Get the content of a release

        The first argument is the resource type you want to get
        The second argument is optionally the ID of a specific resource
        The third argument is optionally a dictionary of parameters
        """
        r = axosoft_client.get('releases', r['data']['id'])

        """
        Update a release

        The first argument is the resource type you want to update
        The second argument is the ID of the resource you are updating
        The third arguments is a dictionary containing all the fields of your resource
        """
        r = axosoft_client.update('releases', r['data']['id'], payload={'name': 'testRelease', 'release_type': {'id': 1}})

        """
        Delete a release

        The first argument is the resource type you want to delete
        The second argument is the ID of the resource you want to delete
        Returns true if the delete was successful
        """
        r = self.axosoft_client.delete('releases', r['data']['id'])

    ````

For info on using the various resources of the API see Axosoft's documentation:
http://developer.axosoft.com/api

##To Do
- ~~Implement code grant type authentication.~~
- ~~Figure out an elegent way to access a resource's children.~~
    - ~~e.g. `/features/{id}/emails`~~
- Handle binary attachments.

##Contributing
See the `CONTRIBUTING` file.

##License
See the `LICENSE` file.

This project and its contributers are in no way affiliated with Axosoft. Axosoft is the trademark of Axosoft, LLC
