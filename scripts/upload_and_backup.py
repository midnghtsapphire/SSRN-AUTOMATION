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
        self.github_repo = "midnghtsapphire/SSRN_Whitepapers"
        self.github_dir = Path("/home/ubuntu/SSRN_Whitepapers")
        
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
    
    def backup_to_github(self, pdf_path, metadata=None):
        """Backup PDF to GitHub repository"""
        print(f"\n→ Backing up to GitHub...")
        
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ Error: File not found: {pdf_path}")
            return False
        
        # Verify filename starts with Walter_Evans_
        if not pdf_path.name.startswith('Walter_Evans_'):
            print(f"❌ Error: Filename must start with 'Walter_Evans_': {pdf_path.name}")
            return False
        
        # Clone or pull repository
        if not self.github_dir.exists():
            print(f"→ Cloning repository...")
            result = subprocess.run(
                ['gh', 'repo', 'clone', self.github_repo, str(self.github_dir)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Clone failed: {result.stderr}")
                return False
        else:
            print(f"→ Pulling latest changes...")
            result = subprocess.run(
                ['git', '-C', str(self.github_dir), 'pull'],
                capture_output=True,
                text=True
            )
        
        # Copy PDF to repository
        import shutil
        dest_path = self.github_dir / pdf_path.name
        shutil.copy2(pdf_path, dest_path)
        print(f"✅ Copied to repository: {dest_path}")
        
        # Git add
        subprocess.run(
            ['git', '-C', str(self.github_dir), 'add', pdf_path.name],
            capture_output=True
        )
        
        # Git commit
        commit_msg = f"Add paper: {pdf_path.name}"
        if metadata:
            commit_msg += f"\n\nTitle: {metadata.get('title', 'N/A')}"
            commit_msg += f"\nDate: {metadata.get('date', 'N/A')}"
            commit_msg += f"\nKeywords: {metadata.get('keywords', 'N/A')}"
        
        result = subprocess.run(
            ['git', '-C', str(self.github_dir), 'commit', '-m', commit_msg],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 and 'nothing to commit' not in result.stdout:
            print(f"❌ Commit failed: {result.stderr}")
            return False
        
        # Git push
        print(f"→ Pushing to GitHub...")
        result = subprocess.run(
            ['git', '-C', str(self.github_dir), 'push'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Pushed to GitHub: {self.github_repo}")
            
            # Get commit hash
            result = subprocess.run(
                ['git', '-C', str(self.github_dir), 'log', '-1', '--format=%H'],
                capture_output=True,
                text=True
            )
            commit_hash = result.stdout.strip()
            commit_url = f"https://github.com/{self.github_repo}/commit/{commit_hash}"
            print(f"📎 Commit URL: {commit_url}")
            
            return commit_url
        else:
            print(f"❌ Push failed: {result.stderr}")
            return False
    
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
        """Complete upload and backup process"""
        print(f"\n{'='*60}")
        print("SSRN Paper Upload & Backup")
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
        
        # Backup to GitHub
        github_url = self.backup_to_github(pdf_path, metadata)
        
        # Verify upload
        self.verify_upload(pdf_path.name)
        
        print(f"\n{'='*60}")
        if gdrive_link and github_url:
            print("✅ Upload and backup complete!")
            print(f"\nGoogle Drive: {gdrive_link}")
            print(f"GitHub: {github_url}")
        else:
            print("⚠️  Upload or backup incomplete. Please check errors above.")
        print(f"{'='*60}\n")
        
        return {
            'gdrive_link': gdrive_link,
            'github_url': github_url
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
