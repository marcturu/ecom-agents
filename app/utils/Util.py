"""
.. module:: Util.py

Util.py
******

:Description: Util.py

    Different Auxiliary functions used for different purposes

"""
import socket

from pif import get_public_ip

__author__ = 'SergiMarcMiquel'


def gethostname():
    try:
        return socket.gethostbyaddr(get_public_ip())[0]  # type: ignore
    except:
        return socket.gethostname()
