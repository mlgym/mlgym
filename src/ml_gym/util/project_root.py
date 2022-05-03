#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os


def get_project_root():
    """
    get project root
    """
    project_root_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
    return project_root_dir
