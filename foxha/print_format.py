#!/usr/bin/env python
# -*- coding: utf-8 -*-
from colored import fore, style


def fore_red(text, bold=False):
    if bold:
        text = (style.BOLD + fore.RED_3B + text + style.RESET)
    else:
        text = (fore.RED_3B + text + style.RESET)
    
    return text


def fore_green(text):
    return fore.SPRING_GREEN_3A + text + style.RESET


def print_warning(text):
    print fore.LIGHT_YELLOW + text + style.RESET


def print_error(text):
    print fore.RED_3B + text + style.RESET


"""
class ForeColor:
    OKGREEN = '\033[92m'
    OKCYAN = '\033[36m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
"""
