#!/usr/bin/env python3

from __future__ import print_function

import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from pathlib import Path
import gdown
import re


USAGE_STR = f"{sys.argv[0]} <locally mounted google drive folder path>"



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
            file_keys['Name']+='.docx'
            file_keys['Mime']='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            return file_keys
        elif file_type == 'spreadsheets':
            file_keys['Name']+='.xlsx'
            file_keys['Mime']='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif file_type == 'presentation':
            file_keys['Name']+='.pptx'
            file_keys['Mime']='application/vnd.openxmlformats-officedocument.presentationml.presentation'

        print(file_keys)
        return file_keys


def main():


    if len(sys.argv) < 2 or sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print("USAGE: ", USAGE_STR)
        sys.exit()

    if not Path(sys.argv[1]).exists():
        print("Check that the provided path exists.")
        print("USAGE: ", USAGE_STR)
        sys.exit()
        
    google_folder_path = sys.argv[1] 


    
    failed = [] 
    count = 0
    for file_path in Path(google_folder_path).glob('*.desktop'):
        print(file_path)
        file_keys = symbolic_link_to_document_info( str(file_path) )

        try:

            if file_keys is None:
                continue

            gdown.download(id=file_keys['Id'], output=file_keys['Name'])
            
   
        except (HttpError,  as error:
            # TODO: keep track of which files have failed on oversize
            print(f'An error occurred: {error}')
            details = re.search(r'Details: (.*)$', str(error) )
            failed.append( (str(file_path), file_keys['URL'], details.group(1) if details else 'Unknown reason') )
            continue

    print(f'{count} files successfully downloaded; {len(failed)} failures.')
    if failed:
        print('Failures:')
        for fl in failed:
            print('\n'.join([ f'File path: {fl[0]}', f'URL: {fl[1]}', 
                             f'Reason: {fl[2]}' ]), '\n') 



if __name__ == '__main__':
    main()
