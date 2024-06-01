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
        ip = get_public_ip()
        if not ip:
            raise ValueError("Could not obtain public IP")
        return socket.gethostbyaddr(ip)[0]
    except Exception as e:
        print(f"Error: {e}")
        return socket.gethostname()

