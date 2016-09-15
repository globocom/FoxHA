# -*- coding: utf-8 -*-

import ConfigParser
import logging
from logging import handlers
from os import path
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from .print_format import print_error


class Utils(object):

    @staticmethod
    def get_key_path():
        return path.dirname(__file__) + '/../config/.key'

    @staticmethod
    def get_config_path():
        return path.dirname(__file__) + '/../config/foxha_config.ini'

    @staticmethod
    def parse_config_file(
            cipher_suite, config_file="./config/foxha_config.ini"
    ):
        try:
            repo_host, repo_port, repo_database, repo_user,\
                encrypted_repo_pass =\
                Utils.get_config_values_from_config_file(config_file)
        except (ConfigParser.NoSectionError) as err:
            print_error("Config file error: {}".format(err))
            exit(99)
        except (ConfigParser.NoOptionError) as err:
            print_error("Config file error: {}".format(err))
            exit(99)

        try:
            decrypted_repo_pass = cipher_suite.decrypt(encrypted_repo_pass)
            return repo_host, repo_port, repo_database,\
                repo_user, decrypted_repo_pass
        except InvalidToken as e:
            print_error("ERROR: InvalidToken")
            exit(99)
        except Exception as e:
            print_error("ERROR: %s" % e)
            exit(3)

    @staticmethod
    def get_config_values_from_config_file(config_file):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_file)

        return config_parser.get('repository', 'Host'),\
            config_parser.getint('repository', 'Port'),\
            config_parser.get('repository', 'Database'),\
            config_parser.get('repository', 'User'),\
            config_parser.get('repository', 'Pass')

    @staticmethod
    def parse_key_file(keyfile="./config/.key"):
        try:
            key = Utils.get_key_value_from_key_file(keyfile)
        except IOError:
            error_message = "ERROR: \"{}\" file does not exist or you don`t"\
                " have permission to read it.".format(keyfile)
            print_error(error_message)
            exit(3)

        try:
            return Fernet(key)
        except ValueError as e:
            print_error("ERROR: {} may be empty because {}".format(keyfile, e))
            exit(3)
        except TypeError as e:
            print_error("ERROR: {} is not a valid key because {}".format(key, e))
            exit(3)

    @staticmethod
    def get_key_value_from_key_file(key_file):
        key_file_handler = open(key_file, "r+")
        return key_file_handler.readline().rstrip('\n')

    @staticmethod
    def generate_new_keyfile(keyfile=None):
        if not keyfile:
            keyfile = '.new_keyfile'

        try:
            key = Fernet.generate_key()
            f = open(keyfile, 'w')
            f.write(key + '\n')
            f.close()
            keyfile_path = path.abspath(keyfile)
            print "New keyfile generated at %s" % keyfile_path
        except Exception as e:
            print_error("ERROR: %s" % e)
            exit(3)

    @staticmethod
    def crypt_pass(cipher_suite, password):
        try:
            cipher_text = cipher_suite.encrypt(password)
            print cipher_text
        except InvalidToken as e:
            print_error("ERROR: InvalidToken")
            exit(99)

    @staticmethod
    def decrypt_pass(cipher_suite, password):
        try:
            cipher_text = cipher_suite.decrypt(password)
            print cipher_text
        except InvalidToken as e:
            print_error("ERROR: InvalidToken")
            exit(99)

    @staticmethod
    def logfile(logname, logretention=4):
        #logsize = 10485760 #size = 10*1024*1024 - Default equal to 10MB
        logrotation = 1  # 1 Day
        LOGGER = logging.getLogger()
        try:
            handler = logging.handlers.TimedRotatingFileHandler(
                filename=logname, when='midnight', interval=logrotation, backupCount=logretention)
            formatter = logging.Formatter(
                fmt='%(asctime)-4s - %(name)-4s => %(levelname)-5s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            LOGGER.addHandler(handler)
            LOGGER.setLevel(logging.INFO)
            return LOGGER
        except IOError:
            print_error("ERROR: Path does not exist or you don`t have "\
            "permission to the logfile \"%s\"" % logname)
            exit(3)
