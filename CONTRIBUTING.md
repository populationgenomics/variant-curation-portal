# Contributing

## Getting started

### Requirements

To develop locally you will need Python 3.6 or higher, docker, nodejs and yarn.

### Setup

- Install dependencies

  ```sh
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  yarn install
  ```

- Migrate database
  Export these into your shell environment

  ```sh
  export ALLOWED_HOSTS=127.0.0.1,localhost
  export SECRET_KEY="generate_a_django_secret_key"
  export REMOTE_USER=someuser
  export NODE_ENV=development
  export DB_PASSWORD=password
  export DB_HOST=localhost
  export DB_PORT=5432
  export DB_USER=curator-dev
  export DB_DATABASE=curator-dev
  ```

  You can generate a secret key using the following command

  ```sh
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

  If you are having issues with Nodejs and OpenSSL then set the OpenSSL legacy provider flag

  ```sh
  export NODE_OPTIONS=--openssl-legacy-provider
  ```

  These must be exported everytime you work on this project, so either put them into your shell's
  login profile (i.e bash_profile, or zprofile, etc), or use [direnv](https://direnv.net/).

- Run docker-compose to get your database running

  ```sh
  docker-compose -f docker/docker-compose-dev.yml up
  ```

  In a new terminal, migrate your database and set it up with some dummy data

  ```sh
  python manage.py migrate
  python manage.py create_test_assignments --variants=/path/to/variants/json/file
  ```

  Ask a member of the software team for this file. This files may contain sensitive information
  so please refrain from adding them to version control.

- Start Django and webpack development servers

  Set REMOTE_USER to simulate an authenticated user

  ```
  REMOTE_USER=someuser ./start.sh
  ```

- Open browser to http://localhost:3000

## Testing

### Python

Backend tests are written using [pytest](https://docs.pytest.org/).
Run tests with either `pytest` or `tox -e py36`.

#### Coverage

[pytest-cov](https://pytest-cov.readthedocs.io) is used to generate coverage reports.

To generate and view an HTML coverage report, use:

```sh
pytest --cov-report=html
python3 -m http.server --directory htmlcov
```

### JavaScript

Frontend tests use [jest](https://jestjs.io/).
Run tests with either `jest` or `yarn test`.

## Conventions

### Python

Python code is formatted with [Black](https://black.readthedocs.io/).

Check formatting of Python code with `black --check curation_portal` or `tox -e formatting`.

### JavaScript

JavaScript code is formatted with [Prettier](https://prettier.io/).

Check formatting of JS code with `yarn run prettier --check 'assets/**'`.

## Dependencies

- [Python 3.6+](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [django-filter](https://pypi.org/project/django-filter/)
- [rules](https://pypi.org/project/rules/)
- [Django webpack loader](https://github.com/owais/django-webpack-loader)
- [WhiteNoise](https://pypi.org/project/whitenoise/)
- [React](https://reactjs.org/)
- [Semantic UI React](https://react.semantic-ui.com/)

### Python

requirements.txt is generated from requirements.in using [pip-tools](https://github.com/jazzband/pip-tools).
To upgrade dependencies, use [pip-compile](https://github.com/jazzband/pip-tools#updating-requirements).

### JavaScript

To upgrade JS dependencies, use [yarn upgrade](https://yarnpkg.com/en/docs/cli/upgrade) or
[yarn upgrade-interactive](https://yarnpkg.com/en/docs/cli/upgrade-interactive).
