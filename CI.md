# Continuous Integration (CI)

## AWS Testing

GitHub Actions are used to run the CI for the `community.aws` collection. The workflows used for the CI can be found in the [.github/workflows](.github/workflows) directory.

### PR Testing Workflows

The following tests run on every pull request:

| Job | Description | Python Versions | ansible-core Versions |
| --- | ----------- | --------------- | --------------------- |
| [Changelog](.github/workflows/changelog_and_linters.yml) | Checks for the presence of changelog fragments | 3.12 | N/A |
| [Linters](.github/workflows/changelog_and_linters.yml) | Runs `black`, `isort`, `flynt`, `flake8`, and `ansible-lint` via tox | 3.10 | 2.17 |
| [Sanity](.github/workflows/sanity.yml) | Runs ansible sanity checks | See compatibility table below | devel, milestone, stable-2.17, stable-2.18, stable-2.19, stable-2.20 |
| [Unit tests](.github/workflows/unit.yml) | Executes unit test cases | See compatibility table below | devel, milestone, stable-2.17, stable-2.18, stable-2.19, stable-2.20 |
| [Galaxy Importer](.github/workflows/galaxy-importer.yml) | Validates collection can be imported by Galaxy | 3.12 | latest |

**Note:** Integration tests currently run via a Zuul build.

### Python Version Compatibility by ansible-core Version

These are outlined in the collection's [tox.ini](tox.ini) file (`envlist`) and GitHub Actions workflow exclusions.

| ansible-core Version | Sanity Tests | Unit Tests |
| -------------------- | ------------ | ---------- |
| devel | 3.12, 3.13, 3.14 | 3.12, 3.13, 3.14 |
| milestone | 3.12, 3.13, 3.14 | 3.12, 3.13, 3.14 |
| stable-2.20 | 3.12, 3.13, 3.14 | 3.12, 3.13, 3.14 |
| stable-2.19 | 3.11, 3.12, 3.13 | 3.11, 3.12, 3.13, 3.14 |
| stable-2.18 | 3.11, 3.12, 3.13 | 3.11, 3.12, 3.13, 3.14 |
| stable-2.17 | 3.10, 3.11, 3.12 | 3.10, 3.11, 3.12 |
