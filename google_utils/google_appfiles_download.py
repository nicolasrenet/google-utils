#!/usr/bin/env python3

import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from pathlib import Path
from argparse import ArgumentParser
import re


def main():

    SCOPES = ['https://www.googleapis.com/auth/drive']

    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    

    parser = ArgumentParser(prog=f'{sys.argv[0]}', description='Download Google appfiles from Drive.')
    parser.add_argument('-n', '--dry-run', help='List the files that would be downloaded instead.', action='store_true')
    parser.add_argument('google_pathname', nargs='+', help='A "*.desktop" file or folder path.', type=str)

    args = parser.parse_args()

    present = 0
    failed = []
    count = 0

    for file_pathname in args.google_pathname:

        file_path = Path( file_pathname )
        if not file_path.exists():
            print("Check that the provided path {file_pathname} exists.")
            print("USAGE: ", USAGE_STR)
            sys.exit()

        if file_path.is_dir():

            for sl_file_path in file_path.glob('*.desktop'):
                present += 1
                count += retrieve_content(service, sl_file_path, failed, dry_run=args.dry_run )
        elif file_path.suffix == '.desktop':
            present += 1
            count += retrieve_content(service, file_path, failed, dry_run=args.dry_run )

    if args.dry_run:
        print('(DRY RUN: no file downloaded)')
    if failed:
        print('Failures:')
    for fl in failed:
        print('\n'+'\n'.join([ f'File path: {fl[0]}', f'URL: {fl[1]}', f'Mesg: {fl[2]}']))
    print(f'{present} files processed; {count} files successfully downloaded; {len(failed)} failures.')


def retrieve_content(service: Resource, fp: Path, failed: list, dry_run: bool=False):

        print(fp)
        file_keys = symbolic_link_to_document_info( str(fp) )

        try:

            if file_keys is None or dry_run:
                return 0

            data = service.files().export(fileId=file_keys['Id'], mimeType=file_keys['Mime']).execute()
            if data:
                filename = file_keys['Name']
                with open(filename, 'wb') as pdf_file:
                    pdf_file.write(data)
            return 1
   
        except HttpError as error:
            # TODO: keep track of which files have failed on oversize
            print(f'An error occurred: {error}')
            details = re.search(r'Details: (.*)$', str(error) )
            failed.append( (str(file_path), file_keys['URL'], details.group(1) if details else 'Unknown reason') )
            return 0


def symbolic_link_to_document_info( sl: str ):

    with open(sl, 'r') as slin:
        file_keys = {}
        for line in slin:
            keyword = re.match(r'(URL|Name)=(.+)$', line)
            if keyword:
                file_keys[keyword.group(1)] = keyword.group(2)
        url_blocks = re.search(r'google.com\/([^/]+)\/d/([^/]+)\/', file_keys['URL'])
        if url_blocks is None:
            return None
        file_type, file_id = url_blocks.group(1), url_blocks.group(2)
        file_keys['Id']=file_id

        if file_type not in ['document', 'spreadsheets', 'presentation']:
            return None
        if file_type == 'document':
            file_keys['Name']+='.odt'
            file_keys['Mime']='application/vnd.oasis.opendocument.text'
            return file_keys
        elif file_type == 'spreadsheets':
            file_keys['Name']+='.ods'
            file_keys['Mime']='application/vnd.oasis.opendocument.spreadsheet'
        elif file_type == 'presentation':
            file_keys['Name']+='.odp'
            file_keys['Mime']='application/vnd.oasis.opendocument.presentation'

        print(file_keys)
        return file_keys

if __name__ == '__main__':
    main()
