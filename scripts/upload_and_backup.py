#!/usr/bin/env python3
"""
SSRN Paper Upload and Backup
Uploads papers to Google Drive and backs up to GitHub
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class PaperUploader:
    """Handles paper upload and backup operations"""
    
    def __init__(self):
        self.gdrive_folder_id = "1qVmicFsMOLngIoRIAkeVZNreVblXbLic"
        self.gdrive_config = "/home/ubuntu/.gdrive-rclone.ini"
        # Papers stored locally in output/ directory only
        # No GitHub backup of papers (only automation scripts)
        
    def upload_to_gdrive(self, pdf_path):
        """Upload PDF to Google Drive"""
        print(f"\n→ Uploading to Google Drive...")
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ Error: File not found: {pdf_path}")
            return False
        
        # Verify filename starts with Walter_Evans_
        if not pdf_path.name.startswith('Walter_Evans_'):
            print(f"❌ Error: Filename must start with 'Walter_Evans_': {pdf_path.name}")
            return False
        
        # Upload using rclone
        cmd = [
            'rclone', 'copy',
            str(pdf_path),
            f'manus_google_drive:{self.gdrive_folder_id}',
            '--config', self.gdrive_config
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Uploaded to Google Drive: {pdf_path.name}")
            
            # Generate shareable link
            link_cmd = [
                'rclone', 'link',
                f'manus_google_drive:{self.gdrive_folder_id}/{pdf_path.name}',
                '--config', self.gdrive_config
            ]
            
            link_result = subprocess.run(link_cmd, capture_output=True, text=True)
            if link_result.returncode == 0:
                link = link_result.stdout.strip()
                print(f"📎 Shareable link: {link}")
                return link
            
            return True
        else:
            print(f"❌ Upload failed: {result.stderr}")
            return False
    
    def store_locally(self, pdf_path):
        """Store PDF in local output directory (already there, just verify)"""
        print(f"\n→ Verifying local storage...")
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ Error: File not found: {pdf_path}")
            return False
        
        # Verify filename starts with Walter_Evans_
        if not pdf_path.name.startswith('Walter_Evans_'):
            print(f"❌ Error: Filename must start with 'Walter_Evans_': {pdf_path.name}")
            return False
        
        print(f"✅ Paper stored locally: {pdf_path}")
        print(f"   Location: {pdf_path.parent}")
        print(f"   Note: Papers are NOT committed to GitHub (only stored in output/ directory)")
        
        return str(pdf_path)
    
    def verify_upload(self, filename):
        """Verify file exists in Google Drive"""
        cmd = [
            'rclone', 'ls',
            f'manus_google_drive:{self.gdrive_folder_id}',
            '--config', self.gdrive_config
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if filename in result.stdout:
            print(f"✅ Verified in Google Drive: {filename}")
            return True
        else:
            print(f"⚠️  Not found in Google Drive: {filename}")
            return False
    
    def process_paper(self, pdf_path, metadata_path=None):
        """Complete upload process (Google Drive only)"""
        print(f"\n{'='*60}")
        print("SSRN Paper Upload")
        print(f"{'='*60}\n")
        
        pdf_path = Path(pdf_path)
        print(f"Paper: {pdf_path.name}\n")
        
        # Load metadata if provided
        metadata = None
        if metadata_path:
            import json
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        # Upload to Google Drive
        gdrive_link = self.upload_to_gdrive(pdf_path)
        
        # Verify local storage
        local_path = self.store_locally(pdf_path)
        
        # Verify upload
        self.verify_upload(pdf_path.name)
        
        print(f"\n{'='*60}")
        if gdrive_link and local_path:
            print("✅ Upload complete!")
            print(f"\nGoogle Drive: {gdrive_link}")
            print(f"Local Storage: {local_path}")
        else:
            print("⚠️  Upload incomplete. Please check errors above.")
        print(f"{'='*60}\n")
        
        return {
            'gdrive_link': gdrive_link,
            'local_path': local_path
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_and_backup.py <pdf_path> [metadata_json_path]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    metadata_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    uploader = PaperUploader()
    uploader.process_paper(pdf_path, metadata_path)


if __name__ == '__main__':
    main()
