# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # 头部加上这句
from flask import Flask, render_template, request, make_response, redirect, flash, get_flashed_messages
import logging
from logging.handlers import RotatingFileHandler
