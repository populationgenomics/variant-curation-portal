# Variant Curation Portal

![CI status bage](https://github.com/populationgenomics/variant-curation-portal/workflows/CI/badge.svg)

## Deployment

In the [upstream repository](https://github.com/macarthur-lab/lof-curation-portal-env), deployment is based on Kubernetes. At the CPG, we use the Identity-Aware Proxy (IAP) and Cloud Run instead.

The following steps use the `prod` environment, but simply replace `prod` with another environment like `dev` for isolated namespaces.

1. Create a GCP project and set the environment variable `GCP_PROJECT` to the corresponding GCP project ID.

    ```sh
    export GCP_PROJECT=curator-348003
    ```

1. Set up a billing budget, if desired.
1. Reserve a static external IP address.
1. Create a CNAME record to associate the IP address with a subdomain.
1. Create a managed PostgreSQL instance, called `curator-postgres`, with a public IP and the smallest possible resource footprint. Make sure to enable regular backups. To enable [full query logs](https://cloud.google.com/sql/docs/postgres/pg-audit), enable the `cloudsql.enable_pgaudit` flag and set the `pgaudit.log` flag to `all`.
1. Add a `curator-prod` DB user and a database of the same name.
1. Connect to the instance to configure audit logs:

    ```sh
    gcloud sql connnect curator-postgres
    ```

    Enable the `pgaudit` extension:

    ```sql
    CREATE EXTENSION pgaudit;
    ```

1. In the Secret Manager, create two secrets:
    - `postgres-password-prod` (copy password from the `curator-prod` DB user)
    - `django-secret-key-prod` (50 random characters)
1. Create a service account `curator-prod` for running the Cloud Run instance.
1. Grant the `curator-prod` service account the *Secret Manager Secret Accessor* role to the secrets.
1. Grant the `curator-prod` service account the *Cloud SQL Client* role.
1. Open a Cloud Shell and build the Docker container:

    ```sh
    git clone https://github.com/populationgenomics/variant-curation-portal.git

    cd variant-curation-portal

    docker build --tag curator-prod .
    ```

    When running the container, copy the environment variables (`-e ...`) from the [`deploy_prod` workflow](.github/workflows/deploy_prod.yaml). However, for `DB_HOST` replace the `/cloudsql` prefix with `/app/cloudsql`, as the Cloud SQL Auth proxy doesn't have write permissions to `/cloudsql`.

    ```sh
    docker run --init -it -e ... curator-prod /bin/sh
    ```

    To perform the initial database setup, run the following within the container and execute the [Python code to grant user permissions](https://github.com/macarthur-lab/variant-curation-portal/blob/main/docs/permissions.md#granting-permissions) in the Django shell.

    ```sh
    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy

    chmod +x cloud_sql_proxy

    ./cloud_sql_proxy -instances=curator-348003:australia-southeast1:curator-postgres -dir=/app/cloudsql &

    ./manage.py migrate

    PYTHONPATH=. django-admin shell -i python
    ```

1. Deploy to Cloud Run, using the `gcloud run deploy` command from the [`deploy_prod` workflow](.github/workflows/deploy_prod.yaml).
1. Set up a `curator-deploy` service account and store its JSON key as the `GCP_DEPLOY_KEY` GitHub Actions secret.
1. Grant the `curator-deploy` service account the *Cloud Run Admin* role for the `curator-prod` Cloud Run service.
1. Set up an HTTPS load balancer pointing to the Cloud Run endpoint, using the previously reserved external IP address. Create a new Google-managed certificate that points to the subdomain chosen before.
1. Configure an OAuth consent screen.
1. Set up IAP for the HTTPS load balancer.
1. Create a Google Group called `curator-prod-access` to control who can access the portal through IAP.
1. On the IAP resource, grant the *IAP-Secured Web App User* role to the `curator-prod-access` group.

## Authentication using IAP

IAP sets the [`X-Goog-Authenticated-User-Email`](https://cloud.google.com/iap/docs/identity-howto#getting_the_users_identity_with_signed_headers) header, which has a value of the form `accounts.google.com:example@gmail.com`. In order to use this header in the Django [`RemoteUserMiddleware`](https://docs.djangoproject.com/en/4.0/howto/auth-remote-user/), `CURATION_PORTAL_AUTH_HEADER` must be set to `HTTP_X_GOOG_AUTHENTICATED_USER_EMAIL` (note the `HTTP_` prefix), as that's used for the HTTP header key in Django's `request.META`.

We override `clean_username` in the [`AuthBackend`](curation_portal/auth.py), to remove the `accounts.google.com:` prefix from the user name.
