# Site Builder

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

This is a set of Python scripts for installing HTML, PHP-based, or Python-based sites on a Linux server, particularly an [Amazon Web Services (AWS)](https://aws.amazon.com/) EC2 sever.  It can be used for either development or production.  Among other things, it:

- Clones (copies) code from different repositories
- Creates MySQL databases and users
- Sets up NGINX configuration files (production only)
- Generates SSL certificates (production only)
- Sets up Google reCAPTCHAv3 keys
- Creates and sets up systemd services for Gunicorn

The files provided are used to create [https://spiffindustries.com/](https://spiffindustries.com/)

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Background

At a certain point it became of interest to create a repository for the Spiff Industries.  Rather than create backups of raw code, it seemed better to take the same approach as the Raspberry Pi [initpi](https://github.com/rbrutherford3/initpi) project and develop software to streamline installation of the site on a blank server.  In the end, a [separate repository](https://github.com/rbrutherford3/Spiff-Industries-Website.git) was created for the static portion of the site while creating this project to build the other modules and server configuration.  It was made as abstract as possible for general distribution. 

## Install

To install the repository, simply clone it:

```
git clone https://github.com/rbrutherford3/Site-Builder.git
```

There are two dependent Python files that are omitted from this repository:

- `passwords.py`
- `recaptchav3.py`

Create each of these files in the root directory of the project, replacing the values with your own.

`passwords.py`:

```
#!/bin/python3

# Class for storing passwords
class Passwords:
    baltaa_password = "password"
    lesley_password = "password"
```

`recaptchav3.py`:

```
#!/bin/python3

# Class for storing the Google reCAPTCHAv3 keys
class reCAPTCHAv3:
    local_site_key = "GOOGLE_RECAPTCHA_V3_SITE_KEY_1"
    local_secret_key = "GOOGLE_RECAPTCHA_V3_SECRET_KEY_1"
    aws_site_key = "GOOGLE_RECAPTCHA_V3_SITE_KEY_2"
    aws_secret_key = "GOOGLE_RECAPTCHA_V3_SECRET_KEY_2"
```

Note that, without these files, the installations `lesley.py` and `baltaa.py` will fail.  Some installations include supporting files, such as `.sql` database installations that are required to set the site up for initial use.

## Usage

To install the Spiff Industries website on a server, simply run `site.py` as root:
```
sudo python3 site.py
```
If installing on a development server, use the `--debug` or `-d` option:
```
sudo python3 site.py --debug
```
Note that each module has its own installation, including the root module which inludes all the root HTML files.  `site.py` invokes all of these modules separately.  If you wish to be more selective, you can run scripts indvidually, instead.  They are:

- `spiffindustries.py`
- `baltaa.py`
- `chess.py`
- `lesley.py`

Each script also has the debug option available, if desired.

> **NOTE:** 
>
>`sitebuilder.py` is the heart of the program and can be used to create a different site on a similar server the same way the component sites for spiffindustries.com were created.

## Contributing

Please contact rbrutherford3 on GitHub if interested in contribution.

## License

[MIT © Robert Rutherford](../LICENSE)
