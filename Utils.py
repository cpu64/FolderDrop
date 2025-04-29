import datetime
import os
import igd
import curio
import socket
from enum import IntEnum
from requests import get

class Sort(IntEnum):
    NAME_ASCENDING = 1
    NAME_DESCENDING = 2
    SIZE_ASCENDING = 3
    SIZE_DESCENDING = 4
    DATE_ASCENDING = 5
    DATE_DESCENDING = 6

def to_bytes(size: float, unit: str) -> float:
    """Convert a size in human-readable format to bytes."""
    units = {
        "B": 1,
        "KiB": 1024,
        "MiB": 1024**2,
        "GiB": 1024**3,
        "TiB": 1024**4,
        "PiB": 1024**5,
        "EiB": 1024**6,
        "ZiB": 1024**7,
    }
    return size * units[unit]

def from_bytes(size: float, unit: str) -> float:
    """Convert a size in bytes to a human-readable format."""
    units = {
        "B": 1,
        "KiB": 1024,
        "MiB": 1024**2,
        "GiB": 1024**3,
        "TiB": 1024**4,
        "PiB": 1024**5,
        "EiB": 1024**6,
        "ZiB": 1024**7,
    }
    return size / units[unit]


def size_human_readable(size):
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"):
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}YiB"

def size_of_dir(path: str):
    size = 0
    for path, dirs, files in os.walk(path):
        for f in files:
            size += os.path.getsize(os.path.join(path, f))
    return size

def num_of_items(path: str):
    try:
        return len(os.listdir(path))
    except OSError:
        return 0 

# Get the contents of a directory
# Returns a list of tuples with the following format:
# (type, name, size, modified time)
# type: 'd' for directory, 'f' for file
# name: The name of the file or directory
# size: The size of the file or directory in human readable format
# modified time: The last modified time of the file or directory
def get_contents(path: str, order: Sort):
    contents = []
    for f in os.listdir(path):
        mod_time = os.path.getmtime(os.path.join(path, f))
        if os.path.isdir(os.path.join(path, f)):
            size = size_of_dir(os.path.join(path, f))
            contents.append(('d', f, size, mod_time))
        elif os.path.isfile(os.path.join(path, f)):
            size = os.path.getsize(os.path.join(path, f))
            contents.append(('f', f, size, mod_time))
    match order:
        case Sort.NAME_ASCENDING:
            contents.sort(key=lambda tup: tup[1], reverse=False)
        case Sort.NAME_DESCENDING:
            contents.sort(key=lambda tup: tup[1], reverse=True)
        case Sort.SIZE_ASCENDING:
            contents.sort(key=lambda tup: tup[2], reverse=False)
        case Sort.SIZE_DESCENDING:
            contents.sort(key=lambda tup: tup[2], reverse=True)
        case Sort.DATE_ASCENDING:
            contents.sort(key=lambda tup: tup[3], reverse=False)
        case Sort.DATE_DESCENDING:
            contents.sort(key=lambda tup: tup[3], reverse=True)

    res = [(i[0], i[1], size_human_readable(i[2]), datetime.datetime.fromtimestamp(i[3]).replace(microsecond=0).isoformat(' ')) for i in contents]
    res.sort(key=lambda tup: tup[0])
    return res

def ping(host="8.8.8.8", port=53, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    except OSError as error:
        return False
    else:
        s.close()
        return True

def get_local_ip(ip):
    try:
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((ip, 80))
        return s.getsockname()[0]
    except Exception as e:
        raise Exception("Local ip not found. Can't proceed.") from e

async def get_gateway():
    try:
        async with curio.timeout_after(2):
            gateway = await igd.find_gateway()
            gateway = gateway.ip
    except:
        try:
            import netifaces
            gateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
            if not ping(gateway, 80, 1):
                raise Exception
        except:
            if not ping("192.168.0.1", 80, 1):
                print("Gateway not found.")
                return False
            gateway = "192.168.0.1"
    return gateway

async def get_public_ip():
    try:
        async with curio.timeout_after(2):
            gateway = await igd.find_gateway()
        async with curio.timeout_after(2):
            ip = await gateway.get_ext_ip()
        return ip
    except:
        return False

async def open_port(local_ip, port):
    try:
        async with curio.timeout_after(2):
            gateway = await igd.find_gateway()
            mapping = igd.proto.PortMapping(remote_host='', external_port=port, internal_port=port,
                protocol='TCP', ip=local_ip, enabled=True, description='FolderDrop', duration=12*60*60)
            await gateway.add_port_mapping(mapping)
    except curio.TaskTimeout as e:
        raise Exception(f"Trying to open a port took too long. It's likely the router doesn't support the required protocols and FolderDrop will not work outside your local network. (original: {repr(e)})")
    except igd.soap.HttpError as e:
        raise Exception(f"Failed to open a port. FolderDrop will not work outside your local network. (original: {repr(e)})")
    return gateway
