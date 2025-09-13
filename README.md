# Temp Email 

A PyQt5-based desktop application to create and listen to temporary email addresses using MailTM

## Features

* Generate temporary email addresses.
* Optional custom username and password registration.
* Real-time inbox listener for incoming emails.
* View email content (plain text or HTML) in a readable format.
* Copy email address to clipboard automatically.
* Simple and modern GUI with PyQt5.


## Installation

1. Clone this repository:

```bash
git clone https://github.com/skun0/temp-mail.git
cd temp-mail
```

2. Run the application:

```bash
python main.py
```

## Usage

1. Launch the app.
2. (Optional) Enter a custom username and password.
3. Click **Start Email Listener**.
4. The generated temporary email will appear and be copied to your clipboard.
5. Incoming emails will be listed in the inbox list. Click an email to view its content.

## Dependencies

* [PyQt5](https://pypi.org/project/PyQt5/) — GUI framework
* [mailtm](https://pypi.org/project/mailtm/) — Temporary email service API

You can install dependencies manually:

```bash
pip install PyQt5 mailtm
```
