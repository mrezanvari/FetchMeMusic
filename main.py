# This Version of the code is programmed for macOS X and python +3.8,
# meaning that it uses pytube3 NOT pytube, pip3 instal pytube3
from imap_tools import MailBox, Q
from pytube import YouTube
import signal
from subprocess import TimeoutExpired
# import winsound
import sys
import os

frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second

# desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  #for windows

desktop = os.path.expanduser("~/Desktop/")
directory = desktop + '/SongDownloaded'
lstHosts = ['Chill Nation', 'Trap Nation', 'Trap City', 'Bass Nation', 'Future Bass', 'Lowly.', 'NoCopyrightSounds',
            'Teminite']

file_size = 0


def input_with_timeout(prompt, timeout):
    # set signal handler
    def alarm_handler(signum, frame):
        raise TimeoutExpired

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout)  # produce SIGALRM in `timeout` seconds

    try:
        return input(prompt)
    finally:
        signal.alarm(0)  # cancel alarm

def on_progress(chunk, file_handler, bytes_remaining):
    # Gets the percentage of the file that has been downloaded.
    percent = (100 * (file_size - bytes_remaining)) / file_size
    print('\033[92m' + '            {:00.0f}% downloaded'.format(percent) + '\033[0m', end='\r')


def downloadUreadYoutubeEmails():
    try:
        with MailBox('imap.gmail.com').login('urmail@gmail.com', 'somePass!') as mailbox:
            print('\n\n******')
            for msg in mailbox.fetch(Q(seen=False), mark_seen=False):
                if msg.from_ == 'noreply@youtube.com':
                    for host in lstHosts:
                        if host in msg.subject:

                            lnk = msg.text.splitlines()[2].split('&', 1)[0]  # pulls out the herf

                            yt = YouTube(lnk)

                            if yt.title == 'YouTube': # Somethimes s*%t happens and the title doesnt load so read it from email text...
                                title = msg.text.splitlines()[1]
                            else:
                                title = yt.title

                            yt.register_on_progress_callback(on_progress)

                            print(host + ' --> ' + title + '\r\n')

                            try:
                                os.stat(directory)
                            except:
                                os.mkdir(directory)

                            video = yt.streams.first()

                            global file_size
                            file_size = video.filesize

                            video.download(output_path=directory, filename=title + ' (' + lnk + ')')
                            # f = open(directory + '/_lstDownloaded.txt', 'a+')
                            # f.write('\r\n' + title)
                            # f.close()
                            MailBox.seen(mailbox, msg.uid, seen_val = True)
                            MailBox.flag(mailbox, msg.uid, 'DELETED', True)
                            MailBox.delete(mailbox, msg.uid)
                            return 1
            return 0
    except Exception as ex:
        # winsound.Beep(frequency, duration)
        print(str(ex.__doc__))

        if 'pytube' in str(ex.__class__):
            print('\033[91m' + '\r\n\r\nDELETED!!!' + '\033[0m')
            with MailBox('imap.gmail.com').login('urmail@mail.com', 'somePass!') as mailbox:
                MailBox.seen(mailbox, msg.uid, seen_val = True)
                MailBox.delete(mailbox, msg.uid)
        else:
            print('\033[91m' + str(ex.__class__))
            try:
                strInput = input_with_timeout('\033[91m' + '\r\nWould You Like To Continue?! This will delete the email with error and continue... Y/N\r\n\r\n' + '\033[0m', 6)
                if strInput.lower() == 'y':
                    print('\033[91m' + '\r\n\r\nDELETED!!!' + '\033[0m')
                    with MailBox('imap.gmail.com').login('urmail@mail.com', 'somePass!') as mailbox:
                        MailBox.seen(mailbox, msg.uid, seen_val=True)
                        MailBox.delete(mailbox, msg.uid)
                        return 1
                else:
                    print('\033[91m' + '\r\n\r\nProgram Error!   :(\r\n\r\nProgram Terminated!' + '\033[0m' + '\r\n\r\n')
                    return 0

            except:
                print('\033[91m' + 'input time out! I will continue but I wont delete the email that caused this...!' + '\033[0m' + '\r\n\r\n\r\n')
                with MailBox('imap.gmail.com').login('urmail@mail.com', 'somePass!') as mailbox:
                    MailBox.seen(mailbox, msg.uid, seen_val=True)
                    return 1

        return 1


while (True):
    ExitHandler = downloadUreadYoutubeEmails()
    if ExitHandler == 0: quit()

