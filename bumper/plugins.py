#!/usr/bin/env python3
import asyncio
from aiohttp import web

class ConfServerApp():
    name = None
    plugin_type = None
    path_prefix = None
    app = None
    sub_api = None
    routes = None
    
    
