# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： m.py.py
    @date：2025/7/28 16:15
    @desc:
"""
import argparse
import os
import sys
import warnings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(os.path.dirname(BASE_DIR), 'apps')
os.chdir(BASE_DIR)
sys.path.insert(0, APP_DIR)

warnings.filterwarnings("ignore", category=UserWarning, module="drf_yasg")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
           MaxKB-v1-to-v2-migrator tools;

           Example: \r\n

           python migrate.py export 
           python migrate.py import ;
           """
    )
    parser.add_argument(
        'action', type=str,
        choices=("export", "import"),
        help="Action to run"
    )
    args = parser.parse_args()
    action = args.action
    if action == "export":
        from exporter import export

        export()
    else:
        from importer import app_import

        app_import()
