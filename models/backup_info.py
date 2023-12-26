# -*- coding: utf-8 -*-
import base64
import os
import subprocess

import pytz
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import config
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class backup_info(models.Model):
    _name = 'autonsi.server'
    _description = 'autonsi_server.autonsi_server'

    dbhost = fields.Char(string="Host", required=True)
    dbname = fields.Char(string="Database's name", required=True)
    dbpassword = fields.Char(string="Master Password", required=True)
    
    TERM_SELECTION = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    PLACE_SELECTION = [
        ('google_drive', 'Google Drive'),
        ('amazon_s3', 'Amazon S3'),
    ]

    company = fields.Many2one('res.partner', required=True)
    date_of_use = fields.Date(string="Date of use")
    place = fields.Selection(selection=PLACE_SELECTION, string='Auto backup', required=True)
    last_backup = fields.Datetime(string="Last backup" , readonly=True)
    schedule = fields.Integer(string='Schedule (Hours)', required=True, default=1, min_value=1, max_value=24)
    term = fields.Selection(selection=TERM_SELECTION, string='Term', required=True)
    autorestore = fields.Boolean(string='Auto restore')
    status = fields.Boolean(string='Status', readonly=True)

    @api.constrains('schedule')
    def _check_schedule_range(self):
        for record in self:
            if record.schedule < 1 or record.schedule > 24:
                raise ValidationError("Schedule value must be between 1 and 24.")

    def scheduleTask(self):
        model = self.env['autonsi.server']
        records = model.search([])
        for record in records:
            self.perform_backup(record)

    def perform_backup(self,record):
        # self.backup(record)
        # return
        utc_now = datetime.utcnow()
        gmt_plus_7 = pytz.timezone('Asia/Bangkok')
        current_datetime = utc_now.replace(tzinfo=pytz.utc).astimezone(gmt_plus_7)

        #current_datetime = datetime.now()
        
        current_hour = current_datetime.hour
        current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        if (record.last_backup == False) :
            record.write({
                'last_backup': current_datetime_str
            })
            self.backup(record)
            return
        difference = 0
        if (record.term == "daily") :
            difference = (current_datetime - record.last_backup).days
        elif (record.term == "weekly") :
            difference = (current_datetime - record.last_backup).days // 7
        elif (record.term == "monthly") :
            difference = (current_datetime.year - record.last_backup.year) * 12 + current_datetime.month - record.last_backup.month
        if (difference == 0 or current_hour != record.schedule) :
            return
        self.backup(record)

    def backup(self,record):
        file_name = record.dbname+"_" + get_date_string() +".zip"
        file_path = os.path.join("/tmp", file_name)

        self.postgres_backup(record, file_path)
        if (record.autorestore == True) :
            self.postgres_restore(record, file_path)
        if (record.place == "google_drive") :
            self.upload_google_drive(record,file_path)
        elif (record.place == "amazon_s3") :
            self.upload_amazon_s3(file_path)
        
        history = self.env['autonsi.server_backup_history']
        values = {
            'date': datetime.now(),
            'db_name': record.dbname,
            'device': "OK",
            'file_name': file_name,
            'status': True,
        }
        history.create(values)

        os.remove(file_path)

    def postgres_backup(self, record, path):
        url = f"http://{record.dbhost}:8069/web/database/backup"
        db = record.dbname
        password = record.dbpassword
        command = [
            "curl", "-X", "POST",
            "-F", f"master_pwd={password}",
            "-F", f"name={db}",
            "-F", "backup_format=zip",
            "-o", path,
            url
        ]
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        print(result.stderr)

    def postgres_restore(self, record, path) :
        url = f"http://{record.dbhost}:8069/web/database/restore"
        password = record.dbpassword
        dbname = os.path.basename(path).split('.')[0]
        command = [
            "curl",
            "-F", f"master_pwd={password}",
            "-F", f"backup_file=@{path}",
            "-F", "copy=true",
            "-F", f"name={dbname}",
            url
        ]
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        print(result.stderr)

    def upload_google_drive(self, record,file_path) :
        folderId = record.company.folder_id
        if (folderId == None) :
            return
        credentials_path = os.path.join('/tmp', "service"+str(record.id)+".json")
        
        with open(credentials_path, 'wb') as f:
            f.write(base64.b64decode(record.company.service_file))

        credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=['https://www.googleapis.com/auth/drive'])
        service = build('drive', 'v3', credentials=credentials)
        media = MediaFileUpload(file_path)
        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [folderId]
        }
        file = service.files().create(body=file_metadata, media_body=media, fields='id,name').execute()
        print(f"File '{file_name}' uploaded to Google Drive with ID: {file['id']}")
        os.remove(credentials_path)
        
    def upload_amazon_s3(self,db_name,file_path) :
        print("Dummy upload amazon s3 ")

def execute_command(command_args, output_file = None):
    try:
        if (output_file == None) :
            return subprocess.run(command_args, stderr=subprocess.PIPE, check=True).returncode
            # Open a binary file for writing the output
        with open(output_file, "wb") as output_handle:
            # Execute the command and capture its output
            result = subprocess.run(command_args, stdout=output_handle, stderr=subprocess.PIPE, check=True)
            # Return the command's return code
    except Exception as e:
        print(e)
    
def get_date_string():
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d-%h-%m-%s")
    return date_string

def get_module_path(module_name):
    addons_path = config.get('addons_path')
    module_path = False
    addons_paths = addons_path.split(',')
    for path in addons_paths:
        module_path_candidate = os.path.join(path.strip(), module_name)
        if os.path.isdir(module_path_candidate):
            module_path = module_path_candidate
            break
    return module_path