import argparse
import sys
import signal
import logging
import time
import os
import glob

logging.basicConfig(filename='test.log', level=logging.INFO,
                    format='%(levelname)s:%(message)s')

exit_flag = False


def signal_handler(sig_num, frame):
    global exit_flag
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here
    as well (SIGHUP?) Basically it just sets a global flag, and main() will
    exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    print 'Signal Number ', sig_num
    signame = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                   if v.startswith('SIG') and not v.startswith('SIG_'))
    logging.warn('Received {}'.format(signame[sig_num]))
    exit_flag = True


def search_files(directory):
    global path_to_watch
    original_directory = os.getcwd()
    os.chdir(directory)

    for file in glob.glob('*.txt'):
        file_object = open(file, 'r')
        line_num = 0
        search_phrase = 'magic-string'

        for line in file_object.readlines():
            line_num += 1
            with open(original_directory + '/' + 'test.log') as logfile:
                log_text = logfile.read()
                if line.find(search_phrase) >= 0:
                    if ('INFO: ' + str(line_num) + ' ' + file + " "
                            + search_phrase not in log_text):
                        logging.info(" " + str(line_num) + " " + file +
                                     " " + search_phrase)
    os.chdir(original_directory)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='dir to monitor for magic string')
    return parser


def main(args):
    start_time = time.time()
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)
    path_to_watch = './' + parsed_args.directory
    before = dict([(f, None) for f in os.listdir(path_to_watch)])

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logging.info('Searching for string in {}'.format(parsed_args.directory))

    while not exit_flag:
        try:
            time.sleep(2.0)
            search_files('./' + parsed_args.directory)

            after = dict([(f, None) for f in os.listdir(path_to_watch)])
            added = [f for f in after if f not in before]
            removed = [f for f in before if f not in after]

            if added:
                for each in added:
                    logging.info('Added: ' + each)

            if removed:
                for each in removed:
                    logging.info('Removed: ' + each)

            before = after

        except Exception:
            time.sleep(5.0)
            logging.exception('Exception')

    logging.info("""Stopped dirwatcher.py -
                Uptime was {} seconds""".format(time.time() - start_time))


if __name__ == '__main__':
    main(sys.argv[1:])
