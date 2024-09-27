#!/usr/bin/env python3

from __future__ import print_function

import os.path
import sys

from pathlib import Path
from argparse import ArgumentParser
import gdown
import re


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
                count += retrieve_content( sl_file_path, failed, dry_run=args.dry_run )
        elif file_path.suffix == '.desktop':
            present += 1
            count += retrieve_content( file_path, failed, dry_run=args.dry_run )

    if args.dry_run:
        print('(DRY RUN: no file downloaded)')
    print(f'{present} files processed; {count} files successfully downloaded; {len(failed)} failures.')

    for fl in failed:
        print('\n'+'\n'.join([ f'File path: {fl[0]}', f'URL: {fl[1]}', f'Mesg: {fl[2]}']))

def retrieve_content( fp: Path, failed: list, dry_run: bool=False):

            print(fp)

            file_keys = symbolic_link_to_document_info( str(fp) )
            error_str = ''

            try:

                if file_keys is None or dry_run:
                    return 0

                gdown.download(id=file_keys['Id'], output=file_keys['Name'])

                return 1
                
            except Exception as error:
                altURL = ''
                s = re.search(r'https://drive.google.com\S+', str(error))
                altURL = s.group(0) if s else ''
                failed.append( (str(fp), 
                                file_keys['URL'], 
                                'Cannot retrieve the public link of the file.' + ( f' Try download manually from {altURL}.' if altURL else '')))
                return 0


if __name__ == '__main__':
    main()
